# STAGE A SUMMARY

- Stage: A (Phase 0, Phase 1, Phase 2 shared helper + env/P2.2 notebook, Phase 3 license collection)
- UTC: 2026-11-13T04:21:09Z
- Repo commit: 185af2eb8d4a18825219677612f9b6458702f122
- Kaggle kernel: https://www.kaggle.com/code/forts845/openmontage-stage-a-env-smoke (version 2)
- Status: **PASS** (environment, libx264, NVENC); licenses collected; no models run.
- GPU: 2 x Tesla T4 (14911 MiB each, cc 7.5), torch 2.11.0+cu130
- Wall time: 36.147 s; upper-bound GPU-hours: 0.020082
- Blockers:
  - FINAL_PRODUCTION_DECISION not found (documented, not invented)
  - Real-ESRGAN x4plus weight license: FAIL
  - DepthFlow: AGPL-3.0 -> legal review BLOCKED
  - CosyVoice 3 reference voice: BLOCKED (no cleared recording)
  - Music/SFX: NOT TESTED (no assets selected)
  - Live Kaggle docs: reCAPTCHA; quotes from search index
- Next stage preconditions:
  - Stage B needs: cleared reference voice or approved synthetic voice; Real-ESRGAN weight license decision; model weight download plan.
  - Stage B/C/D need the GPU quota confirmed in the account UI.
- Evidence: `audit/PRODUCTION_SMOKE_TEST_REPORT.md`, `audit/results.json`, `audit/licenses/STATUS.json`.
