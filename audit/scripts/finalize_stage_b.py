#!/usr/bin/env python3
"""Finalize Stage B artifacts without overwriting Stage A evidence."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
BK = AUDIT / "backups" / datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
BK.mkdir(parents=True, exist_ok=True)

for name in ("results.json", "results/component_results.json", "PRODUCTION_SMOKE_TEST_REPORT.md", "licenses/STATUS.json"):
    src = AUDIT / name
    if src.exists():
        dst = BK / Path(name).name
        shutil.copy2(src, dst)

RUNS = {
    "rife": {"dir": AUDIT / "logs/kaggle/p0-rife", "kernel": "forts845/openmontage-p0-practical-rife-4-25", "versions": [1, 2]},
    "ltx": {"dir": AUDIT / "logs/kaggle/p0-ltx/v3", "kernel": "forts845/openmontage-p0-ltx-video-2b-0-9-5", "versions": [3]},
    "flux": {"dir": AUDIT / "logs/kaggle/p0-flux/v2", "kernel": "forts845/openmontage-p0-flux2-klein-4b", "versions": [2]},
    "cosy": {"dir": AUDIT / "logs/kaggle/p0-cosy/v10", "kernel": "forts845/openmontage-p0-cosyvoice3", "versions": [10]},
    "esrgan": {"dir": AUDIT / "logs/kaggle/p0-esrgan/v2", "kernel": "forts845/openmontage-p0-real-esrgan-x4plus", "versions": [2]},
}

# --- licenses: license_basis + conditional PASS ---------------------------
MODEL_CARD_ONLY = {"cosyvoice3", "kokoro-82m", "whisper-large-v3-turbo", "depth-anything-v2-small", "video-depth-anything-small"}
status = json.loads((AUDIT / "licenses/STATUS.json").read_text())
for name, rec in status.items():
    if name in MODEL_CARD_ONLY:
        rec["license_basis"] = "model_card_metadata"
        rec["license_status"] = "CONDITIONAL PASS"
        rec["rationale"] = rec["rationale"] + " Weight license is known only from the model-card license field; no separate weight license file exists in the model repo."
        d = AUDIT / "licenses" / name
        f = d / "LICENSE-weights.txt"
        if not f.exists():
            f.write_text(
                f"{name}: no separate weight license file in the model repository.\n"
                "license_basis: model_card_metadata\n"
                "The model card declares the license; see MODEL_CARD.md and PROVENANCE.json.\n"
                "Status is CONDITIONAL PASS, not final PASS.\n",
                encoding="utf-8",
            )
    else:
        rec.setdefault("license_basis", "license_text")
    # mark weight license file when present
    f = AUDIT / "licenses" / name / "LICENSE-weights.txt"
    rec["weight_license_file"] = str(f.relative_to(ROOT)) if f.exists() else None
(AUDIT / "licenses/STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")

# --- stage B component results -------------------------------------------
def load_summary(key):
    d = RUNS[key]["dir"]
    for name in ("summary.json",):
        p = d / "audit/results" / {"rife": "practical-rife-4.25", "ltx": "ltx-video-2b-0.9.5", "flux": "flux2-klein-4b", "cosy": "cosyvoice3", "esrgan": "real-esrgan-x4plus"}[key] / name
        if p.exists():
            return json.loads(p.read_text())
    return None

s_ltx = load_summary("ltx") or {}
s_flux = load_summary("flux") or {}
s_cosy = load_summary("cosy") or {}
s_esr = load_summary("esrgan") or {}

stage_b = [
    {
        "name": "ltx-video-2b-0.9.5",
        "priority": "P0",
        "version": "0.9.5 (Lightricks/LTX-Video-0.9.5)",
        "source_url": "https://huggingface.co/Lightricks/LTX-Video-0.9.5",
        "revision": "e58e28c39631af4d1468ee57a853764e11c1d37e",
        "checkpoint_files": ["transformer/diffusion_pytorch_model.safetensors", "vae/diffusion_pytorch_model.safetensors", "text_encoder/model-*.safetensors"],
        "checkpoint_sha256": [],
        "code_license": "LTX-Video repo code license (Apache-2.0); see LICENSE-code.txt",
        "weight_license": "Open RAIL-M (commercial use with use restrictions)",
        "license_evidence": ["audit/licenses/ltx-video-2b-0.9.5/LICENSE-weights.txt"],
        "license_status": "PASS",
        "license_basis": "license_text",
        "dtype": "torch.float16",
        "attention_backend": "unknown (no FA2 installed; set_attn_implementation unavailable)",
        "gpu_index": 0,
        "gpu_name": "Tesla T4",
        "peak_vram_allocated_mb": 11033.0,
        "peak_vram_reserved_mb": 11050.0,
        "peak_ram_mb": None,
        "runtime_seconds": 62.47,
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
    },
    {
        "name": "flux2-klein-4b",
        "priority": "P0",
        "version": "FLUX.2 klein 4B",
        "source_url": "https://huggingface.co/black-forest-labs/FLUX.2-klein-4B",
        "revision": "e7b7dc27f91d",
        "checkpoint_files": ["transformer/*.safetensors", "vae/*.safetensors", "text_encoder/*.safetensors"],
        "checkpoint_sha256": [],
        "code_license": "Apache-2.0 (FLUX.2 repo)",
        "weight_license": "Apache-2.0",
        "license_evidence": ["audit/licenses/flux2-klein-4b/LICENSE-weights.txt"],
        "license_status": "PASS",
        "license_basis": "license_text",
        "dtype": "torch.float16",
        "attention_backend": "unknown (no FA2 installed)",
        "gpu_index": 0,
        "gpu_name": "Tesla T4",
        "peak_vram_allocated_mb": 7936.3,
        "peak_vram_reserved_mb": 7948.0,
        "peak_ram_mb": None,
        "runtime_seconds": 23.61,
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
        "notes": "3 prompts/seeds, 512x512, 4 steps, guidance 1.0; all PNG 512x512 RGB verified locally.",
    },
    {
        "name": "cosyvoice3",
        "priority": "P0",
        "version": "Fun-CosyVoice3-0.5B-2512",
        "source_url": "https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512",
        "revision": "29e01c4e8d00",
        "checkpoint_files": ["model.pt", "cosyvoice2.yaml", "hift.pt"],
        "checkpoint_sha256": [],
        "code_license": "Apache-2.0 (CosyVoice repo)",
        "weight_license": "Apache-2.0 (model-card metadata only)",
        "license_evidence": ["audit/licenses/cosyvoice3/MODEL_CARD.md", "audit/licenses/cosyvoice3/LICENSE-weights.txt"],
        "license_status": "CONDITIONAL PASS",
        "license_basis": "model_card_metadata",
        "dtype": "torch.float32",
        "attention_backend": "unknown (no FA2 installed)",
        "gpu_index": 0,
        "gpu_name": "Tesla T4",
        "peak_vram_allocated_mb": 3589.6,
        "peak_vram_reserved_mb": 4264.0,
        "peak_ram_mb": None,
        "runtime_seconds": 594.76,
        "rtf": 0.9875,
        "fps": None,
        "automatic_quality_status": "PASS",
        "human_review_status": "NEEDS HUMAN REVIEW",
        "runtime_status": "PASS",
        "production_status": "BLOCKED",
        "input_artifacts": ["audit/config/science_voice_script.txt", "audit/config/science_terms.json"],
        "output_artifacts": ["audit/logs/kaggle/p0-cosy/v10/audit/results/cosyvoice3/out.wav"],
        "log_path": "audit/logs/kaggle/p0-cosy/v10/cosy_logs.txt",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p0-cosyvoice3",
        "errors": None,
        "notes": "43 chunks; 602.28 s audio at 24 kHz mono; reference voice Kokoro af_heart (Apache-2.0 metadata, CONDITIONAL PASS).",
    },
    {
        "name": "practical-rife-4.25",
        "priority": "P0",
        "version": "4.25",
        "source_url": "https://github.com/hzwer/Practical-RIFE",
        "revision": "bbfd2ea90910789a860ea3e2b32a240cd577b75e",
        "checkpoint_files": ["train_log/flownet.pkl"],
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
    },
    {
        "name": "real-esrgan-x4plus",
        "priority": "P0",
        "version": "RealESRGAN_x4plus (release v0.1.0)",
        "source_url": "https://github.com/xinntao/Real-ESRGAN",
        "revision": "a4abfb2979a7",
        "checkpoint_files": ["weights/RealESRGAN_x4plus.pth"],
        "checkpoint_sha256": [],
        "code_license": "BSD-3-Clause",
        "weight_license": "NOT EXPLICIT (no statement for the exact .pth)",
        "license_evidence": ["audit/licenses/real-esrgan-x4plus/LICENSE-code.txt", "audit/licenses/real-esrgan-x4plus/RELEASE_ASSETS.json"],
        "license_status": "FAIL",
        "license_basis": "license_text",
        "dtype": "FP32",
        "attention_backend": None,
        "gpu_index": 0,
        "gpu_name": "Tesla T4",
        "peak_vram_allocated_mb": 1041,
        "peak_vram_reserved_mb": None,
        "peak_ram_mb": None,
        "runtime_seconds": 16.6,
        "rtf": None,
        "fps": None,
        "automatic_quality_status": "PASS",
        "human_review_status": "NEEDS HUMAN REVIEW",
        "runtime_status": "PASS",
        "production_status": "BLOCKED",
        "input_artifacts": ["audit/fixtures/esrgan/inputs/frame_00.png"],
        "output_artifacts": ["audit/logs/kaggle/p0-esrgan/v2/audit/fixtures/esrgan/outputs/frame_00_out.png"],
        "log_path": "audit/logs/kaggle/p0-esrgan/v2/esrgan_logs.txt",
        "kaggle_kernel_url": "https://www.kaggle.com/code/forts845/openmontage-p0-real-esrgan-x4plus",
        "errors": None,
        "notes": "10/10 outputs 1024x1024 verified locally; peak VRAM from nvidia-smi (subprocess), not torch API.",
    },
]

# --- update results.json --------------------------------------------------
res = json.loads((AUDIT / "results.json").read_text())
existing = {c["name"] for c in res["components"]}
for c in stage_b:
    if c["name"] not in existing:
        res["components"].append(c)
res["kaggle"]["notebook_runs"] = [
    {"kernel_id": "forts845/openmontage-p0-practical-rife-4-25", "version": 1, "status": "CANCEL_ACKNOWLEDGED", "url": "https://www.kaggle.com/code/forts845/openmontage-p0-practical-rife-4-25", "wall_seconds": 90, "gpu_upper_bound_hours": 0.05},
    {"kernel_id": "forts845/openmontage-p0-practical-rife-4-25", "version": 2, "status": "CANCEL_ACKNOWLEDGED", "url": "https://www.kaggle.com/code/forts845/openmontage-p0-practical-rife-4-25", "wall_seconds": 94, "gpu_upper_bound_hours": 0.052},
    {"kernel_id": "forts845/openmontage-p0-ltx-video-2b-0-9-5", "version": 3, "status": "COMPLETE", "url": "https://www.kaggle.com/code/forts845/openmontage-p0-ltx-video-2b-0-9-5", "wall_seconds": 317, "gpu_upper_bound_hours": 0.176},
    {"kernel_id": "forts845/openmontage-p0-flux2-klein-4b", "version": 2, "status": "COMPLETE", "url": "https://www.kaggle.com/code/forts845/openmontage-p0-flux2-klein-4b", "wall_seconds": 267, "gpu_upper_bound_hours": 0.148},
    {"kernel_id": "forts845/openmontage-p0-cosyvoice3", "version": 10, "status": "COMPLETE", "url": "https://www.kaggle.com/code/forts845/openmontage-p0-cosyvoice3", "wall_seconds": 904, "gpu_upper_bound_hours": 0.502},
    {"kernel_id": "forts845/openmontage-p0-real-esrgan-x4plus", "version": 2, "status": "COMPLETE", "url": "https://www.kaggle.com/code/forts845/openmontage-p0-real-esrgan-x4plus", "wall_seconds": 142, "gpu_upper_bound_hours": 0.079},
]
res["kaggle"]["estimated_gpu_hours_used"] = round(sum(r["gpu_upper_bound_hours"] for r in res["kaggle"]["notebook_runs"]), 4)
res["unconfirmed_claims"] = list(dict.fromkeys(res["unconfirmed_claims"] + [
    "Practical-RIFE: kernel CANCEL_ACKNOWLEDGED twice at ~90 s; cause not established; diagnostics (CPU/GPU/GPU+net/uv/gdown) all COMPLETE.",
    "CosyVoice/Whisper/Kokoro/DepthAnything license basis is model_card_metadata (conditional PASS), not an explicit weight license text.",
    "Real-ESRGAN x4plus weight license not explicit -> license FAIL.",
    "LTX/FLUX attention backend is UNKNOWN; no flash-attn installed and set_attn_implementation was unavailable.",
]))
res["human_review_items"] = res.get("human_review_items", []) + [
    {"path": "audit/logs/kaggle/p0-ltx/v3/audit/results/ltx-video-2b-0.9.5/out.mp4", "what": "video stability/flicker/deformation", "status": "PENDING HUMAN REVIEW"},
    {"path": "audit/logs/kaggle/p0-flux/v2/audit/results/flux2-klein-4b/flux_1.png", "what": "image scientific accuracy/artifacts", "status": "PENDING HUMAN REVIEW"},
    {"path": "audit/logs/kaggle/p0-cosy/v10/audit/results/cosyvoice3/out.wav", "what": "voice naturalness/pronunciation/numbers/units", "status": "PENDING HUMAN REVIEW"},
    {"path": "audit/logs/kaggle/p0-esrgan/v2/audit/fixtures/esrgan/outputs/frame_00_out.png", "what": "ESRGAN halos/textures", "status": "PENDING HUMAN REVIEW"},
]
(AUDIT / "results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

# --- component_results.json ----------------------------------------------
comp = json.loads((AUDIT / "results/component_results.json").read_text())
names = {c["name"] for c in comp}
for c in stage_b:
    if c["name"] not in names:
        comp.append(c)
(AUDIT / "results/component_results.json").write_text(json.dumps(comp, indent=2), encoding="utf-8")

# --- report append --------------------------------------------------------
report = AUDIT / "PRODUCTION_SMOKE_TEST_REPORT.md"
addition = """

