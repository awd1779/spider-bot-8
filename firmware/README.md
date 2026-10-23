# Firmware

Arduino sketches for the ESP32 (board: **ESP32 Dev Module**). They also compile for an Arduino Uno. You need one library: **Adafruit PWM Servo Driver**. Serial Monitor: **115200 baud**, line ending **Newline**.

| Sketch | Manual | What it does |
|---|---|---|
| `P1_i2c_scanner` | 2.3 | Finds the PCA9685 (address 0x40) |
| `P2_one_servo` | 3.1 | Moves one servo on channel 0 |
| `P3_servo_tester` | 3.2 | Type `channel angle` to move any servo |
| `P4_one_leg_step` | 3.3 | Hip + lift servo: one leg takes a step |
| `P5_center_all` | 4.2 | All 8 servos to 90°, before fitting the horns |
| `P6_calibrate` | 4.9 | Find each joint's trim and direction; `print` gives lines to paste into P7–P9 |
| `P7_stand_sit` | 5 | `s` stand up, `d` sit down |
| `P8_walk_forward` | 6 | + `f` walk forward (crawl gait) |
| `P9_walk_backward` | 7 | + `b` walk backward. The complete robot |

**Before P7:** paste your calibration numbers from P6 between the `PASTE YOUR CALIBRATION HERE` lines.

## Main settings (top of P7–P9)
| Name | Default | Meaning |
|---|---|---|
| `STAND` | −15 | lift angle when standing (negative = foot down) |
| `SIT` | 35 | lift angle when sitting (feet up, body on the floor) |
| `STEP` | 14 | hip swing per walking step, in degrees |
| `UP` | 10 | lift angle while a foot is in the air |
| `LIMIT` | 35 | no joint ever goes further than this from centre |
