## Welcome {#welcome}

In this manual you build a four-legged spider robot and teach it to stand up, sit down and walk forward and backward. Each chapter adds one idea and ends with a short check.

{{IMG:assembled_iso.png|The finished spider robot: ESP32 and servo module on top, 4 × AA batteries inside, 8 servos in the legs}}

**The chapters**

1. How servo motors work
2. The servo module (PCA9685)
3. Controlling servo motors with code
4. Assembly and calibration
5. Stand up and sit down
6. Walk forward
7. Walk backward

**Parts**

| Part | Qty |
| --- | --- |
| ESP32 38-pin board on its expansion board, plus USB cable | 1 |
| MG90S servo motor (with single-arm horn and small screws) | 8 |
| PCA9685 16-channel servo module | 1 |
| 4 × AA battery holder with switch, plus 4 AA batteries | 1 |
| Jumper wires, female to female | 4 |
| 3D-printed parts: body plate, lid, 4 spacers, 4 shoulders, 4 legs, sensor head | 1 set |
| M2 × 5 or M2 × 6 self-tapping screws (for the horns) | 16 |
| M3 screws (body and lid), M2.5 screws (servo module), zip ties, Velcro strap | 1 set |

**Software (set up once)**

1. Install **Arduino IDE 2**.
2. **Tools → Board → Boards Manager**: search **esp32**, install **esp32 by Espressif Systems**.
3. **Tools → Board**: choose **ESP32 Dev Module**. **Tools → Port**: choose the port that appears when you plug in the ESP32.
4. **Tools → Manage Libraries**: search **Adafruit PWM Servo Driver** and install it.
5. In the **Serial Monitor**, set the speed to **115200 baud** and the line ending to **Newline**.

<div class="note" markdown="1">
**Upload stuck at "Connecting..."?** Hold the **BOOT** button on the ESP32 until the upload starts, then let go.
</div>

**Safety rules**

- Unplug the batteries before you change any wire.
- The batteries go **only** into the green terminal on the servo module. Never connect them to the ESP32 pins.
- Never turn a servo shaft by hand. Let the code move it.
- If anything gets hot or smells, switch off the batteries and tell your teacher.

## Chapter 1 · How servo motors work {#ch1}

A servo is a motor that turns to an exact angle and holds it there. An ordinary motor just spins while it has power. A servo checks where its shaft is and keeps correcting until it reaches the angle you asked for. The spider uses 8 of them. On each leg, one swings the leg forward and back (**hip**), and one lifts it up and down (**lift**).

### 1.1 What's inside

{{LOOP}}

1. **Control board**: reads the signal and decides which way to drive the motor.
2. **DC motor**: small and fast, but weak on its own.
3. **Gearbox**: metal gears in the MG90S slow the motor down and make it much stronger.
4. **Potentiometer**: a knob joined to the output shaft. It tells the board the shaft's real angle.

The board compares *the angle it was told* with *the angle the potentiometer reads*, and drives the motor until they match. This is called a **closed loop**. It's why a servo pushes back when you try to move it.

### 1.2 MG90S at a glance

| Spec | Value |
| --- | --- |
| Rotation | about 0° to 180° |
| Supply voltage | 4.8 to 6.0 V |
| Strength (stall torque) | about 1.8 kg·cm at 4.8 V, 2.2 kg·cm at 6 V |
| Speed | about 0.10 s per 60° at 4.8 V |
| Current | about 10 mA resting, 100–250 mA moving, up to 700 mA when blocked |
| Weight | 13.4 g |

**What does 1.8 kg·cm mean?** The servo can just hold 1.8 kg on an arm 1 cm long, or 0.9 kg on an arm 2 cm long. A longer arm makes it weaker. Our robot weighs about 460 g, and each lift servo carries about 115 g at the foot. That's well inside what an MG90S can hold, but only if the foot isn't too far out to the side (Chapter 5).

### 1.3 Pulse length sets the angle

The orange signal wire carries a **pulse**: it switches on for a short time, then off, 50 times every second (every 20 ms). The **length of the on part** tells the servo which angle to go to.

| Pulse length | Angle |
| --- | --- |
| 500 µs (0.5 ms) | 0° |
| 975 µs | 45° |
| 1450 µs | 90° (centre) |
| 1925 µs | 135° |
| 2400 µs | 180° |