---

# Stage B (2026-11-13) — P0 runtime + Phase 6 fixtures

## B1. Scope
Phase 4 (P0) and Phase 6 fixtures. Stage A results are unchanged.

## B2. Phase 6 fixtures
- `audit/config/science_voice_script.txt` — 1491 words (~9.9 min at 150 wpm).
- `audit/config/science_terms.json` — 28 terms with variants and match rules.
- `audit/config/image_video_prompts.json` — 3 image prompts/seeds (424242, 202607, 271828), video prompt/seed 424242.
- SHA256 recorded in `audit/config/SHA256SUMS.txt`.

## B3. P0 results

| Component | License | Runtime | dtype | Peak VRAM | Time | Log |
|---|---|---|---|---|---|---|
| LTX-Video 2B v0.9.5 | PASS (Open RAIL-M) | PASS | FP16 | 11033 MiB alloc / 11050 reserved | 62.47 s / 49 frames | audit/logs/kaggle/p0-ltx/v3/ltx_logs.txt |
| FLUX.2 klein 4B | PASS (Apache-2.0) | PASS | FP16 | 7936 MiB alloc / 7948 reserved | 23.6 s / image (3 images) | audit/logs/kaggle/p0-flux/v2/flux_logs.txt |
| CosyVoice 3 | CONDITIONAL PASS (model-card metadata) | PASS | FP32 | 3589.6 MiB alloc / 4264 reserved | 594.76 s / 602.28 s audio (RTF 0.988) | audit/logs/kaggle/p0-cosy/v10/cosy_logs.txt |
| Practical-RIFE 4.25 | PASS (MIT) | BLOCKED | — | — | — | audit/logs/kaggle/p0-rife/v2/openmontage-p0-practical-rife-4-25.log |
| Real-ESRGAN x4plus | FAIL (weight license not explicit) | PASS | FP32 | 1041 MiB (nvidia-smi) | 16.6 s / 10 images | audit/logs/kaggle/p0-esrgan/v2/esrgan_logs.txt |

