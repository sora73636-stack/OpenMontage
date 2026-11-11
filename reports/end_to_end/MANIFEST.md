# End-to-end sample — manifest

**Sample:** `work/master-run/e2e/final_demo.mp4` (65.0 s, 1920×1080@30, H.264 High,
AAC-LC 48 kHz stereo, Fast Start, 8.0 Mbps video, 66.9 MB).
**SHA-256:** see `work/master-run/logs/deliverables_final.sha256`.
**QC:** `work/master-run/e2e/qc_report.json` — 16/16 PASS.
**Status:** `PENDING_HUMAN_REVIEW`.

## Included artifacts

| Artifact | Path |
|---|---|
| Final video | `work/master-run/e2e/final_demo.mp4` |
| QC report | `work/master-run/e2e/qc_report.json` |
| Narration manifest | `work/master-run/e2e/narration.json` |
| Subtitles (SRT, ≤42 chars/line) | `work/master-run/e2e/subtitles.srt` |
| Claim ledger | `work/master-run/e2e/claims.json`, `claim_ledger.md` |
| Rights records | `work/master-run/e2e/rights_records.json` |
| Edit decisions | `work/master-run/e2e/edit_decisions.json` |
| Contact sheet | `work/master-run/e2e/contact_sheet.jpg` |
| Rig contact sheet | `work/master-run/animation/rig_contact_sheet.jpg` |
| Stems | narration: `work/master-run/e2e/audio/`; music: `assets/music/ardune_red_moon.mp3` |

## What this sample is

A technical vertical slice: 14 original PIL diagrams, animated Stickman Rig-1 overlay,
Piper narration, PD music, burned subtitles, full QC. It is **not** a 15–20 minute
release and it is **not** a 10/10 claim. The 10of10 task requires a Manim diagram and a
human watch-through; Manim is not installed and no human review has occurred.

## Missing from the full 10of10 sample

- Manim diagram (tool not installed; PIL diagram used instead).
- One I2V clip (LTX/Wan not tested; procedural motion used instead).
- 1–3 purposeful SFX (music only).
- Human watch-through + independent reviewer score.