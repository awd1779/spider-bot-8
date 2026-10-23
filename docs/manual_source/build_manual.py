# Builds docs/manual.html (one file, works offline) from manual.md
#   python build_manual.py
import base64, html, io, os, re
import markdown
from PIL import Image
import figures

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(HERE)
REPO = os.path.dirname(DOCS)
CODE = os.path.join(REPO, "firmware")
RENDERS = os.path.join(DOCS, "images")
OUT = os.path.join(DOCS, "manual.html")
A = lambda n: open(os.path.join(HERE, "assets", n), encoding="utf-8").read()

def img_data(name):
    im = Image.open(os.path.join(RENDERS, name)).convert("RGB")
    im.thumbnail((1100, 1100))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def sketch(name):
    return open(os.path.join(CODE, name, name + ".ino"), encoding="utf-8").read().rstrip()

def lib_example(name):
    return open(os.path.join(REPO, "library", "SpiderBot8", "examples", name, name + ".ino"), encoding="utf-8").read().rstrip()

def code_block(src):
    return ('<div class="code"><button class="copy" type="button">Copy</button><pre><code>'
            + html.escape(src) + "</code></pre></div>")

def part(name, start, end=None):
    """Lines of a sketch from the line containing `start` up to (not including) the line containing `end`."""
    lines = sketch(name).split("\n")
    i = next(k for k, l in enumerate(lines) if start in l)
    j = next((k for k, l in enumerate(lines) if k > i and end and end in l), len(lines))
    return "\n".join(lines[i:j]).rstrip()

md = open(os.path.join(HERE, "manual.md"), encoding="utf-8").read()

# raw-HTML blocks are swapped in after markdown; keep them out of its way
blocks = {}
def stash(htm):
    key = f"@@BLOCK{len(blocks)}@@"
    blocks[key] = htm
    return "\n\n" + key + "\n\n"

md = re.sub(r"\{\{CODE:(\w+)\}\}", lambda m: stash(code_block(sketch(m.group(1)))), md)
md = re.sub(r"\{\{LIBEX:(\w+)\}\}", lambda m: stash(code_block(lib_example(m.group(1)))), md)
md = re.sub(r"\{\{FULL:(\w+)\}\}", lambda m: stash(
    f'<details class="full"><summary>Full sketch: {m.group(1)}.ino</summary>' + code_block(sketch(m.group(1))) + "</details>"), md)
md = re.sub(r"\{\{PART:(\w+)\|([^|}]+)\|?([^}]*)\}\}",
            lambda m: stash(code_block(part(m.group(1), m.group(2), m.group(3) or None))), md)
md = re.sub(r"\{\{IMG:([\w.]+)\|([^}]+)\}\}", lambda m: stash(
    f'<figure><img alt="{html.escape(m.group(2))}" src="{img_data(m.group(1))}">'
    f"<figcaption>{html.escape(m.group(2))}</figcaption></figure>"), md)
md = md.replace("{{LOOP}}", stash(A("loop.html").replace(">Arduino<", ">ESP32<")))
md = md.replace("{{SERVOSIM}}", stash(A("servo_sim.html")))
md = md.replace("{{GAIT}}", stash(figures.gait_widget()))
md = md.replace("{{STANDSIT}}", stash(figures.stand_sit_svg()))
md = md.replace("{{WIRING}}", stash(figures.wiring_svg()))

body = markdown.markdown(md, extensions=["tables", "attr_list", "fenced_code", "sane_lists", "md_in_html"])

body = body.replace("\\|", "|")      # escaped pipes inside table cells
for k, v in blocks.items():
    body = body.replace(f"<p>{k}</p>", v).replace(k, v)
body = re.sub(r"<table>", '<div class="tablewrap"><table>', body)
body = body.replace("</table>", "</table></div>")
body = re.sub(r"<p><strong>([^<]+)</strong></p>", r'<p class="sub">\1</p>', body)

n = [0]
def check(m):
    n[0] += 1
    return f'<li class="check"><label><input type="checkbox" data-k="e{n[0]}"><span>{m.group(1)}</span></label></li>'
body = re.sub(r"<li>\[ \] (.*?)</li>", check, body)
body = re.sub(r"<ul>(\s*<li class=\"check\">)", r'<ul class="checklist">\1', body)

# one <section> per chapter, plus the side navigation
heads = re.findall(r'<h2 id="([\w-]+)">(.*?)</h2>', body)
first = body.index("<h2")
intro, rest = body[:first], body[first:]
rest = re.sub(r'(?=<h2 id=)', '</section><section class="chapter">', rest)
rest = rest.replace('</section>', '', 1) + "</section>"
nav = "".join(f'<li><a href="#{i}">{re.sub("<[^>]+>", "", t)}</a></li>' for i, t in heads)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spider Robot Manual</title>
<style>
{A("style.css")}
{figures.GAIT_CSS}
details.full {{ margin:12px 0; border:1px solid var(--line); border-radius:10px; padding:8px 12px; background:var(--paper); }}
details.full summary {{ cursor:pointer; font-weight:650; }}
.note {{ border-left:3px solid var(--blue); background:var(--code); padding:10px 14px; border-radius:0 8px 8px 0; margin:12px 0; }}
.warn {{ border-left:3px solid var(--accent); background:var(--accent-soft); padding:10px 14px; border-radius:0 8px 8px 0; margin:12px 0; }}
.note p, .warn p {{ margin:4px 0; }}
</style>
</head>
<body>
<div class="layout">
<nav aria-label="Chapters">
  <div class="brand">Spider Robot <span>Manual</span></div>
  <ol>{nav}</ol>
</nav>
<main>
<header class="cover">
  <div class="kicker">Student manual · ESP32 + PCA9685 · 8 servos</div>
  <h1>Build a walking spider robot</h1>
  <p>From one servo motor to a robot that walks forward and backward. Work through the chapters in order. Tick the boxes as you go: this page remembers them on this computer.</p>
</header>
{intro}{rest}
</main>
</div>
<script>
{A("base.js")}
{A("servo_sim.js")}
{figures.GAIT_JS}
</script>
</body>
</html>
"""
open(OUT, "w", encoding="utf-8").write(page)
print("wrote", OUT, round(len(page) / 1024), "KB,", len(heads), "chapters,", n[0], "checkboxes")
