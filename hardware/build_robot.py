# Parametric MG90S quadruped spider robot
# Run headless:  freecadcmd.exe build_robot.py
# Change a parameter below, re-run, and every STL/STEP is regenerated.
#
# Frames used throughout (all mm):
#   Servo frame  : origin on the shaft axis, in the plane of the tab UNDERSIDE.
#                  +z = shaft direction, the case body extends toward -x.
#   Link frame   : servo frame raised to the horn face (HORN_FACE_Z). The link
#                  plate occupies z = 0..LINK_T, horn pocket on its z=0 face,
#                  horn arm points along +x when the servo is at 90 degrees.

import os, math, json
import FreeCAD as App
import Part, MeshPart, Import
from FreeCAD import Vector as V, Placement as P, Rotation as R

OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
OUT = os.environ.get("ROBOT_OUT", OUT)

# ---------------------------------------------------------------- parameters
# MG90S servo (nominal datasheet sizes - measure yours and adjust)
SERVO_L        = 22.8   # case length
SERVO_W        = 12.2   # case width
SHAFT_FROM_END = 5.9    # shaft centre to the near end of the case
TAB_SPAN       = 32.2   # tip-to-tip length of the mounting tabs
TAB_HOLE_PITCH = 27.8   # distance between the two tab screw holes
TAB_T          = 2.5    # tab thickness
BELOW_TAB      = 15.9   # case bottom to tab underside
ABOVE_TAB      = 6.6    # tab underside to top of case
HORN_FACE_Z    = 12.0   # tab underside to UNDERSIDE of the horn arm
HORN_HUB_R     = 3.9    # radius of the horn around the shaft
HORN_TIP_R     = 2.0    # radius of the rounded arm tip
HORN_ARM_LEN   = 17.0   # shaft centre to end of horn arm
HORN_T         = 1.6    # horn arm thickness

# Fit / printing
SERVO_CLEAR    = 0.5    # added around the servo case in pockets (was 0.3: too tight)
HORN_CLEAR     = 0.4    # added around the horn in pockets (was 0.2: horn too tight)
HORN_POCKET_D  = HORN_T + 0.4   # pocket depth
HORN_SLOT      = (6.5, 15.0)    # screw slot along the horn arm: from / to (mm from shaft)
HORN_SLOT_W    = 1.5    # M2 self-tapping screws cut their thread into the slot sides,
                        # so they grip at any of the horn's holes (hole spacing varies by brand)
TAB_SCREW_D    = 1.8    # pilot for servo tab screws (self tapping)
ACCESS_D       = 5.0    # hole to reach the horn centre screw
LINK_T         = 4.0    # plate thickness of all links

# Leg geometry (matches the regishsu spider code: length_c, length_a, length_b)
COXA_LEN       = 27.5
FEMUR_LEN      = 55.0
TIBIA_LEN      = 77.5

# 8-servo version (2 joints per leg): one L-shaped leg on the "lift" servo
LEG_OUT        = 45.0   # lift axis -> elbow, straight out
LEG_DOWN       = 75.0   # elbow -> foot tip, straight down
LEG_T          = 5.0    # leg plate thickness

# Body
BODY_HALF      = 63.0   # half width of the bottom plate
BODY_CHAMFER   = 112.0  # corners cut where |x|+|y| > this
BODY_T         = 4.0
HIP_R          = 46.0 * math.sqrt(2)  # hip shaft distance from centre (diagonals)
LID_Z          = 40.0   # underside of the lid above the bottom plate top
LID_HALF       = 54.0   # half width (left-right)
LID_HALF_Y     = 57.0   # half length (front-back): sensor head + ESP32 board + PCA9685
LID_CHAMFER    = 90.0
PILLARS        = [(48, 20), (48, -20), (-48, 20), (-48, -20)]   # at the sides, clear of the boards
COXA_WALL_T    = 5.0    # shoulder wall that holds the lift servo
M3_PILOT       = 2.5
M3_CLEAR       = 3.4
M25_PILOT      = 2.2

