# Implementation Plan: OpenMontage V13 — cleanup, core fixes, V13 pilot

## Overview
Execute `OpenMontage_V13_Unified_Review_Architecture_and_Agent_Task.docx` (Appendix D = VIDEO_BUILD_TASK_V13.md) on the live branch `kilo/mega-100` (HEAD `1717fc20`). Work strictly in the current branch (no checkout/switch/reset/new branch), $0 budget, no Flow/Veo/paid APIs, no Remotion/HyperFrames. Deliverables: cleaned active architecture, fixed zero-cost/approval/release-gate code + regression tests, reduced duplication, new V13 MP4 pilot (FFmpeg+PIL), full QC JSON/MD report, contact sheet, review package. Final status: READY_FOR_OWNER_REVIEW / PARTIAL / BLOCKED (never OWNER_APPROVED).

## Architecture Decisions
- Single public production orchestrator decided by S3.1 call-graph evidence (run_factory.py / assemble_pilot_final.py / run_episode.py).
- Zero-cost: `lib/zero_cost_gate.py` is the single fail-closed gate; `BudgetGuard` must not turn unknown cost into 0.0.
- Approval propagation: no hardcoded `user_approved=True` in provider calls.
- Release gate: explicit REQUIRED vs SOFT registry; NOT_RUN/missing/unknown REQUIRED => `can_publish=False`.
- Deduplication: canonical facades per role + thin wrappers; no module removal without zero-callers proof + deletion manifest.
- V13 pilot: existing assets only, generation=0, Kokoro `af_heart` if available else voice stage BLOCKED, no new images.

## Task List

### Phase 0: Identification, safety tag, baseline
- [ ] Task 0.1: Repo/branch/HEAD/status/disk inventory; save raw stdout to work/v13/logs
- [ ] Task 0.2: Create annotated safety tag `pre-v13-maintenance-<utc>` on current HEAD
- [ ] Task 0.3: Baseline `pytest --collect-only -q` + test suites; record collected/errors/failed
- [ ] Task 0.4: Backup dirty/user-changed file inventory + SHA256 outside repo

### Phase 1: Cleanup manifest (S2)
- [ ] Task 1.1: Build cleanup_manifest.json (path, tracked, type, size, sha256, last_commit, refs x4, reproducible, action, reason, risk, backup_path, status) — 3 reference checks per candidate
- [ ] Task 1.2: Archive proven-stale docs to archive/ via git mv + archive/README.md
- [ ] Task 1.3: Remove only proven regenerable caches/temp (S2.4) with manifest; NEEDS_OWNER where proof incomplete
- [ ] Task 1.4: Re-run pytest collect; zero new collection errors vs baseline

### Phase 2: Architecture fixes (S3 P0)
- [ ] Task 2.1: Call-graph + entrypoints.json; pick single canonical production orchestrator
- [ ] Task 2.2: Fix BudgetGuard/zero_cost_gate (None=unknown, only explicit 0.0 allowed); regression tests (6 required cases)
- [ ] Task 2.3: Fix image_generation_engine approval propagation (no hardcoded True); mock-provider test
- [ ] Task 2.4: Make release_gate fail-closed (REQUIRED registry; NOT_RUN/missing/unknown=>can_publish=False); regression tests
- [ ] Task 2.5: Flow/CDP fail-closed guard dry-run test (network count = 0)

### Phase 3: Dedup (S3 P1)
- [ ] Task 3.1: AST import graph + runtime call graph for audio/render/QC/state
- [ ] Task 3.2: Canonical facades per role; thin wrappers for duplicates; single QC thresholds config + consistency tests
- [ ] Task 3.3: Single state/resume mechanism with checkpoint compatibility

### Phase 4: V13 production (S4)
- [ ] Task 4.1: Script + claims (script_v13.md, claims_v13.json, script_blocks.json); claim IDs + sources; owner framing note
- [ ] Task 4.2: Storyboard/EDL/assets/rights (24–32 scenes, provenance, no AI generation)
- [ ] Task 4.3: Voice/ASR/captions (Kokoro af_heart; BLOCKED if missing; WER gate; SRT)
- [ ] Task 4.4: FFmpeg/PIL assembly v13_master.mp4 + low-res preview first
- [ ] Task 4.5: QC (ffprobe, full decode, ebur128, blackdetect, silencedetect, freezedetect, scdet, A/V delta, subtitle lint, SHA/perceptual hash)

### Phase 5: Review package + final (S5/S6)
- [ ] Task 5.1: v13_qc.json, v13_qc.md, contact sheet, watch_notes.md, claims_and_rights, rubric.csv, owner_review_template.json
- [ ] Task 5.2: Final report (Appendix A2 format), compare before/after, status READY_FOR_OWNER_REVIEW/PARTIAL/BLOCKED

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Kokoro/weights missing | Voice BLOCKED; can't render V13 | Verify live deps early; continue safe non-render tasks; mark PARTIAL/BLOCKED |
| ASR missing | WER gate BLOCKED | Don't fake WER=0; manual listen path; mark accordingly |
| Dirty/user files | Can't touch safely | Backup outside repo or NEEDS_OWNER; don't reset/stash |
| Disk <15% | Stop heavy work | df before render; clean only S2.4 regenerable caches |

## Open Questions
- None blocking: proceed with live verification of deps and entrypoints.
