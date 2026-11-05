// Confirms which XIAO pin actually reaches each LCD pad, using only a multimeter.
//
// Each line outputs a different PWM duty, which a DC voltmeter reads as a steady
// voltage. Measured at the breakout pad, that voltage identifies the XIAO pin
// feeding the pad, and also proves the whole path through the resistor.

#include <Arduino.h>

struct Line {
  uint8_t gpio;
  const char *xiaoPin;
  uint8_t pad;
  uint8_t dutyPercent;
};

constexpr Line kLines[] = {
    {1, "D0", 8, 10}, {2, "D1", 9, 25}, {4, "D3", 10, 40},
    {7, "D8", 11, 55}, {8, "D9", 12, 70}, {9, "D10", 13, 85},
};
constexpr uint32_t kPwmHz = 2000;
constexpr uint8_t kPwmBits = 8;
constexpr float kSupplyVolts = 3.25f;

void setup() {
  Serial.begin(115200);
  for (const Line &line : kLines) {
    ledcAttach(line.gpio, kPwmHz, kPwmBits);
    ledcWrite(line.gpio, (static_cast<uint32_t>(line.dutyPercent) * 255) / 100);
  }
}

void loop() {
  Serial.println("--- LCD_WIRE_CHECK ---");
  for (const Line &line : kLines) {
    Serial.printf("pad %u should read %.2f V (%s)\n", line.pad,
                  kSupplyVolts * line.dutyPercent / 100.0f, line.xiaoPin);
  }
  delay(3000);
}