# Derived servo numbers
CASE_X0 = -(SERVO_L - SHAFT_FROM_END)      # -16.9
CASE_X1 = SHAFT_FROM_END                   #  +5.9
CASE_XC = (CASE_X0 + CASE_X1) / 2          #  -5.5
TAB_X0  = CASE_XC - TAB_SPAN / 2
TAB_X1  = CASE_XC + TAB_SPAN / 2
TAB_HOLES = [CASE_XC - TAB_HOLE_PITCH / 2, CASE_XC + TAB_HOLE_PITCH / 2]
HW = SERVO_W / 2

# Coxa bracket layout (in coxa link frame)
WALL_FACE_Y = -14.0                        # femur servo tabs rest on this face
FEMUR_Z     = 12.5                         # femur servo shaft height
WALL_TOP    = FEMUR_Z + HW + SERVO_CLEAR + 4.0

# ---------------------------------------------------------------- helpers
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

def cyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))

def prism(pts, z0, z1):
    w = Part.makePolygon([V(x, y, z0) for x, y in pts] + [V(pts[0][0], pts[0][1], z0)])
    return Part.Face(w).extrude(V(0, 0, z1 - z0))

def hull2(c1, r1, c2, r2, z0, z1):
    """Solid convex hull of two circles (a rounded, tapered bar)."""
    (x1, y1), (x2, y2) = c1, c2
    d = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    px, py = -uy, ux
    k = (r1 - r2) / d
    s = math.sqrt(max(0.0, 1 - k * k))
    pts = []
    for sign in (1, -1):
        nx, ny = k * ux + sign * s * px, k * uy + sign * s * py
        pts.append(((x1 + r1 * nx, y1 + r1 * ny), (x2 + r2 * nx, y2 + r2 * ny)))
    quad = [pts[0][0], pts[0][1], pts[1][1], pts[1][0]]
    return prism(quad, z0, z1).fuse([cyl(r1, z0, z1, x1, y1), cyl(r2, z0, z1, x2, y2)])

def placed(shape, pl):
    s = shape.copy()
    s.Placement = pl.multiply(s.Placement)
    return s

def fuse(*shapes):
    return shapes[0].fuse(list(shapes[1:])).removeSplitter()

def octagon(half, chamfer, half_y=None):
    hy = half if half_y is None else half_y
    cx, cy = chamfer - half, chamfer - hy
    return [(half, cx), (cy, hy), (-cy, hy), (-half, cx),
            (-half, -cx), (-cy, -hy), (cy, -hy), (half, -cx)]

# ---------------------------------------------------------------- cutters
def servo_pocket(plate_t):
    """Cut for a servo dropped into a plate (plate occupies z=-plate_t..0)."""
    c = SERVO_CLEAR
    cut = box(CASE_X0 - c, CASE_X1 + c, -HW - c, HW + c, -plate_t - 1, 1)
    # corner reliefs: printed inside corners come out rounded, so give the
    # servo's sharp corners somewhere to go
    for cx in (CASE_X0 - c, CASE_X1 + c):
        for cy in (-HW - c, HW + c):
            cut = cut.fuse(cyl(1.0, -plate_t - 1, 1, cx, cy))
    for hx in TAB_HOLES:
        cut = cut.fuse(cyl(TAB_SCREW_D / 2, -plate_t - 1, 1, hx, 0))
    return cut

def horn_pocket():
    """Cut on the z=0 face of a link: horn arm recess, centre screw access,
    and a through slot under the horn's holes for M2 self-tapping screws."""
    c = HORN_CLEAR
    arm = hull2((0, 0), HORN_HUB_R + c, (HORN_ARM_LEN - HORN_TIP_R, 0), HORN_TIP_R + c,
                -1, HORN_POCKET_D)
    slot = hull2((HORN_SLOT[0], 0), HORN_SLOT_W / 2, (HORN_SLOT[1], 0), HORN_SLOT_W / 2, -1, LINK_T + 8)
    return arm.fuse([cyl(ACCESS_D / 2, -1, LINK_T + 8), slot])

