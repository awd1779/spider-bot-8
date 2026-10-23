# Generates the SVG figures for the manual from the robot's real geometry.
import math

# ---------------------------------------------------------------- robot numbers (match build_robot.py and P9)
HIP_R = 46.0 * math.sqrt(2)          # hip shaft distance from the body centre
COXA_LEN = 27.5                      # hip shaft -> lift shaft
LEG_OUT, LEG_DOWN = 45.0, 75.0
LIFT_AXIS_Z = 24.5                   # lift shaft height above the bottom plate top
SERVO_BOTTOM_Z = -15.9               # lowest point of the body (hip servo cases)
STAND, SIT, UP, STEP = -15, 35, 10, 14
A = [45, 135, 225, 315]              # body-frame angle of each hip: 0 RL, 1 RR, 2 FR, 3 FL
FWD = [-1, 1, 1, -1]                 # turning direction that moves each foot forward
NAMES = ["rear-left", "rear-right", "front-right", "front-left"]
FWD_ORDER, BACK_ORDER = [0, 3, 1, 2], [2, 1, 3, 0]

def foot_rel(lift_up):
    """Foot position from the lift shaft: (out, z). lift_up > 0 = foot up."""
    p = math.radians(lift_up)
    return LEG_OUT * math.cos(p) + LEG_DOWN * math.sin(p), LEG_OUT * math.sin(p) - LEG_DOWN * math.cos(p)

def feet_xy(hips, lift=STAND):
    R = COXA_LEN + foot_rel(lift)[0]
    out = []
    for i in range(4):
        h = math.radians(A[i])
        a = math.radians(A[i] + FWD[i] * hips[i])
        out.append((HIP_R * math.cos(h) + R * math.cos(a), HIP_R * math.sin(h) + R * math.sin(a)))
    return out

def margin(tri):
    m = 1e9
    for k in range(3):
        (x1, y1), (x2, y2), (x3, y3) = tri[k], tri[(k + 1) % 3], tri[(k + 2) % 3]
        ex, ey = x2 - x1, y2 - y1
        s = (ex * (0 - y1) - ey * (0 - x1)) / math.hypot(ex, ey)
        s3 = ex * (y3 - y1) - ey * (x3 - x1)
        m = min(m, s if s3 > 0 else -s)
    return m

# ---------------------------------------------------------------- gait step-through widget
S, CX, CY = 1.15, 160, 150
def P(x, y):                         # body frame -> svg (front = up, robot's left = page left)
    return CX - x * S, CY + y * S

def octagon(half, ch):
    c = ch - half
    return [(half, c), (c, half), (-c, half), (-half, c), (-half, -c), (-c, -half), (c, -half), (half, -c)]

def frame_svg(hips, lifted, note_arrow):
    f = feet_xy(hips)
    parts = []
    body = " ".join("%.1f,%.1f" % P(x, y) for x, y in octagon(63, 112))
    parts.append(f'<polygon points="{body}" class="g-body"/>')
    down = [i for i in range(4) if i != lifted]
    poly = " ".join("%.1f,%.1f" % P(*f[i]) for i in (down if lifted is not None else [0, 1, 2, 3]))
    parts.append(f'<polygon points="{poly}" class="g-sup"/>')
    for i in range(4):
        hx, hy = P(HIP_R * math.cos(math.radians(A[i])), HIP_R * math.sin(math.radians(A[i])))
        fx, fy = P(*f[i])
        parts.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{fx:.1f}" y2="{fy:.1f}" class="g-leg"/>')
        parts.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="4" class="g-hip"/>')
        cls = "g-up" if i == lifted else "g-foot"
        parts.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="7" class="{cls}"/>')
        lx, ly = fx + (14 if fx > CX else -14), fy + 4
        anchor = "start" if fx > CX else "end"
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="g-lab" text-anchor="{anchor}">{["RL","RR","FR","FL"][i]}</text>')
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="5" class="g-cog"/>')
    if note_arrow:
        y0, y1 = (CY + 30, CY - 30) if note_arrow == "fwd" else (CY - 30, CY + 30)
        parts.append(f'<path d="M{CX} {y0}V{y1}" class="g-arrow" marker-end="url(#garr)"/>')
    return "".join(parts)

