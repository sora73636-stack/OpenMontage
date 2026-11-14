# Stage F Summary — Wan2.2 TI2V-5B GGUF (Q4_K_M) on Kaggle T4

**Date:** 2026-11-14 (UTC)
**Branch:** audit/kaggle-t4
**HEAD SHA:** feee3e8e20209a62c9558360df85238de15fdec3
**Kernel:** forts845/openmontage-vq-wan2-2-ti2v-5b-gguf (v2, COMPLETE)

## What was done
- Verified license of `QuantStack/Wan2.2-TI2V-5B-GGUF` (HF cardData license = apache-2.0; base model also apache-2.0; no extra terms; no separate LICENSE file → CONDITIONAL PASS per L6). Saved under `audit/licenses/wan22-ti2v-5b-gguf/` (LICENSE.txt, MODEL_CARD.md, STATUS.json).
- Ran a single-model GPU test on one Kaggle T4 using diffusers 0.35.2 + transformers 4.51.3 (Kaggle pre-installed torch 2.11.0+cu130), loading the GGUF Q4_K_M transformer via `WanTransformer3DModel.from_single_file` with `GGUFQuantizationConfig(compute_dtype=fp16)`, VAE (fp32), UMT5 text encoder (forced fp16). Attention backend = PyTorch SDPA (flash_attn unavailable on T4 sm_75).
- Generated the same 3 scenes (Europa flyby / Saturn solar probe / Enceladus plumes) with the same seeds (424242 / 202607 / 271828) as `audit/previews/video_quality_comparison/COMPARISON.md`, at 832×480, 49 frames, 24 fps, 20 steps.
- Saved 3 clips with prefix `wan22_ti2v5b_*` in `audit/previews/video_quality_comparison/`. Ran ffprobe + blackdetect + freezedetect (0 black, 0 freeze on all).
- Updated COMPARISON.md (appended new section; existing ltx/wan 1.3B rows untouched), `audit/results.json` and `audit/results/component_results.json` with entry `wan2.2-ti2v-5b-gguf-q4km`, `audit/licenses/STATUS.json`.
- Added lesson L16 (torch version / transformers incompatibility on Kaggle).

## Results
- **runtime_status:** PASS
- **license_status:** CONDITIONAL PASS (apache-2.0 via model card)
- **dtype_mixed:** true (VAE fp32 for stability; text encoder fp16 OK; transformer GGUF Q4_K_M, compute fp16)
- **peak_vram_allocated_mb:** 13863.3
- **disk_usage_mb:** 18162.4 (under 20 GiB limit)
- **rtf:** 0.0056 (≈ 6.0 min per 2.04 s clip)
- **gen time per clip:** europa 369.0 s, saturn 362.7 s, enceladus 361.8 s
- **errors:** none (final run)

## production_status
BLOCKED — pending human review of the 3 clips (`human_review_status = PENDING_HUMAN_REVIEW`). Automated checks (ffprobe, blackdetect, freezedetect) are sanity checks only and do not assess visual quality. The human must watch the clips and compare to the Wan 1.3B probes before any production use.

## What was NOT done (per scope)
- Did not test Wan2.1-14B-GGUF or Wan2.2-I2V-A14B (separate command required; weekly GPU quota limited).
- Did not upscale (Real-ESRGAN) or interpolate (RIFE) the probes.
- Did not run a quality verdict — left to human review.
EOF
echo done