# ---------------------------------------------------------------- parts
# Placement of the femur servo frame inside the coxa link frame:
#   servo x -> +X (outward), servo y -> -Z, servo z (shaft) -> +Y
PL_FEMUR_SERVO_IN_COXA = P(V(COXA_LEN, WALL_FACE_Y, FEMUR_Z), R(V(1, 0, 0), -90))

def make_coxa():
    """Shoulder: a flat plate on the hip horn + one straight wall that holds the lift servo."""
    t, w = LINK_T, COXA_WALL_T
    x_end = TAB_X1 + COXA_LEN + 6.0      # 3 mm free space past each servo tab
    x_start = TAB_X0 + COXA_LEN - 6.0
    hub = hull2((0, 0), 11, (15, 0), 6, 0, t)
    arm = box(0, x_end, WALL_FACE_Y - w, -5, 0, t)
    wall = box(x_start, x_end, WALL_FACE_Y - w, WALL_FACE_Y, 0, WALL_TOP)
    body = fuse(hub, arm, wall)
    body = body.cut(horn_pocket())
    body = body.cut(placed(servo_pocket(w), PL_FEMUR_SERVO_IN_COXA))
    return body.removeSplitter()

def make_femur():
    t = LINK_T
    bar = hull2((0, 0), 9, (FEMUR_LEN - 15, 0), 7, 0, t)
    seat = box(FEMUR_LEN + TAB_X0 - 2, FEMUR_LEN + TAB_X1 + 3, -HW - 3.3, HW + 3.3, 0, t)
    body = fuse(bar, seat).cut(horn_pocket())
    body = body.cut(placed(servo_pocket(t), P(V(FEMUR_LEN, 0, t), R())))
    return body.removeSplitter()

def tibia_hub():
    return hull2((0, 0), 9, (15, 0), 5.5, 0, LINK_T)

def make_tibia():
    leg = hull2((0, 0), 9, (0, TIBIA_LEN - 4), 4, 0, LINK_T)
    return fuse(tibia_hub(), leg).cut(horn_pocket()).removeSplitter()

def make_leg():
    """8-servo leg: hub on the lift servo horn, out LEG_OUT, then down LEG_DOWN (+y = down at centre)."""
    upper = hull2((0, 0), 9.5, (LEG_OUT, 0), 7.5, 0, LEG_T)
    lower = hull2((LEG_OUT, 0), 7.5, (LEG_OUT, LEG_DOWN - 4.5), 4.5, 0, LEG_T)
    return fuse(upper, lower).cut(horn_pocket()).removeSplitter()

def make_leg_interface():
    """Student starting file: the hub that fits the horn + a short stub to design from."""
    stub = hull2((0, 0), 9.5, (20, 0), 7.5, 0, LEG_T)
    return stub.cut(horn_pocket()).removeSplitter()

def make_tibia_interface():
    stub = hull2((0, 0), 9, (0, 18), 6, 0, LINK_T)
    return fuse(tibia_hub(), stub).cut(horn_pocket()).removeSplitter()

def hip_placements():
    out = []
    for i in range(4):
        a = 45 + 90 * i
        ar = math.radians(a)
        out.append(P(V(HIP_R * math.cos(ar), HIP_R * math.sin(ar), 0), R(V(0, 0, 1), a)))
    return out

# 4 x AA holder sits INSIDE on the bottom plate (flat holder ~63 x 58 x 16 mm), strapped down
AA_HOLDER = (63.0, 58.0, 16.0)
STRAP_X = 36.0                         # strap slots just outside the holder
# Buck-boost 5V module (powers the ESP32 board from the AA pack), behind the battery
BUCK_POS = (-12.0, 40.0)

