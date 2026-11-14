# PRODUCTION SMOKE TEST REPORT (Stage A)

Generated: 2026-11-13T04:21:09Z
Repository commit: 185af2eb8d4a18825219677612f9b6458702f122 (working tree was dirty; no project files were modified by this audit)
Kaggle kernel: https://www.kaggle.com/code/forts845/openmontage-stage-a-env-smoke (version 2, COMPLETE)

## 1. Executive summary
Stage A proves the Codespaces -> Kaggle control plane, the accelerator type and the license evidence. It does **not** run any model. Result: environment PASS, libx264 PASS, NVENC PASS, licenses collected. No production approval is granted.

## 2. Date, repo revision, decision-document provenance
- UTC: 2026-11-13T04:21:09Z
- Repo commit: 185af2eb8d4a18825219677612f9b6458702f122
- FINAL_PRODUCTION_DECISION: **NOT FOUND**. Searched working tree (find, maxdepth 5), all 45 refs (`git ls-tree -r`), all reachable objects (`git rev-list --all --objects`), stash and reflog. No matches. Per instruction, no thresholds, model IDs or license terms were invented.

## 3. Kaggle CLI auth/execution evidence
- CLI 2.2.5, auth method ACCESS_TOKEN (credentials never printed).
- `kaggle datasets list -s titanic -p 1` -> exit 0 (authenticated).
- Push exit 0: kernel version 2.
- Status polled: RUNNING -> COMPLETE.
- Output retrieved with `kaggle kernels output .../2` and verified by size + SHA256 + JSON parse.

## 4. Official limits, quoted documentation, actual runtime comparison
Official pages returned a reCAPTCHA challenge to non-browser clients (HTTP 200 challenge). Quotes were captured from the search index of the same official URLs (see `audit/provenance/kaggle_quota.json`):
- "12 hours execution time for CPU and GPU notebook sessions ... 20 Gigabytes of auto-saved disk space (/kaggle/working)" — https://www.kaggle.com/docs/notebooks
- "T4 x2 GPU Specifications: 2 Nvidia Tesla T4 GPUs, 4 CPU cores, 29 Gigabytes of RAM" — same page.
- "30 hours or sometimes higher depending on demand and resources" weekly GPU quota — https://www.kaggle.com/docs/efficient-gpu-usage
- "1 hour of Notebook runtime in the 2xT4 setup only consumes 1 hour of your GPU quota" — Kaggle Staff, https://www.kaggle.com/discussions/product-feedback/361104
Actual runtime: 2 x Tesla T4, 4 CPU cores, 31 GiB RAM, 20 GiB /kaggle/working, no /kaggle/temp. This matches the documented T4 x2 profile.

## 5. Verified T4 x2 snapshot proving separate devices
- torch 2.11.0+cu130, CUDA 13.0, `torch.cuda.is_available()=True`, `device_count=2`.
- Device 0: Tesla T4, 14911 MiB, cc 7.5; device 1: Tesla T4, 14911 MiB, cc 7.5.
- nvidia-smi return code 0. Memory is reported per device; never pooled.
Raw: `audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/logs/kaggle/environment_snapshot_before.json`.

## 6. GPU budget and consumption per notebook
- Wall time: 36.147 s. Allocated GPUs: 2.
- Conservative upper bound: 0.020082 GPU-hours (wall x GPUs).
- Quota-accounted estimate: 0.010041 h (official 2xT4 = 1 h per wall hour).
- Account quota is not exposed by the CLI; remaining quota was not verified.

## 7. License audit/missing/conditional permissions
Full per-component evidence: `audit/licenses/STATUS.json` and `audit/licenses/<component>/`.
Key points:
- LTX-Video 2B v0.9.5: Open RAIL-M, commercial use allowed with use restrictions.
- SDXL Base 1.0: CreativeML Open RAIL++-M, commercial use with restrictions.
- Real-ESRGAN x4plus: code BSD-3-Clause; **weight license not explicitly stated -> FAIL**.
- DepthFlow: AGPL-3.0 -> **BLOCKED / legal review**.
- DeepFilterNet3: code and weights dual MIT/Apache-2.0 (commit 7b14b89 clarified weights).
- Practical-RIFE 4.25: MIT; maintainer states linked model content is under the same MIT license.
- CosyVoice 3, Kokoro, Whisper, Parakeet, Wan2.1, Depth Anything V2, Video Depth Anything, FLUX.2 klein 4B, Manim, FFmpeg: evidence recorded; see STATUS.json for evidence type and residual conditions.

## 8. Per-component results
Stage A ran no model. See `audit/results/component_results.json`. Model runtime_status = NOT TESTED (Stage B/C/D).

## 9. P0 results
NOT TESTED in Stage A (Stage B). License evidence collected.

## 10. P1 results
NOT TESTED in Stage A (Stage C). License evidence collected.

## 11. P2 results
P2.2 FFmpeg/NVENC: PASS (libx264 and h264_nvenc, 10 s 1920x1080 30 fps, clean decode).
P2.1 DepthFlow: BLOCKED (AGPL legal review, no runtime test).

