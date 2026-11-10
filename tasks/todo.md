# Tasks: OpenMontage V13 — cleanup, core fixes, V13 pilot (branch kilo/mega-100)

Statuses: [x] done, [~] in progress, [ ] pending, [BLOCKED] = cannot proceed without dep/owner

## Phase 0 — identification, safety tag, baseline (DONE)
[x] 0.1 Repo/branch/HEAD/status/disk inventory + raw logs in work/v13/logs/s0/
[x] 0.2 Safety tag `pre-v13-maintenance-20261110-114934` on HEAD 1717fc20
[x] 0.3 Baseline pytest collect: 2803 collected, 3 pre-existing errors (soundfile×2, checkpoint test)
[x] 0.4 Dirty/untracked inventory + SHA256 of modified tracked files saved

## Phase 1 — cleanup manifest & archive (S2) — DONE
[x] 1.1 cleanup_manifest.json (26 candidates; 11 archived, 15 keep; 3-way reference evidence)
[x] 1.2 Archived 11 stale V7/V8 docs via git mv into archive/ + archive/README.md
[x] 1.3 Cleaned regenerable caches: 37 __pycache__ dirs, 517 .pyc, 1 .pytest_cache (S2.4)
[x] 1.4 Re-run pytest collect: back to baseline 3 pre-existing errors, 0 NEW collection errors

## Phase 2 — architecture P0 fixes + regression tests (S3) — DONE
[x] 2.1 entrypoints.json + call graph; canonical = scripts/run_factory.py (run_episode = test-covered alt, venv missing; assemble_pilot_final = FFmpeg renderer helper)
[x] 2.2 budget_guard.py: estimated_usd default None; unknown cost => blocked (not 0.0)
[x] 2.3 Zero-cost regression tests: tests/lib/test_budget_guard.py (8) + tests/factory/test_zero_cost_flow_cdp.py (2)
[x] 2.4 image_generation_engine.py: pass user_approved through (no hardcoded True)
[x] 2.5 release_gate.py: REQUIRED vs SOFT registry; NOT_RUN/missing/unknown REQUIRED => can_publish=False
[x] 2.6 Release-gate regression tests: tests/lib/test_v13_release_gate.py (10; every case asserts can_publish)
[x] 2.7 Flow/CDP fail-closed dry-run test: tests/factory/test_zero_cost_flow_cdp.py

## Phase 3 — dedup P1 (S3.5)
[~] 3.1 AST import graph + runtime call graph — DONE (stickman/hyperframes proven referenced => KEEP, nothing provably dead deleted)
[ ] 3.2 Document canonical facades per role; thin wrappers only where zero-callers proven
[ ] 3.3 QC thresholds single canonical config (config/qc_thresholds.json + final_qc.py aligned to LUFS -16 ±1.5, TP -1.5); consistency test
[ ] 3.4 Reuse existing state_store + checkpoint; no third state store

## Phase 4 — V13 production prep (S4.1/S4.2)
[ ] 4.1 Script draft script_v13.md + claims_v13.json + script_blocks.json; claim IDs + sources; owner approval NOTE (no final render without owner approval)
[x] 4.2 Storyboard/EDL/assets/rights draft — IN PROGRESS (from frames_klein + shot_list, ~170-190s, no new AI generation)
[ ] 4.3 Voice/ASR: BLOCKED (Kokoro af_heart + faster_whisper missing); no placeholder WAV — documented

## Phase 5 — V13 render + QC (S4.4/S4.5)
[ ] 5.1 Low-res preview from EDL; verify scene IDs/timing
[ ] 5.2 v13_master.mp4 (FFmpeg/PIL) music-only preview (narration BLOCKED), clearly marked
[ ] 5.3 v13_qc.json + v13_qc.md; full QC battery
[ ] 5.4 Contact sheet + review_package (watch_notes.md, claims_and_rights, rubric.csv, owner_review_template.json)

## Phase 6 — final report + status (S5/S6)
[ ] 6.1 Final report (Appendix A2 format); before/after comparison
[ ] 6.2 FINAL STATUS: READY_FOR_OWNER_REVIEW / PARTIAL / BLOCKED (never OWNER_APPROVED)
