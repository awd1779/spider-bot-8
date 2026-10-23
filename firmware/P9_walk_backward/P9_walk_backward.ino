// spider-bot-8 by DRODI | MIT licence | https://github.com/awd1779/spider-bot-8
// P9 - Walk forward and backward: the whole robot
// Serial Monitor (115200 baud):  s = stand,  d = sit,  f = forward,  b = backward

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
bool standing = false;        // true after standUp()

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
  standing = true;
}

void sitDown() {
  float hip[4]  = {0, 0, 0, 0};
  float lift[4] = {SIT, SIT, SIT, SIT};
  moveLegs(hip, lift, 1500);
  standing = false;
}

// ---- walking ----
const int STEP = 14;           // hip swing for one walking "unit" (degrees)
const float UP = 10;           // lift angle with the foot in the air

// Move just one leg; the other three stay where they are
void moveOneLeg(int leg, float hip, float lift, int ms) {
  float h[4], l[4];
  for (int i = 0; i < 4; i++) { h[i] = hipNow[i]; l[i] = liftNow[i]; }
  h[leg] = hip;
  l[leg] = lift;
  moveLegs(h, l, ms);
}

// Lift a leg, carry it to a new hip angle in the air, put it down
void stepLeg(int leg, float hip) {
  moveOneLeg(leg, hipNow[leg], UP, 150);     // 1. foot up
  moveOneLeg(leg, hip, UP, 200);             // 2. swing in the air
  moveOneLeg(leg, hip, STAND, 150);          // 3. foot down
}

// All 4 feet stay on the floor and every hip turns by "by" degrees.
// by < 0: the feet push back, so the body slides forward.
void shiftBody(float by) {
  float h[4], l[4];
  for (int i = 0; i < 4; i++) { h[i] = hipNow[i] + by; l[i] = liftNow[i]; }
  moveLegs(h, l, 300);
}

// Starting pattern for walking: the legs are at -2, -1, 0 and +1 units,
// in the order they will step (dir = +1 forward, -1 backward)
void getReady(const int order[4], int dir) {
  if (!standing) standUp();
  for (int j = 0; j < 4; j++) {
    int leg = order[j];
    float target = dir * (j - 2) * STEP;
    if (hipNow[leg] != target) stepLeg(leg, target);
  }
}

// Put every foot back to hip 0, one leg at a time
void standStill() {
  for (int leg = 0; leg < 4; leg++)
    if (hipNow[leg] != 0) stepLeg(leg, 0);
}

// Leg order for walking forward: rear-left, front-left, rear-right, front-right
const int FWD_ORDER[4] = {0, 3, 1, 2};

void walkForward(int cycles) {
  getReady(FWD_ORDER, +1);
  for (int c = 0; c < cycles; c++) {
    for (int j = 0; j < 4; j++) {
      stepLeg(FWD_ORDER[j], 2 * STEP);   // the back-most leg steps to the front
      shiftBody(-STEP);                  // all feet push back: the body moves forward
    }
  }
  standStill();
}

// Leg order for walking backward: the forward order, reversed
const int BACK_ORDER[4] = {2, 1, 3, 0};   // front-right, rear-right, front-left, rear-left

void walkBackward(int cycles) {
  getReady(BACK_ORDER, -1);
  for (int c = 0; c < cycles; c++) {
    for (int j = 0; j < 4; j++) {
      stepLeg(BACK_ORDER[j], -2 * STEP);  // the front-most leg steps to the back
      shiftBody(+STEP);                   // all feet push forward: the body moves back
    }
  }
  standStill();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pca.begin();
  pca.setOscillatorFrequency(27000000);
  pca.setPWMFreq(50);
  delay(10);
  for (int leg = 0; leg < 4; leg++) { setLeg(leg, 0, SIT); delay(300); }   // start sitting
  Serial.println("s = stand, d = sit, f = forward, b = backward");
}

void loop() {
  if (Serial.available() == 0) return;
  char c = Serial.read();
  if (c == 's') { Serial.println("Standing up"); standStill(); standUp(); }
  if (c == 'd') { Serial.println("Sitting down"); standStill(); sitDown(); }
  if (c == 'f') { Serial.println("Forward"); walkForward(2); }
  if (c == 'b') { Serial.println("Backward"); walkBackward(2); }
}
