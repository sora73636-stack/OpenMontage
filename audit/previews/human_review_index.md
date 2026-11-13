# HUMAN REVIEW INDEX — Stage B (P0 runtime)

Stage B produced real model outputs for LTX, FLUX, CosyVoice and Real-ESRGAN.
Practical-RIFE produced no output (kernel cancelled twice at ~90 s). All model
quality decisions remain **PENDING HUMAN REVIEW**; nothing is production-approved.

Review the compressed copies in `audit/previews/stage_b/`. Full-resolution originals
stay under `audit/logs/kaggle/` and are listed for traceability.

## Stage B previews

| Preview | What to evaluate | Model/version | Prompt/seed | Status |
|---|---|---|---|---|
| `audit/previews/stage_b/cosyvoice3_af_heart.mp3` | voice naturalness, pronunciation (JWST, LIGO, mitochondrion, ATP), numbers/units, stability, artifacts | CosyVoice 3 0.5B (FP32), reference Kokoro `af_heart` | `audit/config/science_voice_script.txt`, 43 chunks | PENDING HUMAN REVIEW |
| `audit/previews/stage_b/flux_1.jpg` | scientific accuracy, anatomy, artifacts | FLUX.2 klein 4B (FP16) | mitochondrion cutaway, seed 424242 | PENDING HUMAN REVIEW |
| `audit/previews/stage_b/flux_2.jpg` | telescope proportions, accuracy, artifacts | FLUX.2 klein 4B (FP16) | JWST observing exoplanet, seed 202607 | PENDING HUMAN REVIEW |
| `audit/previews/stage_b/flux_3.jpg` | interferometer geometry, realism, artifacts | FLUX.2 klein 4B (FP16) | gravitational-wave observatory, seed 271828 | PENDING HUMAN REVIEW |
| `audit/previews/stage_b/ltx_out.mp4` | stability, flicker, deformation, black/frozen frames, camera motion | LTX-Video 2B 0.9.5 (FP16) | spacecraft approaching exoplanet, seed 424242 | PENDING HUMAN REVIEW |
| `audit/previews/stage_b/esrgan_frame_00_before.jpg` / `_after.jpg` | halos, invented texture, edge quality (frame 00) | Real-ESRGAN x4plus (FP32) | 256x256 -> 1024x1024 | PENDING HUMAN REVIEW |
| `audit/previews/stage_b/esrgan_frame_01_before.jpg` / `_after.jpg` | halos, invented texture, edge quality (frame 01) | Real-ESRGAN x4plus (FP32) | 256x256 -> 1024x1024 | PENDING HUMAN REVIEW |
| `audit/previews/stage_b/esrgan_frame_02_before.jpg` / `_after.jpg` | halos, invented texture, edge quality (frame 02) | Real-ESRGAN x4plus (FP32) | 256x256 -> 1024x1024 | PENDING HUMAN REVIEW |

Preview sizes and SHA256: `audit/previews/stage_b/SHA256SUMS.txt`.
The CosyVoice MP3 is the full 602.28 s narration at mono 96 kbps (7.2 MB).

## Full-resolution originals

| Artifact | Path |
|---|---|
| LTX video (512x512, 24 fps, 49 frames) | `audit/logs/kaggle/p0-ltx/v3/audit/results/ltx-video-2b-0.9.5/out.mp4` |
| FLUX images (512x512 PNG) | `audit/logs/kaggle/p0-flux/v2/audit/results/flux2-klein-4b/flux_1.png` … `flux_3.png` |
| CosyVoice audio (24 kHz mono WAV, 602.28 s) | `audit/logs/kaggle/p0-cosy/v10/audit/results/cosyvoice3/out.wav` |
| ESRGAN outputs (1024x1024 PNG) | `audit/logs/kaggle/p0-esrgan/v2/audit/fixtures/esrgan/outputs/frame_00_out.png` … `frame_09_out.png` |
| ESRGAN inputs (256x256 PNG) | `audit/logs/kaggle/p0-esrgan/v2/audit/fixtures/esrgan/inputs/frame_00.png` … `frame_09.png` |
| RIFE | no output — `CANCEL_ACKNOWLEDGED` at ~90 s (v1, v2) |

## Stage A (still valid)

Stage A technical test patterns remain available for decode sanity only; they are
not model evidence:

| Path | What to evaluate | Model/version | Status |
|---|---|---|---|
| `audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_libx264.mp4` | decode sanity only (test pattern) | FFmpeg libx264 6.1.1 | OPTIONAL |
| `audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_h264_nvenc.mp4` | decode sanity only (test pattern) | FFmpeg h264_nvenc 6.1.1 | OPTIONAL |

## Review decision

Human approval fields are intentionally empty. No component is production-approved:
Real-ESRGAN also fails weight-license clearance, and RIFE has no runtime evidence.