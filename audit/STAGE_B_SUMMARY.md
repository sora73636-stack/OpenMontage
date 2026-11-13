# STAGE B SUMMARY

- Stage: B (Phase 4 P0 + Phase 6 fixtures)
- UTC: 2026-11-13T06:58:26Z (finalized); results JSON rebuilt from preserved logs at 2026-11-13T10:51:23Z
- Repo commit: 185af2eb8d4a18825219677612f9b6458702f122 (Stage A base; Stage B evidence commit 392f32a3)
- Kaggle CLI: 2.2.5; account forts845
- Status: PASS for LTX, FLUX, CosyVoice, ESRGAN runtime; RIFE BLOCKED; licenses: 1 FAIL, 1 CONDITIONAL PASS, 3 PASS.
- GPU used (upper bound): 1.007 GPU-hours; quota-accounted ~0.50 h.
- Evidence: `audit/results.json`, `audit/results/component_results.json`, per-component summaries under `audit/logs/kaggle/`, previews under `audit/previews/stage_b/`.

## P0 results

| Component | License | Runtime | dtype | Peak VRAM | Time | Log |
|---|---|---|---|---|---|---|
| LTX-Video 2B v0.9.5 | PASS (Open RAIL-M) | PASS | FP16 | 11033 MiB alloc / 11050 reserved | 62.47 s generation (49 frames) | `audit/logs/kaggle/p0-ltx/v3/ltx_logs.txt` |
| FLUX.2 klein 4B | PASS (Apache-2.0) | PASS | FP16 | 7936 MiB alloc / 7948 reserved | 23.6 / 21.4 / 21.1 s **per image**; 66.0 s for all three | `audit/logs/kaggle/p0-flux/v2/flux_logs.txt` |
| CosyVoice 3 | CONDITIONAL PASS (model-card metadata) | PASS | FP32 | 3589.6 MiB alloc / 4264 reserved | 594.76 s generation / 602.28 s audio (RTF 0.988) | `audit/logs/kaggle/p0-cosy/v10/cosy_logs.txt` |
| Practical-RIFE 4.25 | PASS (MIT) | BLOCKED | — | — | no inference (CANCEL_ACKNOWLEDGED at ~90 s, v1/v2) | `audit/logs/kaggle/p0-rife/v2/openmontage-p0-practical-rife-4-25.log` |
| Real-ESRGAN x4plus | FAIL (weight license not explicit) | PASS | FP32 | 1041 MiB (nvidia-smi) | 16.6 s / 10 images | `audit/logs/kaggle/p0-esrgan/v2/esrgan_logs.txt` |

FLUX timing clarification: **23.6 s is one image, not three.** The per-image
generation times were 23.6065 s (seed 424242), 21.3675 s (seed 202607) and
21.0611 s (seed 271828); total generation = 66.035 s. Model load (130.916 s) is
excluded from the 66.0 s figure.

## Blockers

- Practical-RIFE: CANCEL_ACKNOWLEDGED at ~90 s (v1, v2); cause not established; diagnostics complete.
- Real-ESRGAN x4plus: weight license not explicit -> license FAIL.
- CosyVoice/Kokoro/Whisper/DepthAnything: license basis model_card_metadata -> CONDITIONAL PASS.
- CosyVoice FP32: `AutoModel(model_dir=...)` was called without `fp16=True`; official `CosyVoice3.__init__(..., fp16=False)` exposes an FP16 path.
- LTX/FLUX attention backend UNKNOWN (no flash-attn installed).

## Next stage preconditions

- Human quality review of LTX video, FLUX images, CosyVoice audio, ESRGAN images (previews ready).
- Real-ESRGAN weight license clarification or replacement (license exception requires human approval).
- RIFE investigation in Kaggle web UI before any further GPU attempt.
- Stage C not started.