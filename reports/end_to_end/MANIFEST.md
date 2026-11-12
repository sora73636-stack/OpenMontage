# End-to-end sample — manifest (v3)

**Sample:** `work/master-run/e2e/final_demo.mp4` — 76.07 s, 1920×1080@30, H.264 High,
AAC-LC 48 kHz stereo, Fast Start, 7.98 Mbps video, 79.1 MB.
**SHA-256:** `2b22174dcc264a412bd26517368ae6e64db8a00ad23a25888e1d182bb599cb01`
**QC:** `work/master-run/e2e/qc_report.json` — 16/16 PASS (verdict PASS).
**Status:** `PENDING_HUMAN_REVIEW`.

## What is in the cut

- **0–11.07 s:** original Manim CE diagram (ice density / why ice floats), 1080p30.
- **11.07–76.07 s:** 16 original PIL diagrams with zoom/pan motion and the animated
  Stickman Rig-1 overlay.
- **Audio stems:** narration (Piper lessac), music (PD Mark 1.0), ambience + ice crack +
  sonar (original synthesized SFX), final master.
- **Subtitles:** burned-in, ≤42 chars/line, max 2 lines, shifted to the Manim intro.
- **Loudness:** I=-16.0 LUFS, TP=-2.0 dBTP.

## Artifacts

| Artifact | Path |
|---|---|
| Final video | `work/master-run/e2e/final_demo.mp4` |
| QC report | `work/master-run/e2e/qc_report.json` |
| Narration manifest | `work/master-run/e2e/narration.json` |
| Subtitles | `work/master-run/e2e/subtitles.srt` |
| Edit decisions (17 cuts) | `work/master-run/e2e/edit_decisions.json` |
| Rights records (5) | `work/master-run/e2e/rights_records.json` |
| Source blend | `work/master-run/e2e/source_blend_report.json` |
| Stems | `narration76.wav`, `audio76.wav`, `sfx/*.wav`, `manim/manim_ice_30.mp4` |
| Manim scene | `work/master-run/animation/manim_ice.py` |
| Hook variants | `work/master-run/e2e/hook_variants.md` |
| Contact sheet | `work/master-run/e2e/contact_sheet.jpg` |

## Missing from the full 10of10 sample

- One I2V clip (LTX/Wan blocked by Kaggle disk; procedural motion used instead).
- ACE-Step score / MOSS-SFX (not downloaded; PD music + synthesized SFX used).
- Human watch-through + independent reviewer score.

## Integrity

No third-party footage, no YouTube downloads, no paid API, no Flow/Veo.
Music PD Mark 1.0; voice CC-BY-4.0 (attribution in credits); diagrams/rig original.