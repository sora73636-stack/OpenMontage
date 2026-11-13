# STAGE B SUMMARY

- Stage: B (Phase 4 P0 + Phase 6 fixtures)
- UTC: 2026-11-13T06:58:26Z
- Repo commit: 185af2eb8d4a18825219677612f9b6458702f122 (Stage A base)
- Kaggle CLI: 2.2.5; account forts845
- Status: PASS for LTX, FLUX, CosyVoice, ESRGAN runtime; RIFE BLOCKED; licenses: 1 FAIL, 1 CONDITIONAL PASS, 3 PASS.
- GPU used (upper bound): 1.007 GPU-hours; quota-accounted ~0.50 h.
- Blockers:
  - Practical-RIFE: CANCEL_ACKNOWLEDGED at ~90 s (v1, v2); cause not established; diagnostics complete.
  - Real-ESRGAN x4plus: weight license not explicit -> license FAIL.
  - CosyVoice/Kokoro/Whisper/DepthAnything: license basis model_card_metadata -> CONDITIONAL PASS.
  - LTX/FLUX attention backend UNKNOWN.
- Next stage preconditions:
  - Human quality review of LTX video, FLUX images, CosyVoice audio, ESRGAN images.
  - Real-ESRGAN weight license clarification or replacement (license exception requires human approval).
  - RIFE investigation in Kaggle web UI before any further GPU attempt.
- Evidence: audit/PRODUCTION_SMOKE_TEST_REPORT.md (Stage B section), audit/results.json, audit/results/component_results.json.
