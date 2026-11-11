"""Render original PIL diagrams for the 60-90 s science demo (16 scenes)."""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspaces/OpenMontage/work/master-run/e2e")
SCENES = ROOT / "scenes"
SCENES.mkdir(parents=True, exist_ok=True)
W, H = 2112, 1188  # 1.1x of 1920x1080 for zoompan headroom
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (11, 16, 32)
INK = (238, 242, 248)
MUTED = (148, 163, 184)
ACCENT = (42, 157, 143)
ACCENT2 = (244, 162, 97)
CARD = (20, 28, 48)

SCENES_DEF = [
    # id, kicker, headline, subline, diagram, pose, expression
    ("s00_intro", "SCIENCE / 14 FACTS", "SOUND WRONG.\nSTILL TRUE.", "A rapid tour of counter-intuitive science.", "title", "idle", "curious"),
    ("s01_ice", "FACT 01 / DENSITY", "ICE FLOATS", "Water expands when it freezes.", "ice", "explaining", "neutral"),
    ("s02_lightyear", "FACT 02 / DISTANCE", "A LIGHT-YEAR IS TIME?", "No — it is a distance.", "lightyear", "pointing", "surprised"),
    ("s03_cells", "FACT 03 / BIOLOGY", "37 TRILLION CELLS", "That is roughly the adult human count.", "cells", "explaining", "neutral"),
    ("s04_sound", "FACT 04 / PHYSICS", "SPACE IS SILENT", "Sound needs a medium.", "sound", "explaining", "neutral"),
    ("s05_photosynthesis", "FACT 05 / CHEMISTRY", "LEAVES EAT LIGHT", "Photosynthesis stores light as sugar.", "photosynthesis", "pointing", "happy"),
    ("s06_core", "FACT 06 / GEOLOGY", "THE CORE IS A SUN", "Roughly 5,200 °C — near the Sun's surface.", "core", "explaining", "surprised"),
    ("s07_resistance", "FACT 07 / MEDICINE", "BACTERIA EVOLVE", "Antibiotics select for resistance.", "resistance", "thinking", "concerned"),
    ("s08_blackhole", "FACT 08 / ASTROPHYSICS", "NO RETURN", "The event horizon is a one-way boundary.", "blackhole", "pointing", "focused"),
    ("s09_honey", "FACT 09 / ARCHAEOLOGY", "HONEY NEVER SPOILS", "3,000-year-old honey found in Egyptian tombs.", "honey", "examining", "curious"),
    ("s10_octopus", "FACT 10 / ZOOLOGY", "THREE HEARTS", "Two pump blood to the gills; one to the body.", "octopus", "explaining", "surprised"),
    ("s11_venus", "FACT 11 / PLANETOLOGY", "A DAY IS A YEAR", "Venus rotates slower than it orbits.", "venus", "thinking", "neutral"),
    ("s12_banana", "FACT 12 / BOTANY", "BANANAS ARE BERRIES", "Strawberries are not, botanically.", "banana", "pointing", "happy"),
    ("s13_shark", "FACT 13 / EVOLUTION", "SHARKS BEAT TREES", "Sharks: ~450M years. Trees: ~385M.", "shark", "explaining", "neutral"),
    ("s14_neutron", "FACT 14 / ASTROPHYSICS", "A TEASPOON OF STAR", "Neutron-star matter: ~10^12 kg per teaspoon.", "neutron", "examining", "focused"),
    ("s15_outro", "YOUR TURN", "WHICH ONE?", "Tell me in the comments. Follow for more.", "outro", "idle", "happy"),
]

nar = json.loads((ROOT / "narration.json").read_text())
by_id = {x["id"]: x for x in nar["timeline"]}


def font(size, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def base_canvas(kicker, num, headline, subline, accent=ACCENT):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im, "RGBA")
    # subtle grid
    for x in range(0, W, 96):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 8), width=1)
    for y in range(0, H, 96):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 8), width=1)
    # accent bar
    d.rectangle([0, 0, 18, H], fill=accent)
    # kicker
    d.text((92, 74), kicker, font=font(34), fill=accent)
    # progress
    d.text((W - 330, 78), f"{num:02d} / 14" if num else "OPEN", font=font(32), fill=MUTED)
    # headline
    y = 170
    for line in headline.split("\n"):
        d.text((92, y), line, font=font(104), fill=INK)
        y += 122
    # subline
    for line in wrap(d, subline, font(42, False), 1250)[:3]:
        d.text((92, y + 24), line, font=font(42, False), fill=MUTED)
        y += 58
    return im, d


