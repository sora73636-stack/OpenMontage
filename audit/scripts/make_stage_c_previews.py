#!/usr/bin/env python3
"""Build Stage C previews (compressed, reviewable) from the downloaded Kaggle outputs.

Reads only files that already exist under audit/logs/kaggle/p1-*/; never downloads.
Writes audit/previews/stage_c/ and refreshes SHA256SUMS.txt.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
OUT = AUDIT / "previews/stage_c"
OUT.mkdir(parents=True, exist_ok=True)


def ff(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def find(pattern: str) -> list[Path]:
    return sorted(AUDIT.glob(f"logs/kaggle/**/{pattern}"))


def pick(paths: list[Path], prefer: str) -> Path | None:
    for p in paths:
        if prefer in str(p):
            return p
    return paths[0] if paths else None


def sha(p: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


made: list[Path] = []

# --- Kokoro: mp3 of the same script used for CosyVoice (af_heart) ----------
kok = pick(find("kokoro-82m/out.wav"), "v1")
if kok:
    dst = OUT / "kokoro82m_af_heart.mp3"
    ff(["-i", str(kok), "-ac", "1", "-ar", "24000", "-b:a", "64k", str(dst)])
    made.append(dst)

# --- SDXL: 3 jpgs, same seeds/prompts as FLUX in Stage B ------------------
for i in (1, 2, 3):
    src = pick(find(f"sdxl_{i}.png"), "p1-sdxl")
    if src:
        dst = OUT / f"sdxl_{i}.jpg"
        ff(["-i", str(src), "-q:v", "3", str(dst)])
        made.append(dst)

# --- Depth Anything V2: depth map png -> jpg ------------------------------
d2 = pick(find("depth_00.png"), "p1-depth/v7")
if d2:
    dst = OUT / "depth_anything_v2_small_depth_00.jpg"
    ff(["-i", str(d2), "-q:v", "2", str(dst)])
    made.append(dst)

# --- Video Depth Anything: depth video -> 1 frame jpg + short mp4 ---------
vd = pick(find("input_vis.mp4"), "p1-vd/v2")
if vd:
    dst = OUT / "video_depth_anything_small_depth.mp4"
    ff(["-i", str(vd), "-t", "2", "-c:v", "libx264", "-crf", "30", "-preset", "veryfast", str(dst)])
    made.append(dst)
    jpg = OUT / "video_depth_anything_small_depth_frame.jpg"
    ff(["-i", str(vd), "-vf", "select=eq(n\\,12)", "-vframes", "1", "-q:v", "2", str(jpg)])
    made.append(jpg)

# --- Wan2.1: short clip --------------------------------------------------
wan = pick(find("wan*.mp4"), "p1-wan")
if wan:
    dst = OUT / "wan21_t2v_1_3b.mp4"
    ff(["-i", str(wan), "-t", "5", "-vf", "scale=640:-2", "-c:v", "libx264", "-crf", "30",
        "-preset", "veryfast", "-an", str(dst)])
    made.append(dst)

# --- DeepFilterNet3: noisy vs enhanced snippets (10 s mp3) ----------------
dfn = pick(find("*_DeepFilterNet3.wav"), "p1-dfn")
if dfn:
    noisy = dfn.parent / "noisy.wav"
    for src, name in ((noisy, "deepfilternet3_noisy_10s.mp3"), (dfn, "deepfilternet3_enhanced_10s.mp3")):
        if src.exists():
            dst = OUT / name
            ff(["-t", "10", "-i", str(src), "-ac", "1", "-ar", "24000", "-b:a", "64k", str(dst)])
            made.append(dst)

lines = []
for p in made:
    lines.append(f"{sha(p)}  {p.relative_to(ROOT)}")
(OUT / "SHA256SUMS.txt").write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")
print(json.dumps({"made": [str(p.relative_to(ROOT)) for p in made]}, indent=2))