## B4. Failures/blockers
- Practical-RIFE: v1 and v2 CANCEL_ACKNOWLEDGED at ~90 s. CPU-only, GPU-only, GPU+internet, uv+torch and gdown diagnostics all COMPLETE. Cause not established. No further retries.
- Real-ESRGAN: runtime PASS but weight license FAIL.
- CosyVoice: license is model-card metadata only -> CONDITIONAL PASS.
- Attention backend for LTX/FLUX is UNKNOWN (no flash-attn installed).

## B5. GPU budget
Stage B upper bound: 0.05 + 0.052 + 0.176 + 0.148 + 0.502 + 0.079 = 1.007 GPU-hours (wall x GPUs). Quota-accounted estimate ~0.50 h (2xT4 = 1 h per wall hour). No stage limit of 24 h approached.

## B6. Production gate
No component is production-approved: human quality review is pending for all; Real-ESRGAN also fails license.
"""
with report.open("a", encoding="utf-8") as fh:
    fh.write(addition)

# --- stage B summary ------------------------------------------------------
summary = f"""# STAGE B SUMMARY

- Stage: B (Phase 4 P0 + Phase 6 fixtures)
- UTC: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
- Repo commit: 185af2eb8d4a18825219677612f9b6458702f122 (Stage A base)
- Kaggle CLI: 2.2.5; account forts845
- Status: PASS for LTX, FLUX, CosyVoice, ESRGAN runtime; RIFE BLOCKED; licenses: 1 FAIL, 1 CONDITIONAL PASS, 3 PASS.
- GPU used (upper bound): 1.007 GPU-hours; quota-accounted ~0.50 h.
- Blockers:
  - Practical-RIFE: CANCEL_ACKNOWLEDGED at ~90 s (v1, v2); cause not established; diagnostics complete.
  - Real-ESRGAN x4plus: weight license not explicit -> license FAIL.
  - CosyVoice/Kokoro/Whisper/DepthAnything: license basis model_card_metadata -> CONDITIONAL PASS.
  - LTX/FLUX attention backend UNKNOWN.
- Next stage preconditions:
  - Human quality review of LTX video, FLUX images, CosyVoice audio, ESRGAN images.
  - Real-ESRGAN weight license clarification or replacement (license exception requires human approval).
  - RIFE investigation in Kaggle web UI before any further GPU attempt.
- Evidence: audit/PRODUCTION_SMOKE_TEST_REPORT.md (Stage B section), audit/results.json, audit/results/component_results.json.
"""
(AUDIT / "STAGE_B_SUMMARY.md").write_text(summary, encoding="utf-8")
print("stage B finalize done")