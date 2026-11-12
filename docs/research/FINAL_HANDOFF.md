# Final Handoff — 2026-11-11

**Branch:** `kilo/mega-100` · **HEAD:** `f066842` (docs checkpoint) after `bcedcd4`
**Working tree:** dirty only in pre-existing user files (`flow_audit/flow_audit.log`,
`work/v12/qc_raw/final_v12_qc_baseline.json`, `work/v12/render/final_v12.mp4`); no user
work was overwritten.
**Source task:** `OpenMontage_10of10_Four_Factories_OpenCode_Agent_Task_2026-11-11.md`
(origin/main @ `2f8f1915`, SHA-256 `8d8fe0f0…`). The second named file
(`OpenMontage_4_Factories_Deep_Research_2026-11-11.md`) is not present in any reachable
ref; the 10of10 document marks it optional and embeds the model lists.

## Files created / modified

| Area | Files |
|---|---|
| Research | `docs/research/SOURCE_FILES_DISCOVERY.md`, `TASK_STATEMENT_RECONSTRUCTED.md`, `BASELINE_AUDIT.md`, `COMPETITOR_VIDEO_AUDIT.md`, `COMPETITOR_VIDEO_AUDIT.csv`, `YOUTUBE_QUALITY_STANDARD.md`, `MODEL_LICENSE_MATRIX.csv`, `MODEL_TEST_MATRIX.csv`, `FACTORY_DECISION_REPORT.md`, `MASTER_REQUIREMENTS_TRACKER.md`, `OPENMONTAGE_EXECUTION_CHECKPOINT.md`, `FINAL_HANDOFF.md` |
| Config | `configs/model_matrix.yaml`, `configs/quality_gates.yaml` |
| Tests | `lib/audio_engine.py` (lazy Kokoro import), `tests/factory/test_dry_run_chain.py`, `tests/qa/test_08_end_to_end.py` |
| Kaggle | `work/master-run/kaggle/preflight/`, `work/master-run/kaggle/tts_bench/` |
| Benchmarks | `work/master-run/tts_bench/LOCAL_TTS_BENCH.json`, `reports/benchmark_runs/2026-11-11-tts-local/benchmark_result.json` |
| E2E | `work/master-run/e2e/` (video, QC, SRT, manifests, scripts), `reports/end_to_end/MANIFEST.md` |

## Commands and results

| Command | Result |
|---|---|
| `pytest tests/factory -q` | 138 passed, 23 skipped (exit 0) |
| `pytest --collect-only -q` | 3,075 tests collected (exit 0) |
| `python tests/qa/test_08_end_to_end.py` | 38/38 passed |
| Kaggle preflight | kernel `forts845/openmontage-preflight`, COMPLETE |
| Kaggle TTS | kernel `forts845/openmontage-tts-bench`, **ERROR** (spacy/py3.13) |
| Local TTS | `LOCAL_TTS_BENCH.json` — Kokoro WER 2.78%, RTF 1.326; Piper WER 2.78%, RTF 0.805 |
| E2E QC | `qc_report.json` — 16/16 PASS, verdict PASS |

## Kaggle facts

- Preflight: **2× Tesla T4, 14.56 GiB each**, driver 580.178.04, CUDA 13.0,
  PyTorch 2.11.0+cu130, 4 vCPU, **31.35 GB RAM**, **19.5 GB free disk**,
  HuggingFace/PyPI/GitHub HTTP 200.
- Quota: not exposed by the Kaggle API; no assumption made. No paid GPU used.
- TTS kernel failed during `pip install misaki[en]` on Kaggle Python 3.13 (`spacy`
  build failure). No weights were downloaded by that kernel.

## Model decisions

