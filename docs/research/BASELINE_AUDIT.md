# Baseline Audit — 2026-11-11

**Branch:** `kilo/mega-100` · **HEAD:** `3448322` · **Worktree:** `/workspaces/OpenMontage`
**Rule:** observed evidence only; no PASS without a command/artifact.

## 1. Repository scale (observed)

| Metric | Value | Source |
|---|---:|---|
| Python files (excl. node_modules) | 876 | `find . -name '*.py'` |
| Test files (`test_*.py`) | 233 | `find tests -name 'test_*.py'` |
| Tool modules (`tools/**/*.py`) | 251 | `find tools -name '*.py'` |
| Tools discovered by registry | 143 | `ToolRegistry().discover('tools')` |
| Tests collected (whole suite) | 3,075 | `pytest --collect-only -q` (exit 0) |
| Pipelines | 15 YAML manifests | `pipeline_defs/` |
| Artifact schemas | 31 JSON schemas | `schemas/artifacts/` |

## 2. Git state (observed)

- Current branch `kilo/mega-100`; **not** `main`.
- Dirty files at start (preserved, not overwritten):
  - `M flow_audit/flow_audit.log`
  - `M work/v12/qc_raw/final_v12_qc_baseline.json`
  - `M work/v12/render/final_v12.mp4`
  - untracked docs/reports/prompts/`work/v13/render`/`work/v14`/`remotion-composer/node_modules`
- No push/reset/clean/rebase/force-push performed.

## 3. Test baseline and fixes (observed)

### 3.1 Initial state
`python -m pytest tests/factory -q` → **8 failed, 122 passed, 23 skipped, 8 errors**.

Root causes (all fixed in this run):

1. **Eager optional import** — `lib/audio_engine.py` imported `kokoro` at module import;
   the test env lacks it, so 8 environment tests errored at collection.
   **Fix:** lazy import inside `_get_pipeline()`, fail-closed with an actionable install
   message. No behavior change when Kokoro is installed.
2. **Stale test fixture vs V8 §8.1** — `tests/factory/test_dry_run_chain.py` marked stages
   `completed` without `checksums`/`qc_passed`.
   **Fix:** fixture now computes SHA-256 checksums per artifact and sets `qc_passed=True`
   before writing a completed checkpoint. Production validation was **not** weakened.
3. **Ad-hoc QA script** — `tests/qa/test_08_end_to_end.py` wrote completed checkpoints at
   import without checksums. **Fix:** added `_completed()` helper; all 8 checkpoints now
   satisfy the contract.
4. **Missing optional runtime** — `soundfile` was absent from the test interpreter.
   Installed `soundfile 0.14.0` (CPU, no GPU).

### 3.2 Final state (observed)

| Command | Result |
|---|---|
| `pytest tests/factory -q` | **138 passed, 23 skipped** (85 s) |
| `pytest --collect-only -q` | **3,075 tests collected, exit 0** |
| `python tests/qa/test_08_end_to_end.py` | **38 passed, 0 failed** |
| `pytest tests -k "stickman or rig"` | collection blocked before fix; re-run after fix: rig render test passes (32/32 frames) |

## 4. Architecture inventory (observed)

### Voice / TTS
- Tools: `piper_tts`, `kokoro_tts`, `tts_kaggle`, plus cloud providers
  (`elevenlabs`, `azure`, `google`, `openai`, `dashscope`, `doubao`, `fish`, `cartesia`,
  `inworld`, `gemini`, `minimax`, `kling`).
- Local runtime state: **no Kokoro/Piper installed in the repo interpreter** before this run;
  Kokoro installed in an isolated `/tmp` venv for the Kaggle E2E asset path.
- `lib/audio_engine.py` now lazy-imports Kokoro and fails closed.

### Video
- 60+ tools under `tools/video/` (stock adapters, provider APIs, local LTX/Wan/Hunyuan/CogVideo,
  HyperFrames, Remotion caption burn, stitch/trim/compose).
- Local composition paths: `video_compose` (Remotion/HyperFrames/FFmpeg), `video_stitch`.
- No local GPU in the Codespace; GPU tests must run on Kaggle.

### Animation
- **One** rig only: `lib/stickman_rig.py` (463 lines), `lib/stickman_pose_library.py` (242),
  `lib/stickman_continuity.py` (108). 11 poses, 8 expressions, 4 views, signature lens.