def gait_frames(direction):
    order = FWD_ORDER if direction == "fwd" else BACK_ORDER
    sgn = 1 if direction == "fwd" else -1
    hips = [0.0] * 4
    for j, leg in enumerate(order):
        hips[leg] = sgn * (j - 2) * STEP
    word = "front" if sgn > 0 else "back"
    frames = [(frame_svg(hips, None, None),
               "Ready: the legs are spread out, one step apart, in the order they will move.")]
    for j, leg in enumerate(order):
        hips[leg] = sgn * 2 * STEP
        m = margin([feet_xy(hips)[i] for i in range(4) if i != leg])
        frames.append((frame_svg(hips, leg, None),
                       f"Step {j + 1}a: lift the {NAMES[leg]} leg and carry it to the {word}. "
                       f"The dot (centre of mass) is {m:.0f} mm inside the triangle of feet on the floor, so the robot doesn't tip."))
        frames.append((frame_svg(hips, None, None), f"Step {j + 1}b: put the {NAMES[leg]} foot down."))
        hips = [h - sgn * STEP for h in hips]
        frames.append((frame_svg(hips, None, direction),
                       f"Step {j + 1}c: all 4 feet push {'back' if sgn > 0 else 'forward'} together, "
                       f"so the body slides {'forward' if sgn > 0 else 'backward'}."))
    return frames

def gait_widget():
    out = ['<div class="gait" id="gaitSim">',
           '<div class="gait-bar"><div role="group" aria-label="Direction">'
           '<button type="button" data-dir="fwd" class="on">Forward</button>'
           '<button type="button" data-dir="back">Backward</button></div>'
           '<div role="group" aria-label="Step"><button type="button" data-go="-1">◀ Back</button>'
           '<button type="button" data-go="play">▶ Play</button>'
           '<button type="button" data-go="1">Next ▶</button></div></div>',
           '<svg viewBox="0 0 320 300" role="img" aria-label="Top view of the robot walking, one step at a time">'
           '<defs><marker id="garr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
           '<path d="M0 0L10 5L0 10z" class="g-arrowhead"/></marker></defs>'
           f'<text x="{CX}" y="16" class="g-front">FRONT (sensor head)</text>']
    for d in ("fwd", "back"):
        for k, (svg, cap) in enumerate(gait_frames(d)):
            hidden = "" if (d == "fwd" and k == 0) else ' style="display:none"'
            cap = cap.replace('"', "&quot;")
            out.append(f'<g data-d="{d}" data-k="{k}" data-cap="{cap}"{hidden}>{svg}</g>')
    out.append('</svg>')
    out.append('<p class="gait-cap" id="gaitCap" aria-live="polite"></p>')
    out.append('<p class="gait-key"><span class="k-foot"></span> foot on the floor '
               '<span class="k-up"></span> foot in the air <span class="k-sup"></span> support area '
               '<span class="k-cog"></span> centre of mass</p></div>')
    return "\n".join(out)

GAIT_JS = r"""
(function () {
  var root = document.getElementById('gaitSim'); if (!root) return;
  var dir = 'fwd', k = 0, timer = null, cap = document.getElementById('gaitCap');
  function frames() { return root.querySelectorAll('g[data-d="' + dir + '"]'); }
  function show() {
    root.querySelectorAll('g[data-d]').forEach(function (g) { g.style.display = 'none'; });
    var f = frames(); k = (k + f.length) % f.length;
    f[k].style.display = ''; cap.textContent = (k + 1) + ' / ' + f.length + ': ' + f[k].dataset.cap;
  }
  function stop() { if (timer) { clearInterval(timer); timer = null; root.querySelector('[data-go="play"]').textContent = '▶ Play'; } }
  root.querySelectorAll('[data-dir]').forEach(function (b) {
    b.addEventListener('click', function () {
      stop(); dir = b.dataset.dir; k = 0;
      root.querySelectorAll('[data-dir]').forEach(function (x) { x.classList.toggle('on', x === b); });
      show();
    });
  });
  root.querySelectorAll('[data-go]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (b.dataset.go === 'play') {
        if (timer) { stop(); return; }
        b.textContent = '❚❚ Pause';
        timer = setInterval(function () { k++; show(); }, 1400);
        return;
      }
      stop(); k += parseInt(b.dataset.go, 10); show();
    });
  });
  show();
})();
"""