def card(d, box, title):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=32, fill=CARD, outline=(255, 255, 255, 22), width=2)
    d.text((x0 + 34, y0 + 26), title, font=font(30), fill=ACCENT)


def draw_ice(d, box):
    card(d, box, "DENSITY")
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    # glass
    gx0, gy0, gx1, gy1 = cx - 150, y0 + 130, cx + 150, y1 - 90
    d.rounded_rectangle([gx0, gy0, gx1, gy1], radius=18, outline=(210, 230, 255), width=6)
    water_top = gy0 + 130
    d.rectangle([gx0 + 5, water_top, gx1 - 5, gy1 - 5], fill=(38, 110, 170, 180))
    # ice cube
    d.rounded_rectangle([cx - 70, water_top - 45, cx + 70, water_top + 55], radius=12,
                        fill=(225, 242, 255, 235), outline=(255, 255, 255), width=4)
    d.line([(cx - 55, water_top - 30), (cx - 20, water_top + 10)], fill=(160, 200, 230), width=3)
    d.line([(cx + 10, water_top - 30), (cx + 45, water_top + 10)], fill=(160, 200, 230), width=3)
    # arrow
    d.line([(cx + 230, water_top + 80), (cx + 230, water_top - 40)], fill=ACCENT, width=6)
    d.polygon([(cx + 230, water_top - 60), (cx + 214, water_top - 30), (cx + 246, water_top - 30)], fill=ACCENT)
    d.text((cx + 160, water_top + 100), "less dense", font=font(26, False), fill=ACCENT)


def draw_lightyear(d, box):
    card(d, box, "DISTANCE")
    x0, y0, x1, y1 = box
    cy = (y0 + y1) // 2
    d.line([(x0 + 80, cy), (x1 - 80, cy)], fill=(210, 230, 255), width=6)
    for i in range(11):
        x = x0 + 80 + i * (x1 - x0 - 160) / 10
        d.line([(x, cy - 18), (x, cy + 18)], fill=(210, 230, 255), width=4)
    # earth
    d.ellipse([x0 + 40, cy - 42, x0 + 124, cy + 42], fill=(40, 120, 200))
    d.ellipse([x0 + 55, cy - 28, x0 + 95, cy + 10], fill=(60, 170, 110))
    # photon
    px = x0 + 380
    d.ellipse([px - 16, cy - 16, px + 16, cy + 16], fill=ACCENT2)
    d.line([(px + 24, cy), (px + 140, cy)], fill=ACCENT2, width=5)
    # star
    sx = x1 - 150
    d.ellipse([sx - 46, cy - 46, sx + 46, cy + 46], fill=(255, 220, 120))
    d.text((x0 + 160, cy + 54), "one light-year ≈ 9.46 trillion km", font=font(30, False), fill=MUTED)


def draw_cells(d, box):
    card(d, box, "≈ 37,000,000,000,000")
    x0, y0, x1, y1 = box
    cols, rows = 6, 5
    for r in range(rows):
        for c in range(cols):
            cx = x0 + 120 + c * (x1 - x0 - 240) / (cols - 1)
            cy = y0 + 120 + r * (y1 - y0 - 240) / (rows - 1)
            rad = 42 + 4 * math.sin(r + c)
            d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(120, 200, 190), width=5)
            d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(120, 200, 190))
    d.text((x0 + 120, y1 - 80), "one dot ≈ 1.2 trillion cells", font=font(26, False), fill=MUTED)


