#!/usr/bin/env python3
"""Check that STAGE_B_SUMMARY.md values agree with audit/results.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
summary = (ROOT / "audit/STAGE_B_SUMMARY.md").read_text(encoding="utf-8")
results = json.loads((ROOT / "audit/results.json").read_text(encoding="utf-8"))
by_name = {c["name"]: c for c in results["components"]}

checks = []


def check(label: str, ok: bool) -> None:
    checks.append((label, ok))


ltx = by_name["ltx-video-2b-0.9.5"]
flux = by_name["flux2-klein-4b"]
cosy = by_name["cosyvoice3"]
rife = by_name["practical-rife-4.25"]
esrgan = by_name["real-esrgan-x4plus"]

check("LTX runtime PASS", ltx["runtime_status"] == "PASS")
check("LTX dtype FP16", ltx["dtype"] == "torch.float16")
check("LTX 62.47 s", round(ltx["runtime_seconds"], 2) == 62.47)
check("LTX 49 frames", ltx["checks"]["frames"] == 49)
check("LTX VRAM 11033/11050",
      round(ltx["peak_vram_allocated_mb"]) == 11033 and ltx["peak_vram_reserved_mb"] == 11050)
check("table has LTX 62.47 s generation (49 frames)",
      "62.47 s generation (49 frames)" in summary)

check("FLUX runtime PASS", flux["runtime_status"] == "PASS")
check("FLUX per-image values",
      [round(x, 1) for x in flux["checks"]["seconds_per_image"]] == [23.6, 21.4, 21.1])
check("FLUX total 66.035", round(flux["runtime_seconds"], 3) == 66.035)
check("FLUX total rounds to 66.0", round(flux["runtime_seconds"], 1) == 66.0)
check("table has FLUX per-image wording",
      "23.6 / 21.4 / 21.1 s **per image**; 66.0 s for all three" in summary)

check("CosyVoice runtime PASS", cosy["runtime_status"] == "PASS")
check("CosyVoice dtype FP32", cosy["dtype"] == "torch.float32")
check("CosyVoice 594.76 s", round(cosy["runtime_seconds"], 2) == 594.76)
check("CosyVoice audio 602.28 s", round(cosy["checks"]["audio_duration_s"], 2) == 602.28)
check("CosyVoice RTF 0.988", round(cosy["rtf"], 3) == 0.988)
check("CosyVoice VRAM 3589.6/4264",
      round(cosy["peak_vram_allocated_mb"], 1) == 3589.6 and cosy["peak_vram_reserved_mb"] == 4264)
check("table has CosyVoice 594.76 / 602.28 / RTF 0.988",
      "594.76 s generation / 602.28 s audio (RTF 0.988)" in summary)

check("RIFE runtime BLOCKED", rife["runtime_status"] == "BLOCKED")
check("RIFE no runtime", rife["runtime_seconds"] is None)
check("table has RIFE no inference", "no inference (CANCEL_ACKNOWLEDGED at ~90 s, v1/v2)" in summary)

check("ESRGAN runtime PASS", esrgan["runtime_status"] == "PASS")
check("ESRGAN license FAIL", esrgan["license_status"] == "FAIL")
check("ESRGAN dtype FP32", esrgan["dtype"] == "FP32")
check("ESRGAN VRAM 1041 nvidia-smi", esrgan["peak_vram_mib_nvidia_smi"] == 1041)
check("ESRGAN 16.6 s / 10 images",
      round(esrgan["runtime_seconds"], 1) == 16.6 and esrgan["checks"]["images"] == 10)
check("table has ESRGAN FAIL + 16.6 s / 10 images",
      "FAIL (weight license not explicit)" in summary and "16.6 s / 10 images" in summary)

failed = [label for label, ok in checks if not ok]
for label, ok in checks:
    print(("PASS " if ok else "FAIL ") + label)
if failed:
    raise SystemExit(f"{len(failed)} consistency check(s) failed")
print(f"all {len(checks)} consistency checks passed")