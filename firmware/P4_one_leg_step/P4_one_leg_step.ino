// spider-bot-8 by DRODI | MIT licence | see README.md
// P4 - Two servos make one leg take a step
// Hip servo on channel 0 (forward / back), lift servo on channel 1 (up / down).

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver(0x40);

const int HIP = 0;     // channel numbers
const int LIFT = 1;

int angleNow[16];      // the PCA9685 can't tell us where a servo is, so we remember

void writeServo(int channel, int angle) {
  pca.writeMicroseconds(channel, 500 + angle * 10.56);
  angleNow[channel] = angle;
}

// Move one servo slowly from where it is now to a new angle
void moveSlow(int channel, int target) {
  int step = (target > angleNow[channel]) ? 1 : -1;
  while (angleNow[channel] != target) {
    writeServo(channel, angleNow[channel] + step);
    delay(8);
  }
}

void setup() {
  Wire.begin();
  pca.begin();
  pca.setOscillatorFrequency(27000000);
  pca.setPWMFreq(50);
  delay(10);
  writeServo(HIP, 90);
  delay(300);
  writeServo(LIFT, 90);
  delay(1000);
}

void loop() {
  moveSlow(LIFT, 115);   // 1. lift the foot
  moveSlow(HIP, 110);    // 2. swing it forward in the air
  moveSlow(LIFT, 90);    // 3. put it down
  moveSlow(HIP, 90);     // 4. push back along the ground
  delay(500);
}
