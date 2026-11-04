// Bring-up probe for the salvaged b006-01v0 LCD + q1356-fc-a touch panel.
//
// The pinout and controller models for this panel are unverified, so this
// sketch identifies what is connected instead of assuming it:
//   1. Reads the LCD ID over SDA, using opposite pulls to expose a floating line.
//   2. Runs a generic ST77xx-style init and draws colour fills across full GRAM.
//   3. Keeps scanning I2C, because some touch chips only answer after a touch.
//   4. Reads and draws touches for FocalTech/Hynitron-style chips.
//
// GPIOs follow touchscreen_02/DIY_WIRING_GUIDE.md so the wiring carries over to
// the 2.8-inch screen. The exception is touch INT: the planned D17 is an
// underside pad, so it temporarily uses D9, which is otherwise reserved for SD.
//
// Serial commands: i = toggle inversion, b = toggle RGB/BGR, f = repeat fills,
//                  r = reboot.

#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>

constexpr uint8_t kLcdDc = 1;     // D0
constexpr uint8_t kLcdCs = 2;     // D1
constexpr uint8_t kLcdRst = 4;    // D3
constexpr uint8_t kLcdSck = 7;    // D8
constexpr uint8_t kLcdSda = 9;    // D10
constexpr uint8_t kI2cSda = 5;    // D4
constexpr uint8_t kI2cScl = 6;    // D5
constexpr uint8_t kTouchRst = 44; // D7
constexpr uint8_t kTouchInt = 8;  // D9, temporary

// Conservative for jumper wires on a breadboard.
constexpr uint32_t kSpiHz = 10000000;
// Maximum addressable area of these controllers. Filling all of it means the
// panel's unknown resolution and offset cannot leave part of the glass unpainted.
constexpr uint16_t kGramWidth = 240;
constexpr uint16_t kGramHeight = 320;

constexpr uint8_t kMadctlBgr = 0x08;
constexpr uint16_t kRed = 0xF800;
constexpr uint16_t kGreen = 0x07E0;
constexpr uint16_t kBlue = 0x001F;
constexpr uint16_t kWhite = 0xFFFF;
constexpr uint16_t kBlack = 0x0000;

const SPISettings kSpi(kSpiHz, MSBFIRST, SPI_MODE0);

uint64_t idPullUp = 0;
uint64_t idPullDown = 0;
uint8_t powerModeAfterInit = 0;
bool powerModeDriven = false;
bool inverted = true;
bool bgr = false;
bool sdaIdleHigh = false;
bool sclIdleHigh = false;
bool i2cSeen[128] = {};
uint8_t touchAddress = 0;
volatile uint32_t touchIrqCount = 0;
uint32_t touchReads = 0;
uint32_t lastScan = 0;
uint32_t lastReport = 0;

void IRAM_ATTR onTouchIrq() { touchIrqCount = touchIrqCount + 1; }

// --- Bit-banged LCD reads, run while the SPI peripheral is detached ---------

void bitDelay() { delayMicroseconds(2); }

// Sends a command, then clocks in bitCount bits with SDA as a pulled input.
uint64_t readLcd(uint8_t command, uint8_t bitCount, uint8_t inputMode) {
  pinMode(kLcdSck, OUTPUT);
  pinMode(kLcdSda, OUTPUT);
  digitalWrite(kLcdSck, LOW);
  digitalWrite(kLcdDc, LOW);
  digitalWrite(kLcdCs, LOW);
  bitDelay();
  for (int bit = 7; bit >= 0; --bit) {
    digitalWrite(kLcdSda, (command >> bit) & 1);
    bitDelay();
    digitalWrite(kLcdSck, HIGH);
    bitDelay();
    digitalWrite(kLcdSck, LOW);
  }
  digitalWrite(kLcdDc, HIGH);
  pinMode(kLcdSda, inputMode);
  bitDelay();
  uint64_t value = 0;
  for (uint8_t i = 0; i < bitCount; ++i) {
    digitalWrite(kLcdSck, HIGH);
    bitDelay();
    value = (value << 1) | static_cast<uint64_t>(digitalRead(kLcdSda));
    digitalWrite(kLcdSck, LOW);
    bitDelay();
  }
  digitalWrite(kLcdCs, HIGH);
  pinMode(kLcdSda, OUTPUT);
  return value;
}

// Controllers differ in dummy clocks before the ID, so look at every alignment.
const char *identifyLcd(uint64_t raw) {
  for (uint8_t shift = 0; shift <= 16; ++shift) {
    const uint32_t id = static_cast<uint32_t>(raw >> shift) & 0xFFFFFF;
    if (id == 0x858552) return "ST7789V family";
    if (id == 0x009307) return "GC9307 (likely)";
  }
  return "unrecognised";
}

