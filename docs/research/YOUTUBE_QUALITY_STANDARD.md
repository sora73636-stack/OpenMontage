# YouTube Quality Standard — derived, with evidence labels

**Status:** PROPOSED. Thresholds marked `GATE` are enforceable in `tools/qa/qc.py`;
thresholds marked `STANDARD` are editorial targets for human review.
**Evidence basis:** public metadata from 15 science videos (`COMPETITOR_VIDEO_AUDIT.md`),
the existing `config/qc_thresholds.json`, and the repo's delivery target
(1920×1080, 30 fps, H.264, AAC, ~-14 LUFS). No competitor frames were observed.

## 1. Hook (first 10 seconds)

| Rule | Target | Class | Evidence |
|---|---|---|---|
| H1 | A concrete anomaly/object/claim appears within 0–5 s | STANDARD | inferred from top titles; not frame-verified |
| H2 | The title names a specific object or test, not a topic | STANDARD | 15/15 public titles |
| H3 | No logo sting or slow fade before the hook | STANDARD | inference |
| H4 | First spoken sentence < 15 words | STANDARD | editorial rule |

## 2. Script / information density

| Rule | Target | Class |
|---|---|---|
| S1 | One claim/idea per 20–30 s | STANDARD |
| S2 | Every factual claim has a source id in the evidence ledger | GATE (repo contract) |
| S3 | No claim marked `needs_verification` in a released cut | GATE |
| S4 | Narration 140–160 wpm (English documentary) | STANDARD |
| S5 | Spoken numbers written out or shown on screen | STANDARD |

## 3. Visual / animation

| Rule | Target | Class | Evidence |
|---|---|---|---|
| V1 | Visual change (cut, motion, or overlay) every 2–4 s | STANDARD | inferred channel formats |
| V2 | No static frame > 2 s outside an intentional `static_by_design` segment | GATE (`freezedetect`, `static_segments` exemption) |
| V3 | No black segment > 0.5 s | GATE (`blackdetect`) |
| V4 | Diagrams carry claim ids / source labels | GATE (repo QC `claim_ids`) |
| V5 | Character rig signature detail present in every shot | GATE (rig QC) |

## 4. Audio

| Rule | Target | Class |
|---|---|---|
| A1 | Integrated loudness -14 ± 2 LUFS | GATE (`ebur128`) |
| A2 | True peak ≤ -1.5 dBTP | GATE |
| A3 | No silence run > 3 s; silence ratio ≤ 10% | GATE (`silencedetect`) |
| A4 | Narration ≥ 6 dB above music | STANDARD |
| A5 | Music license recorded before use | GATE (rights manifest) |
| A6 | No clipping (`max_volume` ≤ -0.1 dB) | GATE |

## 5. Edit / structure

| Rule | Target | Class |
|---|---|---|
| E1 | Cold open; no title card before the hook | STANDARD |
| E2 | Chapter/beat changes align with sentence boundaries | STANDARD |
| E3 | Subtitle sync drift ≤ 0.5 s | GATE (`subtitle_sync`) |
| E4 | Duration within ±5% of script estimate | GATE (`duration_vs_script`) |
| E5 | No unintended frozen/black/gap segments | GATE |

## 6. Rights / provenance

| Rule | Target | Class |
|---|---|---|
| R1 | Every asset has source URL, author, license URL, retrieval date, SHA-256 | GATE |
| R2 | Unknown license = quarantined, not released | GATE |
| R3 | No YouTube-downloaded stock footage | GATE (policy) |
| R4 | Music/voice/model licenses checked separately for commercial use | GATE |

## 7. Human gate

| Rule | Target | Class |
|---|---|---|
| H-1 | A human watches the **exact final file** end-to-end | GATE (cannot be automated) |
| H-2 | Independent reviewer (not the producer) scores 1–10 | GATE |
| H-3 | No "10/10" claim without H-1 + H-2 | GATE |

## Status of this standard

- Implemented as code: V2, V3, A1–A3, A6, E3–E5, R1 (partially), R2 (partially).
- Not implemented: H1–H4, S1, S4, V1, A4, R3 (policy only), H-1..H-3.
- **This document is a proposal.** It does not change `config/qc_thresholds.json`; changing
  production thresholds requires an owner decision.