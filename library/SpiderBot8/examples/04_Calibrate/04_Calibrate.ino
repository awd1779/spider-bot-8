// SpiderBot8 example 4: calibrate
// Serial Monitor (115200 baud, line ending "Newline"). Type:
//   h 0 5     -> hip trim of leg 0 = 5 degrees      legs: 0 rear-left, 1 rear-right,
//   l 0 -3    -> lift trim of leg 0 = -3 degrees          2 front-right, 3 front-left
//   test      -> each foot swings FORWARD, then goes UP, one leg at a time
//   fh 0      -> flip the hip direction of leg 0 (if it went backward)
//   fl 0      -> flip the lift direction of leg 0 (if it went down)
//   print     -> prints the lines to paste into your own sketches
#include <SpiderBot8.h>

SpiderBot robot;
int hipTrim[4] = {0, 0, 0, 0}, liftTrim[4] = {0, 0, 0, 0};
int hipDir[4] = {-1, 1, 1, -1}, liftDir[4] = {-1, -1, -1, -1};
const char* NAMES[4] = {"REAR_LEFT", "REAR_RIGHT", "FRONT_RIGHT", "FRONT_LEFT"};

void apply() {
  for (int leg = 0; leg < 4; leg++) {
    robot.setTrim(leg, hipTrim[leg], liftTrim[leg]);
    robot.setDirection(leg, hipDir[leg], liftDir[leg]);
    robot.setLeg(leg, 0, 0);
  }
}

void test() {
  for (int leg = 0; leg < 4; leg++) {
    Serial.print(NAMES[leg]); Serial.println(": foot should swing FORWARD ...");
    robot.moveLeg(leg, 20, 0, 400); delay(600); robot.moveLeg(leg, 0, 0, 400);
    Serial.println("   ... then go UP");
    robot.moveLeg(leg, 0, 20, 400); delay(600); robot.moveLeg(leg, 0, 0, 400);
  }
}

void printLines() {
  Serial.println("// ---- paste into setup(), after robot.begin() ----");
  for (int leg = 0; leg < 4; leg++) {
    Serial.print("robot.setTrim("); Serial.print(NAMES[leg]); Serial.print(", ");
    Serial.print(hipTrim[leg]); Serial.print(", "); Serial.print(liftTrim[leg]); Serial.println(");");
  }
  for (int leg = 0; leg < 4; leg++) {
    Serial.print("robot.setDirection("); Serial.print(NAMES[leg]); Serial.print(", ");
    Serial.print(hipDir[leg]); Serial.print(", "); Serial.print(liftDir[leg]); Serial.println(");");
  }
}

void setup() {
  Serial.begin(115200);
  robot.begin();
  apply();
  Serial.println("All joints at 0: every leg should point straight out, level.");
  Serial.println("Commands: h <leg> <deg> | l <leg> <deg> | test | fh <leg> | fl <leg> | print");
}

void loop() {
  if (Serial.available() == 0) return;
  String line = Serial.readStringUntil('\n');
  char cmd[8] = "";
  int leg = -1, value = 0;
  int n = sscanf(line.c_str(), "%7s %d %d", cmd, &leg, &value);
  String c = cmd;
  if (c == "test") { test(); return; }
  if (c == "print") { printLines(); return; }
  if (n < 2 || leg < 0 || leg > 3) { Serial.println("Which leg? 0-3"); return; }
  if (c == "h" && n == 3) hipTrim[leg] = value;
  else if (c == "l" && n == 3) liftTrim[leg] = value;
  else if (c == "fh") hipDir[leg] = -hipDir[leg];
  else if (c == "fl") liftDir[leg] = -liftDir[leg];
  else { Serial.println("Commands: h <leg> <deg> | l <leg> <deg> | test | fh <leg> | fl <leg> | print"); return; }
  apply();
  Serial.print(NAMES[leg]); Serial.print(": hip trim "); Serial.print(hipTrim[leg]);
  Serial.print(", lift trim "); Serial.print(liftTrim[leg]);
  Serial.print(", hip dir "); Serial.print(hipDir[leg]);
  Serial.print(", lift dir "); Serial.println(liftDir[leg]);
}
