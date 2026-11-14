# Video quality comparison — LTX-Video 2B 0.9.5 vs Wan2.1 T2V 1.3B

Channel topics: space / science. Same three prompts, same seeds, same resolution 832×480,
24 fps target, LTX 30 inference steps, Wan 6 steps (SDPA fallback, no FlashAttention 2).
All clips are `PENDING HUMAN REVIEW` — automated checks below do **not** replace watching them.

## Comparison table

| Clip file | Model | Seed | Gen time (s) | Peak VRAM | Resolution | Frames | Duration | blackdetect | freezedetect |
|---|---|---|---|---|---|---|---|---|---|
| `ltx_europa_flyby_424242.mp4` | LTX-Video 2B 0.9.5 | 424242 | 307.6 | 11033.6 MiB | 832×480 | 193 | 8.04 s | 0 | 0 |
| `ltx_saturn_solar_202607.mp4` | LTX-Video 2B 0.9.5 | 202607 | 296.2 | 11033.6 MiB | 832×480 | 193 | 8.04 s | 0 | 0 |
| `ltx_enceladus_plumes_271828.mp4` | LTX-Video 2B 0.9.5 | 271828 | 296.2 | 11033.6 MiB | 832×480 | 193 | 8.04 s | 0 | 0 |
| `wan_europa_flyby_424242.mp4` | Wan2.1 T2V 1.3B | 424242 | 517.1 | not measured | 832×480 | 50 | 2.08 s | 0 | 0 |
| `wan_saturn_solar_202607.mp4` | Wan2.1 T2V 1.3B | 202607 | 492.9 | not measured | 832×480 | 50 | 2.08 s | 0 | 0 |
| `wan_enceladus_plumes_271828.mp4` | Wan2.1 T2V 1.3B | 271828 | 501.5 | not measured | 832×480 | 50 | 2.08 s | 0 | 0 |

## Automated observations (no quality verdict)

- `blackdetect` found 0 black segments and `freezedetect` found 0 freeze segments in all six clips.
- LTX clips are 193 frames at 24 fps (8.04 s), fp16, `FlowMatchEulerDiscreteScheduler`, 30 steps, guidance scale 3.0, 832×480.
- Wan clips are 33 generated frames at the model's native 16 fps, re-timed to 24 fps with `ffmpeg -r 24` (50 frames, 2.08 s, frame duplication). This means the Wan motion is 1.5× faster than native and the clip is 4× shorter than the requested 8–10 s.
- Wan dtype is fp16 (patched from the shipped bf16 config; T5 stays bf16 on CPU). FlashAttention 2 disabled (T4 is sm_75); attention ran through torch SDPA.
- Wan peak VRAM was not recorded in this run (the notebook did not capture it); the 1.3B model on T4 with offload is expected to be ~9–11 GB, but that is an estimate, not a measurement.

## What was NOT done and why

- **Wan 8–10 s clips at 832×480 were not produced.** Wan 1.3B generates 33 frames in ≈ 517 s on T4 (≈ 12.3 s/step at 33 frames). Extrapolated to 193 frames (8 s at 24 fps, 49 latent frames) that is ≈ 460 s/step and ≈ 3.8 h per clip at 30 steps — well past the 2 GPU-h budget. The three clips above are 33-frame / 6-step probes that prove inference works in FP16 on T4; they are not a fair quality comparison.
- **Practical-RIFE 4.25 (48 fps) was not run.** Stage B recorded it as `CANCEL_ACKNOWLEDGED` twice at ~90 s with no established cause; no further retry was budgeted.
- **Real-ESRGAN x4plus was not run.** It was available, but upscaling 2.08 s probe clips would not represent the final look; skipped to keep the budget for generation.

## Review decision

Both models' clips are `PENDING HUMAN REVIEW`. Automated checks (ffprobe, blackdetect, freezedetect) are sanity checks only: they confirm decodability, resolution, frame rate and the absence of fully black / fully frozen frames. They do **not** assess subject consistency, deformation, flicker, or semantic correctness, and they do not decide which model to use. Watch the clips.
---

## Wan2.2 TI2V-5B GGUF (Q4_K_M) — Stage F probe (2026-11-14)

Same three prompts/seeds, 832×480, 49 frames, 24 fps, 20 inference steps, guidance scale 5.0,
FP16 pipeline (transformer is GGUF Q4_K_M with fp16 compute dtype; VAE stays fp32 for
numerical stability; text encoder UMT5 forced to fp16), attention backend = PyTorch SDPA
(flash_attn not installed/available on T4 sm_75; SDPA is the default).

| Clip file | Model | Seed | Gen time (s) | Peak VRAM | Resolution | Frames | Duration | blackdetect | freezedetect |
|---|---|---|---|---|---|---|---|---|---|
| `wan22_ti2v5b_europa_flyby_424242.mp4` | Wan2.2 TI2V-5B GGUF Q4_K_M | 424242 | 369.0 | 13863.3 MiB | 832×480 | 49 | 2.04 s | 0 | 0 |
| `wan22_ti2v5b_saturn_solar_202607.mp4` | Wan2.2 TI2V-5B GGUF Q4_K_M | 202607 | 362.7 | 13863.3 MiB | 832×480 | 49 | 2.04 s | 0 | 0 |
| `wan22_ti2v5b_enceladus_plumes_271828.mp4` | Wan2.2 TI2V-5B GGUF Q4_K_M | 271828 | 361.8 | 13863.3 MiB | 832×480 | 49 | 2.04 s | 0 | 0 |

### Stage F notes
- Disk usage (GGUF 3.43 GB + VAE 1.41 GB + diffusers subset incl. UMT5 text encoder ~11.36 GB + tokenizer) = 18.16 GiB, under the 20 GiB Kaggle limit.
- Runtime: ~6.0 min per clip (≈ 7.4 s/step at 49 frames), 3 clips ≈ 18.2 min total on one T4.
- dtype_mixed: true — VAE stays fp32 (numerical stability); text encoder successfully forced to fp16; transformer is GGUF-quantized (storage uint8, compute dtype fp16 via GGUFQuantizationConfig). No component stuck in bf16.
- Attention backend: PyTorch SDPA (flash_attn not installed/available on T4 sm_75; default path is SDPA).
- All three clips: blackdetect 0, freezedetect 0 (sanity only).
- human_review_status: PENDING_HUMAN_REVIEW (quality assessment by human).
