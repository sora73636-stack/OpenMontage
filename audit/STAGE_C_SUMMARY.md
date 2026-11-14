# STAGE C SUMMARY — P1 runtime (Phase 5)

- UTC: 2026-11-14T02:36Z (finalised)
- Scope: **Stage C only** (Phase 5, P1 components). Stage A and Stage B evidence untouched.
- Hardware: Kaggle, 1 × Tesla T4 per kernel, `NvidiaTeslaT4`, internet on, GPU on.
- Tooling: `kaggle` CLI 2.2.5, account `forts845`, uv-managed venvs (one per component,
  Python pinned to the version the component's own docs/repo require).
- Repos/weights are installed under `/tmp/audit/...` (outside `/kaggle/working`), so
  `kaggle kernels output` only returns evidence.

## Result table

| Component | License (weights) | Runtime | dtype | Peak VRAM | Time / RTF / WER | Log |
|---|---|---|---|---|---|---|
| Kokoro 82M | CONDITIONAL PASS (model_card_metadata) | PASS | float32 | 1165.83 MiB (torch) | 28.61 s for 610.3 s audio, RTF 0.0469 | `audit/logs/kaggle/p1-kokoro/v1/kokoro_logs.txt` |
| Whisper large-v3-turbo | CONDITIONAL PASS (model_card_metadata) | PASS | float16 | 4629.20 MiB (torch) | 173.97 s for 2413.05 s, RTF 0.0721, **WER 0.030298** | `audit/logs/kaggle/p1-whisper/v2/openmontage-p1-whisper-large-v3-turbo.log` |
| Parakeet TDT 0.6B v3 | CONDITIONAL PASS (model_card_metadata) | PASS | FP32 (not measured) | 4848.45 MiB (torch) | 30.43 s for 2413.05 s, RTF 0.0126, **WER 0.020357** | `audit/logs/kaggle/p1-parakeet/v1/audit/logs/kaggle/parakeet-tdt-0.6b-v3.log` |
| SDXL Base 1.0 | PASS (Open RAIL++-M text) | PASS | torch.float16 | 5000.71 MiB (torch) | 35.90 s / 3 images (15.50 + 10.62 + 9.78 s) | `audit/logs/kaggle/p1-sdxl/v2/openmontage-p1-sdxl-base-1-0.log` |
| Depth Anything V2 Small | CONDITIONAL PASS (model_card_metadata) | PASS | torch.float32 | 207.79 MiB (torch) | 0.049–0.081 s per 640×640 frame | `audit/logs/kaggle/p1-depth/v7/openmontage-p1-depth-anything-v2-small.log` |
| Video Depth Anything Small | CONDITIONAL PASS (model_card_metadata) | PASS | FP16 (run.py default) | **not captured** | 14.55 s for 48 frames @12 fps (≈3.3× realtime) | `audit/logs/kaggle/p1-vd/v2/audit/logs/kaggle/video-depth-anything-small.log` |
| DeepFilterNet3 | PASS (MIT OR Apache-2.0, weights named) | PASS | FP32 | 569 MiB (nvidia-smi) | 6.82 s wall for 30 s audio, 0.56 s model (RTF 0.019), 0 ms drift | `audit/logs/kaggle/p1-dfn/v2/audit/logs/kaggle/deepfilternet3.log` |
| Wan2.1 T2V 1.3B | PASS (Apache-2.0) | **BLOCKED** | — | — | no inference | `audit/logs/kaggle/p1-wan/v2/audit/logs/kaggle/wan2.1-t2v-1.3b.log` |

All "PASS" rows mean: kernel `COMPLETE`, `summary.json` written by the kernel,
`status: PASS` inside it, expected non-empty output files downloaded and opened locally.
They do **not** mean production-approved: every media output is `PENDING HUMAN REVIEW`.

## Blocked

- **Wan2.1 T2V 1.3B** — two runs:
  - v1 `BLOCKED`: `uv pip install -r requirements.txt` cannot build `flash_attn` from sdist
    (`setup.py` imports `torch` under build isolation; no wheel exists for torch 2.6 / py310).
  - v2 (the single recovery attempt) `FAIL`: requirements installed (flash_attn filtered out,
    which is optional — Wan falls back to SDPA), model downloaded (22 files, 83 s), then
    `generate.py` died with `ModuleNotFoundError: No module named 'einops'`.
    Wan's `requirements.txt` does not declare `einops` even though `wan/modules/vae.py`
    imports it at line 8.
  - The audit cap is one recovery attempt per component, so no v3 was pushed.
    The fix is one line (`einops>=0.6`) plus re-running the official command:
    `python generate.py --task t2v-1.3B --size 832*480 --ckpt_dir <model> --offload_model True --t5_cpu --sample_shift 8 --sample_guide_scale 6 --prompt ...`

## Not checked / not measured

- Wan2.1: no generation, no VRAM, no clip, no human review.
- Video Depth Anything: peak VRAM not captured. The v2 sampler queried one nvidia-smi
  column while the parser expected three; the builder is fixed but the run was not repeated.
- Parakeet: dtype is not measured. The notebook hard-codes `FP16`; NeMo's default restore is
  FP32 and the 4.85 GB peak is consistent with FP32 weights.
- Whisper/Parakeet: WER is corpus-level on LibriSpeech dev-clean, not per-utterance aligned.
- Kokoro: no ASR round-trip was run on the generated audio (no WER for TTS).
- No component was run twice for variance; all timings are single-run.

## Whisper vs Parakeet (same test set, same normalisation)

Both ran on **the same 330 LibriSpeech dev-clean files (2413.0500625 s)** with the same
selection rule (first files until ≥2400 s) and the same jiwer normalisation
(lowercase → strip punctuation → collapse whitespace).

| Model | WER | CER | RTF | Peak VRAM |
|---|---|---|---|---|
| Whisper large-v3-turbo | 3.0298 % | 1.0440 % | 0.0721 | 4629.20 MiB |
| Parakeet TDT 0.6B v3 | 2.0357 % | 0.5937 % | 0.0126 | 4848.45 MiB |

Parakeet is ~1.49× lower WER, ~1.76× lower CER and ~5.7× faster on the same T4,
at roughly the same memory footprint.

## GPU budget

| Run | Wall s | GPU-h (upper bound, 1 T4) |
|---|---|---|
| kokoro v1 | 106 | 0.029 |
| whisper v2 | 428 | 0.119 |
| parakeet v1 | 167 | 0.046 |
| sdxl v2 | 136 | 0.038 |
| depth v6 | 66 | 0.018 |
| depth v7 | 67 | 0.019 |
| videodepth v1 (ERROR) | 51 | 0.014 |
| videodepth v2 | 80 | 0.022 |
| deepfilternet v1 (ERROR) | 57 | 0.016 |
| deepfilternet v2 | 66 | 0.018 |
| wan v1 (BLOCKED) | 62 | 0.017 |
| wan v2 (ERROR) | 159 | 0.044 |
| **measured total** | **1445** | **0.400** |

Plus ~0.08 GPU-h for the 2026-11-13 partial campaign runs whose summaries were not preserved
(whisper v1, sdxl v1, depth v1–v5). **Stage C total ≈ 0.48 GPU-h of the 24 GPU-h cap.**
Cumulative all stages: 1.407 GPU-h.

## Evidence

- Results: `audit/results.json`, `audit/results/component_results.json`
- Previews: `audit/previews/stage_c/` (+ `SHA256SUMS.txt`), index in `audit/previews/human_review_index.md`
- Licenses: `audit/licenses/<component>/LICENSE-weights.txt`, `audit/licenses/STATUS.json`
- Notebooks: `audit/kaggle/p1/<component>/notebook.py` + `kernel-metadata.json`
- Raw logs/summaries: `audit/logs/kaggle/p1-<component>/vN/`
- Builder: `audit/scripts/build_p1_notebooks.py`; finaliser: `audit/scripts/finalize_stage_c.py`;
  previews: `audit/scripts/make_stage_c_previews.py`