GAIT_CSS = """
.gait { border:1px solid var(--line); border-radius:12px; padding:14px; margin:16px 0; background:var(--paper); }
.gait-bar { display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; margin-bottom:8px; }
.gait-bar div { display:flex; gap:6px; flex-wrap:wrap; }
.gait button { font:600 13px var(--sans); border:1px solid var(--line); background:var(--sheet); color:var(--ink); border-radius:999px; padding:5px 12px; cursor:pointer; }
.gait button.on { background:var(--accent); border-color:var(--accent); color:#fff; }
.gait button:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
.gait svg { width:100%; max-width:440px; height:auto; display:block; margin:0 auto; }
.gait-cap { min-height:3.2em; margin:8px 0 4px; font-size:15px; }
.gait-key { font-size:13px; color:var(--muted); display:flex; gap:6px 14px; flex-wrap:wrap; align-items:center; margin:0; }
.gait-key span { display:inline-block; width:12px; height:12px; border-radius:50%; vertical-align:middle; margin-right:-8px; }
.k-foot { background:var(--blue); } .k-up { border:2px solid var(--accent); } .k-sup { background:var(--accent-soft); border-radius:2px !important; } .k-cog { background:var(--accent); }
.g-body { fill:var(--sheet); stroke:var(--muted); stroke-width:1.2; }
.g-sup { fill:var(--accent-soft); stroke:var(--accent); stroke-width:1; stroke-dasharray:4 3; }
.g-leg { stroke:var(--muted); stroke-width:3; stroke-linecap:round; }
.g-hip { fill:var(--muted); }
.g-foot { fill:var(--blue); }
.g-up { fill:var(--sheet); stroke:var(--accent); stroke-width:2.5; }
.g-cog { fill:var(--accent); stroke:var(--sheet); stroke-width:1.5; }
.g-lab { fill:var(--ink); font:600 12px var(--sans); }
.g-front { fill:var(--muted); font:600 11px var(--sans); text-anchor:middle; letter-spacing:.08em; }
.g-arrow { stroke:var(--accent); stroke-width:3; fill:none; }
.g-arrowhead { fill:var(--accent); }
.side svg { width:100%; height:auto; display:block; }
.ds.start { text-anchor:start; }
.s-ground { stroke:var(--muted); stroke-width:2; }
.s-body { fill:var(--accent-soft); stroke:var(--accent); stroke-width:1.2; }
.s-servo { fill:#2B2E31; }
.s-coxa { fill:none; stroke:var(--blue); stroke-width:5; stroke-linecap:round; stroke-linejoin:round; }
.s-leg { fill:none; stroke:#B8A63A; stroke-width:6; stroke-linecap:round; stroke-linejoin:round; }
.s-axis { fill:var(--sheet); stroke:var(--ink); stroke-width:1.5; }
.s-dim { stroke:var(--ink); stroke-width:1; }
.w-wire { fill:none; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
.w-board { fill:var(--sheet); stroke:var(--muted); stroke-width:1.5; }
.w-pin { fill:var(--paper); stroke:var(--muted); }
.w-servo rect { fill:var(--paper); stroke:var(--muted); }
.w-servo.on rect { fill:var(--accent-soft); stroke:var(--accent); }
"""

# ---------------------------------------------------------------- stand / sit side view
def side_panel(lift_up, ox, title):
    s = 1.45
    fr = foot_rel(lift_up)
    foot_z = LIFT_AXIS_Z + fr[1]
    ground = min(foot_z, SERVO_BOTTOM_Z)
    gy = 200                                         # svg y of the ground
    def T(r, z): return ox + 20 + (r + 60) * s, gy - (z - ground) * s
    p = []
    x0, y0 = T(-60, 0); x1, y1 = T(8, -4)
    p.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" class="s-body"/>')
    x0, y0 = T(-17, 6.6); x1, y1 = T(6, SERVO_BOTTOM_Z)
    p.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" class="s-servo"/>')
    pts = [T(0, 12), T(COXA_LEN + 8, 12), T(COXA_LEN + 8, 34)]
    p.append('<polyline points="%s" class="s-coxa"/>' % " ".join("%.1f,%.1f" % q for q in pts))
    ax, az = COXA_LEN, LIFT_AXIS_Z
    e = (ax + LEG_OUT * math.cos(math.radians(lift_up)), az + LEG_OUT * math.sin(math.radians(lift_up)))
    f = (ax + fr[0], az + fr[1])
    p.append('<polyline points="%s" class="s-leg"/>' % " ".join("%.1f,%.1f" % T(*q) for q in [(ax, az), e, f]))
    cx, cy = T(ax, az)
    p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" class="s-axis"/>')
    gx0, _ = T(-60, 0); gx1, _ = T(130, 0)
    p.append(f'<line x1="{gx0:.1f}" y1="{gy}" x2="{gx1:.1f}" y2="{gy}" class="s-ground"/>')
    # body height dimension
    bx, by = T(-45, SERVO_BOTTOM_Z)
    h = SERVO_BOTTOM_Z - ground
    if h > 1:
        p.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx:.1f}" y2="{gy}" class="s-dim"/>')
        p.append(f'<text x="{bx + 6:.1f}" y="{(by + gy) / 2 + 4:.1f}" class="ds start">{h:.0f} mm off the floor</text>')
    else:
        p.append(f'<text x="{ox + 20}" y="{gy + 18}" class="ds start">body rests on the floor</text>')
    p.append(f'<text x="{ox + 150}" y="22" class="dt">{title}</text>')
    p.append(f'<text x="{cx - 10:.1f}" y="{cy - 8:.1f}" class="ds end">lift servo</text>')
    return "".join(p)