def draw_sound(d, box):
    card(d, box, "NO MEDIUM")
    x0, y0, x1, y1 = box
    cy = (y0 + y1) // 2
    # speaker
    d.polygon([(x0 + 110, cy - 45), (x0 + 180, cy - 45), (x0 + 250, cy - 105),
               (x0 + 250, cy + 105), (x0 + 180, cy + 45), (x0 + 110, cy + 45)], fill=(210, 230, 255))
    for i, rr in enumerate((40, 75, 110)):
        d.arc([x0 + 260 - rr, cy - rr, x0 + 260 + rr, cy + rr], -60, 60, fill=ACCENT2, width=6)
    # vacuum barrier
    bx = x0 + 560
    d.line([(bx, y0 + 90), (bx, y1 - 90)], fill=(255, 120, 120), width=8)
    for k in range(8):
        yy = y0 + 120 + k * 55
        d.line([(bx - 18, yy - 18), (bx + 18, yy + 18)], fill=(255, 120, 120), width=4)
    d.text((bx + 36, cy - 20), "vacuum", font=font(32), fill=(255, 140, 140))
    d.text((x0 + 110, y1 - 78), "sound is a pressure wave", font=font(26, False), fill=MUTED)


def draw_photosynthesis(d, box):
    card(d, box, "LIGHT → SUGAR")
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # sun
    d.ellipse([cx - 230, y0 + 90, cx - 130, y0 + 190], fill=(255, 210, 90))
    for a in range(0, 360, 45):
        r1, r2 = 62, 82
        d.line([(cx - 180 + r1 * math.cos(math.radians(a)), y0 + 140 + r1 * math.sin(math.radians(a))),
                (cx - 180 + r2 * math.cos(math.radians(a)), y0 + 140 + r2 * math.sin(math.radians(a)))],
               fill=(255, 210, 90), width=5)
    # leaf
    d.polygon([(cx - 90, cy + 150), (cx - 10, cy - 110), (cx + 70, cy + 20), (cx + 10, cy + 150)],
              fill=(60, 160, 100))
    d.line([(cx - 10, cy + 150), (cx - 10, cy - 90)], fill=(20, 80, 50), width=5)
    for k in range(4):
        yy = cy + 40 - k * 45
        d.line([(cx - 10, yy), (cx + 40, yy - 25)], fill=(20, 80, 50), width=3)
        d.line([(cx - 10, yy), (cx - 55, yy - 20)], fill=(20, 80, 50), width=3)
    # arrows
    d.line([(cx - 170, y0 + 210), (cx - 70, cy - 60)], fill=ACCENT2, width=6)
    d.text((cx + 110, cy + 30), "CO₂ + H₂O", font=font(30), fill=INK)
    d.text((cx + 110, cy + 80), "→ sugar + O₂", font=font(30), fill=ACCENT)


def draw_core(d, box):
    card(d, box, "EARTH, CUTAWAY")
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    layers = [(300, (40, 90, 160)), (235, (70, 130, 110)), (165, (230, 140, 60)),
              (95, (255, 220, 120)), (45, (255, 250, 220))]
    for r, col in layers:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=(10, 16, 32), width=4)
    d.text((cx + 180, cy - 230), "inner core", font=font(26, False), fill=INK)
    d.text((cx + 210, cy - 60), "outer core", font=font(26, False), fill=INK)
    d.text((cx + 230, cy + 120), "mantle", font=font(26, False), fill=INK)
    d.text((cx - 300, cy + 250), "≈ 5,200 °C", font=font(34), fill=ACCENT2)


def draw_resistance(d, box):
    card(d, box, "SELECTION")
    x0, y0, x1, y1 = box
    # bacteria
    for i, (bx, by, alive) in enumerate([(x0 + 220, y0 + 230, False), (x0 + 420, y0 + 330, True),
                                         (x0 + 260, y0 + 470, False), (x0 + 520, y0 + 520, True)]):
        d.rounded_rectangle([bx - 80, by - 40, bx + 80, by + 40], radius=40,
                            fill=(90, 180, 140) if alive else (120, 120, 130))
        if not alive:
            d.line([(bx - 40, by - 40), (bx + 40, by + 40)], fill=(255, 110, 110), width=6)
            d.line([(bx + 40, by - 40), (bx - 40, by + 40)], fill=(255, 110, 110), width=6)
    # antibiotic capsule
    d.rounded_rectangle([x0 + 600, y0 + 200, x0 + 700, y0 + 300], radius=50, fill=(240, 240, 245))
    d.rectangle([x0 + 600, y0 + 200, x0 + 650, y0 + 300], fill=(220, 80, 80))
    d.text((x0 + 120, y1 - 80), "survivors reproduce → resistance", font=font(28, False), fill=MUTED)


