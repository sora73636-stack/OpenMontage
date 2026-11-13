#!/usr/bin/env python3
"""Build the Stage A Kaggle script kernel from the canonical shared helper.

The helper file audit/scripts/kaggle_environment_snapshot.py is embedded
byte-for-byte (base64) so the kernel cannot drift from the shared helper.
The kernel verifies the embedded SHA256 before importing it.
"""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "audit/scripts/kaggle_environment_snapshot.py"
OUT_DIR = ROOT / "audit/kaggle/smoke_gpu"
NOTEBOOK = OUT_DIR / "notebook.py"


def main() -> None:
    raw = HELPER.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    blob = base64.b64encode(raw).decode("ascii")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    script = f'''#!/usr/bin/env python3
"""OpenMontage Stage A - shared environment snapshot + P2.2 FFmpeg/NVENC.

Scope of this kernel (RUN_STAGE A): environment snapshot only, plus the
P2.2 FFmpeg software (libx264) and hardware (h264_nvenc) encode test.
No model weights are downloaded and no model inference is run here.

The shared helper below is embedded as base64 and verified by SHA256.
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

HELPER_B64 = "{blob}"
HELPER_SHA256 = "{digest}"

WORK = Path("/kaggle/working/audit")
LOGS = WORK / "logs/kaggle"
RESULTS = WORK / "results"
PREVIEWS = WORK / "previews"
for _p in (WORK, LOGS, RESULTS, PREVIEWS, WORK / "scripts"):
    _p.mkdir(parents=True, exist_ok=True)


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sh(cmd, timeout=900):
    started = time.time()
    rec = {{"cmd": cmd, "returncode": None, "duration_s": None, "stdout": "", "stderr": ""}}
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        rec["returncode"] = proc.returncode
        rec["stdout"] = proc.stdout[-40000:]
        rec["stderr"] = proc.stderr[-16000:]
    except Exception as exc:  # noqa: BLE001
        rec["error"] = f"{{type(exc).__name__}}: {{exc}}"
    rec["duration_s"] = round(time.time() - started, 3)
    return rec


def main() -> int:
    run_started = time.time()
    report = {{
        "stage": "A",
        "kernel_purpose": "shared environment snapshot + P2.2 FFmpeg/NVENC",
        "utc_start": utc(),
        "status": "UNKNOWN",
        "steps": {{}},
    }}

    # --- 1. materialise and verify the shared helper -----------------------
    helper_path = WORK / "scripts/kaggle_environment_snapshot.py"
    helper_path.write_bytes(base64.b64decode(HELPER_B64))
    actual_helper_sha = sha256_file(helper_path)
    report["helper"] = {{
        "path": str(helper_path),
        "embedded_sha256": HELPER_SHA256,
        "actual_sha256": actual_helper_sha,
        "match": actual_helper_sha == HELPER_SHA256,
    }}
    print("helper sha256:", actual_helper_sha, "match:", actual_helper_sha == HELPER_SHA256)
    if actual_helper_sha != HELPER_SHA256:
        report["status"] = "BLOCKED"
        report["blocker"] = "shared helper SHA256 mismatch"
        (LOGS / "stage_a_summary.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return 1

    sys.path.insert(0, str(helper_path.parent))
    import kaggle_environment_snapshot as snap  # noqa: PLC0415

    # --- 2. environment snapshot BEFORE ------------------------------------
    before = snap.collect(LOGS, "before")
    t4 = snap.assert_t4(before)
    report["steps"]["environment_before"] = {{
        "utc_timestamp": before["utc_timestamp"],
        "python_version": before["python_version"],
        "torch": {{
            "version": before["torch"]["torch_version"],
            "cuda_build": before["torch"]["torch_cuda_build"],
            "cuda_available": before["torch"]["cuda_available"],
            "device_count": before["torch"]["device_count"],
            "devices": before["torch"]["devices"],
        }},
        "ffmpeg_version_returncode": before["ffmpeg_version"]["returncode"],
        "ffmpeg_version_first_line": (before["ffmpeg_version"]["stdout"].splitlines() or [""])[0],
        "ffprobe_version_first_line": (before["ffprobe_version"]["stdout"].splitlines() or [""])[0],
        "network_check": before["network_check"],
        "t4_assertion": t4,
    }}
    print("T4 assertion:", json.dumps(t4))
    if not t4["ok"]:
        report["status"] = "BLOCKED"
        report["blocker"] = "GPU assertion failed: " + "; ".join(t4["reasons"])
        (LOGS / "stage_a_summary.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return 2

    # --- 3. P2.2 FFmpeg build + NVENC --------------------------------------
    encoders = before["ffmpeg_encoders"]
    enc_text = (enc_text_val := encoders.get("stdout", "")) or ""
    has_libx264 = "libx264" in enc_text
    has_nvenc = "h264_nvenc" in enc_text
    nvenc_help = sh("ffmpeg -hide_banner -h encoder=h264_nvenc", timeout=60)
    report["steps"]["p2_2_ffmpeg_build"] = {{
        "libx264_present": has_libx264,
        "h264_nvenc_present": has_nvenc,
        "nvenc_help_returncode": nvenc_help["returncode"],
        "nvenc_help_first_lines": "\\n".join(nvenc_help["stdout"].splitlines()[:25]),
        "configuration": next(
            (line for line in enc_text.splitlines() if line.strip().startswith("configuration:")),
            None,
        ),
        "encoder_list_sha256": hashlib.sha256(enc_text.encode("utf-8", "replace")).hexdigest(),
    }}

    # deterministic 10 s 1920x1080 30 fps testsrc2 + 48 kHz tone
    src = (
        "ffmpeg -y -hide_banner -loglevel error "
        "-f lavfi -i testsrc2=size=1920x1080:rate=30:duration=10 "
        "-f lavfi -i sine=frequency=440:sample_rate=48000:duration=10 "
        "-c:v libx264 -preset ultrafast -qp 0 -pix_fmt yuv420p "
        "-c:a pcm_s16le -shortest /kaggle/working/audit/previews/p2_2_source.mp4"
    )
    src_run = sh(src, timeout=600)
    report["steps"]["source_generation"] = {{
        "cmd": src,
        "returncode": src_run["returncode"],
        "duration_s": src_run["duration_s"],
        "stderr": src_run["stderr"][-4000:],
    }}

    def sample_gpu(path: Path, seconds: int = 8) -> subprocess.Popen:
        cmd = (
            f"timeout {{seconds}} nvidia-smi "
            "--query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader -l 1 "
            f"> {{path}} 2>&1"
        )
        return subprocess.Popen(cmd, shell=True)

    def encode_case(name: str, cmd: str) -> dict:
        out = f"/kaggle/working/audit/previews/p2_2_{{name}}.mp4"
        full = cmd.replace("<<OUT>>", out)
        sampler = None
        samples_path = LOGS / f"p2_2_{{name}}_nvidia_smi.csv"
        if name == "h264_nvenc":
            sampler = sample_gpu(samples_path, 8)
            time.sleep(0.5)
        run = sh(full, timeout=900)
        if sampler is not None:
            try:
                sampler.wait(timeout=12)
            except Exception:  # noqa: BLE001
                sampler.kill()
        rec = {{
            "name": name,
            "cmd": full,
            "returncode": run["returncode"],
            "duration_s": run["duration_s"],
            "stderr": run["stderr"][-6000:],
            "output": None,
            "probe": None,
            "decode": None,
        }}
        if samples_path.exists():
            lines = [l for l in samples_path.read_text(errors="replace").splitlines() if l.strip()]
            rec["nvidia_smi_samples"] = lines[:20]
            rec["nvidia_smi_sample_count"] = len(lines)
        if Path(out).exists() and Path(out).stat().st_size > 0:
            rec["output"] = {{
                "path": out,
                "bytes": Path(out).stat().st_size,
                "sha256": sha256_file(Path(out)),
            }}
            probe = sh(
                f"ffprobe -v error -show_streams -show_format -of json {{out}}", timeout=120
            )
            try:
                rec["probe"] = json.loads(probe["stdout"])
            except Exception:  # noqa: BLE001
                rec["probe"] = {{"parse_error": True, "raw": probe["stdout"][-4000:]}}
            decode = sh(f"ffmpeg -v error -i {{out}} -f null -", timeout=600)
            rec["decode"] = {{
                "returncode": decode["returncode"],
                "stderr": decode["stderr"][-8000:],
                "clean": decode["returncode"] == 0 and not decode["stderr"].strip(),
            }}
        return rec

    libx264 = None
    if has_libx264:
        libx264 = encode_case(
            "libx264",
            "ffmpeg -y -hide_banner -loglevel error "
            "-f lavfi -i testsrc2=size=1920x1080:rate=30:duration=10 "
            "-f lavfi -i sine=frequency=440:sample_rate=48000:duration=10 "
            "-c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p "
            "-c:a aac -b:a 128k -shortest <<OUT>>",
        )
        probe = libx264.get("probe") or {{}}
        streams = probe.get("streams", []) if isinstance(probe, dict) else []
        video = next((s for s in streams if s.get("codec_type") == "video"), {{}})
        audio = next((s for s in streams if s.get("codec_type") == "audio"), {{}})
        libx264["checks"] = {{
            "video_codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "avg_frame_rate": video.get("avg_frame_rate"),
            "nb_frames": video.get("nb_frames"),
            "pix_fmt": video.get("pix_fmt"),
            "audio_codec": audio.get("codec_name"),
            "sample_rate": audio.get("sample_rate"),
            "duration_s": float((probe.get("format") or {{}}).get("duration") or 0),
            "valid_10s_1080p30": (
                video.get("codec_name") == "h264"
                and video.get("width") == 1920
                and video.get("height") == 1080
                and video.get("avg_frame_rate") == "30/1"
                and abs(float((probe.get("format") or {{}}).get("duration") or 0) - 10.0) < 0.5
            ),
        }}
        libx264["pass"] = bool(
            libx264["returncode"] == 0
            and libx264.get("decode", {{}}).get("clean")
            and libx264["checks"]["valid_10s_1080p30"]
        )

    nvenc = None
    if has_nvenc:
        nvenc = encode_case(
            "h264_nvenc",
            "ffmpeg -y -hide_banner -loglevel error "
            "-f lavfi -i testsrc2=size=1920x1080:rate=30:duration=10 "
            "-f lavfi -i sine=frequency=440:sample_rate=48000:duration=10 "
            "-c:v h264_nvenc -preset p4 -rc vbr -cq 23 -b:v 0 -pix_fmt yuv420p "
            "-c:a aac -b:a 128k -shortest <<OUT>>",
        )
        probe = nvenc.get("probe") or {{}}
        streams = probe.get("streams", []) if isinstance(probe, dict) else []
        video = next((s for s in streams if s.get("codec_type") == "video"), {{}})
        nvenc["checks"] = {{
            "video_codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "avg_frame_rate": video.get("avg_frame_rate"),
            "nb_frames": video.get("nb_frames"),
            "duration_s": float((probe.get("format") or {{}}).get("duration") or 0),
        }}
        nvenc["pass"] = bool(
            nvenc["returncode"] == 0
            and nvenc.get("decode", {{}}).get("clean")
            and video.get("codec_name") == "h264"
            and video.get("width") == 1920
            and video.get("height") == 1080
        )

    report["steps"]["p2_2_results"] = {{
        "libx264": libx264,
        "h264_nvenc": nvenc,
        "nvenc_tested": has_nvenc,
        "note": "libx264 PASS does not imply NVENC PASS",
    }}

    # --- 4. snapshot AFTER -------------------------------------------------
    after = snap.collect(LOGS, "after")
    report["steps"]["environment_after"] = {{
        "utc_timestamp": after["utc_timestamp"],
        "torch": {{
            "version": after["torch"]["torch_version"],
            "cuda_available": after["torch"]["cuda_available"],
            "device_count": after["torch"]["device_count"],
            "devices": after["torch"]["devices"],
        }},
        "network_check": after["network_check"],
        "disk_usage": after["disk_usage"],
        "working_dir_size": after["output_dir_size"],
    }}
    report["utc_end"] = utc()
    report["wall_seconds"] = round(time.time() - run_started, 3)

    libx264_ok = bool((libx264 or {{}}).get("pass"))
    nvenc_present = has_nvenc
    nvenc_ok = bool((nvenc or {{}}).get("pass"))
    if not has_libx264:
        report["status"] = "FAIL"
        report["blocker"] = "libx264 encoder missing"
    elif not libx264_ok:
        report["status"] = "FAIL"
        report["blocker"] = "libx264 encode/decode/validation failed"
    elif nvenc_present and not nvenc_ok:
        report["status"] = "FAIL"
        report["blocker"] = "h264_nvenc present but encode/decode/validation failed"
    elif not nvenc_present:
        report["status"] = "PASS"
        report["nvenc_status"] = "FAIL (encoder missing)"
    else:
        report["status"] = "PASS"
        report["nvenc_status"] = "PASS"
    report["libx264_status"] = "PASS" if libx264_ok else "FAIL"

    (LOGS / "stage_a_summary.json").write_text(json.dumps(report, indent=2))
    (LOGS / "stage_a_summary.txt").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        print(tb)
        try:
            (LOGS / "stage_a_summary.json").write_text(
                json.dumps(
                    {{
                        "stage": "A",
                        "status": "FAIL",
                        "blocker": "unhandled exception",
                        "traceback": tb,
                        "utc_end": utc(),
                    }},
                    indent=2,
                )
            )
        except Exception:  # noqa: BLE001
            pass
        raise SystemExit(4)
'''
    NOTEBOOK.write_text(script, encoding="utf-8")
    print(f"wrote {NOTEBOOK} ({len(script)} bytes); helper sha256={digest}")


if __name__ == "__main__":
    main()