Every 1° adds about 10.56 µs:

<div class="formula">pulse (µs) = 500 + angle × 10.56</div>

Drag the slider to see the pulse and the horn move together:

{{SERVOSIM}}

**What does the battery voltage change?** Not the angle. At 4.8 V or 6 V, a 1450 µs pulse means 90°. A higher voltage only makes the servo **faster and stronger**. Flat batteries make it weak, slow and jittery.

### 1.4 The three wires

| Wire colour | Job | Goes to |
| --- | --- | --- |
| Brown | GND (−) | battery − (through the servo module) |
| Red | power (+), 4.8–6 V | battery + (through the servo module) |
| Orange | signal (the pulse) | a servo module channel |

### 1.5 The horn and its teeth

The horn pushes onto the shaft's teeth (the **spline**). The MG90S shaft has about 20 teeth, so the horn can only go on in steps of about 18°. It's very unlikely to point exactly where you want: it will usually be a few degrees off. That's why we **centre every servo with code before fitting the horn** (4.2), then fix the last few degrees with **trim numbers** in the code (4.9).

**Check yourself (Chapter 1)**

- [ ] What part inside the servo measures the real angle?
- [ ] What pulse length gives 90°? And 135°?
- [ ] Does a higher battery voltage change the angle? What does it change?
- [ ] Why can't a horn point at exactly any angle you like?

## Chapter 2 · The servo module (PCA9685) {#ch2}

The ESP32 could make servo pulses itself, but 8 servos cause two problems:

- **Power:** 8 moving servos can pull 2–3 A. The ESP32 and its USB cable can give only about 0.5 A. The board would keep resetting.
- **Pins and timing:** 8 servos need 8 pins all sending perfect pulses, all the time, while the ESP32 is busy with other jobs.

The **PCA9685** module solves both. It makes the pulses for up to **16 servos** by itself. The servos take their power from the batteries through the module's green terminal, not from the ESP32. The ESP32 only sends commands like "channel 4: 1450 µs" over two wires called **I2C**.

### 2.1 The module's pins

| Pin | Job | Connect to |
| --- | --- | --- |
| GND | ground | ESP32 GND |
| OE | output enable | leave it unconnected |
| SCL | I2C clock | ESP32 GPIO 22 |
| SDA | I2C data | ESP32 GPIO 21 |
| VCC | power for the chip (3.3 V) | ESP32 3V3 |
| V+ | servo power | leave it: the green terminal feeds it |
| Green terminal | servo power in | 4 × AA pack: red to **V+**, black to **GND** |
| 16 × 3-pin rows | servo plugs, channels 0–15 | brown wire on the GND side |

**I2C** is a way for chips to talk over two shared wires, SDA (data) and SCL (clock). Every device has an **address**. The PCA9685 is at **0x40**.

### 2.2 Wiring

{{WIRING}}

There are **two separate power supplies** here. The USB cable powers the ESP32, and the ESP32's 3V3 pin powers the module's chip. The batteries power only the servos. The GND wire joins the two, so the signals have a common reference.

<div class="warn" markdown="1">
Check the battery polarity at the green terminal before you switch on: **red to V+, black to GND**. The wrong way round can destroy the module.
</div>

### 2.3 Activity: find the module

Upload this sketch, open the Serial Monitor, and check that the ESP32 can see the module.

{{CODE:P1_i2c_scanner}}

| Code | What it does |
| --- | --- |
| `Wire.begin();` | Starts I2C. On the ESP32 that's SDA = GPIO 21, SCL = GPIO 22 |
| `Wire.beginTransmission(address);` | "Is anyone at this address?" |
| `Wire.endTransmission() == 0` | 0 means a device answered |
| `Serial.println(address, HEX);` | Prints the address in hexadecimal, like `40` |

You should see `Found a device at 0x40`. If you see "Nothing found", check the four wires: VCC, GND, SDA and SCL. SDA and SCL swapped is the most common mistake.

**Check yourself (Chapter 2)**

- [ ] Give two reasons we use the servo module instead of plugging servos into the ESP32.
- [ ] Which two wires does I2C use? What are they connected to on the ESP32?
- [ ] Where do the batteries connect? Where must they never connect?
- [ ] The scanner found `0x40`. What is at that address?

