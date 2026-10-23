// spider-bot-8 by DRODI | MIT licence | see README.md
// P3 - Servo tester
// Type a channel and an angle in the Serial Monitor (115200 baud, "Newline"), e.g.
//   0 90     -> channel 0 to 90 degrees
//   5 120    -> channel 5 to 120 degrees
// It prints the pulse length it sent.

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver(0x40);

int writeServo(int channel, float angle) {
  int us = 500 + angle * 10.56;
  pca.writeMicroseconds(channel, us);
  return us;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pca.begin();
  pca.setOscillatorFrequency(27000000);
  pca.setPWMFreq(50);
  delay(10);
  Serial.println("Type: channel angle   (example: 0 90)");
}

void loop() {
  if (Serial.available() == 0) return;          // nothing typed yet
  String line = Serial.readStringUntil('\n');
  int channel = -1, angle = -1;
  if (sscanf(line.c_str(), "%d %d", &channel, &angle) != 2) {
    Serial.println("Type two numbers, e.g. 0 90");
    return;
  }
  if (channel < 0 || channel > 15 || angle < 0 || angle > 180) {
    Serial.println("Channel 0-15, angle 0-180");
    return;
  }
  int us = writeServo(channel, angle);
  Serial.print("Channel "); Serial.print(channel);
  Serial.print(" -> "); Serial.print(angle);
  Serial.print(" deg = "); Serial.print(us); Serial.println(" us");
}
