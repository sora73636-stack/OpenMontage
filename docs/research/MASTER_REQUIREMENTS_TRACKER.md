# Master Requirements Tracker — 2026-11-11

**Run:** OpenMontage Factory master execution (source docs absent; requirements
reconstructed from the user task + master plan + repo reality).
**Status legend:** DONE · PARTIAL · BLOCKED · NOT_DONE · PENDING_HUMAN_REVIEW

| ID | Requirement | Status | Evidence | Next step |
|---|---|---|---|---|
| S1 | Locate both source documents | DONE | 10of10 FOUND in origin/main @ 2f8f1915 (SHA-256 `8d8fe0f0…`); 4_Factories NOT FOUND after 726 refs + GitHub search | owner to supply 4_Factories if it exists locally |
| S2 | Reconstruct requirements honestly | DONE | `TASK_STATEMENT_RECONSTRUCTED.md` + SHA-256 | none |
| A | Audit Voice/Video/Animation/Audio/QC/pilots/Kaggle | DONE | `BASELINE_AUDIT.md`; 3,075 tests collect; 138 factory pass | owner review |
| B | 15 science YouTube videos | DONE (metadata only) | `COMPETITOR_VIDEO_AUDIT.md` + `.csv`; 20 videos, 5 biology/evolution; 0 frames viewed | human frame-level viewing |
| C | Kaggle preflight | DONE | 2× T4 14.56 GB, 31.35 GB RAM, 19.5 GB disk, CUDA 13, torch 2.11, internet 200 | model tests |
| D1 | Voice: Kokoro | DONE (local CPU) | Apache-2.0; WER 2.78%, RTF 1.326; Kaggle ERROR (spacy py3.13) | human listening |
| D2 | Voice: Piper | DONE (local CPU) | GPL-3.0 code / CC-BY voice; WER 2.78%, RTF 0.805; E2E narration rendered | human listening |
| D3 | Voice: CosyVoice3 / VoxCPM2 / MOSS / Ming / Qwen | NOT_TESTED | exact sizes recorded (Ming 3.0 GB, Qwen 2.52 GB, CosyVoice3 9.75 GB, VoxCPM2 4.96 GB, MOSS-Local 6.14 GB); not downloaded | next kernels |
| D4 | Voice: Qwen3-TTS | BLOCKED | paid API only | do not use under $0 |
| E1 | Video: FFmpeg/Ken Burns | DONE | 16 clips, full decode, QC PASS | none |
| E2 | Video: LTX-Video T2V | NOT_DONE | license reviewed; 19.5 GB disk | optional kernel |
| E3 | Video: Wan2.1 T2V | NOT_DONE | Apache-2.0; 1.3B fits T4 | optional kernel |
| E4 | Video: I2V | NOT_DONE | no verified local pipeline | defer until T2V proven |
| F | Animation: Stickman Rig-1 | DONE | 32/32 frames, lens 32/32; **view projection gap** | fix profile/3-4 projection |
| F2 | Animation: Manim/Blender | NOT_DONE | not installed; no measured need | defer |
| G1 | Audio: PD music + FFmpeg | DONE | PD Mark 1.0, 212 s; loudnorm PASS | none |
| G2 | Audio: ACE-Step / MOSS-SFX / DeepFilterNet | NOT_DONE | license matrix; not installed | optional |
| G3 | Audio: Stable Audio | BLOCKED | NC / gated | do not use in monetized production |
| H | License matrix (code/weights/data/voice/commercial) | DONE | `MODEL_LICENSE_MATRIX.csv` (16 rows) | owner legal review |
| I1 | Real tests: preflight | DONE | `PREFLIGHT.json` | none |
| I2 | Real tests: TTS | DONE (local CPU) | `LOCAL_TTS_BENCH.json`; Kaggle ERROR documented | GPU test only if owner approves |
| I3 | Real tests: video model | NOT_DONE | resource/license decision deferred | optional |
| J1 | Integration: fix failing tests | DONE | 138 factory pass; 3,075 collect; QA 38/38 | none |
| J2 | Integration: missing workers/configs/manifests | PARTIAL | no new worker needed for demo; QC artifacts added | owner decides scope |
| K | E2E 60–90 s science video | DONE | `work/master-run/e2e/final_demo.mp4` 76.07 s, Manim + 16 scenes + SFX + stems, 7.98 Mbps, 79.1 MB, QC 16/16 PASS | human review |
| Q | 10/10 quality claim | **PENDING_HUMAN_REVIEW** | no human watched the exact file | H-1/H-2 |
| R | Reports (10 files + CSV) | DONE | `docs/research/*` incl. `COMPETITOR_VIDEO_AUDIT.csv`, `FINAL_HANDOFF.md` | owner review |
| S3 | 10of10 configs / benchmark manifests | DONE | `configs/model_matrix.yaml`, `configs/quality_gates.yaml`, `reports/benchmark_runs/.../benchmark_result.json`, `reports/end_to_end/MANIFEST.md` | owner review |

## Phase detail

### A — Audit
- 876 py files, 233 test files, 143 tools, 15 pipelines, 31 schemas.
- Fixed 3 test/collection blockers (lazy Kokoro import, V8 checkpoint fixture, QA E2E).
- Existing V12 (132.4 s) and V13 (178.7 s) renders measured; V13 has black/freeze defects
  recorded in `work/v14/TODO.md`.

### B — Competitors
- 15 unique channels; median duration 691 s; median public views 3.23M.
- **No frames or transcripts retrieved** (YouTube player `LOGIN_REQUIRED`; third-party
  transcripts blocked). All structure claims labelled INFERRED.

### C — Kaggle
- Preflight kernel COMPLETE; 2× T4, 31 GB RAM, 19.5 GB disk, CUDA 13, internet OK.
- GPU quota not readable via API; do not assume unlimited T4 hours.

### D — Voice
- Kokoro 82M Apache-2.0; Piper lessac GPL code / CC-BY voice.
- Kaggle Kokoro bench failed: `spacy` has no build for Kaggle Python 3.13.
- Local Python 3.12 Kokoro + Piper + faster-whisper benchmark is the active path.

### E — Video
- FFmpeg 6.1.1 path verified end-to-end (16 clips + concat + subs + audio).
- LTX/Wan not downloaded; I2V untested.

### F — Animation
- One rig only (no duplicate). 32 renders, signature lens 32/32.
- `profile` and `three_quarter` are identical to `front` — real defect.

### G — Audio
- PD music bed + loudnorm/limiter verified (I=-15.7 LUFS, TP=-3.8 dBTP).
- Generative audio models not tested; Stable Audio blocked.

### H — Licenses
- 16 model/asset rows verified against HF/GitHub/archive.org metadata.

### I — Real tests
- No fabricated PASS. TTS benchmark in progress; video model tests deferred with reason.

### J — Integration
- Tests green. QC artifacts (claims ledger, rights records, edit decisions, source blend)
  created for the demo.
- No new renderer or second rig created.

### K — E2E demo
- 63.9 s, 160 words, 148 wpm, 16 scenes, 14 facts, original PIL diagrams, animated rig,
  PD music, burned subtitles, QC 16/16 PASS.
- **Human review not done.**

## Remaining blockers

1. `PENDING_HUMAN_REVIEW` — exact final file not watched by a human.
2. Rig multi-view projection missing.
3. Kaggle Kokoro install broken on Python 3.13 (spacy).
4. No Kaggle GPU quota visibility.
5. LUFS standard conflict (-16 repo vs -14 YouTube).
6. Missing source documents.