// spider-bot-8 by DRODI | MIT licence | https://github.com/awd1779/spider-bot-8
// P7 - Stand up and sit down
// Serial Monitor (115200 baud):  s = stand up,  d = sit down

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver(0x40);

// Legs: 0 rear-left, 1 rear-right, 2 front-right, 3 front-left
const int HIP_CH[4]  = {0, 4, 8, 12};
const int LIFT_CH[4] = {1, 5, 9, 13};

// ---- PASTE YOUR CALIBRATION HERE (from P6) ----
int HIP_TRIM[4]  = {0, 0, 0, 0};
int LIFT_TRIM[4] = {0, 0, 0, 0};
int HIP_DIR[4]   = {-1, 1, 1, -1};
int LIFT_DIR[4]  = {-1, -1, -1, -1};
// -----------------------------------------------

const int LIMIT = 35;          // never more than 35 degrees from centre
const float STAND = -15;       // lift angle when standing (foot pushed down)
const float SIT = 35;          // lift angle when sitting (feet up, body on the floor)

float hipNow[4], liftNow[4];   // where every joint is now

void writeServo(int ch, float deg) {
  pca.writeMicroseconds(ch, 500 + deg * 10.56);
}

// Put one leg at a hip angle (+ = forward) and a lift angle (+ = foot up)
void setLeg(int leg, float hip, float lift) {
  hip = constrain(hip, -LIMIT, LIMIT);
  lift = constrain(lift, -LIMIT, LIMIT);
  writeServo(HIP_CH[leg], 90 + HIP_DIR[leg] * hip + HIP_TRIM[leg]);
  writeServo(LIFT_CH[leg], 90 + LIFT_DIR[leg] * lift + LIFT_TRIM[leg]);
  hipNow[leg] = hip;
  liftNow[leg] = lift;
}

// Move all 4 legs together to new angles, taking ms milliseconds
void moveLegs(float hip[4], float lift[4], int ms) {
  float hip0[4], lift0[4];
  for (int i = 0; i < 4; i++) { hip0[i] = hipNow[i]; lift0[i] = liftNow[i]; }
  int steps = max(1, ms / 20);
  for (int s = 1; s <= steps; s++) {
    float f = (float)s / steps;                     // 0 -> 1
    for (int i = 0; i < 4; i++)
      setLeg(i, hip0[i] + (hip[i] - hip0[i]) * f, lift0[i] + (lift[i] - lift0[i]) * f);
    delay(20);
  }
}

void standUp() {
  float hip[4]  = {0, 0, 0, 0};
  float lift[4] = {STAND, STAND, STAND, STAND};
  moveLegs(hip, lift, 1500);
}

void sitDown() {
  float hip[4]  = {0, 0, 0, 0};
  float lift[4] = {SIT, SIT, SIT, SIT};
  moveLegs(hip, lift, 1500);
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pca.begin();
  pca.setOscillatorFrequency(27000000);
  pca.setPWMFreq(50);
  delay(10);
  for (int leg = 0; leg < 4; leg++) { setLeg(leg, 0, SIT); delay(300); }   // start sitting
  Serial.println("s = stand up, d = sit down");
}

void loop() {
  if (Serial.available() == 0) return;
  char c = Serial.read();
  if (c == 's') { Serial.println("Standing up"); standUp(); }
  if (c == 'd') { Serial.println("Sitting down"); sitDown(); }
}