const char *lcdReplyVerdict() {
  if (idPullUp != idPullDown) return "FLOATING: nothing is driving SDA";
  if (idPullUp == 0) return "STUCK LOW: reads all zero";
  if (idPullUp == 0xFFFFFFFFFFULL) return "STUCK HIGH: reads all ones";
  return "DRIVEN: controller answered";
}

// --- LCD drawing -------------------------------------------------------------

void lcdCommand(uint8_t command, const uint8_t *data = nullptr, size_t length = 0) {
  SPI.beginTransaction(kSpi);
  digitalWrite(kLcdCs, LOW);
  digitalWrite(kLcdDc, LOW);
  SPI.write(command);
  if (length > 0) {
    digitalWrite(kLcdDc, HIGH);
    SPI.writeBytes(data, length);
  }
  digitalWrite(kLcdCs, HIGH);
  SPI.endTransaction();
}

void lcdCommand8(uint8_t command, uint8_t value) { lcdCommand(command, &value, 1); }

void fillRect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color) {
  if (x >= kGramWidth || y >= kGramHeight) return;
  width = min<uint16_t>(width, kGramWidth - x);
  height = min<uint16_t>(height, kGramHeight - y);
  const uint16_t right = x + width - 1;
  const uint16_t bottom = y + height - 1;
  const uint8_t columns[] = {uint8_t(x >> 8), uint8_t(x), uint8_t(right >> 8), uint8_t(right)};
  const uint8_t rows[] = {uint8_t(y >> 8), uint8_t(y), uint8_t(bottom >> 8), uint8_t(bottom)};
  lcdCommand(0x2A, columns, sizeof(columns));
  lcdCommand(0x2B, rows, sizeof(rows));

  static uint8_t line[kGramWidth * 2];
  for (uint16_t i = 0; i < width; ++i) {
    line[i * 2] = color >> 8;
    line[i * 2 + 1] = color & 0xFF;
  }
  SPI.beginTransaction(kSpi);
  digitalWrite(kLcdCs, LOW);
  digitalWrite(kLcdDc, LOW);
  SPI.write(0x2C);
  digitalWrite(kLcdDc, HIGH);
  for (uint16_t row = 0; row < height; ++row) {
    SPI.writeBytes(line, width * 2);
  }
  digitalWrite(kLcdCs, HIGH);
  SPI.endTransaction();
}

void showFills() {
  const struct {
    const char *name;
    uint16_t color;
  } fills[] = {{"RED", kRed}, {"GREEN", kGreen}, {"BLUE", kBlue}, {"WHITE", kWhite}};
  for (const auto &fill : fills) {
    Serial.printf("FILL %s\n", fill.name);
    fillRect(0, 0, kGramWidth, kGramHeight, fill.color);
    delay(1000);
  }
  fillRect(0, 0, kGramWidth, kGramHeight, kBlack);
}

void applyColorMode() {
  lcdCommand(inverted ? 0x21 : 0x20);
  lcdCommand8(0x36, bgr ? kMadctlBgr : 0x00);
  Serial.printf("COLOR inverted=%d bgr=%d\n", inverted, bgr);
}

void initLcd() {
  lcdCommand(0x01); // Software reset
  delay(150);
  lcdCommand(0x11); // Sleep out
  delay(120);
  lcdCommand8(0x3A, 0x55); // RGB565
  applyColorMode();
  lcdCommand(0x13); // Normal mode
  lcdCommand(0x29); // Display on
  delay(20);
}

// --- Touch and I2C -----------------------------------------------------------

void scanI2c() {
  for (uint8_t address = 0x08; address < 0x78; ++address) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      i2cSeen[address] = true;
      if (address == 0x15 || address == 0x38) touchAddress = address;
    }
  }
}

// FocalTech and Hynitron chips share this layout from register 0x02:
// points, XH, XL, YH, YL.
void readTouch() {
  Wire.beginTransmission(touchAddress);
  Wire.write(0x02);
  if (Wire.endTransmission(false) != 0) return;
  if (Wire.requestFrom(touchAddress, static_cast<uint8_t>(5)) != 5) return;
  const uint8_t points = Wire.read() & 0x0F;
  const uint8_t xh = Wire.read();
  const uint8_t xl = Wire.read();
  const uint8_t yh = Wire.read();
  const uint8_t yl = Wire.read();
  if (points == 0) return;
  const uint16_t x = ((xh & 0x0F) << 8) | xl;
  const uint16_t y = ((yh & 0x0F) << 8) | yl;
  ++touchReads;
  Serial.printf("TOUCH points=%u x=%u y=%u\n", points, x, y);
  fillRect(x > 2 ? x - 2 : 0, y > 2 ? y - 2 : 0, 5, 5, kGreen);
}