## 12. Integrated render results
NOT TESTED (Stage D).

## 13. Failures and preserved logs
- FINAL_PRODUCTION_DECISION not found (not a failure; documented absence).
- Live Kaggle docs blocked by reCAPTCHA (documented; quotes from search index).
- Real-ESRGAN weight license FAIL (preserved README/release assets).
- DepthFlow AGPL -> BLOCKED.
- No runtime failures.

## 14. What Must Not Be Considered Confirmed
- No model inference, quality, speed, VRAM or license-cleared weight hash for any model.
- No production stack approval.
- No human quality acceptance.

## 15. Recommended Stack Based on Test Results
Not produced in Stage A. Only environment and FFmpeg/NVENC are proven.

## 16. Human Review Required
- Optional sanity check of the two test-pattern videos.
- All model quality gates remain PENDING HUMAN REVIEW.
- Legal review: DepthFlow (AGPL), Real-ESRGAN weights, LTX/SDXL use restrictions.

## 17. Production final gate
Not reached. No component satisfies all ten conditions.

## 18. Reproduction commands
```
kaggle kernels push -p audit/kaggle/smoke_gpu
kaggle kernels status forts845/openmontage-stage-a-env-smoke
kaggle kernels output forts845/openmontage-stage-a-env-smoke/2 -p audit/logs/kaggle/openmontage-stage-a-env-smoke/v2 -o
```

## 19. Output artifact inventory
See `audit/results.json` and `audit/provenance/source_manifest.json`.


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
| LTX-Video 2B v0.9.5 | PASS (Open RAIL-M) | PASS | FP16 | 11033 MiB alloc / 11050 reserved | 62.47 s generation / 49 frames | audit/logs/kaggle/p0-ltx/v3/ltx_logs.txt |
| FLUX.2 klein 4B | PASS (Apache-2.0) | PASS | FP16 | 7936 MiB alloc / 7948 reserved | 23.6 / 21.4 / 21.1 s per image; 66.0 s for 3 images | audit/logs/kaggle/p0-flux/v2/flux_logs.txt |
| CosyVoice 3 | CONDITIONAL PASS (model-card metadata) | PASS | FP32 | 3589.6 MiB alloc / 4264 reserved | 594.76 s / 602.28 s audio (RTF 0.988) | audit/logs/kaggle/p0-cosy/v10/cosy_logs.txt |
| Practical-RIFE 4.25 | PASS (MIT) | BLOCKED | — | — | no inference (CANCEL_ACKNOWLEDGED at ~90 s, v1/v2) | audit/logs/kaggle/p0-rife/v2/openmontage-p0-practical-rife-4-25.log |
| Real-ESRGAN x4plus | FAIL (weight license not explicit) | PASS | FP32 | 1041 MiB (nvidia-smi) | 16.6 s / 10 images | audit/logs/kaggle/p0-esrgan/v2/esrgan_logs.txt |

FLUX timing clarification: **23.6 s is one image, not all three.** Per-image generation
times were 23.6065 s (seed 424242), 21.3675 s (seed 202607) and 21.0611 s (seed 271828);
total generation = 66.035 s. The 130.916 s model-load time is excluded. The JSON records
`runtime_seconds: 66.035` with `runtime_seconds_basis` and `checks.seconds_per_image`.

## B4. Failures/blockers
- Practical-RIFE: v1 and v2 CANCEL_ACKNOWLEDGED at ~90 s. CPU-only, GPU-only, GPU+internet, uv+torch and gdown diagnostics all COMPLETE. Cause not established. No further retries.
- Real-ESRGAN: runtime PASS but weight license FAIL.
- CosyVoice: license is model-card metadata only -> CONDITIONAL PASS.
- CosyVoice ran in FP32 because the notebook called `AutoModel(model_dir=...)` without `fp16=True`; the official `CosyVoice3.__init__(..., fp16=False)` does expose an FP16 path.
- Attention backend for LTX/FLUX is UNKNOWN (no flash-attn installed).

## B5. GPU budget
Stage B upper bound: 0.05 + 0.052 + 0.176 + 0.148 + 0.502 + 0.079 = 1.007 GPU-hours (wall x GPUs). Quota-accounted estimate ~0.50 h (2xT4 = 1 h per wall hour). No stage limit of 24 h approached.

## B6. Production gate
No component is production-approved: human quality review is pending for all; Real-ESRGAN also fails license.

## B7. Human-review previews (compressed copies)
- CosyVoice: `audit/previews/stage_b/cosyvoice3_af_heart.mp3` — full 602.28 s, mono 96 kbps, 7.2 MB.
- FLUX: `audit/previews/stage_b/flux_1.jpg`, `flux_2.jpg`, `flux_3.jpg` — 512x512 JPEG.
- LTX: `audit/previews/stage_b/ltx_out.mp4` — 45 KB, 512x512, 24 fps, 49 frames.
- Real-ESRGAN: `esrgan_frame_00_before.jpg` / `_after.jpg` through `frame_02` — 256x256 before, 1024x1024 after.
- Checksums: `audit/previews/stage_b/SHA256SUMS.txt`; review index: `audit/previews/human_review_index.md`.
- Practical-RIFE: no preview (kernel cancelled before inference).
- Results JSON rebuilt from logs by `audit/scripts/rebuild_stage_b_results.py`; previews by `audit/scripts/make_stage_b_previews.py`.