## Chapter 3 · Controlling servo motors {#ch3}

### 3.1 Activity: move one servo

Plug one servo into **channel 0**, brown wire on the GND side. Switch on the batteries, then upload:

{{CODE:P2_one_servo}}

| Code | What it does |
| --- | --- |
| `#include <Adafruit_PWMServoDriver.h>` | Loads the library that talks to the PCA9685 |
| `Adafruit_PWMServoDriver pca = ...(0x40);` | Creates `pca`, the module at address 0x40 |
| `pca.setPWMFreq(50);` | 50 pulses a second: what servos expect |
| `pca.setOscillatorFrequency(27000000);` | Tells the library the chip's real clock speed, so the pulse lengths come out right |
| `void writeServo(int channel, float angle)` | Our own **function**: changes an angle into a pulse length (1.3) and sends it |
| `pca.writeMicroseconds(channel, us);` | "Channel 0: send pulses this many µs long", from now until we say otherwise |
| `for (int a = 90; a <= 135; a++)` | Counts 90, 91, 92 ... 135. Moving 1° at a time makes the movement smooth |
| `delay(15);` | 15 ms per degree. Smaller is faster |

Try it: change `delay(15)` to `delay(5)`, then to `delay(40)`. What happens?

### 3.2 Activity: the servo tester

This sketch lets you type any channel and angle. You'll use it again to check servos and wiring.

{{CODE:P3_servo_tester}}

| Code | What it does |
| --- | --- |
| `Serial.readStringUntil('\n')` | Reads one line you typed in the Serial Monitor |
| `sscanf(line.c_str(), "%d %d", &channel, &angle)` | Splits the line into two whole numbers. It gives back how many it found |
| `if (channel < 0 \|\| channel > 15 ...)` | Ignores numbers that don't make sense, so a typing mistake can't hurt a servo |

Try it: type `0 90`, then `0 0`, then `0 180`. Then move the plug to channel 5 and type `5 45`.

### 3.3 Activity: one leg takes a step

A leg has two servos: the **hip** (forward and back) and the **lift** (up and down). Plug the hip servo into **channel 0** and the lift servo into **channel 1**. A step only works if the moves happen in the right order: lift, swing forward, put down, push back.

{{CODE:P4_one_leg_step}}

| Code | What it does |
| --- | --- |
| `int angleNow[16];` | An **array**: 16 numbers in a row, one for each channel. The module can't tell us where a servo is, so the code remembers it |
| `angleNow[channel] = angle;` | Remembers where we sent it |
| `void moveSlow(int channel, int target)` | Moves one servo 1° at a time from where it is now to `target` |
| `(target > angleNow[channel]) ? 1 : -1` | Count up (+1) if the target is bigger, otherwise down (−1) |
| `while (angleNow[channel] != target)` | Keep going until it gets there |

Try it: swap lines 2 and 3 in `loop()`. The foot now drags along the floor. Why?

### 3.4 From servo angles to leg angles

In the robot code we stop thinking in servo angles (0–180) and think in **leg angles** instead. **0 means the middle**:

| Leg angle | Meaning |
| --- | --- |
| hip = 0 | the leg points straight out |
| hip > 0 | the foot moves **forward** (towards the sensor head) |
| lift = 0 | the top of the leg is level |
| lift > 0 | the foot goes **up** |
| lift < 0 | the foot goes **down**, pushing the body up |

The code changes leg angles into servo angles with one line:

<div class="formula">servo angle = 90 + DIR × leg angle + TRIM</div>

- **TRIM** fixes the few degrees the horn is off (1.5).
- **DIR** is +1 or −1. The servos on the left and right sides face opposite ways, so the same servo turn moves a left foot back but a right foot forward. DIR flips it so that "+" always means forward.

You'll find each leg's TRIM and DIR in Chapter 4.

**Check yourself (Chapter 3)**

- [ ] What does `pca.writeMicroseconds(0, 1450)` do?
- [ ] Why does the code keep the angles in an array?
- [ ] In 3.3, why must the foot lift before the hip swings forward?
- [ ] A leg has TRIM = 4 and DIR = −1. Which servo angle gives hip = 10?

## Chapter 4 · Assembly and calibration {#ch4}

