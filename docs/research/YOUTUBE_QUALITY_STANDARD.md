# YouTube Quality Standard — official baseline vs OpenMontage house targets

**Date:** 2026-11-11 · **Source task:** `OpenMontage_10of10_Four_Factories_OpenCode_Agent_Task_2026-11-11.md` Part D.
**Rule:** official YouTube upload requirements and OpenMontage house targets are kept
separate. House targets are not YouTube mandates.

## 1. Official YouTube baseline (D1)

Source: https://support.google.com/youtube/answer/1722171

| Item | Requirement |
|---|---|
| Container | MP4, `moov atom` at start (Fast Start), no edit lists that degrade processing |
| Video codec | H.264 High Profile, progressive, 4:2:0, closed GOP, no interlacing |
| Audio | AAC-LC or Opus, 48 kHz, stereo |
| Frame rate | Keep source frame rate; do not inflate FPS |
| Color | BT.709 SDR for an SDR master |
| Reference bitrate, SDR 1080p 24/25/30 | **8 Mbps** |
| Reference bitrate, SDR 1080p 48/50/60 | 12 Mbps |
| Reference bitrate, SDR 1440p 24/25/30 | 16 Mbps |
| Reference bitrate, 4K 24/25/30 | 35–45 Mbps |
| Reference audio bitrate, stereo | **384 kbps** |

## 2. OpenMontage house targets (D2) — not YouTube mandates

| Item | Target |
|---|---|
| Integrated loudness | **-16 LUFS ±1 LU** |
| True peak | **≤ -1.0 dBTP** |
| Narration intelligibility | voice not masked by music/SFX |
| Subtitle sidecar | SRT or VTT; max 2 lines; ≤42 chars/line; ≤20 chars/s |
| Captions safe area | must not cover diagrams/labels |
| Text contrast | WCAG AA where applicable |
| Pauses | allowed when motivated; do not fill every second with music |

## 3. Script and retention rules (D3)

- 0–15 s: concrete visual/story hook; no long logo/intro.
- By 30 s: clear promise of the question the viewer will get answered.
- One central idea/question per release; 1–3 learning outcomes.
- Chapters usually 2–5 min; each answers a sub-question and advances the story.
- Narration pacing ~125–155 wpm for English explainer; slow down for complex passages.
- Target 15–20+ min only when the topic supports it; do not pad.
- Each chapter promises the next answer/discovery.
- No "Today we are going to explore…"; no unresolved cliffhanger.
- Per release: `hook_variants.md` with ≥3 variants + thumbnail/title concept options.

## 4. Internal 10/10 rubric (D4)

| Criterion | Weight |
|---|---:|
| Hook / packaging fulfillment | 12% |
| Scientific accuracy / claim integrity | 18% |
| Story arc / pacing / payoff | 12% |
| Visual relevance and clarity | 12% |
| Motion and visual pacing | 10% |
| Narration / audio mix / sound design | 10% |
| Captions / labels / accessibility | 8% |
| Visual consistency / art direction | 8% |
| Originality / authenticity | 5% |
| Rights / provenance / source quality | 5% |

**Hard gates:** no unresolved science or rights FAIL; no incorrect critical scientific
visualization; exact master watched end-to-end; all mandatory QC gates PASS; a second
reviewer confirms. The average score does not override a hard gate.

## 5. Measured status of the current demo

File: `work/master-run/e2e/final_demo.mp4` (76.07 s; v3 with Manim + SFX)

| Metric | Measured | Target | Status |
|---|---|---|---|
| Container / Fast Start | MP4, `+faststart` | MP4 Fast Start | PASS |
| Video | H.264 High, 1920×1080, 30 fps, progressive, yuv420p | 1080p SDR | PASS |
| Video bitrate | **7.98 Mbps** | 8 Mbps reference | PASS (at reference) |
| Audio | AAC-LC, 48 kHz, stereo, **330 kbps** | 384 kbps reference | REVIEW (below reference, not a YouTube hard fail) |
| Loudness | **-16.0 LUFS** | -16 ±1 LUFS | PASS |
| True peak | **-2.0 dBTP** | ≤ -1.0 dBTP | PASS |
| Subtitles | max 42 chars/line, 2 lines | ≤42 chars, ≤2 lines | PASS |
| QC | 16/16 PASS | all gates | PASS |
| Human watch-through | not done | required for 10/10 | **PENDING_HUMAN_REVIEW** |

**Conclusion:** the demo meets the technical baseline and house loudness targets, but
cannot be called 10/10 until a human watches the exact master and a second reviewer scores
it. The AAC bitrate is below the 384 kbps reference; YouTube re-encodes audio, so this is
a review item, not a release blocker.