---

# Stage C (2026-11-14) — P1 runtime

Scope: Phase 5 only (Kokoro 82M, Whisper large-v3-turbo + jiwer, Parakeet TDT 0.6B v3,
DeepFilterNet3, Wan2.1 T2V 1.3B, Depth Anything V2 Small, Video Depth Anything Small,
SDXL Base 1.0). One notebook and one isolated uv environment per component; Python pinned
per component (3.10 or 3.11); global torch/CUDA untouched.

## C1. Per-component outcome

| Component | License | Runtime | dtype | Peak VRAM | Metric | Log |
|---|---|---|---|---|---|---|
| Kokoro 82M | CONDITIONAL PASS | PASS | float32 | 1165.83 MiB | 28.61 s / 610.3 s audio (RTF 0.0469) | `audit/logs/kaggle/p1-kokoro/v1/kokoro_logs.txt` |
| Whisper large-v3-turbo | CONDITIONAL PASS | PASS | float16 | 4629.20 MiB | RTF 0.0721, WER 0.030298 | `audit/logs/kaggle/p1-whisper/v2/openmontage-p1-whisper-large-v3-turbo.log` |
| Parakeet TDT 0.6B v3 | CONDITIONAL PASS | PASS | FP32 (not measured) | 4848.45 MiB | RTF 0.0126, WER 0.020357 | `audit/logs/kaggle/p1-parakeet/v1/audit/logs/kaggle/parakeet-tdt-0.6b-v3.log` |
| SDXL Base 1.0 | PASS | PASS | torch.float16 | 5000.71 MiB | 35.90 s / 3 images | `audit/logs/kaggle/p1-sdxl/v2/openmontage-p1-sdxl-base-1-0.log` |
| Depth Anything V2 Small | CONDITIONAL PASS | PASS | torch.float32 | 207.79 MiB | 0.049-0.081 s / 640x640 frame | `audit/logs/kaggle/p1-depth/v7/openmontage-p1-depth-anything-v2-small.log` |
| Video Depth Anything Small | CONDITIONAL PASS | PASS | FP16 | not captured | 14.55 s / 48 frames | `audit/logs/kaggle/p1-vd/v2/audit/logs/kaggle/video-depth-anything-small.log` |
| DeepFilterNet3 | PASS | PASS | FP32 | 569 MiB | 6.82 s wall / 30 s audio, drift 0 ms | `audit/logs/kaggle/p1-dfn/v2/audit/logs/kaggle/deepfilternet3.log` |
| Wan2.1 T2V 1.3B | PASS | BLOCKED | - | - | no inference | `audit/logs/kaggle/p1-wan/v2/audit/logs/kaggle/wan2.1-t2v-1.3b.log` |

## C2. Blockers

- Wan2.1: v1 BLOCKED on `flash_attn` sdist build; v2 (the single recovery attempt) FAIL on
  `ModuleNotFoundError: No module named 'einops'` — Wan's requirements.txt omits a module
  that `wan/modules/vae.py` imports. No v3 (one recovery attempt per component).
- Video Depth Anything peak VRAM missing (nvidia-smi sampler queried one column, parser
  expected three). Builder fixed; run not repeated.
- Parakeet dtype not measured (hard-coded in the notebook).

## C3. Whisper vs Parakeet (identical test set and normalisation)

Same 330 LibriSpeech dev-clean files (2413.0500625 s), same selection rule, same jiwer
normalisation. Whisper 3.0298 % WER / 1.0440 % CER / RTF 0.0721 vs Parakeet 2.0357 % WER /
0.5937 % CER / RTF 0.0126 on the same T4.

## C4. GPU budget

Measured wall time across the 12 preserved Stage C kernels: 1445 s = 0.400 GPU-h
(upper bound, 1 T4 each); ~0.08 GPU-h more for the 2026-11-13 runs without a preserved
summary. Stage C total ~0.48 GPU-h of the 24 GPU-h cap. Cumulative all stages: 1.407 GPU-h.

## C5. Human-review previews

`audit/previews/stage_c/`: Kokoro mp3 (same script as CosyVoice), 3 SDXL jpgs (same seeds
and prompts as FLUX), Depth Anything V2 depth map jpg, Video Depth Anything mp4 + frame,
DeepFilterNet3 noisy/enhanced 10 s snippets. Index: `audit/previews/human_review_index.md`.

## C6. Production gate

No P1 component is production-approved. Seven of eight ran successfully, but every media
output is PENDING HUMAN REVIEW and four weight licences rest on model-card metadata only
(CONDITIONAL PASS).
