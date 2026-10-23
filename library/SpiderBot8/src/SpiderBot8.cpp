// SpiderBot8: simple movement library for the spider-bot-8 robot
// https://github.com/awd1779/spider-bot-8   (MIT licence, by DRODI)

#include "SpiderBot8.h"

// Gait patterns. "sign" turns a gait unit into a hip angle for each leg:
// walking moves every foot forward/back, turning moves the right feet forward
// and the left feet back, so every foot goes the same way round the body.
static const int WALK_SIGN[4] = {1, 1, 1, 1};
static const int TURN_SIGN[4] = {-1, 1, 1, -1};
static const int FWD_ORDER[4] = {REAR_LEFT, FRONT_LEFT, REAR_RIGHT, FRONT_RIGHT};
static const int BACK_ORDER[4] = {FRONT_RIGHT, REAR_RIGHT, FRONT_LEFT, REAR_LEFT};
static const int LEFT_ORDER[4] = {FRONT_LEFT, REAR_LEFT, REAR_RIGHT, FRONT_RIGHT};
static const int RIGHT_ORDER[4] = {FRONT_RIGHT, REAR_RIGHT, REAR_LEFT, FRONT_LEFT};

SpiderBot::SpiderBot(uint8_t address) : _pca(address) {
  const int hipCh[4] = {0, 4, 8, 12};
  const int liftCh[4] = {1, 5, 9, 13};
  const int hipDir[4] = {-1, 1, 1, -1};
  for (int i = 0; i < 4; i++) {
    _hipCh[i] = hipCh[i];
    _liftCh[i] = liftCh[i];
    _hipTrim[i] = 0;
    _liftTrim[i] = 0;
    _hipDir[i] = hipDir[i];
    _liftDir[i] = -1;
    _hip[i] = 0;
    _lift[i] = 0;
  }
  _standing = false;
  _speed = 100;
  _stand = -15;
  _sit = 35;
  _up = 10;
  _step = 14;
}

// ---------------------------------------------------------------- start
void SpiderBot::begin() {
  Wire.begin();
  _start();
}

void SpiderBot::begin(int sdaPin, int sclPin) {
#if defined(ARDUINO_ARCH_ESP32)
  Wire.begin(sdaPin, sclPin);
#else
  (void)sdaPin;
  (void)sclPin;
  Wire.begin();
#endif
  _start();
}

void SpiderBot::_start() {
  _pca.begin();
  _pca.setOscillatorFrequency(27000000);
  _pca.setPWMFreq(50);
  delay(10);
  for (int leg = 0; leg < 4; leg++) {   // start sitting, one leg at a time
    setLeg(leg, 0, _sit);
    delay(300);
  }
  _standing = false;
}

// ---------------------------------------------------------------- calibration
void SpiderBot::setTrim(int leg, int hipTrim, int liftTrim) {
  if (leg < 0 || leg > 3) return;
  _hipTrim[leg] = hipTrim;
  _liftTrim[leg] = liftTrim;
}

void SpiderBot::setDirection(int leg, int hipDir, int liftDir) {
  if (leg < 0 || leg > 3) return;
  _hipDir[leg] = hipDir < 0 ? -1 : 1;
  _liftDir[leg] = liftDir < 0 ? -1 : 1;
}

void SpiderBot::setChannels(int leg, int hipChannel, int liftChannel) {
  if (leg < 0 || leg > 3) return;
  _hipCh[leg] = hipChannel;
  _liftCh[leg] = liftChannel;
}

// ---------------------------------------------------------------- low level
int SpiderBot::_t(int ms) {
  return (long)ms * 100 / _speed;
}

void SpiderBot::_writeServo(int ch, float deg) {
  _pca.writeMicroseconds(ch, 500 + deg * 10.56);
}

void SpiderBot::setLeg(int leg, float hip, float lift) {
  if (leg < 0 || leg > 3) return;
  hip = constrain(hip, -LIMIT, LIMIT);
  lift = constrain(lift, -LIMIT, LIMIT);
  _writeServo(_hipCh[leg], 90 + _hipDir[leg] * hip + _hipTrim[leg]);
  _writeServo(_liftCh[leg], 90 + _liftDir[leg] * lift + _liftTrim[leg]);
  _hip[leg] = hip;
  _lift[leg] = lift;
}

void SpiderBot::moveLegs(const float hip[4], const float lift[4], int ms) {
  float hip0[4], lift0[4];
  for (int i = 0; i < 4; i++) {
    hip0[i] = _hip[i];
    lift0[i] = _lift[i];
  }
  int steps = max(1, _t(ms) / 20);
  for (int s = 1; s <= steps; s++) {
    float f = (float)s / steps;
    for (int i = 0; i < 4; i++)
      setLeg(i, hip0[i] + (hip[i] - hip0[i]) * f, lift0[i] + (lift[i] - lift0[i]) * f);
    delay(20);
  }
}

void SpiderBot::moveLeg(int leg, float hip, float lift, int ms) {
  if (leg < 0 || leg > 3) return;
  float h[4], l[4];
  for (int i = 0; i < 4; i++) {
    h[i] = _hip[i];
    l[i] = _lift[i];
  }
  h[leg] = hip;
  l[leg] = lift;
  moveLegs(h, l, ms);
}