const char *nameI2c(uint8_t address) {
  switch (address) {
    case 0x15: return "Hynitron CST8xx?";
    case 0x38: return "FocalTech FT6xxx?";
    case 0x14:
    case 0x5D: return "Goodix GT911?";
    case 0x18: return "TLV320DAC3100?";
    default: return "unknown";
  }
}

void report() {
  Serial.println("--- WATCH_PROBE ---");
  Serial.printf("LCD id pullup=0x%010llX pulldown=0x%010llX -> %s\n",
                idPullUp, idPullDown, lcdReplyVerdict());
  Serial.printf("LCD model hint: %s\n", identifyLcd(idPullUp));
  if (powerModeDriven) {
    Serial.printf("LCD power mode after init: 0x%02X (0x9C = awake, display on)\n",
                  powerModeAfterInit);
  } else {
    Serial.println("LCD power mode after init: no driven reply");
  }
  Serial.printf("I2C idle before pullups: SDA=%d SCL=%d (0 = pullup missing or touch unpowered)\n",
                sdaIdleHigh, sclIdleHigh);
  Serial.print("I2C seen:");
  bool any = false;
  for (uint8_t address = 0x08; address < 0x78; ++address) {
    if (i2cSeen[address]) {
      Serial.printf(" 0x%02X[%s]", address, nameI2c(address));
      any = true;
    }
  }
  Serial.println(any ? "" : " none (touch the glass: some chips sleep until touched)");
  Serial.printf("Touch INT edges=%lu valid reads=%lu\n",
                static_cast<unsigned long>(touchIrqCount),
                static_cast<unsigned long>(touchReads));
}

void handleSerial() {
  while (Serial.available() > 0) {
    switch (Serial.read()) {
      case 'i':
        inverted = !inverted;
        applyColorMode();
        showFills();
        break;
      case 'b':
        bgr = !bgr;
        applyColorMode();
        showFills();
        break;
      case 'f':
        showFills();
        break;
      case 'r':
        ESP.restart();
        break;
      default:
        break;
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Hold chip selects and resets in known states before anything is clocked.
  pinMode(kLcdCs, OUTPUT);
  digitalWrite(kLcdCs, HIGH);
  pinMode(kLcdDc, OUTPUT);
  digitalWrite(kLcdDc, HIGH);
  pinMode(kLcdRst, OUTPUT);
  digitalWrite(kLcdRst, LOW);
  pinMode(kTouchRst, OUTPUT);
  digitalWrite(kTouchRst, LOW);
  pinMode(kTouchInt, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(kTouchInt), onTouchIrq, FALLING);

  // LCD reset pulse, then the wake time needed before its first read. Touch
  // stays in reset until the fills finish.
  delay(20);
  digitalWrite(kLcdRst, HIGH);
  delay(150);

  idPullUp = readLcd(0x04, 40, INPUT_PULLUP);
  idPullDown = readLcd(0x04, 40, INPUT_PULLDOWN);

  SPI.begin(kLcdSck, -1, kLcdSda, -1);
  initLcd();

  // Read back power mode to confirm that commands reached the controller.
  SPI.end();
  const uint8_t modeUp = readLcd(0x0A, 8, INPUT_PULLUP);
  const uint8_t modeDown = readLcd(0x0A, 8, INPUT_PULLDOWN);
  powerModeDriven = modeUp == modeDown;
  powerModeAfterInit = modeUp;
  SPI.begin(kLcdSck, -1, kLcdSda, -1);

  showFills();

  // No internal pulls here: this shows whether external I2C pullups are present.
  pinMode(kI2cSda, INPUT);
  pinMode(kI2cScl, INPUT);
  digitalWrite(kTouchRst, HIGH);
  delay(100);
  sdaIdleHigh = digitalRead(kI2cSda);
  sclIdleHigh = digitalRead(kI2cScl);

  Wire.begin(kI2cSda, kI2cScl, 100000);
  Wire.setTimeOut(20);
  scanI2c();
}

void loop() {
  handleSerial();
  const uint32_t now = millis();
  if (now - lastScan >= 250) {
    lastScan = now;
    scanI2c();
  }
  if (touchAddress != 0) readTouch();
  if (now - lastReport >= 3000) {
    lastReport = now;
    report();
  }
  delay(20);
}
