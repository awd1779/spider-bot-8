# SpiderBot8 library

Simple movement commands for the [spider-bot-8](https://github.com/awd1779/spider-bot-8) robot.

```cpp
#include <SpiderBot8.h>

SpiderBot robot;

void setup() {
  robot.begin();
  robot.standUp();
  robot.walkForward(8);
  robot.turnLeft(4);
  robot.wave();
  robot.sitDown();
}

void loop() {
}
```

## Install
1. Download **[SpiderBot8.zip](https://github.com/awd1779/spider-bot-8/raw/main/library/SpiderBot8.zip)**.
2. In Arduino IDE: **Sketch → Include Library → Add .ZIP Library...** and choose the zip.
3. Also install **Adafruit PWM Servo Driver Library** (Tools → Manage Libraries).
4. Examples: **File → Examples → SpiderBot8**.

## Commands

| Command | What it does |
|---|---|
| `robot.begin()` | Starts the servo module; the robot starts sitting. ESP32: SDA 21, SCL 22. `robot.begin(sda, scl)` for other pins |
| `robot.standUp()` / `robot.sitDown()` | Stand up / sit down |
| `robot.walkForward(steps)` | Walk forward. One step moves one leg (about 1.3 cm). 4 steps = one full cycle |
| `robot.walkBackward(steps)` | Walk backward |
| `robot.turnLeft(steps)` / `robot.turnRight(steps)` | Turn on the spot, about 6° per step |
| `robot.wave(times)` | Wave the front-right leg |
| `robot.pushUps(times)` | Push-ups |
| `robot.center()` | Every joint at 0: legs straight out and level (for checking calibration) |
| `robot.relax()` | Switch the servos off to save the batteries |
| `robot.moveLeg(leg, hip, lift, ms)` | Move one leg smoothly. `hip` > 0 = foot forward, `lift` > 0 = foot up |
| `robot.moveLegs(hips[4], lifts[4], ms)` | Move all 4 legs together, smoothly |
| `robot.setLeg(leg, hip, lift)` | Move one leg straight away |
| `robot.setSpeed(percent)` | 100 = normal, 200 = twice as fast, 50 = half speed |
| `robot.setStandHeight(lift)` | Lift angle when standing (default −15; more negative = taller) |
| `robot.setStepSize(hip)` / `robot.setStepHeight(lift)` | Step length (default 14°) / how high a foot lifts (default 10°) |
| `robot.setTrim(leg, hipTrim, liftTrim)` | Calibration: small corrections in degrees |
| `robot.setDirection(leg, hipDir, liftDir)` | Calibration: +1 or −1 so that + is forward and up |
| `robot.setChannels(leg, hipCh, liftCh)` | If your servos are on other channels |

Legs: `REAR_LEFT` (0), `REAR_RIGHT` (1), `FRONT_RIGHT` (2), `FRONT_LEFT` (3). Default channels: hip 0, 4, 8, 12 and lift 1, 5, 9, 13.

## Calibrate first
Run **04_Calibrate**, then type `print`. Paste the lines it prints into your sketch, just after `robot.begin();`.

## How the walking works
It uses a crawl gait: only one foot is in the air at a time. The legs are kept one step apart, so the robot's centre of mass always stays inside the triangle of the three feet on the floor. Chapters 6 and 7 of the [manual](../../docs/manual.html) explain it step by step.

MIT licence · by DRODI
