// SpiderBot8 example 5: make your own moves with moveLeg() and moveLegs()
//   moveLeg(leg, hip, lift, ms)   hip > 0 = foot forward, lift > 0 = foot up
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

  robot.standUp();
}

// Lean the body forward and back (all 4 feet stay on the floor)
void rock(int times) {
  float back[4] = {12, 12, 12, 12};     // feet forward = body back
  float front[4] = {-12, -12, -12, -12};
  float lift[4] = {-15, -15, -15, -15};
  for (int i = 0; i < times; i++) {
    robot.moveLegs(back, lift, 500);
    robot.moveLegs(front, lift, 500);
  }
  float zero[4] = {0, 0, 0, 0};
  robot.moveLegs(zero, lift, 500);
}

// Tip the body: front legs long, back legs short, then the other way
void nod(int times) {
  float hips[4] = {0, 0, 0, 0};
  float lookUp[4] = {5, 5, -25, -25};     // rear-left, rear-right, front-right, front-left
  float lookDown[4] = {-25, -25, 5, 5};
  float level[4] = {-15, -15, -15, -15};
  for (int i = 0; i < times; i++) {
    robot.moveLegs(hips, lookUp, 400);
    robot.moveLegs(hips, lookDown, 400);
  }
  robot.moveLegs(hips, level, 400);
}

void loop() {
  rock(3);
  nod(3);
  robot.wave(2);
  robot.pushUps(2);
  delay(2000);
}