def make_body_bottom():
    """Flat plate. The battery pack and buck-boost sit on top of it, the spacers screw on from below."""
    body = prism(octagon(BODY_HALF, BODY_CHAMFER), -BODY_T, 0)
    cuts = []
    for pl in hip_placements():
        cuts.append(placed(servo_pocket(BODY_T), pl))
        # notch so the servo cable can come up through the plate
        cuts.append(placed(box(CASE_X0 - 6, CASE_X0, -3, 3, -BODY_T - 1, 1), pl))
    for px, py in PILLARS:          # M3 clearance holes, screw heads underneath
        cuts.append(cyl(M3_CLEAR / 2, -BODY_T - 1, 1, px, py))
    for sx in (-STRAP_X, STRAP_X):   # AA holder strap slots
        cuts.append(box(sx - 1.5, sx + 1.5, -12, 12, -BODY_T - 1, 1))
    bx, by = BUCK_POS               # zip-tie slots either side of the buck-boost module
    for sx in (-13, 13):
        cuts.append(box(bx + sx - 1.5, bx + sx + 1.5, by - 4, by + 4, -BODY_T - 1, 1))
    return body.cut(cuts).removeSplitter()

def make_spacer():
    """Lid spacer (print 4, standing up). M3 self-tapping screw into each end."""
    tube = cyl(4.5, 0, LID_Z)
    return tube.cut(cyl(M3_PILOT / 2, -1, LID_Z + 1)).removeSplitter()

# Lid layout (front = -y):  sensor head | ESP32 expansion board | PCA9685
PCA_Y0 = 28.7                                   # front edge of the PCA9685 board
PCA_HOLES = [(-28, PCA_Y0 + 3.2), (28, PCA_Y0 + 3.2), (-28, PCA_Y0 + 22.2), (28, PCA_Y0 + 22.2)]
TOP_MOUNT = [(-31, -50), (31, -50)]             # M3 bolts for the sensor head
ESP_BOARD = (78.0, 63.0)    # ESP32 38-pin expansion board, measure yours (some are 71 x 56)
ESP_YC = -8.2               # board centre
ESP_LIFT = 6.0              # board underside above the lid (room for solder pins)
ESP_CLEAR = 0.6
CABLE_SLOT = (33.0, 43.0, 29.0, 45.0)           # x0, x1, y0, y1: servo + battery wires come up here
DHT_POST = (-44.0, -34.0, 30.0, 36.0, 22.0)     # x0, x1, y0, y1, height: DHT22 on the back face

def bx(xa, xb, ya, yb, z0, z1):
    return box(min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), z0, z1)

def esp_corner_pieces(z1):
    """L-shaped corner holders: the board's corners rest on a ledge, the walls stop it sliding."""
    ax, ay = ESP_BOARD[0] / 2 + ESP_CLEAR, ESP_BOARD[1] / 2 + ESP_CLEAR
    top = z1 + ESP_LIFT + 2.5
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * ax, ESP_YC + sy * ay
            out.append(bx(cx - sx * 6, cx, cy - sy * 6, cy, z1, z1 + ESP_LIFT))       # ledge
            out.append(bx(cx, cx + sx * 2, cy - sy * 10, cy + sy * 2, z1, top))       # wall along y
            out.append(bx(cx - sx * 10, cx + sx * 2, cy, cy + sy * 2, z1, top))       # wall along x
    return out

