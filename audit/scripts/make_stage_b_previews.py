#!/usr/bin/env python3
"""Build small Stage B review previews from the preserved Kaggle outputs.

Outputs (all under audit/previews/stage_b/):
  - cosyvoice3_af_heart.mp3   full 602.28 s narration, mono 96 kbps
  - flux_1.jpg .. flux_3.jpg  512x512 images
  - ltx_out.mp4               copied 512x512 / 24 fps clip (45 KB)
  - esrgan_frame_00_before.jpg / _after.jpg ... frames 00-02
  - SHA256SUMS.txt            checksums of the previews above

No model is run. ffmpeg/ffprobe and Pillow only transcode/copy existing files.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
LOGS = AUDIT / "logs" / "kaggle"
OUT = AUDIT / "previews" / "stage_b"
OUT.mkdir(parents=True, exist_ok=True)

COSY_WAV = LOGS / "p0-cosy/v10/audit/results/cosyvoice3/out.wav"
LTX_MP4 = LOGS / "p0-ltx/v3/audit/results/ltx-video-2b-0.9.5/out.mp4"
FLUX_DIR = LOGS / "p0-flux/v2/audit/results/flux2-klein-4b"
ESRGAN_IN = LOGS / "p0-esrgan/v2/audit/fixtures/esrgan/inputs"
ESRGAN_OUT = LOGS / "p0-esrgan/v2/audit/fixtures/esrgan/outputs"

MAX_BYTES = 10 * 1024 * 1024


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr[-4000:]}")


def make_audio() -> Path:
    dst = OUT / "cosyvoice3_af_heart.mp3"
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(COSY_WAV), "-ac", "1", "-ar", "24000",
        "-c:a", "libmp3lame", "-b:a", "96k", str(dst),
    ])
    if dst.stat().st_size > MAX_BYTES:
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(COSY_WAV), "-ac", "1", "-ar", "24000",
            "-c:a", "libmp3lame", "-b:a", "64k", str(dst),
        ])
    if dst.stat().st_size > MAX_BYTES:
        raise SystemExit(f"{dst} is still above 10 MB: {dst.stat().st_size} bytes")
    return dst


def make_images() -> list[Path]:
    made = []
    for src in sorted(FLUX_DIR.glob("flux_*.png")):
        dst = OUT / f"{src.stem}.jpg"
        with Image.open(src) as im:
            im.convert("RGB").save(dst, "JPEG", quality=90, optimize=True)
        made.append(dst)

    for idx in range(3):
        src_in = ESRGAN_IN / f"frame_0{idx}.png"
        src_out = ESRGAN_OUT / f"frame_0{idx}_out.png"
        for src, suffix in ((src_in, "before"), (src_out, "after")):
            dst = OUT / f"esrgan_frame_0{idx}_{suffix}.jpg"
            with Image.open(src) as im:
                im.convert("RGB").save(dst, "JPEG", quality=90, optimize=True)
            made.append(dst)
    return made


def make_video() -> Path:
    dst = OUT / "ltx_out.mp4"
    shutil.copy2(LTX_MP4, dst)
    return dst


def main() -> None:
    files = [make_audio(), make_video(), *make_images()]
    lines = []
    for path in sorted(files):
        size = path.stat().st_size
        status = "OK" if size <= MAX_BYTES else "TOO LARGE"
        lines.append(f"{sha256(path)}  {path.relative_to(AUDIT)}  ({size} bytes, {status})")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    audio = next(p for p in files if p.suffix == ".mp3")
    probe = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio)],
        capture_output=True, text=True, check=True,
    ).stdout)
    print(f"previews written to {OUT.relative_to(ROOT)}")
    for path in sorted(files):
        print(f"  {path.name}: {path.stat().st_size} bytes")
    print(f"  audio duration: {float(probe['format']['duration']):.2f} s")


if __name__ == "__main__":
    main()