{{IMG:exploded_iso.png|The robot pulled apart: bottom plate with the battery inside, 4 spacers, lid with the ESP32 board and servo module, and the 4 legs}}

### 4.1 Before you start

| Printed part | Qty |
| --- | --- |
| `body_bottom` (flat plate) | 1 |
| `body_top` (lid) | 1 |
| `spacer` (lid pillars) | 4 |
| `coxa` (shoulder) | 4 |
| `leg` | 4 |
| `sensor_head` | 1 |

Print one shoulder and one leg first and test them (4.2–4.4) before printing the rest.

### 4.2 Centre every servo first

Plug all 8 servos into the module: **channels 0, 1, 4, 5, 8, 9, 12 and 13**. Switch on the batteries and upload:

{{CODE:P5_center_all}}

Every servo is now at exactly 90°. Leave the sketch running while you fit the horns (4.3), so nothing gets pushed off centre. Label each servo with its channel number (a piece of tape on the cable).

### 4.3 Fit the horns

{{IMG:joint_exploded.png|One joint: the horn drops into the pocket on the leg, 2 small screws go through the horn's holes into the slot, and the leg pushes onto the servo}}

1. Drop a single-arm horn into the pocket on the **leg**, spline hole facing out.
2. Drive **2 M2 self-tapping screws** through 2 horn holes that sit over the slot. Leave a gap between them, for example the 2nd and 5th holes from the centre. The screws cut their own thread into the sides of the slot.
3. Do the same on the flat plate of each **shoulder**.

### 4.4 Build each leg

{{IMG:shoulder_closeup.png|One leg built: the hip servo (left), the blue shoulder with the lift servo in its wall, and the yellow leg on the lift servo}}

1. Push the **lift servo** through the shoulder's wall, shaft on the leg side, and screw its tabs on with the screws from its bag.
2. Push the **leg** onto the lift servo's shaft so that the top of the L is **level** and the foot points down. Fit the servo's small centre screw through the hole in the middle.
3. Repeat for all 4 legs. Every leg is built the same way.

### 4.5 The body

{{IMG:body_inside.png|Inside the body: hip servos in the 4 corners, the battery pack in the middle, and the 4 spacers}}

1. Push the 4 **hip servos** into the corners of the bottom plate, shafts up, and screw their tabs on. The cables go down through the notch.
2. Strap the **4 × AA holder** to the middle of the plate with the Velcro strap. Bring its wires up to the back-right corner.
3. Screw the 4 **spacers** on from under the plate with M3 screws.
4. Push each **shoulder** onto its hip servo so that it points straight out from the corner, diagonally. Fit the centre screw.

### 4.6 The lid

1. Sit the **ESP32 expansion board** in the 4 corner holders. Pass 2 zip ties through the slots beside it and over the board. The USB socket faces the side.
2. Screw the **PCA9685** to the 4 short posts at the back (M2.5).
3. Bolt the **sensor head** to the 2 front holes (M3).
4. Feed the servo cables and the battery wires up through the **slot at the back-right**. Screw the lid onto the spacers.

### 4.7 Plug in the servos

{{IMG:assembled_top.png|Top view: the front (sensor head) is at the top of the picture}}

| Leg | Hip channel | Lift channel |
| --- | --- | --- |
| 0 rear-left | 0 | 1 |
| 1 rear-right | 4 | 5 |
| 2 front-right | 8 | 9 |
| 3 front-left | 12 | 13 |

Left and right are as the robot sees them, looking forward. Brown wires go on the GND side of every plug.

### 4.8 Why calibrate?

Every servo is a little different, and the horns sit up to about 9° off (1.5). Calibration finds two numbers for every joint:

- **TRIM** (degrees): what to add so that leg angle 0 really is straight out and level.
- **DIR** (+1 or −1): which way round is forward and up for that servo.

### 4.9 Activity: calibrate

Upload this sketch and open the Serial Monitor:

{{FULL:P6_calibrate}}

1. Every joint goes to 0. Look at each leg from above: the shoulder should point **straight out** from the corner, diagonally. Look from the side: the top of the leg should be **level**.
2. If a leg is off, type a trim and watch it move. For example, `h 0 5` moves leg 0's hip trim to +5°, and `l 2 -4` moves leg 2's lift trim to −4°. Try numbers until the joint looks right.
3. Type `test`. Each leg swings its foot, then lifts it, one at a time. Read the Serial Monitor: the foot must swing **forward** (towards the sensor head), then go **up**. If one goes the wrong way, flip it: `fh 1` for leg 1's hip, `fl 1` for its lift. Type `test` again.
4. Type `print`. **Copy the 4 lines it prints** and paste them into the next sketches (P7, P8 and P9), over the lines between `PASTE YOUR CALIBRATION HERE` and the dashed line.

Record your numbers here too:

| Leg | Hip trim | Lift trim | Hip dir | Lift dir |
| --- | --- | --- | --- | --- |
| 0 rear-left |  |  |  |  |
| 1 rear-right |  |  |  |  |
| 2 front-right |  |  |  |  |
| 3 front-left |  |  |  |  |

<div class="note" markdown="1">
**Trim more than about 10°?** The horn is a whole tooth out. Take the leg off, run P5 again, and refit the horn one tooth round.
</div>

**Checklist (Chapter 4)**

- [ ] All 8 servos centred with P5 before the horns went on
- [ ] Every horn held by 2 screws
- [ ] Shoulders point straight out, diagonally
- [ ] Servos plugged into the right channels, brown wire on GND
- [ ] At 0, every leg points straight out and is level (trims done)
- [ ] `test`: every foot swings forward, then goes up (directions done)
- [ ] Calibration numbers copied into P7, P8 and P9

## Chapter 5 · Stand up and sit down {#ch5}

### 5.1 The idea

Standing and sitting use only the 4 **lift** servos. Turning a foot down pushes the body up. Turning it up lowers the body until it rests on the floor.

{{STANDSIT}}

| Pose | Lift angle | What happens |
| --- | --- | --- |
| Sit | +35° (`SIT`) | feet up, the body rests on the floor |
| Stand | −15° (`STAND`) | feet down, the body is about 4 cm off the floor |

**Why stand at −15° and not 0°?** At −15° the foot sits closer in, under the lift servo. The robot's weight then pushes on a shorter arm (about 24 mm instead of 45 mm), so each servo needs about half the strength to hold it up (1.2).

### 5.2 The robot code

From now on, every sketch starts with the same robot code. Three functions do most of the work.

**`setLeg`: put one leg at a hip and lift angle**

{{PART:P7_stand_sit|// Put one leg at a hip angle|// Move all 4 legs together}}

| Code | What it does |
| --- | --- |
| `constrain(hip, -LIMIT, LIMIT)` | Never more than 35° from the middle, so a leg can't hit the body |
| `90 + HIP_DIR[leg] * hip + HIP_TRIM[leg]` | Leg angle → servo angle (3.4) |
| `hipNow[leg] = hip;` | Remembers where the leg is now |

**`moveLegs`: move all 4 legs smoothly, at the same time**

{{PART:P7_stand_sit|// Move all 4 legs together|void standUp() {}}

| Code | What it does |
| --- | --- |
| `hip0[i] = hipNow[i];` | Where each leg starts |
| `int steps = max(1, ms / 20);` | One small move every 20 ms. 1500 ms = 75 small moves |
| `float f = (float)s / steps;` | How far through the move we are: 0.01, 0.02 ... 1.0 |
| `hip0[i] + (hip[i] - hip0[i]) * f` | The angle that far between the start and the end. All legs arrive together |

**`standUp` and `sitDown`**

{{PART:P7_stand_sit|void standUp() {|void setup() {}}

### 5.3 Activity: stand up and sit down

Paste your calibration numbers into the sketch, put the robot on the floor, switch on the batteries and upload:

{{FULL:P7_stand_sit}}

Type `s` to stand up and `d` to sit down.

Try it:

- Change `1500` in `standUp()` to `600`. What changes? Is it better or worse?
- Change `STAND` to `-25`. The robot stands taller. Does it still stand steadily?
- Make the robot do 3 "push-ups" in a row with a `for` loop.

**Check yourself (Chapter 5)**

- [ ] Which servos move when the robot stands up?
- [ ] What does `moveLegs` do that `setLeg` doesn't?
- [ ] Why does the robot stand at −15° and not 0°?

## Chapter 6 · Walk forward {#ch6}

### 6.1 Why the robot can fall over

Hold a table up with 4 legs, then take one away. It stays up only if its weight is **over the triangle** made by the other 3 legs. The point where the weight acts is the **centre of mass**. For our robot it's near the middle of the body.

When the robot lifts one foot, the other 3 make a triangle on the floor. If the centre of mass is **outside or on the edge** of that triangle, the robot tips towards the lifted foot. With all 4 legs straight out, the triangle's long edge runs right through the middle, so the robot is on the very edge of tipping.

The fix is to keep the legs **spread out unevenly**: one step apart from each other. Then the triangle always covers the middle when a leg lifts. This way of walking, with one leg in the air at a time, is called a **creep gait**. Slow animals and most walking robots use it.

### 6.2 How the creep gait works

The legs move in this order: **rear-left → front-left → rear-right → front-right**. Each move has 3 parts:

1. **Step**: lift the leg that is furthest back, carry it to the front in the air, and put it down.
2. **Shift**: all 4 feet push back together on the floor. The feet don't slide, so the **body** moves forward.
3. Repeat with the next leg in the order.

Use the buttons to go through one full cycle:

{{GAIT}}

Each leg is always one step (`STEP` = 14°) apart from the next: −2, −1, 0, +1 steps. The leg at −2 is the next one to lift, and it goes to +2. After the shift every leg is one step further back, and a new leg is at −2.

### 6.3 The walking code

**`moveOneLeg` and `stepLeg`: move one leg while the others stay put**

{{PART:P8_walk_forward|// Move just one leg|// All 4 feet stay on the floor}}

| Code | What it does |
| --- | --- |
| `h[i] = hipNow[i];` | Copies where every leg is now ... |
| `h[leg] = hip;` | ... then changes only the one we want to move |
| `moveOneLeg(leg, hipNow[leg], UP, 150);` | Same hip, foot up (`UP` = +10°): lifts the foot about 2 cm |
| `moveOneLeg(leg, hip, UP, 200);` | Swings it to the new hip angle, still in the air |
| `moveOneLeg(leg, hip, STAND, 150);` | Puts it down |

**`shiftBody`: all 4 feet push together**

{{PART:P8_walk_forward|// All 4 feet stay on the floor|// Starting pattern for walking}}

**`getReady`: spread the legs into the starting pattern**

{{PART:P8_walk_forward|// Starting pattern for walking|// Put every foot back to hip 0}}

`target = dir * (j - 2) * STEP` gives the legs in walking order −2, −1, 0 and +1 steps: −28°, −14°, 0° and +14°.

**`walkForward`: the gait itself**

{{PART:P8_walk_forward|// Leg order for walking forward|void setup() {}}

| Code | What it does |
| --- | --- |
| `FWD_ORDER[4] = {0, 3, 1, 2}` | Leg numbers in walking order: rear-left, front-left, rear-right, front-right |
| `stepLeg(FWD_ORDER[j], 2 * STEP);` | The back-most leg (at −28°) steps to the front (+28°) |
| `shiftBody(-STEP);` | Every hip goes back 14°: the body moves forward about 1.3 cm |
| `standStill();` | At the end, bring every foot back to 0, one leg at a time |

### 6.4 Activity: walk forward

Paste your calibration numbers, put the robot on the floor and upload:

{{FULL:P8_walk_forward}}

Type `f` to walk 2 cycles forward (8 steps). Type `d` to sit when you've finished.

**If it doesn't walk well**

| Problem | Try |
| --- | --- |
| A foot drags on the floor when it swings | Raise `UP` from 10 to 15 |
| It tips towards the lifted leg | Check the batteries are in the middle of the body; increase `STEP` to 16 (wider spread) |
| It walks in a curve | Check the hip trims: at 0 all 4 shoulders must point exactly diagonally |
| It sags or a servo buzzes | Fresh batteries. Or move `STAND` closer to −20 (feet further in) |
| A leg moves backward when it should go forward | That leg's hip DIR is wrong: run P6 `test` again |

Try it:

- Make it walk faster. Which numbers would you change? What goes wrong if you go too fast?
- Change `walkForward(2)` so it walks 5 cycles.

**Check yourself (Chapter 6)**

- [ ] What is the centre of mass, and why must it stay inside the triangle of feet?
- [ ] In what order do the legs step?
- [ ] During the shift, all 4 feet push back. Why does the body move forward?
- [ ] What would happen if all 4 legs stood at hip = 0 and one leg lifted?

## Chapter 7 · Walk backward {#ch7}

### 7.1 The idea: play it backwards

Walking backward is walking forward played in reverse:

| | Forward | Backward |
| --- | --- | --- |
| Leg order | rear-left, front-left, rear-right, front-right | front-right, rear-right, front-left, rear-left (reversed) |
| Which leg steps | the back-most one | the front-most one |
| It steps to | +2 steps (the front) | −2 steps (the back) |
| The shift | hips −14°: body goes forward | hips +14°: body goes backward |

Click **Backward** on the gait diagram in 6.2 to watch it.

### 7.2 The code

`getReady`, `stepLeg`, `shiftBody` and `standStill` stay exactly the same. We add the reversed order and one new function:

{{PART:P9_walk_backward|// Leg order for walking backward|void setup() {}}

| Code | What it does |
| --- | --- |
| `BACK_ORDER[4] = {2, 1, 3, 0}` | `FWD_ORDER` {0, 3, 1, 2} backwards |
| `getReady(BACK_ORDER, -1);` | `dir` = −1 flips the pattern: +28°, +14°, 0°, −14° |
| `stepLeg(BACK_ORDER[j], -2 * STEP);` | The front-most leg steps to the back |
| `shiftBody(+STEP);` | Every hip goes forward 14°: the body moves back |

### 7.3 Activity: the whole robot

This sketch has everything: stand, sit, forward and backward. Paste your calibration numbers and upload:

{{FULL:P9_walk_backward}}

| Type | The robot |
| --- | --- |
| `s` | stands up |
| `d` | sits down |
| `f` | walks forward 2 cycles |
| `b` | walks backward 2 cycles |

**Challenges**

1. **A dance:** stand, walk forward 1 cycle, backward 1 cycle, sit, stand, then sit again. Do it with a new command, `x`.
2. **Turn on the spot:** when the robot turns, every foot moves the same way **round** the body, not forward. Hint: make a `turnBody(by)` that adds `by` to the right legs' hips (1 and 2) and subtracts it from the left legs' hips (0 and 3).
3. **Stop before a wall:** add the ultrasonic sensor on the front. Walk forward one cycle at a time, and sit down when something is closer than 15 cm.

**Check yourself (Chapter 7)**

- [ ] What 3 things change between walking forward and walking backward?
- [ ] Why can `stepLeg` and `shiftBody` stay the same?
- [ ] Your robot can stand, sit, walk forward and walk backward

## Troubleshooting and glossary {#help}

| Problem | Likely cause | Fix |
| --- | --- | --- |
| Scanner finds nothing | I2C wires | Check VCC to 3V3, GND to GND, SDA to 21, SCL to 22. Try swapping SDA and SCL |
| Servos don't move, scanner finds 0x40 | No servo power | Battery switch on? Red to V+, black to GND in the green terminal? |
| ESP32 keeps restarting when servos move | Servos powered from USB | Servo power must come from the batteries, through the green terminal |
| Upload fails: "Failed to connect" | ESP32 not in upload mode | Hold BOOT until the upload starts |
| One servo jitters | Weak batteries or a loose plug | Fresh batteries; push the plug in fully, brown on GND |
| A leg points the wrong way at 0 | Horn a tooth out | Run P5, refit the horn, calibrate again |
| Robot sinks or wobbles when standing | Not enough strength | Fresh batteries; `STAND` −20; lower infill to make the body lighter |

**Glossary**

| Word | Meaning |
| --- | --- |
| Servo | A motor that turns to an angle and holds it |
| Pulse | A short "on" signal; its length tells the servo the angle |
| µs | Microsecond: one millionth of a second |
| PCA9685 | The 16-channel servo module |
| I2C | Two-wire bus (SDA + SCL) that lets chips talk |
| Channel | One of the module's 16 servo outputs (0–15) |
| Horn | The plastic arm that fits on the servo's shaft |
| Spline | The teeth on the shaft that the horn grips |
| Trim | A small correction, in degrees, for one joint |
| Hip / lift | The servo that swings a leg forward and back / up and down |
| Centre of mass | The point where the robot's weight acts |
| Support triangle | The area between the feet on the floor |
| Creep gait | Walking with one leg in the air at a time |
