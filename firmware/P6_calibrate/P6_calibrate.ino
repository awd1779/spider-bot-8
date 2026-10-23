// spider-bot-8 by DRODI | MIT licence | https://github.com/awd1779/spider-bot-8
// P6 - Calibrate the robot
// Open the Serial Monitor (115200 baud, "Newline") and type:
//   test        -> moves each joint a little, one at a time: watch the direction
//   h 0 5       -> hip trim of leg 0 = 5 degrees   (legs: 0 rear-left, 1 rear-right,
//   l 0 -3      -> lift trim of leg 0 = -3 degrees          2 front-right, 3 front-left)
//   fh 0        -> flip the hip direction of leg 0
//   fl 0        -> flip the lift direction of leg 0
//   print       -> prints your numbers, ready to paste into the next sketches

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver(0x40);

const char* LEG_NAME[4] = {"rear-left", "rear-right", "front-right", "front-left"};
const int HIP_CH[4]  = {0, 4, 8, 12};
const int LIFT_CH[4] = {1, 5, 9, 13};

int HIP_TRIM[4]  = {0, 0, 0, 0};
int LIFT_TRIM[4] = {0, 0, 0, 0};
int HIP_DIR[4]   = {-1, 1, 1, -1};
int LIFT_DIR[4]  = {-1, -1, -1, -1};

void writeServo(int ch, float deg) {
  pca.writeMicroseconds(ch, 500 + deg * 10.56);
}

void setLeg(int leg, float hip, float lift) {
  writeServo(HIP_CH[leg], 90 + HIP_DIR[leg] * hip + HIP_TRIM[leg]);
  writeServo(LIFT_CH[leg], 90 + LIFT_DIR[leg] * lift + LIFT_TRIM[leg]);
}

void allZero() {
  for (int leg = 0; leg < 4; leg++) setLeg(leg, 0, 0);
}

void directionTest() {
  for (int leg = 0; leg < 4; leg++) {
    Serial.print("Leg "); Serial.print(leg); Serial.print(" ("); Serial.print(LEG_NAME[leg]);
    Serial.println("): the foot should swing FORWARD (towards the sensor head)");
    setLeg(leg, 20, 0); delay(1200); setLeg(leg, 0, 0); delay(600);
    Serial.println("   ... and now the foot should go UP");
    setLeg(leg, 0, 20); delay(1200); setLeg(leg, 0, 0); delay(600);
  }
  Serial.println("Wrong way? Type fh <leg> or fl <leg>, then test again.");
}

void printNumbers() {
  Serial.println("Copy these 4 lines into the next sketches:");
  const char* names[4] = {"HIP_TRIM", "LIFT_TRIM", "HIP_DIR", "LIFT_DIR"};
  int* arrays[4] = {HIP_TRIM, LIFT_TRIM, HIP_DIR, LIFT_DIR};
  for (int k = 0; k < 4; k++) {
    Serial.print("int "); Serial.print(names[k]); Serial.print("[4] = {");
    for (int i = 0; i < 4; i++) { Serial.print(arrays[k][i]); if (i < 3) Serial.print(", "); }
    Serial.println("};");
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pca.begin();
  pca.setOscillatorFrequency(27000000);
  pca.setPWMFreq(50);
  delay(10);
  for (int leg = 0; leg < 4; leg++) { setLeg(leg, 0, 0); delay(300); }
  Serial.println("All joints at 0. Each leg should point straight out, level.");
  Serial.println("Commands: test | h <leg> <deg> | l <leg> <deg> | fh <leg> | fl <leg> | print");
}

void loop() {
  if (Serial.available() == 0) return;
  String line = Serial.readStringUntil('\n');
  char cmd[8] = "";
  int leg = -1, value = 0;
  int n = sscanf(line.c_str(), "%7s %d %d", cmd, &leg, &value);
  String c = cmd;
  if (c == "test") { directionTest(); return; }
  if (c == "print") { printNumbers(); return; }
  if (n < 2 || leg < 0 || leg > 3) { Serial.println("Which leg? 0-3"); return; }
  if (c == "h" && n == 3) HIP_TRIM[leg] = value;
  else if (c == "l" && n == 3) LIFT_TRIM[leg] = value;
  else if (c == "fh") HIP_DIR[leg] = -HIP_DIR[leg];
  else if (c == "fl") LIFT_DIR[leg] = -LIFT_DIR[leg];
  else { Serial.println("Commands: test | h <leg> <deg> | l <leg> <deg> | fh <leg> | fl <leg> | print"); return; }
  allZero();
  Serial.print("Leg "); Serial.print(leg); Serial.print(" ("); Serial.print(LEG_NAME[leg]);
  Serial.print("): hip trim "); Serial.print(HIP_TRIM[leg]);
  Serial.print(", lift trim "); Serial.print(LIFT_TRIM[leg]);
  Serial.print(", hip dir "); Serial.print(HIP_DIR[leg]);
  Serial.print(", lift dir "); Serial.println(LIFT_DIR[leg]);
}