def make_body_top():
    z0, z1 = LID_Z, LID_Z + BODY_T
    lid = prism(octagon(LID_HALF, LID_CHAMFER, LID_HALF_Y), z0, z1)
    standoffs = [cyl(3.0, z1, z1 + 4, x, y) for x, y in PCA_HOLES]
    px0, px1, py0, py1, ph = DHT_POST
    post = box(px0, px1, py0, py1, z1, z1 + ph)
    body = fuse(lid, post, *standoffs, *esp_corner_pieces(z1))
    cuts = [cyl(M3_CLEAR / 2, z0 - 1, z1 + 1, x, y) for x, y in PILLARS]
    cuts += [cyl(M25_PILOT / 2, z0 + 1, z1 + 5, x, y) for x, y in PCA_HOLES]
    cuts += [cyl(M3_CLEAR / 2, z0 - 1, z1 + 1, x, y) for x, y in TOP_MOUNT]
    x0, x1, y0, y1 = CABLE_SLOT
    cuts.append(box(x0, x1, y0, y1, z0 - 1, z1 + 1))
    # zip-tie slots either side of the ESP32 board (tie goes over the board, under the lid)
    ax = ESP_BOARD[0] / 2 + ESP_CLEAR + 3.5
    for sx in (-ax, ax):
        for sy in (ESP_YC - 18, ESP_YC + 18):
            cuts.append(box(sx - 1.5, sx + 1.5, sy - 2.5, sy + 2.5, z0 - 1, z1 + 1))
    # DHT22: M3 screw through the post (sensor on the back face), zip-tie slot as a backup
    cuts.append(Part.makeCylinder(M3_PILOT / 2, py1 - py0 + 2, V((px0 + px1) / 2, py0 - 1, z1 + ph - 5), V(0, 1, 0)))
    cuts.append(box(px0 - 1, px1 + 1, py0 + 1.5, py1 - 1.5, z1 + 8, z1 + 10.5))
    return body.cut(cuts).removeSplitter()

# Sensor head: bolts onto the 2 front holes of the lid (lid top = z 0 in this part).
# Front wall holds the HC-SR04 (two transducers poke through, facing -y = FRONT).
US_SPACING = 26.0     # HC-SR04 transducer centre distance
US_HOLE_D = 16.6      # transducer hole (16 mm transducers + clearance)
US_Z = 14.0           # transducer centre height above the lid
SH_FRONT = -LID_HALF_Y   # front face of the sensor head = front edge of the lid

def make_sensor_head():
    f = SH_FRONT
    base = box(-36, 36, f, f + 12, 0, 4)
    wall = box(-26, 26, f, f + 4, 0, US_Z + 14)
    gussets = []
    for gx in (-26, 23):   # outside the HC-SR04 board (45 mm wide)
        tri = Part.Face(Part.makePolygon([V(gx, f + 4, 4), V(gx, f + 4, US_Z + 10), V(gx, f + 12, 4), V(gx, f + 4, 4)]))
        gussets.append(tri.extrude(V(3, 0, 0)))
    body = fuse(base, wall, *gussets)
    cuts = [cyl(M3_CLEAR / 2, -1, 5, x, y) for x, y in TOP_MOUNT]
    for sx in (-US_SPACING / 2, US_SPACING / 2):
        cuts.append(Part.makeCylinder(US_HOLE_D / 2, 8, V(sx, f - 2, US_Z), V(0, 1, 0)))
    return body.cut(cuts).removeSplitter()

def make_fit_test():
    t = LINK_T
    plate = box(TAB_X0 - 3, 52, -10, 10, -t, 0)
    plate = plate.cut(servo_pocket(t))
    horn = placed(horn_pocket(), P(V(30, 0, 0), R(V(1, 0, 0), 180)))
    return plate.cut(horn).removeSplitter()

def make_screw_test():
    """Block with one hole of every screw size used on the robot.
    Notches on the edge = hole number (1 notch = hole 1 ...)."""
    holes = [(TAB_SCREW_D, False, "servo tab screw (M2 self-tap)"),
             (M25_PILOT, False, "PCA9685 (M2.5 self-tap)"),
             (M3_PILOT, False, "lid pillars (M3 self-tap)"),
             (M3_CLEAR, True, "lid / top mount (M3 clearance)")]
    pitch, h = 14.0, 10.0
    blk = box(0, pitch * len(holes) + 4, 0, 14, 0, h)
    cuts = []
    for i, (d, through, _) in enumerate(holes):
        x = 9 + pitch * i
        cuts.append(cyl(d / 2, (-1 if through else 2.0), h + 1, x, 7))
        for n in range(i + 1):   # notches on the front edge
            cuts.append(box(x - 4 + n * 2.6, x - 4 + n * 2.6 + 1.2, -1, 1.0, h - 1.5, h + 1))
    return blk.cut(cuts).removeSplitter()

