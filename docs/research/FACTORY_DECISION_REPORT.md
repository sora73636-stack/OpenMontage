# Factory Decision Report — updated 2026-11-12

**Basis:** 10of10 task, Kaggle preflight, real local/Kaggle tests, license evidence.
No paid API, no GPU rental, no Flow/Veo credits.

## Measured benchmark summary

| Factory | Candidate | Environment | Result |
|---|---|---|---|
| Voice | Kokoro-82M af_heart | local CPU py3.12 | WER **2.78%**, RTF **1.326**, load 10.61 s |
| Voice | Piper lessac-medium | local CPU py3.12 | WER **2.78%**, RTF **0.805**, 8 utts 23.74 s |
| Voice | Qwen3-TTS-12Hz-0.6B-Base | Kaggle T4 | kernel `om-10-voice-qwen` running; earlier runs failed on dataset mount, fixed with embedded reference |
| Animation | Manim CE 0.22.1 | Codespaces CPU | 11.07 s, 1920×1080, 13 animations, render PASS |
| Animation | Stickman Rig-1 | Codespaces CPU | 32/32 frames, lens 32/32, view projection gap |
| Audio | DeepFilterNet3 | Codespaces CPU | RTF 0.055; extreme noise WER 69.2%→69.2% (no gain); mild 0%→0% |
| Audio | FFmpeg loudnorm/limiter | Codespaces | E2E master I=-16.0 LUFS, TP=-2.0 dBTP |
| Video | Wan2.1-T2V-1.3B | Kaggle preflight | **BLOCKED_STORAGE**: 17.57 GB > 75% of 19.5 GB free |
| Video | LTX-Video 0.9.6 distilled | Kaggle preflight | **BLOCKED_STORAGE**: 6.34 GB + ~19.3 GB T5 + VAE > 25 GB |

## Voice

### CORE — Kokoro-82M (`hexgrad/Kokoro-82M`, af_heart)
Apache-2.0 code+weights; 82M; CPU-capable; measured WER 2.78%, RTF 1.326.
Used for the E2E narration reference and the first demo.

### FALLBACK — Piper `en_US-lessac-medium`
GPL-3.0 code; CC-BY-4.0 voice (attribution required); measured WER 2.78%, RTF 0.805.
Used for the 76 s E2E narration (reliable CPU path).

### EXPERIMENTAL / NOT TESTED
- Qwen3-TTS-12Hz-0.6B-Base — Apache-2.0, 2.52 GB; P0 kernel in progress. Earlier failures were **our** dataset-mount and missing `qwen-tts` install, not model quality. VRAM-growth issue must be tested with 10 sequential chunks.
- Ming-3.0-tts-0.5B — MIT, 3.0 GB; requires the `Ming-3.0-tts` GitHub repo; not downloaded.
- CosyVoice3-0.5B (9.75 GB), VoxCPM2 (4.96 GB), MOSS-TTS-Local (6.14 GB) — not downloaded; disk fits but integration time not spent.

### BLOCKED
- Qwen3-TTS paid DashScope API — violates strict $0.

## Video

### CORE — FFmpeg 6.1.1 + Ken Burns + PIL/Manim
100% local, deterministic; used for the 76 s E2E master.

### BLOCKED_STORAGE (no download started)
- **Wan2.1-T2V-1.3B:** repo 17.57 GB (diffusion 5.68 + T5 11.36 + VAE 0.51). 19.5 GB free disk; 17.57 GB is >75% → policy says do not start. T2V only.
- **LTX-Video 0.9.6 distilled:** distilled file 6.34 GB + T5 text encoder ~19.3 GB + VAE; full pipeline >25 GB. Repo total 254 GB. I2V/T2V not tested.
- **HunyuanVideo-1.5:** ~33 GB checkpoint, ~14+ GB VRAM → HIGH_END_NOT_T4.

**I2V remains NOT TESTED.** Do not claim I2V capability.

## Animation

### CORE — existing Stickman Rig-1 + PIL/SVG + Manim CE
- Rig-1: one rig only, 32/32 frames, signature lens 32/32.
- Manim CE 0.22.1: installed and rendered an 11.07 s ice-density diagram; used in the E2E.
- **Gap:** rig `profile`/`three_quarter` identical to `front`.

### NOT TESTED
- Blender — not installed; heavy; no measured need for the 60–90 s slice.
- Depth Anything V2 — licence/size not cleared.

## Audio

### CORE — PD music + FFmpeg
- `assets/music/ardune_red_moon.mp3` — Public Domain Mark 1.0, 212.58 s.
- FFmpeg `loudnorm` + `alimiter` (level=false) → measured I=-16.0 LUFS, TP=-2.0 dBTP.

### PARTIAL — DeepFilterNet3
Runs on CPU (RTF 0.055), but did not measurably improve WER on synthetic noise
(extreme 69.2%→69.2%; mild 0%→0%). Not a CORE win for clean TTS; test on real
field recordings before use.

### NOT TESTED — ACE-Step 1.5 / MOSS-SoundEffect v2.0
- ACE-Step1.5: MIT, 10.09 GB; fits disk (52%) but integration time not spent.
- MOSS-SoundEffect-v2.0: Apache-2.0, 11.23 GB; custom code; not downloaded.

### BLOCKED — Stable Audio
- Stable Audio Open 1.0 — CC-BY-NC-4.0 weights.
- Stable Audio Open Small — gated; terms not verified.

## 10/10 status

**PENDING_HUMAN_REVIEW.** No human has watched the exact final master; no independent
reviewer has scored it. The 10of10 hard gates are not satisfied.

## Next smallest step

1. Read the Qwen3-TTS result when the kernel finishes; record PASS/BLOCKED honestly.
2. Human watch-through of `work/master-run/e2e/final_demo.mp4` (76.07 s).
3. Only then decide whether to request a high-end GPU for Wan/LTX, or keep FFmpeg/Manim.