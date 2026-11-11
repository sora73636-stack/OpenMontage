# Factory Decision Report — 2026-11-11

**Decision basis:** observed preflight, real local renders, license evidence, and the
missing-source fallback. No paid API, no GPU rental, no Flow/Veo credits.

## 1. Voice Factory

### Measured local CPU benchmark (2026-11-11)

| Engine | Load | 8 utterances | Audio | RTF | WER |
|---|---:|---:|---:|---:|---:|
| Kokoro-82M af_heart | 10.61 s | 47.53 s | 35.85 s | 1.326 | 2.78% |
| Piper lessac-medium | n/a (CLI) | 23.74 s | 29.48 s | 0.805 | 2.78% |

Both engines transcribed 7/8 sentences at 0% WER; the single 22.2% case is the same
"thirty-seven" → "37" normalization artifact on both. **Naturalness is NOT measured** —
no human listening. Kaggle GPU TTS was not possible: `spacy` has no build for Kaggle's
Python 3.13 and the kernel aborted during install (`TTS_BENCH.json` status=error).

### CORE — Kokoro-82M (`hexgrad/Kokoro-82M`, `af_heart`)
- License: Apache-2.0 (code + weights) — commercial use allowed.
- Size: 82M params; 24 kHz; CPU-capable; fits T4 and the Codespace with an isolated venv.
- Why: already referenced by `tools/audio/kokoro_tts.py` and `lib/audio_engine.py`;
  prior V12 pilot used `af_heart` with WER < 10%; no paid dependency.
- Status: Kaggle benchmark running (T01); local E2E pending.

### FALLBACK — Piper `en_US-lessac-medium`
- Code: GPL-3.0 (`piper1-gpl`); voice: CC-BY-4.0 (attribution required).
- Why: very fast CPU TTS, tiny (~60 MB voice), works without torch.
- Caveat: GPL program; attribution for the voice; lower naturalness than Kokoro.
- Status: Kaggle benchmark running (T02).

### EXPERIMENTAL (not in this run)
- CosyVoice3-0.5B (Apache-2.0, 224k downloads) — zero-shot cloning; needs reference audio
  and consent; not tested.
- VoxCPM2 (Apache-2.0) — not tested.
- MOSS-TTS v1.5 / Nano-100M (Apache-2.0) — not tested.
- Ming-Lite-Omni-1.5 (MIT) — omni model, not a pure TTS; task fit unverified.

### BLOCKED
- Qwen3-TTS — paid DashScope API only; violates strict $0.

## 2. Video Factory

### CORE — FFmpeg 6.1.1 + Ken Burns/zoompan + PIL diagrams
- 100% local, $0, deterministic, already used for V12/V13.
- Proven: 132 s and 178 s 1080p30 H.264/AAC renders decode clean.

### FALLBACK — Wan2.1-T2V-1.3B
- Apache-2.0; 1.3B fits a 14.5 GB T4; T2V only.
- Not tested: 19.5 GB Kaggle disk is enough for one model, but the run was not attempted.

### EXPERIMENTAL — LTX-Video 0.9.6/0.9.7
- Open Weights License 0.X: commercial use allowed **only for entities with <$10M annual
  revenue**, with use restrictions and an AI-content disclaimer; >= $10M requires a paid
  license.
- ~9–12 GB weights; Kaggle disk can hold one model at a time.
- Not tested: license review + disk + integration time.

### I2V status
- **NOT TESTED.** LTX I2V pipeline support in the installed diffusers version is unverified;
  Wan2.1 I2V 14B is too large for one T4. Do not claim I2V capability.

## 3. Animation Factory

### CORE — existing Stickman Rig-1 (SVG + PIL + FFmpeg)
- One rig only: `lib/stickman_rig.py` + `lib/stickman_pose_library.py`.
- Real test: 32 frames (8 poses × 4 views) rendered; signature lens 32/32.
- **Gap:** `profile` and `three_quarter` are byte-identical to `front`; only `back` flips.
  Fix the projection before claiming multi-view.

### NOT USED (no measured need)
- Manim CE — not installed; math-animation value is low for a documentary.
- Blender — not installed; heavy; existing FFmpeg/PIL path is sufficient for 60–90 s.

## 4. Audio Factory

### CORE — PD music bed + FFmpeg loudnorm/limiter
- `assets/music/ardune_red_moon.mp3` — Public Domain Mark 1.0, 212.58 s, documented.
- `ffmpeg loudnorm` + `alimiter` is the proven mastering path.

### EXPERIMENTAL
- ACE-Step v1 3.5B (Apache-2.0) — music generation; 3.5B weights, not tested.
- MOSS-SoundEffect v2.0 (Apache-2.0) — SFX; not tested.
- DeepFilterNet (MIT/Apache-2.0 dual) — noise suppression; not installed.

### BLOCKED for monetized production
- Stable Audio Open 1.0 — CC-BY-NC-4.0 weights.
- Stable Audio Open Small — gated, terms not verified.

## 5. QC / Release

- CORE: `tools/qa/qc.py` + `config/qc_thresholds.json` + rights manifest.
- **Unresolved:** repo target is **-16 LUFS**, YouTube reference is **-14 LUFS**.
  Owner must choose before publishing.
- **Cannot certify:** human review (H-1..H-3) not performed; final status must be
  `PENDING_HUMAN_REVIEW`.

## 6. Model budget (strict $0)

| Item | Cost | Evidence |
|---|---:|---|
| Kaggle T4 kernels (preflight + TTS bench) | $0 | free tier; no paid GPU |
| Kokoro/Piper weights | $0 | Apache-2.0 / CC-BY voice |
| PD music | $0 | Public Domain Mark 1.0 |
| Local CPU renders | $0 | FFmpeg/PIL |
| Paid APIs / Flow / Veo | $0 used | none invoked |

**No paid route was invoked.** No secrets were printed.

## 7. Recommended next smallest step

1. Collect the TTS benchmark output (T01/T02) and record real WER/RTF.
2. Build the 60–90 s E2E demo with Kokoro + PD music + PIL diagrams + rig overlay + QC.
3. Send the exact final file to a human for H-1/H-2; keep status `PENDING_HUMAN_REVIEW`.
4. Only then decide whether to run Wan2.1 or LTX on Kaggle.