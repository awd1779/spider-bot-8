// SpiderBot8 example 2: walk a square-ish path, then sit down
#include <SpiderBot8.h>

SpiderBot robot;

void setup() {
  robot.begin();

  // ---- paste your calibration from 04_Calibrate here ----
  robot.setTrim(REAR_LEFT,   0, 0);
  robot.setTrim(REAR_RIGHT,  0, 0);
  robot.setTrim(FRONT_RIGHT, 0, 0);
  robot.setTrim(FRONT_LEFT,  0, 0);
  // ---------------------------------------------------------

  delay(1000);
  robot.standUp();
  robot.walkForward(8);   // 8 steps, about 10 cm
  robot.turnLeft(8);      // about 50 degrees
  robot.walkForward(8);
  robot.walkBackward(8);
  robot.turnRight(8);
  robot.wave();
  robot.sitDown();
}

void loop() {
}
