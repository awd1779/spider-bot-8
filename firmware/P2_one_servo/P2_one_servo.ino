// spider-bot-8 by DRODI | MIT licence | see README.md
// P2 - Move one servo with the PCA9685
// Servo on channel 0. It goes to 90, 45 and 135 degrees, then sweeps smoothly.

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver(0x40);

// Angle (0 to 180) -> pulse length in microseconds, then send it
void writeServo(int channel, float angle) {
  int us = 500 + angle * 10.56;
  pca.writeMicroseconds(channel, us);
}

void setup() {
  Wire.begin();                       // ESP32: SDA = 21, SCL = 22
  pca.begin();
  pca.setOscillatorFrequency(27000000);
  pca.setPWMFreq(50);                 // servos want 50 pulses a second
  delay(10);

  writeServo(0, 90);  delay(1000);    // centre
  writeServo(0, 45);  delay(1000);
  writeServo(0, 135); delay(1000);
  writeServo(0, 90);  delay(1000);
}

void loop() {
  for (int a = 90; a <= 135; a++) {   // count up, 1 degree at a time
    writeServo(0, a);
    delay(15);                        // 15 ms per degree sets the speed
  }
  for (int a = 135; a >= 45; a--) {   // count back down
    writeServo(0, a);
    delay(15);
  }
  for (int a = 45; a <= 90; a++) {    // back to the centre
    writeServo(0, a);
    delay(15);
  }
  delay(500);
}
