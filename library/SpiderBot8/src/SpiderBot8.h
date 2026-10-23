// SpiderBot8: simple movement library for the spider-bot-8 robot
// https://github.com/awd1779/spider-bot-8   (MIT licence, by DRODI)
//
//   #include <SpiderBot8.h>
//   SpiderBot robot;
//   robot.begin();
//   robot.standUp();
//   robot.walkForward(8);
//
// Leg angles are in degrees from the middle:
//   hip  > 0 : foot forward      hip  < 0 : foot back
//   lift > 0 : foot up           lift < 0 : foot down (body up)

#ifndef SPIDERBOT8_H
#define SPIDERBOT8_H

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Leg numbers (left and right as the robot sees them, looking forward)
enum SpiderLeg { REAR_LEFT = 0, REAR_RIGHT = 1, FRONT_RIGHT = 2, FRONT_LEFT = 3 };

class SpiderBot {
 public:
  explicit SpiderBot(uint8_t address = 0x40);

  // ---- start ----
  void begin();                         // ESP32: SDA = GPIO 21, SCL = GPIO 22
  void begin(int sdaPin, int sclPin);   // other I2C pins (ESP32 only)

  // ---- calibration (find the numbers with the 04_Calibrate example) ----
  void setTrim(int leg, int hipTrim, int liftTrim);
  void setDirection(int leg, int hipDir, int liftDir);
  void setChannels(int leg, int hipChannel, int liftChannel);

  // ---- poses ----
  void standUp();
  void sitDown();
  void center();                        // every joint at 0: legs straight out and level
  void relax();                         // switch the servos off (saves the batteries)

  // ---- walking: one step moves one leg (4 steps = one full cycle) ----
  void walkForward(int steps = 4);      // about 1.3 cm per step
  void walkBackward(int steps = 4);
  void turnLeft(int steps = 4);         // about 6 degrees per step
  void turnRight(int steps = 4);

  // ---- fun ----
  void wave(int times = 3);             // front-right leg waves hello
  void pushUps(int times = 3);

  // ---- your own moves ----
  void moveLeg(int leg, float hip, float lift, int ms = 300);       // one leg, smoothly
  void moveLegs(const float hip[4], const float lift[4], int ms);  // all 4 together, smoothly
  void setLeg(int leg, float hip, float lift);                     // one leg, straight away
  float hipAngle(int leg);
  float liftAngle(int leg);
  bool isStanding();

  // ---- settings ----
  void setSpeed(int percent);           // 100 = normal, 200 = twice as fast, 50 = half speed
  void setStandHeight(float lift);      // lift angle when standing (default -15)
  void setStepSize(float hip);          // hip swing per step (default 14)
  void setStepHeight(float lift);       // lift angle with a foot in the air (default 10)

  static const int LIMIT = 35;          // no joint goes further than this from the middle

 private:
  Adafruit_PWMServoDriver _pca;
  int _hipCh[4], _liftCh[4];
  int _hipTrim[4], _liftTrim[4];
  int _hipDir[4], _liftDir[4];
  float _hip[4], _lift[4];
  bool _standing;
  int _speed;
  float _stand, _sit, _up, _step;

  void _start();
  int _t(int ms);
  void _writeServo(int ch, float deg);
  void _stepLeg(int leg, float hip);
  void _shift(const int sign[4], float by);
  void _gait(const int order[4], const int sign[4], int dir, int steps);
  void _feetHome();
};

#endif