def stand_sit_svg():
    return ('<figure class="side"><svg viewBox="0 0 640 235" role="img" aria-label="Side view of one leg: '
            'sitting with the lift at +35 degrees, standing with the lift at -15 degrees">'
            + side_panel(SIT, 0, f"Sitting: lift = {SIT}° (foot up)")
            + side_panel(STAND, 320, f"Standing: lift = {STAND}° (foot down)")
            + '</svg><figcaption>Side view of one leg. Only the lift servo moves: '
              'turning the foot down pushes the body up.</figcaption></figure>')

# ---------------------------------------------------------------- wiring
def wiring_svg():
    W = []
    # boards
    W.append('<rect x="20" y="150" width="190" height="150" rx="10" class="w-board"/>'
             '<text x="115" y="178" class="dt">ESP32 expansion board</text>'
             '<text x="115" y="196" class="ds">USB cable to the computer</text>')
    esp_pins = [("3V3", 215), ("GND", 240), ("GPIO 21 (SDA)", 265), ("GPIO 22 (SCL)", 290)]
    for name, y in esp_pins:
        W.append(f'<circle cx="205" cy="{y - 4}" r="4" class="w-pin"/><text x="195" y="{y}" class="ds end">{name}</text>')
    W.append('<rect x="330" y="150" width="230" height="210" rx="10" class="w-board"/>'
             '<text x="445" y="178" class="dt">PCA9685 servo module</text>'
             '<text x="445" y="196" class="ds">address 0x40</text>')
    pca_pins = [("VCC", 215), ("GND", 240), ("SDA", 265), ("SCL", 290)]
    for name, y in pca_pins:
        W.append(f'<circle cx="335" cy="{y - 4}" r="4" class="w-pin"/><text x="353" y="{y}" class="ds start">{name}</text>')
    colors = {"3V3": "#D9412B", "GND": "#3B3F44", "GPIO 21 (SDA)": "#2A66A8", "GPIO 22 (SCL)": "#D9A21B"}
    for (en, ey), (pn, py) in zip(esp_pins, pca_pins):
        W.append(f'<path d="M209 {ey - 4}C270 {ey - 4} 270 {py - 4} 331 {py - 4}" class="w-wire" stroke="{colors[en]}"/>')
    # green terminal + battery
    W.append('<rect x="420" y="120" width="70" height="30" rx="4" fill="#2E8B57"/>'
             '<text x="438" y="140" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">V+</text>'
             '<text x="472" y="140" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">GND</text>')
    W.append('<rect x="400" y="20" width="160" height="52" rx="8" class="w-board"/>'
             '<text x="480" y="42" class="dt">4 × AA + switch</text><text x="480" y="60" class="ds">red → V+, black → GND</text>')
    W.append('<path d="M438 120V96H450V72" class="w-wire" stroke="#D9412B"/>'
             '<path d="M472 120V96H510V72" class="w-wire" stroke="#3B3F44"/>')
    # servo outputs
    legs = {0: "RL hip", 1: "RL lift", 4: "RR hip", 5: "RR lift", 8: "FR hip", 9: "FR lift", 12: "FL hip", 13: "FL lift"}
    W.append('<text x="445" y="300" class="ds">servo plugs, channels 0-15</text>'
             '<text x="445" y="388" class="ds">plug: brown = GND (outer edge),</text>'
             '<text x="445" y="404" class="ds">red = V+, orange = signal</text>')
    for ch in range(16):
        x = 336 + ch * 14
        on = ch in legs
        W.append(f'<g class="w-servo{" on" if on else ""}"><rect x="{x}" y="310" width="11" height="20" rx="2"/></g>')
        if ch % 4 == 0:
            W.append(f'<text x="{x + 5}" y="346" class="ds">{ch}</text>')
    rows = [(0, "ch 0 / 1"), (4, "ch 4 / 5"), (8, "ch 8 / 9"), (12, "ch 12 / 13")]
    names = ["rear-left", "rear-right", "front-right", "front-left"]
    for k, (ch, lab) in enumerate(rows):
        y = 432 + k * 20
        W.append(f'<text x="330" y="{y}" class="ds start"><tspan font-weight="700">{lab}</tspan>: {names[k]} leg (hip / lift)</text>')
    return ('<figure class="diagram"><svg viewBox="0 0 580 505" role="img" aria-label="Wiring: ESP32 3V3, GND, GPIO 21 and GPIO 22 '
            'go to PCA9685 VCC, GND, SDA and SCL. The 4 AA pack goes to the green terminal. Servos plug into channels 0, 1, 4, 5, 8, 9, 12 and 13.">'
            + "".join(W) + '</svg><figcaption>Four wires between the boards, the battery only into the green terminal.</figcaption></figure>')

if __name__ == "__main__":
    for d in ("fwd", "back"):
        print(d, [round(margin([feet_xy([0]*4)[i] for i in range(3)]), 1)])
    print(stand_sit_svg()[:200])
