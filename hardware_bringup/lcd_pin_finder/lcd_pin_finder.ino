// Finds which LCD pad does which job on the salvaged FPC-JL201 panel.
//
// Measurements show pads 8-13 are signals, but a meter cannot tell them apart.
// This sketch tries every ordering of RESET, CS, DC, SCL and SDA across the six
// lines and asks the controller for its ID. A wrong ordering gets no valid reply.
// A controller reply is only accepted if it reads the same with the data line
// pulled up and pulled down, proving the panel is driving the line.
//
// Each line must go through a 1 kOhm series resistor. One line may be an output
// from the panel, and the resistor limits the current if both sides drive it.

#include <Arduino.h>

struct Line {
  uint8_t gpio;
  const char *xiaoPin;
  uint8_t pad;
};

constexpr Line kLines[] = {
    {1, "D0", 8}, {2, "D1", 9}, {4, "D3", 10}, {7, "D8", 11}, {8, "D9", 12}, {9, "D10", 13},
};
constexpr uint8_t kLineCount = sizeof(kLines) / sizeof(kLines[0]);
constexpr uint64_t kAllOnes = 0xFFFFFFFFFFULL;
constexpr uint8_t kMaxHits = 16;
constexpr uint8_t kConfirmReads = 3;

struct Assignment {
  uint8_t rst, cs, dc, scl, sda, spare;
};

struct Hit {
  Assignment roles;
  bool readOnSpare;
  uint64_t raw;
  uint32_t count;
};

Hit hits[kMaxHits];
uint8_t hitCount = 0;
uint32_t passCount = 0;
uint32_t triedCount = 0;

uint8_t gpioOf(uint8_t line) { return kLines[line].gpio; }

void bitDelay() { delayMicroseconds(3); }

void releaseAll() {
  for (uint8_t line = 0; line < kLineCount; ++line) {
    pinMode(gpioOf(line), INPUT_PULLUP);
  }
}

// Sends one command, then clocks in 40 bits from readLine with the given pull.
uint64_t readController(const Assignment &a, uint8_t command, uint8_t readLine, uint8_t pull) {
  pinMode(gpioOf(a.cs), OUTPUT);
  digitalWrite(gpioOf(a.cs), HIGH);
  pinMode(gpioOf(a.dc), OUTPUT);
  digitalWrite(gpioOf(a.dc), LOW);
  pinMode(gpioOf(a.scl), OUTPUT);
  digitalWrite(gpioOf(a.scl), LOW);
  pinMode(gpioOf(a.sda), OUTPUT);
  pinMode(gpioOf(a.spare), INPUT_PULLUP);

  digitalWrite(gpioOf(a.cs), LOW);
  bitDelay();
  for (int bit = 7; bit >= 0; --bit) {
    digitalWrite(gpioOf(a.sda), (command >> bit) & 1);
    bitDelay();
    digitalWrite(gpioOf(a.scl), HIGH);
    bitDelay();
    digitalWrite(gpioOf(a.scl), LOW);
  }
  digitalWrite(gpioOf(a.dc), HIGH);
  pinMode(gpioOf(a.sda), INPUT);
  pinMode(gpioOf(readLine), pull);
  bitDelay();

  uint64_t value = 0;
  for (uint8_t i = 0; i < 40; ++i) {
    digitalWrite(gpioOf(a.scl), HIGH);
    bitDelay();
    value = (value << 1) | static_cast<uint64_t>(digitalRead(gpioOf(readLine)));
    digitalWrite(gpioOf(a.scl), LOW);
    bitDelay();
  }
  digitalWrite(gpioOf(a.cs), HIGH);
  return value;
}

void pulseReset(const Assignment &a) {
  pinMode(gpioOf(a.rst), OUTPUT);
  digitalWrite(gpioOf(a.rst), LOW);
  delay(5); // Long enough to discharge a capacitor through the series resistor.
  digitalWrite(gpioOf(a.rst), HIGH);
  delay(20);
}

// Returns true when the panel itself drives readLine with non-constant data.
bool readsDriven(const Assignment &a, uint8_t readLine, uint64_t &raw) {
  const uint64_t up = readController(a, 0x04, readLine, INPUT_PULLUP);
  const uint64_t down = readController(a, 0x04, readLine, INPUT_PULLDOWN);
  if (up != down || up == 0 || up == kAllOnes) return false;
  raw = up;
  return true;
}

void recordHit(const Assignment &a, bool onSpare, uint64_t raw) {
  for (uint8_t i = 0; i < hitCount; ++i) {
    const Assignment &r = hits[i].roles;
    if (r.rst == a.rst && r.cs == a.cs && r.dc == a.dc && r.scl == a.scl && r.sda == a.sda &&
        hits[i].readOnSpare == onSpare && hits[i].raw == raw) {
      ++hits[i].count;
      return;
    }
  }
  if (hitCount < kMaxHits) hits[hitCount++] = {a, onSpare, raw, 1};
}