def draw_blackhole(d, box):
    card(d, box, "EVENT HORIZON")
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.ellipse([cx - 220, cy - 70, cx + 220, cy + 70], outline=(255, 160, 70), width=26)
    d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=(0, 0, 0), outline=(255, 200, 120), width=4)
    d.ellipse([cx - 210, cy - 210, cx + 210, cy + 210], outline=(255, 120, 120), width=3)
    d.text((cx + 230, cy - 240), "point of no return", font=font(26, False), fill=(255, 150, 150))


def draw_honey(d, box):
    card(d, box, "3,000 YEARS")
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.rounded_rectangle([cx - 120, cy - 100, cx + 120, cy + 150], radius=26, fill=(230, 160, 40), outline=(255, 220, 150), width=5)
    d.rectangle([cx - 90, cy - 150, cx + 90, cy - 100], fill=(180, 120, 30))
    # dipper
    d.line([(cx + 180, cy - 180), (cx + 60, cy - 40)], fill=(210, 210, 210), width=8)
    for k in range(4):
        d.ellipse([cx + 40 + k * 10, cy - 50 + k * 18, cx + 70 + k * 10, cy - 30 + k * 18], fill=(230, 160, 40))
    d.text((cx - 130, cy + 190), "low water + high sugar", font=font(28, False), fill=MUTED)


def draw_octopus(d, box):
    card(d, box, "3 HEARTS")
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 30
    d.ellipse([cx - 150, cy - 150, cx + 150, cy + 90], fill=(200, 90, 120))
    d.ellipse([cx - 40, cy - 60, cx - 10, cy - 30], fill=(255, 255, 255))
    d.ellipse([cx + 20, cy - 60, cx + 50, cy - 30], fill=(255, 255, 255))
    for k in range(8):
        sx = cx - 140 + k * 40
        d.arc([sx - 50, cy + 40, sx + 50, cy + 260], 20, 160, fill=(200, 90, 120), width=12)
    for hx, hy in [(cx - 70, cy - 90), (cx, cy - 110), (cx + 70, cy - 90)]:
        d.ellipse([hx - 18, hy - 18, hx + 18, hy + 18], fill=(255, 120, 140))
    d.text((x0 + 110, y1 - 80), "two gill hearts + one body heart", font=font(26, False), fill=MUTED)


def draw_venus(d, box):
    card(d, box, "243 vs 225")
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.ellipse([cx - 60, cy - 250, cx + 60, cy - 130], fill=(255, 210, 90))
    d.ellipse([cx - 250, cy - 90, cx + 250, cy + 90], outline=(120, 150, 200), width=4)
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(220, 180, 120))
    d.ellipse([cx + 250, cy - 14, cx + 278, cy + 14], fill=(220, 180, 120))
    # clock
    ccx, ccy = x1 - 160, y1 - 150
    d.ellipse([ccx - 55, ccy - 55, ccx + 55, ccy + 55], outline=(255, 255, 255), width=5)
    d.line([(ccx, ccy), (ccx, ccy - 38)], fill=(255, 255, 255), width=5)
    d.line([(ccx, ccy), (ccx + 30, ccy + 12)], fill=(255, 255, 255), width=5)
    d.text((x0 + 110, y1 - 80), "one Venus day > one Venus year", font=font(28, False), fill=MUTED)