def make_leg_test_stand():
    """Clamp this to a table edge (rails on the table, +x edge flush with the table edge).
    One hip servo drops into the pocket, the leg hangs off the table."""
    t, rail_h = 5.0, 20.0
    shaft_x = 26.0
    plate = box(-40, 40, -35, 35, -t, 0)
    rails = [box(-40, 40, sy - 4, sy + 4, -t - rail_h, -t) for sy in (-31, 31)]
    body = fuse(plate, *rails)
    body = body.cut(placed(servo_pocket(t), P(V(shaft_x, 0, 0), R(V(0, 0, 1), 0))))
    body = body.cut(placed(box(CASE_X0 - 6, CASE_X0, -3, 3, -t - 1, 1), P(V(shaft_x, 0, 0), R())))
    return placed(body, P(V(0, 0, t + rail_h), R())).removeSplitter()

# ---------------------------------------------------------------- dummies (assembly only)
def servo_dummy():
    case = box(CASE_X0, CASE_X1, -HW, HW, -BELOW_TAB, ABOVE_TAB)
    tabs = box(TAB_X0, TAB_X1, -HW, HW, 0, TAB_T)
    boss = cyl(HW - 0.2, ABOVE_TAB, ABOVE_TAB + 2.4)
    hub = cyl(3.4, ABOVE_TAB + 2.4, HORN_FACE_Z)
    return fuse(case, tabs, boss, hub)

def horn_dummy():   # in link frame
    return hull2((0, 0), HORN_HUB_R, (HORN_ARM_LEN - HORN_TIP_R, 0), HORN_TIP_R, 0, HORN_T)

def horn_screws_dummy(at=(9.0, 13.0), length=6.0):   # M2 pan-head self-tappers, link frame
    return fuse(*[cyl(1.9, -1.3, 0, x, 0).fuse(cyl(1.0, 0, length, x, 0)) for x in at])

def esp32_dummy():
    """38-pin expansion board on the lid with the ESP32 DevKit plugged in on top."""
    z = LID_Z + BODY_T + ESP_LIFT
    w, l = ESP_BOARD
    pcb = box(-w / 2, w / 2, ESP_YC - l / 2, ESP_YC + l / 2, z, z + 1.6)
    sockets = [box(-26, 26, ESP_YC + sy - 1.3, ESP_YC + sy + 1.3, z + 1.6, z + 10) for sy in (-12.7, 12.7)]
    devkit = box(-27.2, 27.2, ESP_YC - 14, ESP_YC + 14, z + 10, z + 11.6)
    module = box(9.2, 27.2, ESP_YC - 9, ESP_YC + 9, z + 11.6, z + 14.8)
    jack = box(-w / 2, -w / 2 + 14, ESP_YC + 12, ESP_YC + 21, z + 1.6, z + 12.6)
    return fuse(pcb, devkit, module, jack, *sockets)

def sensors_dummy():
    z, f = LID_Z + BODY_T, SH_FRONT
    pcb = box(-22.5, 22.5, f + 4.2, f + 5.8, z + US_Z - 10, z + US_Z + 10)
    cans = [Part.makeCylinder(8, 12, V(sx, f + 4.4, z + US_Z), V(0, -1, 0)) for sx in (-13, 13)]
    px0, px1, py0, py1, ph = DHT_POST
    dht = box(-46.5, -31.5, py1 + 0.2, py1 + 7.9, z + 0.5, z + 25.5)   # DHT22 body 15 x 25 x 7.7
    return fuse(pcb, dht, *cans)