- Real render test: 8 poses × 4 views = **32 PNGs**, lens present **32/32**.
- **Gap:** `profile`/`three_quarter` renders are byte-identical to `front` (only `back`
  applies a flip). The rig has no true 3/4 or profile projection. Do not claim multi-view
  support.

### Audio / Music / QC
- `assets/music/ardune_red_moon.mp3` — **Public Domain Mark 1.0**, 212.58 s, documented in
  `assets/music/manifest.json`. Safe for commercial use, no attribution required.
- QC: `tools/qa/qc.py` (ffprobe, full decode, blackdetect, freezedetect, silencedetect,
  ebur128, SRT sanity), `lib/release_gate.py`, `tools/qa/release_gate.py`.
- Thresholds: `config/qc_thresholds.json` — black ≤5%, freeze ≤2 s, silence ≤10%,
  LUFS target -16 ±1.5, TP ≤ -1.5 dBTP, subtitle drift ≤0.5 s.
  Note: repo target is **-16 LUFS**, not the -14 LUFS YouTube reference in
  `YOUTUBE_QUALITY_STANDARD.md`. This is an unresolved standards conflict, not changed here.

### Existing pilots (observed)

| Artifact | Measured | Notes |
|---|---|---|
| `work/v12/render/final_v12.mp4` | 132.425 s, 1920×1080, 30 fps, h264+aac, 20.6 MB | Kokoro narration, SRT, 41 scenes; preserved |
| `work/v13/render/v13_preview.mp4` | 178.733 s, 1920×1080, 30 fps, h264+aac, 25.7 MB | QC **WARNING**: music-only, -70 LUFS, 2 NOT_RUN; `work/v14/TODO.md` lists black frames 0–3.77 s and 83.93–102.87 s, freezes 70.63–83.1 s |
| `projects/pilot/ekzoplanety-poisk-vtoryh-zemel` | script only | earlier pilot |
| `assets/signal-from-tomorrow-demo.mp4` | 20.9 MB | demo asset, not a current pilot |

**Conclusion:** the repo already has a working 1080p30 FFmpeg path and a Kokoro narration
path; the main weaknesses are black/freeze segments in V13, no music in V12/V13, and no
verified multi-view rig.

## 5. Environment (observed)

### Codespace (local)
- CPU-only; no `nvidia-smi`, no CUDA, no `torch` in the repo interpreter.
- `ffmpeg 6.1.1`, `ffprobe 6.1.1`, PIL 13.0, numpy 2.5.4, pytest 9.2.
- Disk: `/` 8.3 GB free; `/tmp` 40 GB free.
- Python 3.14.2 (repo), Python 3.12.3 available (isolated venv used for Kokoro/cairosvg).

### Kaggle preflight (observed, real kernel)
- Kernel `forts845/openmontage-preflight`, status COMPLETE.
- **2× Tesla T4**, 15,360 MiB each (14.56 GiB usable), driver 580.178.04.
- CUDA 13.0, PyTorch 2.11.0+cu130, `cuda_available=True`.
- 4 vCPU, 31.35 GB RAM, **19.5 GB free disk**.
- Internet: HuggingFace 200, PyPI 200, GitHub 200.
- Preflight JSON: `work/master-run/kaggle/preflight/output/PREFLIGHT.json`.

## 6. Gaps / blockers (observed)

| ID | Gap | Impact |
|---|---|---|
| B1 | Missing source documents | requirements reconstructed; no hidden spec can be honored |
| B2 | No local GPU | all heavy model tests must go through Kaggle |
| B3 | Kaggle disk 19.5 GB | only **one** heavy video model at a time; LTX (~9–12 GB) + Wan (~20 GB) cannot coexist |
| B4 | No Kaggle quota API | GPU weekly quota cannot be read programmatically; must not assume unlimited T4 hours |
| B5 | Rig views nominal | profile/3/4 identical to front; fix before claiming multi-view |
| B6 | No human review | cannot claim 10/10; final status `PENDING_HUMAN_REVIEW` |
| B7 | LUFS standard conflict | repo -16 vs YouTube -14; owner decision needed |
| B8 | No transcript access | competitor audit is metadata-only |

## 7. Rights baseline (observed)

- Repo license: see `LICENSE` (AGPL-3.0 per prior audit).
- Music: PD Mark 1.0 (documented).
- Model licenses: see `MODEL_LICENSE_MATRIX.csv`.
- No secrets read or printed; `KAGGLE_API_TOKEN` presence checked without printing value.