void tryAssignment(const Assignment &a) {
  ++triedCount;
  releaseAll();
  pulseReset(a);
  const uint8_t readLines[] = {a.sda, a.spare};
  for (uint8_t i = 0; i < 2; ++i) {
    uint64_t raw = 0;
    if (!readsDriven(a, readLines[i], raw)) continue;
    // A real reply repeats exactly. Noise on a toggling output line does not.
    bool confirmed = true;
    for (uint8_t repeat = 1; repeat < kConfirmReads && confirmed; ++repeat) {
      uint64_t again = 0;
      confirmed = readsDriven(a, readLines[i], again) && again == raw;
    }
    if (confirmed) recordHit(a, i == 1, raw);
  }
}

void describeLine(const char *role, uint8_t line) {
  Serial.printf(" %s=pad%u(%s)", role, kLines[line].pad, kLines[line].xiaoPin);
}

void floatAll() {
  for (uint8_t line = 0; line < kLineCount; ++line) {
    pinMode(gpioOf(line), INPUT);
  }
}

// Every other line floats during each read, so no earlier drive can skew it.
void reportIdleLines() {
  Serial.print("Idle lines (up/down reads, 1/0 = nothing driving it):");
  for (uint8_t line = 0; line < kLineCount; ++line) {
    floatAll();
    delay(2);
    pinMode(gpioOf(line), INPUT_PULLUP);
    delay(2);
    const int up = digitalRead(gpioOf(line));
    pinMode(gpioOf(line), INPUT_PULLDOWN);
    delay(2);
    const int down = digitalRead(gpioOf(line));
    Serial.printf(" pad%u=%d/%d", kLines[line].pad, up, down);
  }
  Serial.println();
}

// Two lines that follow each other in both directions are joined by a wiring
// short. A powered chip's inputs do not pass a drive from one pad to another.
void reportLinks() {
  Serial.print("Linked lines:");
  bool any = false;
  for (uint8_t driver = 0; driver < kLineCount; ++driver) {
    for (uint8_t other = driver + 1; other < kLineCount; ++other) {
      floatAll();
      pinMode(gpioOf(driver), OUTPUT);
      digitalWrite(gpioOf(driver), HIGH);
      pinMode(gpioOf(other), INPUT_PULLDOWN);
      delay(1);
      const bool followsHigh = digitalRead(gpioOf(other)) == HIGH;
      digitalWrite(gpioOf(driver), LOW);
      pinMode(gpioOf(other), INPUT_PULLUP);
      delay(1);
      const bool followsLow = digitalRead(gpioOf(other)) == LOW;
      if (followsHigh && followsLow) {
        Serial.printf(" pad%u-pad%u", kLines[driver].pad, kLines[other].pad);
        any = true;
      }
    }
  }
  floatAll();
  Serial.println(any ? "" : " none");
}

void report() {
  Serial.printf("--- PIN_FINDER pass=%lu tried=%lu ---\n", static_cast<unsigned long>(passCount),
                static_cast<unsigned long>(triedCount));
  reportIdleLines();
  reportLinks();
  releaseAll();
  if (hitCount == 0) {
    Serial.println("No controller reply yet.");
    return;
  }
  for (uint8_t i = 0; i < hitCount; ++i) {
    const Hit &hit = hits[i];
    Serial.printf("HIT raw=0x%010llX seen=%lu", hit.raw, static_cast<unsigned long>(hit.count));
    describeLine("RST", hit.roles.rst);
    describeLine("CS", hit.roles.cs);
    describeLine("DC", hit.roles.dc);
    describeLine("SCL", hit.roles.scl);
    describeLine("SDA", hit.roles.sda);
    describeLine(hit.readOnSpare ? "SDO" : "OTHER", hit.roles.spare);
    Serial.println();
  }
}

// One full pass over every ordering. Reports during the pass so that a monitor
// opened late still sees results within a few seconds.
void runPass() {
  uint32_t lastReport = millis();
  Assignment a;
  for (a.rst = 0; a.rst < kLineCount; ++a.rst) {
    for (a.cs = 0; a.cs < kLineCount; ++a.cs) {
      if (a.cs == a.rst) continue;
      for (a.dc = 0; a.dc < kLineCount; ++a.dc) {
        if (a.dc == a.rst || a.dc == a.cs) continue;
        for (a.scl = 0; a.scl < kLineCount; ++a.scl) {
          if (a.scl == a.rst || a.scl == a.cs || a.scl == a.dc) continue;
          for (a.sda = 0; a.sda < kLineCount; ++a.sda) {
            if (a.sda == a.rst || a.sda == a.cs || a.sda == a.dc || a.sda == a.scl) continue;
            a.spare = 15 - a.rst - a.cs - a.dc - a.scl - a.sda; // Lines 0-5 sum to 15.
            tryAssignment(a);
            if (millis() - lastReport >= 3000) {
              lastReport = millis();
              report();
            }
          }
        }
      }
    }
  }
  ++passCount;
}

void setup() {
  Serial.begin(115200);
  releaseAll();
  delay(1500);
}

void loop() {
  runPass();
  report();
}
