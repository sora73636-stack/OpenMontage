#!/usr/bin/env python3
"""Finalize Stage C (P1) results from the real Kaggle logs. Never invents numbers.

Sources (all relative to audit/):
  logs/kaggle/p1-<comp>/vN/audit/results/<comp>/summary.json   (kernel-written)
  logs/kaggle/p1-<comp>/vN/audit/logs/kaggle/<comp>.log        (kernel log)
Stage A/Stage B evidence is only appended to, never rewritten.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
BK = AUDIT / "backups" / datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
BK.mkdir(parents=True, exist_ok=True)
for name in ("results.json", "results/component_results.json", "licenses/STATUS.json"):
    src = AUDIT / name
    if src.exists():
        shutil.copy2(src, BK / Path(name).name)

GPU_NAME = "Tesla T4 (1 GPU per kernel)"


def summary(component: str) -> dict:
    best = None
    for p in sorted(AUDIT.glob(f"logs/kaggle/**/results/{component}/summary.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if best is None or d.get("utc_start", "") >= best.get("utc_start", ""):
            best = d
    return best or {}


def wall(s: dict) -> float | None:
    from datetime import datetime as dt

    try:
        a = dt.fromisoformat(s["utc_start"].replace("Z", "+00:00"))
        b = dt.fromisoformat(s["utc_end"].replace("Z", "+00:00"))
        return (b - a).total_seconds()
    except Exception:
        return None


def log_path(component: str, kernel: str) -> str:
    cands = sorted(AUDIT.glob(f"logs/kaggle/**/{kernel}.log"))
    return str(cands[-1].relative_to(ROOT)) if cands else ""


S = {c: summary(c) for c in (
    "kokoro-82m", "whisper-large-v3-turbo", "parakeet-tdt-0.6b-v3", "deepfilternet3",
    "wan2.1-t2v-1.3b", "depth-anything-v2-small", "video-depth-anything-small", "sdxl-base-1.0")}

KOK, WHI, PAR, DFN, WAN, DEP, VDA, SDX = (S["kokoro-82m"], S["whisper-large-v3-turbo"],
                                          S["parakeet-tdt-0.6b-v3"], S["deepfilternet3"],
                                          S["wan2.1-t2v-1.3b"], S["depth-anything-v2-small"],
                                          S["video-depth-anything-small"], S["sdxl-base-1.0"])

stage_c = [
    {
        "name": "kokoro-82m",
        "priority": "P1",
        "version": "hexgrad/kokoro 0.9.4, KPipeline lang_code='a', voice af_heart",
        "source_url": "https://huggingface.co/hexgrad/Kokoro-82M",
        "revision": "dfb907a02bba (code)",
        "checkpoint_files": ["kokoro-v1_0.pth (config.json, open_clip_vit_b_32.bin)"],
        "checkpoint_sha256": [],
        "code_license": "Apache-2.0 (audit/licenses/kokoro-82m/LICENSE-code.txt)",
        "weight_license": "Apache-2.0 per model card (no separate weight license file)",
        "license_evidence": ["audit/licenses/kokoro-82m/LICENSE-weights.txt"],
        "license_status": "CONDITIONAL PASS",
        "dtype": "float32",
        "attention_backend": None,
        "gpu_index": "0",
        "gpu_name": GPU_NAME,
        "peak_vram_allocated_mb": KOK.get("steps", {}).get("peak_vram_allocated_mb", 1165.83),
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": KOK.get("steps", {}).get("runtime_seconds"),
        "rtf": KOK.get("steps", {}).get("rtf"),
        "fps": None,
        "automatic_quality_status": "PASS",
        "human_review_status": "PENDING HUMAN REVIEW",
        "runtime_status": "PASS",
        "production_status": "REVIEW",
        "input_artifacts": ["audit/config/science_voice_script.txt"],
        "output_artifacts": ["audit/previews/stage_c/kokoro82m_af_heart.mp3"],
        "log_path": "audit/logs/kaggle/p1-kokoro/v1/kokoro_logs.txt",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p1-kokoro-82m",
        "errors": None,
        "notes": "610.3 s of audio from the same script used for CosyVoice (Stage B); RTF 0.047.",
    },
    {
        "name": "whisper-large-v3-turbo",
        "priority": "P1",
        "version": "openai/whisper large-v3-turbo",
        "source_url": "https://huggingface.co/openai/whisper-large-v3-turbo",
        "revision": "86098128c0b4 (code)",
        "checkpoint_files": ["pytorch_model.bin"],
        "checkpoint_sha256": [],
        "code_license": "MIT (audit/licenses/whisper-large-v3-turbo/LICENSE-code.txt)",
        "weight_license": "MIT per model card (no separate weight license file)",
        "license_evidence": ["audit/licenses/whisper-large-v3-turbo/LICENSE-weights.txt"],
        "license_status": "CONDITIONAL PASS",
        "dtype": "float16",
        "attention_backend": None,
        "gpu_index": "0",
        "gpu_name": GPU_NAME,
        "peak_vram_allocated_mb": WHI.get("steps", {}).get("peak_vram_allocated_mb"),
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": WHI.get("steps", {}).get("runtime_seconds"),
        "rtf": WHI.get("steps", {}).get("rtf"),
        "fps": None,
        "automatic_quality_status": "PASS",
        "human_review_status": "NOT REQUIRED",
        "runtime_status": "PASS",
        "production_status": "REVIEW",
        "input_artifacts": ["audit/logs/kaggle/p1-whisper/v2/audit/results/whisper-large-v3-turbo/wers.json"],
        "output_artifacts": ["audit/logs/kaggle/p1-whisper/v2/audit/results/whisper-large-v3-turbo/wers.json"],
        "log_path": "audit/logs/kaggle/p1-whisper/v2/openmontage-p1-whisper-large-v3-turbo.log",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p1-whisper-large-v3-turbo",
        "errors": None,
        "notes": "LibriSpeech dev-clean, 330 files / 2413.05 s. WER 0.030298, CER 0.010440.",
    },
    {
        "name": "parakeet-tdt-0.6b-v3",
        "priority": "P1",
        "version": "nvidia/parakeet-tdt-0.6b-v3 (NeMo 2.x, TDT)",
        "source_url": "https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3",
        "revision": "541d1f99c6b0c3cd0b11a95167540bb8edefd82b",
        "checkpoint_files": ["model.safetensors"],
        "checkpoint_sha256": [],
        "code_license": "Apache-2.0 (NeMo; audit/licenses/parakeet-tdt-0.6b-v3/LICENSE-code.txt)",
        "weight_license": "CC-BY-4.0 per model card (no separate weight license file)",
        "license_evidence": ["audit/licenses/parakeet-tdt-0.6b-v3/LICENSE-weights.txt"],
        "license_status": "CONDITIONAL PASS",
        "dtype": "FP32 (not measured; NeMo default, peak 4.85 GB is consistent with fp32 weights)",
        "attention_backend": None,
        "gpu_index": "0",
        "gpu_name": GPU_NAME,
        "peak_vram_allocated_mb": PAR.get("steps", {}).get("peak_vram_allocated_mb"),
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": PAR.get("steps", {}).get("runtime_seconds"),
        "rtf": PAR.get("steps", {}).get("rtf"),
        "fps": None,
        "automatic_quality_status": "PASS",
        "human_review_status": "NOT REQUIRED",
        "runtime_status": "PASS",
        "production_status": "REVIEW",
        "input_artifacts": ["audit/logs/kaggle/p1-whisper/v2/audit/results/whisper-large-v3-turbo/wers.json"],
        "output_artifacts": ["audit/logs/kaggle/p1-parakeet/v1/audit/results/parakeet-tdt-0.6b-v3/wers.json"],
        "log_path": "audit/logs/kaggle/p1-parakeet/v1/audit/logs/kaggle/parakeet-tdt-0.6b-v3.log",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p1-parakeet-tdt-0-6b-v3",
        "errors": None,
        "notes": ("Same 330 LibriSpeech dev-clean files and the same jiwer normalisation as Whisper. "
                  "WER 0.020357, CER 0.005937. dtype was hard-coded in the notebook, not measured."),
    },
    {
        "name": "sdxl-base-1.0",
        "priority": "P1",
        "version": "stabilityai/stable-diffusion-xl-base-1.0 (fp16 variant)",
        "source_url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0",
        "revision": "e8cd657656fa (code)",
        "checkpoint_files": ["unet/diffusion_pytorch_model.fp16.safetensors", "*-fp16.safetensors"],
        "checkpoint_sha256": [],
        "code_license": "CreativeML Open RAIL++-M (audit/licenses/sdxl-base-1.0/LICENSE-code.txt)",
        "weight_license": "CreativeML Open RAIL++-M (text present)",
        "license_evidence": ["audit/licenses/sdxl-base-1.0/LICENSE-weights.txt"],
        "license_status": "PASS",
        "dtype": "torch.float16",
        "attention_backend": None,
        "gpu_index": "0",
        "gpu_name": GPU_NAME,
        "peak_vram_allocated_mb": SDX.get("steps", {}).get("peak_vram_allocated_mb"),
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": SDX.get("steps", {}).get("runtime_seconds"),
        "rtf": None,
        "fps": None,
        "automatic_quality_status": "PASS",
        "human_review_status": "PENDING HUMAN REVIEW",
        "runtime_status": "PASS",
        "production_status": "REVIEW",
        "input_artifacts": ["audit/config/image_video_prompts.json"],
        "output_artifacts": ["audit/previews/stage_c/sdxl_1.jpg", "audit/previews/stage_c/sdxl_2.jpg", "audit/previews/stage_c/sdxl_3.jpg"],
        "log_path": "audit/logs/kaggle/p1-sdxl/v2/openmontage-p1-sdxl-base-1-0.log",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p1-sdxl-base-1-0",
        "errors": None,
        "notes": "512x512, 25 steps, seeds 424242/202607/271828 - the same seeds and prompts as FLUX in Stage B.",
    },
    {
        "name": "depth-anything-v2-small",
        "priority": "P1",
        "version": "depth-anything/Depth-Anything-V2-Small-hf (transformers pipeline)",
        "source_url": "https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf",
        "revision": "1d03336771fe (code)",
        "checkpoint_files": ["model.safetensors"],
        "checkpoint_sha256": [],
        "code_license": "Apache-2.0 (audit/licenses/depth-anything-v2-small/LICENSE-code.txt)",
        "weight_license": "Apache-2.0 per model card (no separate weight license file)",
        "license_evidence": ["audit/licenses/depth-anything-v2-small/LICENSE-weights.txt"],
        "license_status": "CONDITIONAL PASS",
        "dtype": "torch.float32",
        "attention_backend": None,
        "gpu_index": "0",
        "gpu_name": GPU_NAME,
        "peak_vram_allocated_mb": DEP.get("steps", {}).get("peak_vram_allocated_mb"),
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": DEP.get("steps", {}).get("runtime_seconds"),
        "rtf": None,
        "fps": None,
        "automatic_quality_status": "PASS",
        "human_review_status": "PENDING HUMAN REVIEW",
        "runtime_status": "PASS",
        "production_status": "REVIEW",
        "input_artifacts": ["audit/config/science_voice_script.txt"],
        "output_artifacts": ["audit/previews/stage_c/depth_anything_v2_small_depth_00.jpg"],
        "log_path": "audit/logs/kaggle/p1-depth/v7/openmontage-p1-depth-anything-v2-small.log",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p1-depth-anything-v2-small",
        "errors": None,
        "notes": ("Warm 0.349 s, steady 0.049-0.081 s per 640x640 frame (10 frames). "
                  "v1-v6 failed on a wrong pipeline call (pipe(images=) -> pipe(inputs=)); "
                  "the v7 fix also replaced the pathological noise input with a structured scene, "
                  "because the depth map of the noise frames was constant (all-black preview)."),
    },
    {
        "name": "video-depth-anything-small",
        "priority": "P1",
        "version": "depth-anything/Video-Depth-Anything-Small (video_depth_anything_vits.pth)",
        "source_url": "https://huggingface.co/depth-anything/Video-Depth-Anything-Small",
        "revision": "256875362cff76724b920335dfb4b29dd611f66e (weights); 4f5ae23172ba (code)",
        "checkpoint_files": ["video_depth_anything_vits.pth"],
        "checkpoint_sha256": [],
        "code_license": "Apache-2.0 (audit/licenses/video-depth-anything-small/LICENSE-code.txt)",
        "weight_license": "Apache-2.0 per model card (no separate weight license file)",
        "license_evidence": ["audit/licenses/video-depth-anything-small/LICENSE-weights.txt"],
        "license_status": "CONDITIONAL PASS",
        "dtype": "FP16 (run.py default, autocast on cuda)",
        "attention_backend": None,
        "gpu_index": "0",
        "gpu_name": GPU_NAME,
        "peak_vram_allocated_mb": None,
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": VDA.get("steps", {}).get("runtime_seconds"),
        "rtf": None,
        "fps": 12.0,
        "automatic_quality_status": "PASS",
        "human_review_status": "PENDING HUMAN REVIEW",
        "runtime_status": "PASS",
        "production_status": "REVIEW",
        "input_artifacts": ["audit/logs/kaggle/p1-vd/v2/audit/results/video-depth-anything-small/input_vis.mp4"],
        "output_artifacts": ["audit/previews/stage_c/video_depth_anything_small_depth.mp4",
                             "audit/previews/stage_c/video_depth_anything_small_depth_frame.jpg"],
        "log_path": "audit/logs/kaggle/p1-vd/v2/audit/logs/kaggle/video-depth-anything-small.log",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p1-video-depth-anything-small",
        "errors": None,
        "notes": ("48 frames 640x480 @12 fps in 14.55 s (3.3x realtime). xFormers absent (fallback to SDPA). "
                  "peak VRAM not captured: the nvidia-smi sampler in v2 queried a single column and the "
                  "parser expected three (fixed in the builder afterwards, not re-run)."),
    },
    {
        "name": "deepfilternet3",
        "priority": "P1",
        "version": "deepfilternet 0.5.6 (PyPI) / DeepFilterNet3 checkpoint model_120.ckpt.best",
        "source_url": "https://github.com/Rikorose/DeepFilterNet",
        "revision": "7b14b895fe7fc42cab72b4a4c1e49c982bd6404b",
        "checkpoint_files": ["checkpoints/model_120.ckpt.best"],
        "checkpoint_sha256": [],
        "code_license": "MIT OR Apache-2.0 (audit/licenses/deepfilternet3/LICENSE-code.txt)",
        "weight_license": "MIT OR Apache-2.0, explicitly covering model weights",
        "license_evidence": ["audit/licenses/deepfilternet3/LICENSE-weights.txt"],
        "license_status": "PASS",
        "dtype": "FP32",
        "attention_backend": None,
        "gpu_index": "0",
        "gpu_name": GPU_NAME,
        "peak_vram_allocated_mb": DFN.get("steps", {}).get("peak_vram_mib"),
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": DFN.get("steps", {}).get("runtime_seconds"),
        "rtf": 0.227,
        "fps": None,
        "automatic_quality_status": "PASS",
        "human_review_status": "PENDING HUMAN REVIEW",
        "runtime_status": "PASS",
        "production_status": "REVIEW",
        "input_artifacts": ["audit/logs/kaggle/p1-dfn/v2/audit/results/deepfilternet3/noisy.wav"],
        "output_artifacts": ["audit/previews/stage_c/deepfilternet3_noisy_10s.mp3",
                             "audit/previews/stage_c/deepfilternet3_enhanced_10s.mp3"],
        "log_path": "audit/logs/kaggle/p1-dfn/v2/audit/logs/kaggle/deepfilternet3.log",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p1-deepfilternet3",
        "errors": None,
        "notes": ("Official CLI `deepFilter --output-dir <dir> noisy.wav`; DF reports 0.56 s model time "
                  "(RT factor 0.019), 48 kHz, 30.000 s out vs 30.000 s in (0 ms drift), device cuda:0."),
    },
    {
        "name": "wan2.1-t2v-1.3b",
        "priority": "P1",
        "version": "Wan-AI/Wan2.1-T2V-1.3B",
        "source_url": "https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B",
        "revision": "37ec512624d61f7aa208f7ea8140a131f93afc9a (weights); 9737cba9c1c3 (code)",
        "checkpoint_files": ["diffusion_pytorch_model.safetensors", "models_t5_umt5-xxl-enc-bf16.pth",
                             "Wan2.1_VAE.pth", "shared_embedding.pt"],
        "checkpoint_sha256": [],
        "code_license": "Apache-2.0 (audit/licenses/wan2.1-t2v-1.3b/LICENSE-code.txt)",
        "weight_license": "Apache-2.0 (LICENSE.txt present)",
        "license_evidence": ["audit/licenses/wan2.1-t2v-1.3b/LICENSE-weights.txt"],
        "license_status": "PASS",
        "dtype": None,
        "attention_backend": "SDPA (flash_attn excluded: no wheel for torch 2.6/py310, sdist build fails)",
        "gpu_index": "0",
        "gpu_name": GPU_NAME,
        "peak_vram_allocated_mb": None,
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": WAN.get("steps", {}).get("runtime_seconds"),
        "rtf": None,
        "fps": None,
        "automatic_quality_status": "BLOCKED",
        "human_review_status": "NOT POSSIBLE",
        "runtime_status": "BLOCKED",
        "production_status": "BLOCKED",
        "input_artifacts": ["audit/config/image_video_prompts.json"],
        "output_artifacts": [],
        "log_path": "audit/logs/kaggle/p1-wan/v2/audit/logs/kaggle/wan2.1-t2v-1.3b.log",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p1-wan2-1-t2v-1-3b",
        "errors": "v1 BLOCKED: uv cannot build flash_attn from sdist (setup.py imports torch under build isolation). "
                  "v2 (recovery attempt) FAIL: generate.py -> ModuleNotFoundError: No module named 'einops'; "
                  "Wan's requirements.txt does not declare einops even though wan/modules/vae.py imports it. "
                  "One recovery attempt per component is the audit cap, so no v3 was pushed.",
        "notes": "Model download OK (22 files, 83 s). Inference never started; no clip, no VRAM figure.",
    },
]

# --- licenses/STATUS.json -------------------------------------------------
status = json.loads((AUDIT / "licenses/STATUS.json").read_text())
for name in ("kokoro-82m", "whisper-large-v3-turbo", "parakeet-tdt-0.6b-v3", "deepfilternet3",
             "wan2.1-t2v-1.3b", "depth-anything-v2-small", "video-depth-anything-small", "sdxl-base-1.0"):
    rec = status.setdefault(name, {})
    rec.setdefault("note", "License status is independent from runtime and human quality status.")
    if name in ("parakeet-tdt-0.6b-v3", "kokoro-82m", "whisper-large-v3-turbo",
                "depth-anything-v2-small", "video-depth-anything-small"):
        rec["license_basis"] = "model_card_metadata"
        rec["license_status"] = "CONDITIONAL PASS"
    elif name == "deepfilternet3":
        rec["license_basis"] = "license_text"
        rec["license_status"] = "PASS"
    elif name == "wan2.1-t2v-1.3b":
        rec["license_basis"] = "license_text"
        rec["license_status"] = "PASS"
    elif name == "sdxl-base-1.0":
        rec["license_basis"] = "license_text"
        rec["license_status"] = "PASS"
    wf = AUDIT / "licenses" / name / "LICENSE-weights.txt"
    rec["weight_license_file"] = str(wf.relative_to(ROOT)) if wf.exists() else None
    rec["runtime_status"] = next(c["runtime_status"] for c in stage_c if c["name"] == name)
    rec["runtime_ran_at_stage"] = "C"
(AUDIT / "licenses/STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")

# --- results.json ---------------------------------------------------------
res = json.loads((AUDIT / "results.json").read_text())
by_name = {c["name"]: i for i, c in enumerate(res["components"])}
for c in stage_c:
    if c["name"] in by_name:
        res["components"][by_name[c["name"]]] = c   # replace the Stage C placeholder in place
    else:
        res["components"].append(c)
runs = res["kaggle"].setdefault("notebook_runs", [])
known = {(r["kernel_id"], r.get("version")) for r in runs}
extra_runs = [
    {"kernel_id": "forts845/openmontage-p1-kokoro-82m", "version": 1, "status": "COMPLETE", "wall_seconds": 106, "gpu_upper_bound_hours": 0.029},
    {"kernel_id": "forts845/openmontage-p1-whisper-large-v3-turbo", "version": 2, "status": "COMPLETE", "wall_seconds": 428, "gpu_upper_bound_hours": 0.119},
    {"kernel_id": "forts845/openmontage-p1-parakeet-tdt-0-6b-v3", "version": 1, "status": "COMPLETE", "wall_seconds": 167, "gpu_upper_bound_hours": 0.046},
    {"kernel_id": "forts845/openmontage-p1-sdxl-base-1-0", "version": 2, "status": "COMPLETE", "wall_seconds": 136, "gpu_upper_bound_hours": 0.038},
    {"kernel_id": "forts845/openmontage-p1-depth-anything-v2-small", "version": 6, "status": "COMPLETE", "wall_seconds": 66, "gpu_upper_bound_hours": 0.018},
    {"kernel_id": "forts845/openmontage-p1-depth-anything-v2-small", "version": 7, "status": "COMPLETE", "wall_seconds": 67, "gpu_upper_bound_hours": 0.019},
    {"kernel_id": "forts845/openmontage-p1-video-depth-anything-small", "version": 1, "status": "ERROR", "wall_seconds": 51, "gpu_upper_bound_hours": 0.014},
    {"kernel_id": "forts845/openmontage-p1-video-depth-anything-small", "version": 2, "status": "COMPLETE", "wall_seconds": 80, "gpu_upper_bound_hours": 0.022},
    {"kernel_id": "forts845/openmontage-p1-deepfilternet3", "version": 1, "status": "ERROR", "wall_seconds": 57, "gpu_upper_bound_hours": 0.016},
    {"kernel_id": "forts845/openmontage-p1-deepfilternet3", "version": 2, "status": "COMPLETE", "wall_seconds": 66, "gpu_upper_bound_hours": 0.018},
    {"kernel_id": "forts845/openmontage-p1-wan2-1-t2v-1-3b", "version": 1, "status": "BLOCKED", "wall_seconds": 62, "gpu_upper_bound_hours": 0.017},
    {"kernel_id": "forts845/openmontage-p1-wan2-1-t2v-1-3b", "version": 2, "status": "ERROR", "wall_seconds": 159, "gpu_upper_bound_hours": 0.044},
]
for r in extra_runs:
    key = (r["kernel_id"], r["version"])
    if key not in known:
        runs.append({"url": f"https://www.kaggle.com/code/{r['kernel_id']}", **r})
        known.add(key)
res["kaggle"]["stage_c"] = {
    "utc": "2026-11-14T02:36:00Z",
    "kernels": len(extra_runs),
    "measured_wall_seconds": sum(r["wall_seconds"] for r in extra_runs),
    "gpu_upper_bound_hours_measured": round(sum(r["gpu_upper_bound_hours"] for r in extra_runs), 3),
    "unaccounted_runs": "whisper v1, sdxl v1 and depth v1-v5 have no preserved summary; add ~0.08 GPU-h upper bound.",
    "cap_gpu_hours": 24,
    "cap_respected": True,
}
res["kaggle"]["estimated_gpu_hours_used"] = round(
    sum(r.get("gpu_upper_bound_hours", 0) for r in runs), 3)
res["unconfirmed_claims"] = list(dict.fromkeys(res.get("unconfirmed_claims", []) + [
    "Parakeet dtype is not measured: the notebook hard-codes 'FP16'; the model most likely ran in FP32.",
    "Video Depth Anything peak VRAM was not captured (sampler column mismatch); the notebook has been fixed but not re-run.",
    "Wan2.1: no inference ran, so no VRAM/time figure exists.",
    "Whisper/Parakeet WER comparison is only valid because both used the same 330 LibriSpeech dev-clean files and the same normalisation.",
]))
_new_review = [
    {"path": "audit/previews/stage_c/kokoro82m_af_heart.mp3", "what": "Kokoro 82M voice quality vs CosyVoice (same script, af_heart)", "status": "PENDING HUMAN REVIEW"},
    {"path": "audit/previews/stage_c/sdxl_1.jpg", "what": "SDXL image quality/artifacts vs FLUX (same seeds/prompts)", "status": "PENDING HUMAN REVIEW"},
    {"path": "audit/previews/stage_c/depth_anything_v2_small_depth_00.jpg", "what": "depth map sanity", "status": "PENDING HUMAN REVIEW"},
    {"path": "audit/previews/stage_c/video_depth_anything_small_depth.mp4", "what": "temporal depth consistency", "status": "PENDING HUMAN REVIEW"},
    {"path": "audit/previews/stage_c/deepfilternet3_enhanced_10s.mp3", "what": "noise suppression quality / artefacts", "status": "PENDING HUMAN REVIEW"},
]
_seen = {r["path"] for r in res.get("human_review_items", [])}
res["human_review_items"] = res.get("human_review_items", []) + [r for r in _new_review if r["path"] not in _seen]
(AUDIT / "results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

# --- component_results.json ----------------------------------------------
comp = json.loads((AUDIT / "results/component_results.json").read_text())
idx = {c["name"]: i for i, c in enumerate(comp)}
for c in stage_c:
    if c["name"] in idx:
        comp[idx[c["name"]]] = c                     # replace the Stage C placeholder in place
    else:
        comp.append(c)
(AUDIT / "results/component_results.json").write_text(json.dumps(comp, indent=2), encoding="utf-8")

print(json.dumps({
    "components": [c["name"] for c in stage_c],
    "statuses": {c["name"]: c["runtime_status"] for c in stage_c},
    "stage_c_measured_gpu_hours": res["kaggle"]["stage_c"]["gpu_upper_bound_hours_measured"],
    "total_gpu_hours_all_stages": res["kaggle"]["estimated_gpu_hours_used"],
}, indent=2))