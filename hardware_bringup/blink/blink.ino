#include <Arduino.h>
#include <esp_system.h>

// XIAO ESP32S3 Plus user LED: GPIO21, active LOW.
constexpr uint8_t kUserLed = 21;
uint32_t cycle = 0;

void setup() {
  pinMode(kUserLed, OUTPUT);
  digitalWrite(kUserLed, HIGH);
  Serial.begin(115200);
  delay(1500);
}

void loop() {
  // Two short flashes followed by a pause distinguish this from factory Blink.
  for (int flash = 0; flash < 2; ++flash) {
    digitalWrite(kUserLed, LOW);
    delay(150);
    digitalWrite(kUserLed, HIGH);
    delay(150);
  }
  Serial.printf("MP3_BRINGUP_OK cycle=%lu chip=%s flash=%lu psram=%lu reset=%d\n",
                static_cast<unsigned long>(++cycle), ESP.getChipModel(),
                static_cast<unsigned long>(ESP.getFlashChipSize()),
                static_cast<unsigned long>(ESP.getPsramSize()),
                static_cast<int>(esp_reset_reason()));
  delay(1400);
}
