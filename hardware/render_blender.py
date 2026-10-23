# Preview renders:  blender.exe --background --python render_blender.py
import bpy, os, json, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REN = os.path.join(HERE, "renders")
COLORS = {"body": (0.95, 0.55, 0.10), "lid": (0.95, 0.55, 0.10), "coxa": (0.15, 0.45, 0.85),
          "femur": (0.15, 0.45, 0.85), "tibia": (0.95, 0.85, 0.20), "servo": (0.12, 0.12, 0.14),
          "horn": (0.92, 0.92, 0.92), "board": (0.10, 0.50, 0.30), "battery": (0.55, 0.20, 0.20),
          "clamp": (0.90, 0.25, 0.30), "hardware": (0.45, 0.45, 0.50)}

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light, sh.color_type = "STUDIO", "MATERIAL"
    sh.show_cavity, sh.show_shadows = True, True
    sh.cavity_type = "BOTH"
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("w"); sc.world = world
    world.color = (0.97, 0.97, 0.97)
    sc.view_settings.view_transform = "Standard"
    return sc

def load(tag):
    mdir = os.path.join(REN, "meshes", tag)
    mats = {}
    for item in json.load(open(os.path.join(mdir, "index.json"))):
        bpy.ops.wm.stl_import(filepath=os.path.join(mdir, item["name"] + ".stl"))
        ob = bpy.context.selected_objects[0]
        g = item["group"]
        if g not in mats:
            m = bpy.data.materials.new(g); m.diffuse_color = (*COLORS[g], 1); mats[g] = m
        ob.data.materials.append(mats[g])

def shoot(sc, name, loc, target=(0, 0, 0), ortho=260):
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"; cam_data.ortho_scale = ortho
    cam = bpy.data.objects.new(name, cam_data)
    sc.collection.objects.link(cam)
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.filepath = os.path.join(REN, name + ".png")
    bpy.ops.render.render(write_still=True)

sc = reset(); load("assembled")
shoot(sc, "assembled_iso", (300, -300, 220), (0, 0, -5), 400)
shoot(sc, "assembled_front", (0, -500, 0), (0, 0, 0), 330)
shoot(sc, "assembled_top", (0, 0, 500), (0, 0, 0), 360)
sc = reset(); load("exploded")
shoot(sc, "exploded_iso", (300, -300, 260), (0, 0, 10), 460)

# close-up of the body without the lid (shows ESP32 cradle, buck-boost, battery)
sc = reset(); load("assembled")
for ob in list(bpy.data.objects):
    if ob.name.startswith(("body_top", "pca9685", "sensor", "esp32")):
        bpy.data.objects.remove(ob)
shoot(sc, "body_inside", (230, -230, 200), (0, 0, 5), 230)

sc = reset(); load("assembled")
shoot(sc, "sensor_head_front", (120, -330, 170), (0, -20, 40), 190)

# horn joint close-ups (one lift joint)
sc = reset(); load("joint")
shoot(sc, "joint_assembled", (70, -90, 90), (12, 12, 6), 95)
shoot(sc, "joint_underside", (60, -70, -80), (8, 0, 8), 60)
sc = reset(); load("joint_exploded")
shoot(sc, "joint_exploded", (90, -110, 60), (8, 0, 10), 120)

# one shoulder (coxa) with its servos and leg
sc = reset(); load("assembled")
for ob in list(bpy.data.objects):
    if not ob.name.startswith("leg0_"):
        bpy.data.objects.remove(ob)
shoot(sc, "shoulder_closeup", (150, -40, 110), (62, 62, 18), 120)