def draw_banana(d, box):
    card(d, box, "BOTANY")
    x0, y0, x1, y1 = box
    cy = (y0 + y1) // 2
    # banana
    d.arc([x0 + 100, cy - 190, x0 + 460, cy + 130], 200, 340, fill=(250, 220, 80), width=60)
    d.text((x0 + 140, cy + 150), "BERRY", font=font(34), fill=ACCENT)
    # strawberry
    d.polygon([(x0 + 650, cy - 150), (x0 + 790, cy - 150), (x0 + 720, cy + 120)], fill=(220, 60, 70))
    d.polygon([(x0 + 650, cy - 150), (x0 + 720, cy - 210), (x0 + 790, cy - 150)], fill=(60, 160, 90))
    for k in range(8):
        d.ellipse([x0 + 670 + (k % 3) * 40, cy - 100 + (k // 3) * 55, x0 + 682 + (k % 3) * 40, cy - 88 + (k // 3) * 55], fill=(255, 230, 150))
    d.text((x0 + 640, cy + 150), "NOT A BERRY", font=font(34), fill=(255, 140, 140))


def draw_shark(d, box):
    card(d, box, "450M vs 385M")
    x0, y0, x1, y1 = box
    cy = (y0 + y1) // 2 - 40
    # shark
    d.polygon([(x0 + 120, cy), (x0 + 330, cy - 70), (x0 + 520, cy - 10), (x0 + 620, cy - 90),
               (x0 + 590, cy + 10), (x0 + 660, cy + 80), (x0 + 450, cy + 60), (x0 + 240, cy + 50)],
              fill=(120, 150, 170))
    d.polygon([(x0 + 330, cy - 70), (x0 + 300, cy - 150), (x0 + 380, cy - 80)], fill=(120, 150, 170))
    d.ellipse([x0 + 480, cy - 25, x0 + 500, cy - 5], fill=(20, 20, 20))
    # timeline
    ty = y1 - 120
    d.line([(x0 + 120, ty), (x1 - 120, ty)], fill=(200, 220, 255), width=6)
    for x, label in [(x0 + 200, "shark"), (x0 + 620, "tree")]:
        d.ellipse([x - 16, ty - 16, x + 16, ty + 16], fill=ACCENT2)
        d.text((x - 40, ty + 30), label, font=font(28), fill=INK)


def draw_neutron(d, box):
    card(d, box, "10¹² kg / tsp")
    x0, y0, x1, y1 = box
    cy = (y0 + y1) // 2
    # teaspoon
    d.ellipse([x0 + 110, cy - 60, x0 + 300, cy + 60], outline=(220, 230, 245), width=8)
    d.line([(x0 + 290, cy), (x0 + 520, cy)], fill=(220, 230, 245), width=12)
    # dense sphere
    d.ellipse([x0 + 150, cy - 36, x0 + 222, cy + 36], fill=(180, 210, 255))
    for k in range(6):
        d.ellipse([x0 + 160 + (k % 3) * 20, cy - 20 + (k // 3) * 22,
                   x0 + 170 + (k % 3) * 20, cy - 10 + (k // 3) * 22], fill=(255, 255, 255))
    d.text((x0 + 560, cy - 30), "= a mountain", font=font(34), fill=ACCENT2)


def draw_outro(d, box):
    card(d, box, "YOUR TURN")
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.ellipse([cx - 170, cy - 170, cx + 170, cy + 170], outline=ACCENT, width=8)
    d.text((cx - 120, cy - 80), "?", font=font(180), fill=ACCENT)
    d.text((cx - 170, cy + 210), "comment below", font=font(34, False), fill=MUTED)


DRAW = {
    "ice": draw_ice, "lightyear": draw_lightyear, "cells": draw_cells, "sound": draw_sound,
    "photosynthesis": draw_photosynthesis, "core": draw_core, "resistance": draw_resistance,
    "blackhole": draw_blackhole, "honey": draw_honey, "octopus": draw_octopus,
    "venus": draw_venus, "banana": draw_banana, "shark": draw_shark,
    "neutron": draw_neutron, "outro": draw_outro,
}

manifest = []
for idx, (sid, kicker, headline, subline, diagram, pose, expr) in enumerate(SCENES_DEF):
    num = 0 if sid in ("s00_intro", "s15_outro") else idx
    im, d = base_canvas(kicker, num, headline, subline)
    box = (1090, 250, 2010, 1000)
    if diagram in DRAW:
        DRAW[diagram](d, box)
    elif diagram == "title":
        d.text((1130, 420), "SCIENCE", font=font(96), fill=ACCENT)
        d.text((1130, 540), "IN 60 SECONDS", font=font(64, False), fill=INK)
        d.text((1130, 650), "14 counter-intuitive facts", font=font(36, False), fill=MUTED)
    # footer source line
    d.text((92, H - 92), "OpenMontage · original diagrams · no third-party footage", font=font(26, False), fill=(100, 116, 139))
    path = SCENES / f"{sid}.png"
    im.save(path)
    t = by_id[sid]
    manifest.append({"id": sid, "image": str(path), "start_s": t["start_s"],
                     "end_s": t["end_s"], "text": t["text"], "pose": pose, "expression": expr})

json.dump(manifest, open(ROOT / "scenes.json", "w"), indent=2)
print("rendered", len(manifest), "scenes")