def buck_dummy():
    bx, by = BUCK_POS
    return box(bx - 11, bx + 11, by - 8.5, by + 8.5, 0, 5)

def pca_dummy():
    z = LID_Z + BODY_T + 4
    pcb = box(-31.25, 31.25, PCA_Y0, PCA_Y0 + 25.4, z, z + 1.6)
    pins = box(-20, 20, PCA_Y0, PCA_Y0 + 7.7, z + 1.6, z + 13)
    return fuse(pcb, pins)

def battery_dummy():
    w, l, h = AA_HOLDER
    return box(-w / 2, w / 2, -l / 2, l / 2, 0, h)

# ---------------------------------------------------------------- assembly
LINK_UP = P(V(0, 0, HORN_FACE_Z), R())

def build_assembly(alpha=0.0, theta=0.0, phi=0.0, explode=0.0):
    """Returns list of (name, shape, group). Angles in degrees relative to 90-degree servo centre."""
    coxa, leg = make_coxa(), make_leg()
    sd, hd = servo_dummy(), horn_dummy()
    spacer = make_spacer()
    items = [("body_bottom", make_body_bottom(), "body")]
    items += [(f"spacer{k}", placed(spacer, P(V(px, py, 1.2 * explode), R())), "body") for k, (px, py) in enumerate(PILLARS)]
    items += [
("body_top", placed(make_body_top(), P(V(0, 0, 2.5 * explode), R())), "lid"),
             ("esp32_board", placed(esp32_dummy(), P(V(0, 0, 2.5 * explode), R())), "board"),
             ("buck_boost_5v", placed(buck_dummy(), P(V(0, 0, 0.6 * explode), R())), "board"),
             ("pca9685", placed(pca_dummy(), P(V(0, 0, 2.5 * explode), R())), "board"),
             ("sensor_head", placed(make_sensor_head(), P(V(0, -0.8 * explode, LID_Z + BODY_T + 3.2 * explode), R())), "lid"),
             ("sensors_hcsr04_temp", placed(sensors_dummy(), P(V(0, -0.8 * explode, 3.2 * explode), R())), "board"),
             ("battery_4xAA", placed(battery_dummy(), P(V(0, 0, 0.6 * explode), R())), "battery")]
    for i, s_c in enumerate(hip_placements()):
        out = P(V(0, 0, 0), R())
        if explode:
            a = math.radians(45 + 90 * i)
            out = P(V(explode * math.cos(a), explode * math.sin(a), 0), R())
        s_c = out.multiply(s_c)
        l_c = s_c.multiply(LINK_UP).multiply(P(V(), R(V(0, 0, 1), alpha)))
        l_c = l_c.multiply(P(V(0, 0, 0.6 * explode), R()))
        s_f = l_c.multiply(PL_FEMUR_SERVO_IN_COXA)
        l_f = s_f.multiply(LINK_UP).multiply(P(V(), R(V(0, 0, 1), theta)))
        l_f = l_f.multiply(P(V(0, 0, 0.4 * explode), R()))
        items += [(f"leg{i}_coxa", placed(coxa, l_c), "coxa"),
                  (f"leg{i}_leg", placed(leg, l_f), "tibia"),
                  (f"leg{i}_servo_hip", placed(sd, s_c), "servo"),
                  (f"leg{i}_servo_lift", placed(sd, s_f), "servo"),
                  (f"leg{i}_horn_hip", placed(hd, l_c), "horn"),
                  (f"leg{i}_horn_lift", placed(hd, l_f), "horn")]
    return items

def build_joint(explode=0.0):
    """One lift joint on its own (servo + horn + leg + 2 screws), for the close-up pictures."""
    e = explode
    up = lambda dz: LINK_UP.multiply(P(V(0, 0, dz), R()))
    return [("servo", placed(servo_dummy(), P(V(0, 0, -1.5 * e), R())), "servo"),
            ("horn", placed(horn_dummy(), up(0.6 * e)), "horn"),
            ("leg", placed(make_leg(), up(1.8 * e)), "tibia"),
            ("screws", placed(horn_screws_dummy(), up(-0.4 * e)), "hardware")]

