// spider-bot-8 by DRODI | MIT licence | https://github.com/awd1779/spider-bot-8
// P5 - Centre all 8 servos (run this BEFORE you fit the horns)
// Every leg servo goes to exactly 90 degrees (1450 us) and stays there.
// Leave it running while you push the horns and legs on.

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver(0x40);

const int CHANNELS[8] = {0, 1, 4, 5, 8, 9, 12, 13};   // hip + lift of the 4 legs

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pca.begin();
  pca.setOscillatorFrequency(27000000);
  pca.setPWMFreq(50);
  delay(10);
  for (int i = 0; i < 8; i++) {
    pca.writeMicroseconds(CHANNELS[i], 1450);         // 90 degrees
    delay(300);                                       // one at a time: no big current spike
  }
  Serial.println("All 8 servos are at 90 degrees. Fit the horns now.");
}

void loop() {
}
