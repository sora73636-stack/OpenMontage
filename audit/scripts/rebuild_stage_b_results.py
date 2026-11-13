#!/usr/bin/env python3
"""Rebuild Stage B result JSON from the preserved Kaggle logs.

This script does not call Kaggle or any model. It reads only artifacts already
committed under audit/logs/kaggle/ and rewrites:

  - audit/results.json
  - audit/results/component_results.json
  - audit/results/stage_b_table.md (generated from the same numbers)

Stage A component records are preserved; only the five P0 component records are
replaced with Stage B runtime evidence.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
RESULTS = AUDIT / "results"
LOGS = AUDIT / "logs" / "kaggle"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Stage A values are kept as-is; these five records are replaced by Stage B data.
P0 = {
    "ltx": "ltx-video-2b-0.9.5",
    "flux": "flux2-klein-4b",
    "cosy": "cosyvoice3",
    "rife": "practical-rife-4.25",
    "esrgan": "real-esrgan-x4plus",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ltx_summary() -> dict:
    """LTX wrote its summary as a pretty JSON block at the end of ltx_logs.txt."""
    text = (LOGS / "p0-ltx/v3/ltx_logs.txt").read_text(encoding="utf-8")
    marker = '\n{\n  "component": "ltx-video-2b-0.9.5"'
    start = text.index(marker) + 1
    summary, _ = json.JSONDecoder().raw_decode(text[start:])
    return summary


def build_components() -> list[dict]:
    ltx = ltx_summary()
    ltx_m = ltx["steps"]["metrics"]
    ltx_out = ltx["steps"]["outputs"][0]

    flux = read_json(LOGS / "p0-flux/v2/audit/results/flux2-klein-4b/summary.json")
    flux_m = flux["steps"]["metrics"]
    flux_seconds = [round(float(img["seconds"]), 3) for img in flux_m["images"]]
    flux_total = round(sum(float(img["seconds"]) for img in flux_m["images"]), 3)

    cosy = read_json(LOGS / "p0-cosy/v10/audit/results/cosyvoice3/summary.json")
    cosy_m = cosy["steps"]["metrics"]

    esrgan = read_json(LOGS / "p0-esrgan/v2/audit/results/real-esrgan-x4plus/summary.json")
    esrgan_step = esrgan["steps"]["inference"]

    return [
        {
            "name": P0["ltx"],
            "priority": "P0",
            "stage": "B",
            "version": "0.9.5",
            "source_url": "https://huggingface.co/Lightricks/LTX-Video-0.9.5",
            "revision": "e58e28c39631af4d1468ee57a853764e11c1d37e",
            "checkpoint_files": [],
            "checkpoint_sha256": [],
            "code_license": "LTX-Video repo code license (Apache-2.0); see LICENSE-code.txt",
            "weight_license": "Open RAIL-M (commercial use with use restrictions)",
            "license_evidence": ["audit/licenses/ltx-video-2b-0.9.5/LICENSE-weights.txt"],
            "license_status": "PASS",
            "license_basis": "license_text",
            "dtype": ltx_m["dtype"],
            "attention_backend": ltx_m["attn"],
            "gpu_index": 0,
            "gpu_name": "Tesla T4",
            "peak_vram_allocated_mb": ltx_m["peak_alloc_mb"],
            "peak_vram_reserved_mb": ltx_m["peak_reserved_mb"],
            "peak_ram_mb": None,
            "runtime_seconds": round(float(ltx_m["gen_s"]), 3),
            "runtime_seconds_basis": "generation only; excludes model load",
            "rtf": None,
            "fps": 24,
            "automatic_quality_status": "PASS",
            "human_review_status": "NEEDS HUMAN REVIEW",
            "runtime_status": "PASS",
            "production_status": "BLOCKED",
            "input_artifacts": ["audit/config/image_video_prompts.json"],
            "output_artifacts": ["audit/logs/kaggle/p0-ltx/v3/audit/results/ltx-video-2b-0.9.5/out.mp4"],
            "log_path": "audit/logs/kaggle/p0-ltx/v3/ltx_logs.txt",
            "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p0-ltx-video-2b-0-9-5",
            "errors": None,
            "notes": "512x512, 49 frames, 30 steps, seed 424242; decode clean; cpu offload used to fit 15 GB.",
            "checks": {
                "resolution": "512x512",
                "frames": int(ltx_m["frames"]),
                "steps": 30,
                "seed": 424242,
                "model_load_seconds": round(float(ltx_m["load_s"]), 3),
                "generation_seconds": round(float(ltx_m["gen_s"]), 3),
                "step_seconds": round(float(ltx["steps"]["inference"]["duration_s"]), 3),
                "decode_clean": bool(ltx["steps"].get("decode_clean")),
                "ffprobe_duration_s": 2.041667,
                "ffprobe_size_bytes": ltx_out["bytes"],
                "output_sha256": ltx_out["sha256"],
            },
        },
        {
            "name": P0["flux"],
            "priority": "P0",
            "stage": "B",
            "version": "FLUX.2 klein 4B",
            "source_url": "https://huggingface.co/black-forest-labs/FLUX.2-klein-4B",
            "revision": "e7b7dc27f91deacad38e78976d1f2b499d76a294",
            "checkpoint_files": [],
            "checkpoint_sha256": [],
            "code_license": "Apache-2.0 (FLUX.2 repo)",
            "weight_license": "Apache-2.0",
            "license_evidence": ["audit/licenses/flux2-klein-4b/LICENSE-weights.txt"],
            "license_status": "PASS",
            "license_basis": "license_text",
            "dtype": flux_m["dtype"],
            "attention_backend": flux_m["attn"],
            "gpu_index": 0,
            "gpu_name": "Tesla T4",
            "peak_vram_allocated_mb": round(float(flux_m["peak_alloc_mb"]), 3),
            "peak_vram_reserved_mb": round(float(flux_m["peak_reserved_mb"]), 3),
            "peak_ram_mb": None,
            "runtime_seconds": flux_total,
            "runtime_seconds_basis": "sum of the three per-image generation times; excludes model load",
            "rtf": None,
            "fps": None,
            "automatic_quality_status": "PASS",
            "human_review_status": "NEEDS HUMAN REVIEW",
            "runtime_status": "PASS",
            "production_status": "BLOCKED",
            "input_artifacts": ["audit/config/image_video_prompts.json"],
            "output_artifacts": [
                "audit/logs/kaggle/p0-flux/v2/audit/results/flux2-klein-4b/flux_1.png",
                "audit/logs/kaggle/p0-flux/v2/audit/results/flux2-klein-4b/flux_2.png",
                "audit/logs/kaggle/p0-flux/v2/audit/results/flux2-klein-4b/flux_3.png",
            ],
            "log_path": "audit/logs/kaggle/p0-flux/v2/flux_logs.txt",
            "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p0-flux2-klein-4b",
            "errors": None,
            "notes": "3 prompts/seeds, 512x512, 4 steps, guidance 1.0; 23.6/21.4/21.1 s is per image, not for all three.",
            "checks": {
                "images": len(flux_seconds),
                "resolution": "512x512",
                "steps": 4,
                "guidance": 1.0,
                "seconds_per_image": flux_seconds,
                "generation_seconds_total": flux_total,
                "model_load_seconds": round(float(flux_m["load_s"]), 3),
                "step_seconds": round(float(flux["steps"]["inference"]["duration_s"]), 3),
                "image_sha256": [out["sha256"] for out in flux["steps"]["outputs"]],
            },
        },
        {
            "name": P0["cosy"],
            "priority": "P0",
            "stage": "B",
            "version": "Fun-CosyVoice3-0.5B-2512",
            "source_url": "https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512",
            "revision": "29e01c4e8d000f4bcd70751be16fa94bf3d85a18",
            "checkpoint_files": [],
            "checkpoint_sha256": [],
            "code_license": "Apache-2.0 (CosyVoice repo)",
            "weight_license": "Apache-2.0 (model-card metadata only)",
            "license_evidence": [
                "audit/licenses/cosyvoice3/MODEL_CARD.md",
                "audit/licenses/cosyvoice3/LICENSE-weights.txt",
            ],
            "license_status": "CONDITIONAL PASS",
            "license_basis": "model_card_metadata",
            "dtype": cosy_m["dtype"],
            "attention_backend": "unknown (no FA2 installed)",
            "gpu_index": 0,
            "gpu_name": "Tesla T4",
            "peak_vram_allocated_mb": round(float(cosy_m["peak_alloc_mb"]), 3),
            "peak_vram_reserved_mb": round(float(cosy_m["peak_reserved_mb"]), 3),
            "peak_ram_mb": None,
            "runtime_seconds": round(float(cosy_m["gen_s"]), 3),
            "runtime_seconds_basis": "generation only; excludes model load and weight download",
            "rtf": round(float(cosy["steps"]["rtf"]), 6),
            "fps": None,
            "automatic_quality_status": "PASS",
            "human_review_status": "NEEDS HUMAN REVIEW",
            "runtime_status": "PASS",
            "production_status": "BLOCKED",
            "input_artifacts": [
                "audit/config/science_voice_script.txt",
                "audit/config/science_terms.json",
            ],
            "output_artifacts": ["audit/logs/kaggle/p0-cosy/v10/audit/results/cosyvoice3/out.wav"],
            "log_path": "audit/logs/kaggle/p0-cosy/v10/cosy_logs.txt",
            "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p0-cosyvoice3",
            "errors": None,
            "notes": "43 chunks; 602.28 s audio at 24 kHz mono; FP32 because the notebook did not pass fp16=True; reference voice Kokoro af_heart.",
            "checks": {
                "chunks": int(cosy["steps"]["chunking"]["chunks"]),
                "max_chars_per_chunk": int(cosy["steps"]["chunking"]["max_chars"]),
                "audio_duration_s": float(cosy["steps"]["audio_duration_s"]),
                "sample_rate_hz": int(cosy_m["sr"]),
                "samples": int(cosy_m["samples"]),
                "generation_seconds": round(float(cosy_m["gen_s"]), 3),
                "rtf": round(float(cosy["steps"]["rtf"]), 6),
                "reference_voice": cosy["steps"]["cloning_reference"],
            },
        },
        {
            "name": P0["rife"],
            "priority": "P0",
            "stage": "B",
            "version": "4.25",
            "source_url": "https://github.com/hzwer/Practical-RIFE",
            "revision": "bbfd2ea90910789a860ea3e2b32a240cd577b75e",
            "checkpoint_files": [],
            "checkpoint_sha256": [],
            "code_license": "MIT",
            "weight_license": "MIT (maintainer statement covers linked models)",
            "license_evidence": ["audit/licenses/practical-rife-4.25/LICENSE-code.txt"],
            "license_status": "PASS",
            "license_basis": "license_text",
            "dtype": None,
            "attention_backend": None,
            "gpu_index": None,
            "gpu_name": None,
            "peak_vram_allocated_mb": None,
            "peak_vram_reserved_mb": None,
            "peak_ram_mb": None,
            "runtime_seconds": None,
            "runtime_seconds_basis": "no inference reached",
            "rtf": None,
            "fps": None,
            "automatic_quality_status": "NOT TESTED",
            "human_review_status": "NEEDS HUMAN REVIEW",
            "runtime_status": "BLOCKED",
            "production_status": "BLOCKED",
            "input_artifacts": ["audit/config/image_video_prompts.json"],
            "output_artifacts": [],
            "log_path": "audit/logs/kaggle/p0-rife/v2/openmontage-p0-practical-rife-4-25.log",
            "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p0-practical-rife-4-25",
            "errors": "v1 and v2 CANCEL_ACKNOWLEDGED at ~90 s; CPU/GPU/GPU+net/uv/gdown diagnostics COMPLETE; cause not established.",
            "notes": "No retry beyond one documented recovery attempt (hard rule 45).",
            "checks": {
                "kernel_status": "CANCEL_ACKNOWLEDGED",
                "attempts": [
                    {"version": 1, "approx_seconds": 90},
                    {"version": 2, "approx_seconds": 94},
                ],
                "diagnostics": ["diag_cpu", "diag_gpu", "diag_gpu_net", "diag_uv", "diag_gdown"],
                "diagnostics_status": "COMPLETE",
                "cause": "not established",
            },
        },
        {
            "name": P0["esrgan"],
            "priority": "P0",
            "stage": "B",
            "version": "RealESRGAN_x4plus (release v0.1.0)",
            "source_url": "https://github.com/xinntao/Real-ESRGAN",
            "revision": "a4abfb2979a7bbff3f69f58f58ae324608821e27",
            "checkpoint_files": ["weights/RealESRGAN_x4plus.pth"],
            "checkpoint_sha256": ["4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1"],
            "code_license": "BSD-3-Clause",
            "weight_license": "NOT EXPLICIT (no statement for the exact .pth)",
            "license_evidence": [
                "audit/licenses/real-esrgan-x4plus/LICENSE-code.txt",
                "audit/licenses/real-esrgan-x4plus/RELEASE_ASSETS.json",
            ],
            "license_status": "FAIL",
            "license_basis": "license_text",
            "dtype": "FP32",
            "attention_backend": None,
            "gpu_index": 0,
            "gpu_name": "Tesla T4",
            "peak_vram_allocated_mb": None,
            "peak_vram_reserved_mb": None,
            "peak_vram_mib_nvidia_smi": int(esrgan["peak_vram_mib_nvidia_smi"]),
            "peak_ram_mb": None,
            "runtime_seconds": round(float(esrgan_step["duration_s"]), 3),
            "runtime_seconds_basis": "10 images in one CLI call; excludes install and weight download",
            "rtf": None,
            "fps": None,
            "automatic_quality_status": "PASS",
            "human_review_status": "NEEDS HUMAN REVIEW",
            "runtime_status": "PASS",
            "production_status": "BLOCKED",
            "input_artifacts": ["audit/fixtures/esrgan/inputs/frame_00.png"],
            "output_artifacts": [
                "audit/logs/kaggle/p0-esrgan/v2/audit/fixtures/esrgan/outputs/frame_00_out.png",
                "audit/logs/kaggle/p0-esrgan/v2/audit/fixtures/esrgan/outputs/frame_01_out.png",
                "audit/logs/kaggle/p0-esrgan/v2/audit/fixtures/esrgan/outputs/frame_02_out.png",
            ],
            "log_path": "audit/logs/kaggle/p0-esrgan/v2/esrgan_logs.txt",
            "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p0-real-esrgan-x4plus",
            "errors": None,
            "notes": "10/10 outputs 1024x1024 verified locally; peak VRAM from nvidia-smi (subprocess), not torch API.",
            "checks": {
                "images": int(esrgan["steps"]["validation"]["files"]),
                "input_size": "256x256",
                "output_size": "1024x1024",
                "seconds_per_image": round(float(esrgan_step["duration_s"]) / 10, 3),
                "peak_vram_source": esrgan["peak_vram_source"],
                "weights_bytes": int(esrgan["steps"]["weights"]["bytes"]),
                "weights_sha256": esrgan["steps"]["weights"]["sha256"],
            },
        },
    ]


def main() -> None:
    backup = AUDIT / "backups" / datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    backup.mkdir(parents=True, exist_ok=True)
    for name in ("results.json", "results/component_results.json"):
        src = AUDIT / name
        if src.exists():
            shutil.copy2(src, backup / Path(name).name)

    stage_b = {c["name"]: c for c in build_components()}

    results = read_json(AUDIT / "results.json")
    results["audit_timestamp_utc"] = NOW
    results["stage_a_timestamp_utc"] = "2026-11-13T04:21:09Z"
    results["stage_b_rebuilt_utc"] = NOW
    results["stage_b_rebuild_scope"] = (
        "Rebuilt only the five P0 component records from preserved Kaggle logs; "
        "Stage A records, license evidence and hashes are unchanged."
    )

    components = results["components"]
    replaced = 0
    for i, comp in enumerate(components):
        if comp["name"] in stage_b:
            components[i] = stage_b[comp["name"]]
            replaced += 1
    missing = sorted(set(stage_b) - {c["name"] for c in components})
    if missing:
        raise SystemExit(f"Stage B components missing from results.json: {missing}")

    results["kaggle"]["kernel_ids"] = [
        "forts845/openmontage-stage-a-env-smoke",
        "forts845/openmontage-p0-practical-rife-4-25",
        "forts845/openmontage-p0-ltx-video-2b-0-9-5",
        "forts845/openmontage-p0-flux2-klein-4b",
        "forts845/openmontage-p0-cosyvoice3",
        "forts845/openmontage-p0-real-esrgan-x4plus",
    ]
    results["kaggle"]["notebook_runs_scope"] = "Stage B (Phase 4 P0); Stage A run tracked separately"
    results["kaggle"]["stage_a_gpu_upper_bound_hours"] = 0.020082
    results["kaggle"]["estimated_gpu_hours_used"] = round(
        sum(r["gpu_upper_bound_hours"] for r in results["kaggle"]["notebook_runs"]), 4
    )

    results["unconfirmed_claims"] = [
        "Official Kaggle docs pages could not be fetched live (reCAPTCHA); quotes came from the search index of the same official URLs and must be re-checked from a browser.",
        "FINAL_PRODUCTION_DECISION was not found anywhere in the repository or its history.",
        "Weight SHA256 was not collected in Stage A; Stage B recorded it only for Real-ESRGAN x4plus (4fa0d38905f75ac06eb49a7951b426670021be3018265fd191d2125df9d682f1).",
        "Human quality acceptance is not provided and cannot be self-approved.",
        "Practical-RIFE: kernel CANCEL_ACKNOWLEDGED twice at ~90 s; cause not established; diagnostics (CPU/GPU/GPU+net/uv/gdown) all COMPLETE.",
        "CosyVoice/Whisper/Kokoro/DepthAnything license basis is model_card_metadata (conditional PASS), not an explicit weight license text.",
        "Real-ESRGAN x4plus weight license not explicit -> license FAIL.",
        "LTX/FLUX attention backend is UNKNOWN; no flash-attn installed and set_attn_implementation was unavailable.",
        "FLUX 23.6 s is per image; the three images took 23.6 + 21.4 + 21.1 = 66.0 s of generation time (model load 130.9 s excluded).",
    ]

    results["recommendations"] = {
        "status": "NOT PRODUCED",
        "reason": (
            "Stage B proves P0 runtime on a T4, but all five components remain blocked for production: "
            "human quality review is pending and Real-ESRGAN x4plus fails weight-license clearance."
        ),
    }

    results["human_review_items"] = [
        {
            "path": "audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_libx264.mp4",
            "what": "Stage A decode sanity only (test pattern)",
            "status": "PENDING HUMAN REVIEW (optional)",
        },
        {
            "path": "audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_h264_nvenc.mp4",
            "what": "Stage A decode sanity only (test pattern)",
            "status": "PENDING HUMAN REVIEW (optional)",
        },
        {
            "path": "audit/previews/stage_b/cosyvoice3_af_heart.mp3",
            "what": "voice naturalness, pronunciation, numbers/units, artifacts",
            "status": "PENDING HUMAN REVIEW",
        },
        {
            "path": "audit/previews/stage_b/flux_1.jpg",
            "what": "image scientific accuracy and artifacts (mitochondrion cutaway)",
            "status": "PENDING HUMAN REVIEW",
        },
        {
            "path": "audit/previews/stage_b/flux_2.jpg",
            "what": "image scientific accuracy and artifacts (JWST exoplanet)",
            "status": "PENDING HUMAN REVIEW",
        },
        {
            "path": "audit/previews/stage_b/flux_3.jpg",
            "what": "image scientific accuracy and artifacts (gravitational-wave observatory)",
            "status": "PENDING HUMAN REVIEW",
        },
        {
            "path": "audit/previews/stage_b/ltx_out.mp4",
            "what": "video stability, flicker, deformation, black/frozen frames",
            "status": "PENDING HUMAN REVIEW",
        },
        {
            "path": "audit/previews/stage_b/esrgan_frame_00_before.jpg",
            "what": "ESRGAN before/after: halos, textures, invented detail (frame 00)",
            "status": "PENDING HUMAN REVIEW",
        },
        {
            "path": "audit/previews/stage_b/esrgan_frame_01_after.jpg",
            "what": "ESRGAN before/after: halos, textures, invented detail (frame 01)",
            "status": "PENDING HUMAN REVIEW",
        },
        {
            "path": "audit/previews/stage_b/esrgan_frame_02_after.jpg",
            "what": "ESRGAN before/after: halos, textures, invented detail (frame 02)",
            "status": "PENDING HUMAN REVIEW",
        },
    ]

    (AUDIT / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    comp = read_json(AUDIT / "results/component_results.json")
    comp_names = {c["name"] for c in comp}
    for name, entry in stage_b.items():
        found = False
        for i, existing in enumerate(comp):
            if existing["name"] == name:
                comp[i] = entry
                found = True
                break
        if not found:
            if name not in comp_names:
                comp.append(entry)
    (RESULTS / "component_results.json").write_text(json.dumps(comp, indent=2) + "\n", encoding="utf-8")

    # Generated table, used verbatim in the report and summary.
    rows = [
        ("LTX-Video 2B v0.9.5", "PASS (Open RAIL-M)", "PASS", "FP16", "11033 MiB alloc / 11050 reserved", "62.47 s generation (49 frames)", "p0-ltx/v3/ltx_logs.txt"),
        ("FLUX.2 klein 4B", "PASS (Apache-2.0)", "PASS", "FP16", "7936 MiB alloc / 7948 reserved", "23.6 / 21.4 / 21.1 s per image; 66.0 s for 3 images", "p0-flux/v2/flux_logs.txt"),
        ("CosyVoice 3", "CONDITIONAL PASS (model-card metadata)", "PASS", "FP32", "3589.6 MiB alloc / 4264 reserved", "594.76 s generation / 602.28 s audio (RTF 0.988)", "p0-cosy/v10/cosy_logs.txt"),
        ("Practical-RIFE 4.25", "PASS (MIT)", "BLOCKED", "—", "—", "no inference (CANCEL_ACKNOWLEDGED at ~90 s, v1/v2)", "p0-rife/v2/openmontage-p0-practical-rife-4-25.log"),
        ("Real-ESRGAN x4plus", "FAIL (weight license not explicit)", "PASS", "FP32", "1041 MiB (nvidia-smi)", "16.6 s / 10 images", "p0-esrgan/v2/esrgan_logs.txt"),
    ]
    lines = [
        "| Component | License | Runtime | dtype | Peak VRAM | Time | Log |",
        "|---|---|---|---|---|---|---|",
    ]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    (RESULTS / "stage_b_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"rebuilt {NOW}: replaced={replaced}, components={len(components)}, comp_rows={len(comp)}")
    for c in stage_b.values():
        print(
            f"  {c['name']}: runtime={c['runtime_status']} dtype={c['dtype']} "
            f"seconds={c['runtime_seconds']} rtf={c['rtf']} vram={c['peak_vram_allocated_mb']}"
        )
    print(f"  FLUX per-image seconds: {stage_b[P0['flux']]['checks']['seconds_per_image']} "
          f"total={stage_b[P0['flux']]['runtime_seconds']} s")


if __name__ == "__main__":
    main()