"""Build narration audio for the 60-90 s E2E demo with Piper (local, $0)."""

import json
import subprocess
from pathlib import Path

ROOT = Path("/workspaces/OpenMontage/work/master-run/e2e")
AUDIO = ROOT / "audio"
AUDIO.mkdir(parents=True, exist_ok=True)
PIPER = "/tmp/opencode/omk/bin/piper"
MODEL = "/tmp/opencode/en_US-lessac-medium.onnx"

LINES = [
    ("s00_intro", "Fourteen facts that sound wrong, but are true."),
    ("s01_ice", "Water expands when it freezes, which is why ice floats on a lake."),
    ("s02_lightyear", "A light-year is the distance light travels in one year, not a measure of time."),
    ("s03_cells", "The human body contains about thirty-seven trillion cells."),
    ("s04_sound", "Sound cannot travel through the vacuum of space."),
    ("s05_photosynthesis", "Photosynthesis converts light energy into chemical energy."),
    ("s06_core", "The Earth's core is roughly as hot as the surface of the Sun."),
    ("s07_resistance", "Antibiotic resistance arises when bacteria evolve under selective pressure."),
    ("s08_blackhole", "A black hole's event horizon is the boundary beyond which nothing can escape."),
    ("s09_honey", "Honey never spoils; edible honey has been found in three-thousand-year-old Egyptian tombs."),
    ("s10_octopus", "Octopuses have three hearts and blue blood."),
    ("s11_venus", "A day on Venus is longer than a year on Venus."),
    ("s12_banana", "Bananas are berries, but strawberries are not."),
    ("s13_shark", "Sharks existed before trees."),
    ("s14_neutron", "A teaspoon of neutron star material would weigh billions of tons."),
    ("s15_outro", "Which one surprised you? Tell me in the comments, and follow for more science."),
]


def dur(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return round(float(p.stdout.strip()), 3)


meta = []
for sid, text in LINES:
    out = AUDIO / f"{sid}.wav"
    p = subprocess.run([PIPER, "-m", MODEL, "-f", str(out)], input=text, text=True,
                       capture_output=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr[-1500:])
    meta.append({"id": sid, "text": text, "file": str(out), "duration_s": dur(out)})
    print(sid, meta[-1]["duration_s"], text)

# timeline: 0.35 s lead-in, 0.55 s between facts, 0.9 s tail
timeline = []
t = 0.35
for m in meta:
    timeline.append({"id": m["id"], "text": m["text"], "file": m["file"],
                     "start_s": round(t, 3), "duration_s": m["duration_s"],
                     "end_s": round(t + m["duration_s"], 3)})
    t += m["duration_s"] + (0.55 if m["id"] not in ("s00_intro", "s15_outro") else 0.75)
total = round(t + 0.15, 3)
json.dump({"lines": meta, "timeline": timeline, "total_s": total},
          open(ROOT / "narration.json", "w"), indent=2)
print("total_s", total)
print("word_count", sum(len(m["text"].split()) for m in meta))
print("wpm", round(sum(len(m["text"].split()) for m in meta) / (total / 60), 1))