# ---------------------------------------------------------------- export
def write_stl(shape, path):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.03,
                                  AngularDeflection=0.15, Relative=False)
    mesh.write(path)

def export_step(named_shapes, path):
    doc = App.newDocument("tmp")
    objs = []
    for name, shape in named_shapes:
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        objs.append(o)
    Import.export(objs, path)
    App.closeDocument(doc.Name)

def main():
    for d in ("stl", "step", "renders/meshes"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)

    flip = P(V(), R(V(1, 0, 0), 180))   # print with the horn pocket facing up
    parts = {
        "body_bottom":     (make_body_bottom(), 1, None),
        "body_top":        (make_body_top(), 1, None),
        "spacer":          (make_spacer(), 4, None),
        "coxa":            (make_coxa(), 4, None),
        "leg":             (make_leg(), 4, flip),
        "leg_interface":   (make_leg_interface(), 0, flip),
        "fit_test":        (make_fit_test(), 1, None),
        "screw_test":      (make_screw_test(), 1, None),
        "sensor_head":     (make_sensor_head(), 1, None),
        "leg_test_stand":  (make_leg_test_stand(), 1, P(V(), R(V(1, 0, 0), 180))),
    }
    report = {"parts": {}}
    for name, (shape, qty, pl) in parts.items():
        if not shape.isValid():
            raise RuntimeError(f"{name}: invalid solid")
        export_step([(name, shape)], os.path.join(OUT, "step", f"{name}.step"))
        pshape = placed(shape, pl) if pl else shape
        write_stl(pshape, os.path.join(OUT, "stl", f"{name}.stl"))
        bb = pshape.BoundBox
        report["parts"][name] = {"qty": qty, "volume_cm3": round(shape.Volume / 1000, 2),
                                 "size_mm": [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                                 "solids": len(shape.Solids)}

    # assembled robot (standing pose) and exploded view
    asm = build_assembly()
    export_step([(n, s) for n, s, g in asm], os.path.join(OUT, "step", "assembly.step"))

    # interference check between every pair of assembly items
    hits = []
    for i in range(len(asm)):
        for j in range(i + 1, len(asm)):
            a, b = asm[i][1], asm[j][1]
            if not a.BoundBox.intersect(b.BoundBox):
                continue
            v = a.common(b).Volume
            if v > 0.5:
                hits.append([asm[i][0], asm[j][0], round(v, 2)])
    report["interference"] = hits

    # sweep check: rotate each joint through its working range, look for collisions
    sweep = []
    for alpha in (-35, 0, 35):
        for theta in (-35, 0, 35):
            for phi in (0,):
                items = build_assembly(alpha, theta, phi)
                leg0 = [x for x in items if x[0].startswith("leg0_")]
                others = [x for x in items if not x[0].startswith("leg0_")]
                for n1, s1, _ in leg0:
                    for n2, s2, _ in others:
                        if s1.BoundBox.intersect(s2.BoundBox):
                            v = s1.common(s2).Volume
                            if v > 0.5:
                                sweep.append([alpha, theta, phi, n1, n2, round(v, 2)])
    report["sweep_collisions"] = sweep

    for tag, items in (("assembled", asm), ("exploded", build_assembly(explode=25)),
                       ("joint", build_joint()), ("joint_exploded", build_joint(12))):
        mdir = os.path.join(OUT, "renders", "meshes", tag)
        os.makedirs(mdir, exist_ok=True)
        index = []
        for n, s, g in items:
            write_stl(s, os.path.join(mdir, f"{n}.stl"))
            index.append({"name": n, "group": g})
        with open(os.path.join(mdir, "index.json"), "w") as f:
            json.dump(index, f)

    with open(os.path.join(OUT, "build_report.json"), "w") as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report, indent=1))

main()
