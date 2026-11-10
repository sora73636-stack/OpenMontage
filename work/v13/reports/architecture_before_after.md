# Architecture before/after — V13 maintenance (kilo/mega-100 @ 1717fc20)

## Before (snapshot + live)

- Budget enforcement split across two incompatible policies:
  - `lib/budget_guard.py::guard()` defaulted `estimated_usd=0.0`, so an
    unknown cost was treated as free and allowed (`status="success"`).
  - `lib/zero_cost_gate.py::evaluate_call()` correctly blocks `cost_usd=None`
    and unknown routes (fail-closed).
  - Result: `BudgetGuard` could let an unpriced route through while the gate
    would block it — contradictory policies (S3.2).
- Image generation approval propagation broken:
  - `lib/image_generation_engine.py::execute_approved()` called
    `provider.execute_image(..., user_approved=True)` with a hardcoded literal
    instead of the caller's `user_approved` (S3.3).
- Release gate not fail-closed:
  - `lib/release_gate.py` treated `NOT_RUN` as `WARNING` with
    `can_publish=True`; no REQUIRED vs SOFT check declaration (S3.4).
- QC threshold drift:
  - `config/qc_thresholds.json` (`lufs_target=-14`, `lufs_tolerance=2.0`)
    and `lib/final_qc.py::DEFAULT_THRESHOLDS` (`lufs_target=-14`,
    `lufs_tolerance=2.0`) contradicted the V13 task requirement
    (−16 LUFS-I ±1.5 LU, true_peak ≤ −1.5 dBTP) (S3.5).
- Duplication without a proven canonical role:
  - Overlapping audio modules (`audio_engine`, `audio_production_engine`,
    `audio_mixer`, `audio_mixing`, `audio_master`, `audio_alignment`,
    `audio_sync`, `audio_qc`) and render paths (`render_engine`,
    `render_integration`, direct assembly). Overlap was observed but no
    module was proven dead (no AST/import/call/CI/test/runtime refs check).
- Two entrypoint candidates without a documented decision:
  - `scripts/run_factory.py` (13-stage, complete, untested) and
    `scripts/run_episode.py` (test-covered, real toolchain venv missing).

## After

- `lib/budget_guard.py`: `estimated_usd` default is now `None`; `None` means
  unknown cost → blocked/fallback, never free. Only explicit `0.0` is allowed.
  Module-level `guard()` matches. Callers passing explicit `0.0`
  (`lib/scene_router.py`) are unaffected.
- `lib/image_generation_engine.py`: `execute_approved()` now passes the real
  `user_approved` argument through to `provider.execute_image`; no hardcoded
  `True`. All V13 generation routes remain disabled; tested with a mock.
- `lib/release_gate.py`: explicit REQUIRED vs SOFT check registry
  (`REQUIRED_CHECK_IDS`, `declare_required`). A REQUIRED check that is
  missing, NOT_RUN, BLOCKED, FAIL or unknown → `can_publish=False`.
  SOFT `NOT_RUN` → `WARNING`, stays visible. No default PASS with incomplete
  coverage. `GateDecision` carries `required_problems` and `coverage_complete`.
- `config/qc_thresholds.json` and `lib/final_qc.py::DEFAULT_THRESHOLDS`:
  aligned to the V13 requirement (`lufs_target=-16.0`, `lufs_tolerance=1.5`,
  `true_peak_max=-1.5`); config is the single canonical source; consistency
  tests added.
- Entry points documented in `work/v13/reports/entrypoints.json`:
  `scripts/run_factory.py` = canonical production orchestrator;
  `scripts/assemble_pilot_final.py` = internal FFmpeg renderer helper;
  `scripts/run_episode.py` = test-covered alternative (venv missing).
- Regression tests added:
  - `tests/lib/test_budget_guard.py` (8 cases)
  - `tests/lib/test_release_gate.py` (10 cases; every case asserts `can_publish`)
  - `tests/factory/test_zero_cost_flow_cdp.py` (Flow/CDP blocked, no provider
    call; retry does not duplicate job)
- No module was deleted: every removal requires zero AST/import/call/CI/test/
  runtime refs + safety tag + deletion manifest (S2.1). No protected paths
  touched (`.git/`, `.gflow/`, `assets/music/`, weights, source media, V1–V12,
  user changes).

## Risks / open

- `kokoro` + `faster_whisper` missing → V13 voice/ASR stages BLOCKED; no
  placeholder WAV created; no final narrated V13 master possible until owner
  installs Kokoro `af_heart` weights and approves the script/story framing.
- Existing pilot narration (`narration_master_norm.wav`, 132s) is V12's, uses
  the forbidden V13 hook `Start with a simple question`, and is not verified
  as Kokoro `af_heart` — not substituted for V13 voice.
