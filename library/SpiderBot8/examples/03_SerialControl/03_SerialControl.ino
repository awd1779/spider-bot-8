// SpiderBot8 example 3: drive the robot from the Serial Monitor (115200 baud)
//   f = forward   b = backward   l = turn left   r = turn right
//   s = stand     d = sit down   w = wave        p = push-ups
//   + = faster    - = slower     x = relax (servos off)
#include <SpiderBot8.h>

SpiderBot robot;
int speed = 100;

void setup() {
  Serial.begin(115200);
  robot.begin();

  // ---- paste your calibration from 04_Calibrate here ----
  robot.setTrim(REAR_LEFT,   0, 0);
  robot.setTrim(REAR_RIGHT,  0, 0);
  robot.setTrim(FRONT_RIGHT, 0, 0);
  robot.setTrim(FRONT_LEFT,  0, 0);
  // ---------------------------------------------------------

  Serial.println("f b l r = move, s d = stand / sit, w = wave, p = push-ups, + - = speed, x = relax");
}

void loop() {
  if (Serial.available() == 0) return;
  char c = Serial.read();
  switch (c) {
    case 'f': robot.walkForward(4);  break;
    case 'b': robot.walkBackward(4); break;
    case 'l': robot.turnLeft(4);     break;
    case 'r': robot.turnRight(4);    break;
    case 's': robot.standUp();       break;
    case 'd': robot.sitDown();       break;
    case 'w': robot.wave();          break;
    case 'p': robot.pushUps();       break;
    case 'x': robot.relax();         break;
    case '+': speed = min(speed + 25, 300); robot.setSpeed(speed); break;
    case '-': speed = max(speed - 25, 25);  robot.setSpeed(speed); break;
    default: return;                 // ignore Enter and other keys
  }
  Serial.print("done: ");
  Serial.println(c);
}