| Factory | CORE | FALLBACK | EXPERIMENTAL / BLOCKED |
|---|---|---|---|
| Voice | Kokoro-82M `af_heart` (Apache-2.0; normalized WER 0.0%, RTF 1.326) | Piper `en_US-lessac-medium` (GPL code / CC-BY voice; normalized WER 0.0%, RTF 0.805); Qwen3-TTS 0.6B Base tested (normalized WER 1.0%, VRAM 3.35 GB) | Ming-3.0-tts-0.5B (MIT, 3.0 GB, not run), CosyVoice3 (9.75 GB), VoxCPM2 (4.96 GB), MOSS-TTS-Local (6.14 GB); Qwen paid API BLOCKED |
| Video | FFmpeg 6.1.1 + Ken Burns + PIL | Wan2.1-T2V-1.3B (Apache; not run) | LTX-Video BLOCKED_STORAGE (repo 254 GB; 19.5 GB disk), HunyuanVideo-1.5 HIGH_END_NOT_T4 (~33 GB), I2V NOT TESTED |
| Animation | Stickman Rig-1 + PIL/SVG + FFmpeg | — | Manim not installed; Blender not installed |
| Audio | PD music + FFmpeg loudnorm/limiter | — | ACE-Step1.5 (MIT, 10.09 GB, not run), MOSS-SoundEffect v2.0 (Apache, 11.23 GB, not run), Stable Audio NC/gated BLOCKED, DeepFilterNet not installed |

## Metrics / hashes

- E2E: `work/master-run/e2e/final_demo.mp4` — 76.07 s, 1920×1080@30, H.264 High,
  AAC-LC 48 kHz stereo, 7.98 Mbps video, 79.1 MB.
  SHA-256 `2b22174dcc264a412bd26517368ae6e64db8a00ad23a25888e1d182bb599cb01`.
- QC: 16/16 PASS; loudness -15.7 LUFS, TP -3.8 dBTP; black 0; freeze 0; silence 0.
- TTS: `work/master-run/tts_bench/LOCAL_TTS_BENCH.json`; per-run
  `reports/benchmark_runs/2026-11-11-tts-local/benchmark_result.json`.
- Kaggle preflight: `work/master-run/kaggle/preflight/output/PREFLIGHT.json`.

## Quality score

**Not scored.** No human has watched the exact final master; no independent reviewer
has scored it. Per the 10of10 hard gates, the status is `PENDING_HUMAN_REVIEW`, not
`PASS`, not `10/10`, not `READY_FOR_OWNER_REVIEW`.

## Blockers

1. Human watch-through + independent 1–10 review (H-1/H-2).
2. Manim diagram in the E2E sample (tool not installed).
3. I2V/T2V tests not run (LTX storage/licence; Wan not downloaded).
4. ACE-Step/SFX/DeepFilterNet not tested.
5. Rig `profile`/`three_quarter` projection identical to `front`.
6. Kaggle Kokoro install broken on Python 3.13 (`spacy`).
7. `OpenMontage_4_Factories_Deep_Research_2026-11-11.md` not reachable.
8. LUFS house target -16 vs YouTube -14 reference (owner decision).
9. AAC 250 kbps vs 384 kbps reference (review item).

## Selected stack

- **Primary:** Kokoro-82M voice → PIL/SVG diagrams + Stickman Rig-1 → FFmpeg render →
  PD music + loudnorm → `tools/qa/qc.py` release gate.
- **Fallback:** Piper voice; Wan2.1 T2V if a T2V shot is needed and disk allows.
- **High-end backlog:** LTX-Video 0.9.6 I2V, HunyuanVideo-1.5, ACE-Step 1.5,
  MOSS-SoundEffect v2.0 — metadata/licence only; no download.

## Exact next step

1. Human opens `work/master-run/e2e/final_demo.mp4`, watches end-to-end, and records a
   1–10 score with reviewer identity/date.
2. If approved: fix the rig view projection, add a Manim diagram, then run one LTX or
   Wan T2V test only after an exact-file size check against the 19.5 GB Kaggle disk.
3. Only then update `FACTORY_DECISION_REPORT.md` and consider a release-gate pass.

No `OWNER_APPROVED`, `PUBLISH_READY`, `FINAL_MASTER`, or `READY_FOR_OWNER_REVIEW` status
is created automatically.
---

## Update 2026-11-12 — 10of10 Phase 1–5 results