float SpiderBot::hipAngle(int leg) { return (leg >= 0 && leg < 4) ? _hip[leg] : 0; }
float SpiderBot::liftAngle(int leg) { return (leg >= 0 && leg < 4) ? _lift[leg] : 0; }
bool SpiderBot::isStanding() { return _standing; }

// ---------------------------------------------------------------- poses
void SpiderBot::standUp() {
  _feetHome();
  const float h[4] = {0, 0, 0, 0};
  const float l[4] = {_stand, _stand, _stand, _stand};
  moveLegs(h, l, 1500);
  _standing = true;
}

void SpiderBot::sitDown() {
  _feetHome();
  const float h[4] = {0, 0, 0, 0};
  const float l[4] = {_sit, _sit, _sit, _sit};
  moveLegs(h, l, 1500);
  _standing = false;
}

void SpiderBot::center() {
  const float z[4] = {0, 0, 0, 0};
  moveLegs(z, z, 800);
  _standing = false;
}

void SpiderBot::relax() {
  for (int leg = 0; leg < 4; leg++) {
    _pca.setPWM(_hipCh[leg], 0, 4096);    // 4096 = fully off: no pulse at all
    _pca.setPWM(_liftCh[leg], 0, 4096);
  }
  _standing = false;
}

// ---------------------------------------------------------------- walking
// Lift a leg, carry it to a new hip angle in the air, put it down
void SpiderBot::_stepLeg(int leg, float hip) {
  moveLeg(leg, _hip[leg], _up, 150);
  moveLeg(leg, hip, _up, 200);
  moveLeg(leg, hip, _stand, 150);
}

// All 4 feet stay on the floor and move together: the body slides the other way
void SpiderBot::_shift(const int sign[4], float by) {
  float h[4], l[4];
  for (int i = 0; i < 4; i++) {
    h[i] = _hip[i] + sign[i] * by;
    l[i] = _lift[i];
  }
  moveLegs(h, l, 300);
}

// Crawl gait: only one foot is ever in the air. The legs are kept one step
// apart (-2, -1, 0, +1 units in stepping order) so the robot's centre of mass
// stays inside the triangle of the three feet on the floor.
void SpiderBot::_gait(const int order[4], const int sign[4], int dir, int steps) {
  if (!_standing) standUp();
  for (int j = 0; j < 4; j++) {          // get ready: spread the legs
    int leg = order[j];
    float target = sign[leg] * dir * (j - 2) * _step;
    if (fabs(_hip[leg] - target) > 0.5) _stepLeg(leg, target);
  }
  for (int k = 0; k < steps; k++) {
    int leg = order[k % 4];
    _stepLeg(leg, sign[leg] * dir * 2 * _step);   // the back-most leg steps to the front
    _shift(sign, -dir * _step);                    // every foot pushes back: the body moves
  }
  _feetHome();
}

// Bring every foot back to hip 0, one leg at a time
void SpiderBot::_feetHome() {
  for (int leg = 0; leg < 4; leg++)
    if (fabs(_hip[leg]) > 0.5) {
      if (_standing) _stepLeg(leg, 0);
      else moveLeg(leg, 0, _lift[leg], 300);
    }
}

void SpiderBot::walkForward(int steps) { _gait(FWD_ORDER, WALK_SIGN, 1, steps); }
void SpiderBot::walkBackward(int steps) { _gait(BACK_ORDER, WALK_SIGN, -1, steps); }
void SpiderBot::turnLeft(int steps) { _gait(LEFT_ORDER, TURN_SIGN, 1, steps); }
void SpiderBot::turnRight(int steps) { _gait(RIGHT_ORDER, TURN_SIGN, -1, steps); }

// ---------------------------------------------------------------- fun
void SpiderBot::wave(int times) {
  if (!_standing) standUp();
  _feetHome();
  _shift(WALK_SIGN, 12);                 // lean back, away from the waving leg, so it doesn't tip
  moveLeg(FRONT_RIGHT, 12, LIMIT, 400);
  for (int i = 0; i < times; i++) {
    moveLeg(FRONT_RIGHT, 30, LIMIT, 250);
    moveLeg(FRONT_RIGHT, -5, LIMIT, 250);
  }
  moveLeg(FRONT_RIGHT, 12, _stand, 400);
  _shift(WALK_SIGN, -12);
}

void SpiderBot::pushUps(int times) {
  if (!_standing) standUp();
  const float h[4] = {0, 0, 0, 0};
  const float down[4] = {15, 15, 15, 15};
  const float up[4] = {_stand, _stand, _stand, _stand};
  for (int i = 0; i < times; i++) {
    moveLegs(h, down, 600);
    moveLegs(h, up, 600);
  }
}

// ---------------------------------------------------------------- settings
void SpiderBot::setSpeed(int percent) { _speed = constrain(percent, 20, 300); }
void SpiderBot::setStandHeight(float lift) { _stand = constrain(lift, -LIMIT, 0); }
void SpiderBot::setStepSize(float hip) { _step = constrain(hip, 4, LIMIT / 2); }
void SpiderBot::setStepHeight(float lift) { _up = constrain(lift, _stand + 10, LIMIT); }
