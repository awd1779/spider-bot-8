// SpiderBot8 example 1: stand up and sit down
#include <SpiderBot8.h>

SpiderBot robot;

void setup() {
  robot.begin();          // the robot starts sitting

  // ---- paste your calibration from 04_Calibrate here ----
  robot.setTrim(REAR_LEFT,   0, 0);
  robot.setTrim(REAR_RIGHT,  0, 0);
  robot.setTrim(FRONT_RIGHT, 0, 0);
  robot.setTrim(FRONT_LEFT,  0, 0);
  // ---------------------------------------------------------

  delay(1000);
}

void loop() {
  robot.standUp();
  delay(2000);
  robot.sitDown();
  delay(2000);
}