### Voice
- **Kokoro-82M:** normalized WER **0.0%**, RTF 1.326, load 10.61 s (local CPU).
- **Piper lessac:** normalized WER **0.0%**, RTF 0.805 (local CPU).
- **Qwen3-TTS-12Hz-0.6B-Base:** **PASS (technical)** on Kaggle T4 — 3 sections, 74.56 s audio,
  load 22.51 s, RTF 2.50–3.08, peak VRAM **3347 MB**, 10-chunk VRAM flat (no leak),
  raw WER 6.47% / **number-normalized WER 1.0%**. Naturalness/human listening **PENDING**.
- **Ming-3.0-tts-0.5B:** `BLOCKED_INTEGRATION` (requires GitHub repo; 3.0 GB fits disk).
- CosyVoice3 (9.75 GB), VoxCPM2 (4.96 GB), MOSS-TTS-Local (6.14 GB): `BLOCKED_TIME`
  (fit disk; integration not done). Qwen paid API: `EXCLUDE` ($0).

### Video
- **Wan2.1-T2V-1.3B:** `BLOCKED_STORAGE` — repo 17.57 GB > 75% of 19.5 GB free.
- **LTX-Video 0.9.6 distilled:** `BLOCKED_STORAGE` — 6.34 GB + ~19.3 GB T5 + VAE > 25 GB.
- **HunyuanVideo-1.5:** `HIGH_END_NOT_T4` (~33 GB). I2V/T2V **NOT TESTED**.

### Animation
- **Manim CE 0.22.1:** installed (libcairo/pango dev deps), rendered 11.07 s 1080p ice-density
  diagram; used in the E2E.
- **Stickman Rig-1:** 32/32 frames, lens 32/32; view projection gap remains.
- Blender: not installed; desktop/manual.

### Audio
- **DeepFilterNet3:** RTF 0.055; extreme synthetic noise WER 69.2%→69.2% (no gain),
  mild 0%→0% — `PARTIAL`, not a CORE win for clean TTS.
- **ACE-Step1.5:** 10.09 GB, MIT — not downloaded (`BLOCKED_TIME`).
- **MOSS-SoundEffect v2.0:** 11.23 GB, Apache-2.0 — not downloaded (`BLOCKED_TIME`).
- Stable Audio Open 1.0 (CC-BY-NC) and Small (gated): `EXCLUDE`/`LICENSE_BLOCKED`.
- E2E master: I=-16.0 LUFS, TP=-2.0 dBTP.

### E2E
- `work/master-run/e2e/final_demo.mp4` — **76.07 s**, 1920×1080@30, H.264 High, AAC 48 kHz,
  7.98 Mbps video, 79.1 MB, SHA-256 `2b22174d…`.
- Manim intro + 16 PIL scenes + Rig-1 + PD music + 3 original SFX + stems; QC **16/16 PASS**.

### 10/10 rubric status

| Criterion | Weight | Objective status | Human score |
|---|---:|---|---|
| Hook / packaging | 12% | hook variants written; no human A/B | PENDING |
| Scientific accuracy / claims | 18% | 14/14 claims ledger + sources; no unresolved FAIL | PENDING |
| Story arc / pacing | 12% | 76 s vertical slice; not a full release | PENDING |
| Visual relevance / clarity | 12% | original diagrams; no frame review | PENDING |
| Motion / visual pacing | 10% | 17 cuts, zoom/pan/Manim/rig; QC motion PASS | PENDING |
| Narration / audio mix | 10% | -16 LUFS, TP -2.0, stems | PENDING |
| Captions / accessibility | 8% | ≤42 chars, 2 lines; QC PASS | PENDING |
| Visual consistency | 8% | single palette; no human art-direction review | PENDING |
| Originality | 5% | original diagrams/rig/script; no competitor assets | PENDING |
| Rights / provenance | 5% | 5/5 records PASS; PD music; CC-BY voice | PENDING |

**No 10/10 claim.** Hard gate H-1 (human watch-through of the exact master) and H-2
(independent reviewer) are not satisfied.
