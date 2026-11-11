# Competitor Video Audit — 15 Science YouTube Videos

**Date:** 2026-11-11
**Method:** YouTube InnerTube public search metadata (`/youtubei/v1/search`, no API key,
no login, no download). No video frames, audio, or transcripts were retrieved.

## Evidence classes (strict)

| Class | Meaning | Count in this report |
|---|---|---|
| `FRAME_VIEWED` | I personally watched frames/full video and measured visual/audio | **0** |
| `PUBLIC_METADATA` | Title, channel, view count, duration, relative publish age returned by YouTube | **15** |
| `INFERRED` | Structural inference from title/channel format; explicitly not observed | 15 (structure columns) |

**Why no frame-level evidence:** YouTube's `player` endpoint returned
`playabilityStatus=LOGIN_REQUIRED` from this environment, and third-party transcript
services were blocked by Cloudflare. The report therefore does **not** claim to have
watched any video. All visual/animation/editing/audio/retention statements below are
labelled `INFERRED` and are hypotheses to verify in a human review session.

## Selection

One video per channel, English-language, ≥240 s, ≥500k public views, science/engineering/
space theme. Final 15 chosen for channel diversity and format range. Full candidate pool
(165 items) and the collector script are in `work/master-run/research/`.

## Final 15

| # | Channel | Title | Duration | Public views | Hook type (title) | Format (inferred) |
|---:|---|---|---:|---:|---|---|
| 1 | Mark Rober | Carnival Scam Science (and how to WIN) | 10:53 | 120,376,705 | declarative | experiment/build + hidden-camera proof |
| 2 | Veritasium | The Most Misunderstood Concept in Physics | 27:15 | 31,576,927 | declarative | interview + demonstration + animation |
| 3 | Kurzgesagt – In a Nutshell | The Black Hole Bomb and Black Hole Civilizations | 8:08 | 29,510,228 | declarative | 2D motion-graphics essay |
| 4 | Steve Mould | NASA tested my chain theory in space | 15:03 | 15,455,811 | declarative | build/test + archival footage |
| 5 | NOVA PBS Official | Atomic Clocks Prove Reality Is Stranger Than You Think | 11:31 | 1,156,093 | curiosity-gap | broadcast documentary |
| 6 | Physics Girl | Crazy pool vortex | 4:03 | 14,136,767 | declarative | at-home experiment demo |
| 7 | TED-Ed | Newton's three-body problem explained | 5:31 | 9,943,078 | declarative | narrated animation |
| 8 | Real Engineering | The Insane Engineering of the X-15 | 31:30 | 8,837,284 | number/list | 3D/animation + archival |
| 9 | NASA Jet Propulsion Laboratory | 7 Minutes of Terror: The Challenges of Getting to Mars | 5:08 | 3,228,233 | number/list | mission archival + animation |
| 10 | PBS Space Time | JWST May Have Discovered a New Cosmic Object: The Black Hole Star | 15:16 | 2,805,185 | curiosity-gap | explainer + diagrams |
| 11 | SciShow | Scientists Can't Agree On The First Ancient City | 25:17 | 2,625,157 | declarative | news-explainer + footage |
| 12 | Numberphile | Equally sharing a cake between three people | 7:33 | 2,512,946 | declarative | whiteboard interview |
| 13 | Anton Petrov | Math Suggests We May Be the Only Intelligent Life in the Universe | 16:53 | 584,813 | declarative | narrated space visuals |
| 14 | BBC Earth Science | Giant Space Magnet Reveals a 'Startling Possibility' | 6:14 | 1,246,243 | curiosity-gap | documentary excerpt |
| 15 | European Space Agency, ESA | Journeying through stunning cosmic views with James Webb Space Telescope | 43:26 | 855,431 | declarative | mission footage + music |

**Public aggregate (computed):** duration min 243 s / median 691 s / max 2,606 s;
views min 584,813 / median 3,228,233 / max 120,376,705. Hook mix: 10 declarative,
3 curiosity-gap, 2 number/list, 0 question.

## Findings

### Hook / title
- **No question-title pattern in the top set.** The highest-viewed titles are declarative
  or curiosity-gap, not "Why does…?". A concrete noun + an unexpected claim ("Most
  Misunderstood", "Carnival Scam") carries the hook.
- Short-form winners (Physics Girl 4:03, NASA JPL 5:08, TED-Ed 5:31) lead with a concrete
  experiment or object, not a topic label.
- **INFERRED:** the first 5–10 s likely show the anomaly/result before explaining it.
  This is unverified without frames.

### Duration / pacing
- Median 11.5 min. The 60–90 s target in this project is **not** a competitor length; it
  is a pipeline proof. A real channel episode would need 8–20 min.
- **INFERRED:** experiment channels (Mark Rober, Physics Girl) change visual setup every
  2–5 s; essay channels (Kurzgesagt, Veritasium) use continuous motion graphics; broadcast
  docs use archival cuts every 3–8 s. None measured.

### Script / retention
- **Not observable** from public metadata. View counts are cumulative and cannot be used
  as retention evidence (age, promotion, and thumbnails confound them).
- **INFERRED:** the strongest titles encode a *specific, visual, testable claim*
  ("Elephant Toothpaste", "X-15", "Black Hole Star"), not a broad topic.

### Visual / animation / editing / sound
- **Not observed.** No frames, no audio, no transcript. The format column is channel-level
  inference only.
- **Consequence:** this audit cannot certify any competitor's visual/audio quality. It can
  only set a research agenda for a human viewing session.

## Implications for OpenMontage

1. The current 60–90 s demo must be judged as a **technical pipeline proof**, not as a
   retention-optimized competitor. Label it accordingly.
2. For a real episode, target **8–15 min** with one concrete claim per 20–30 s and a visual
   change every 2–4 s.
3. Title should name a **specific object/anomaly**, not a topic.
4. Before any "10/10" claim: a human must watch 3–5 of these videos frame-by-frame and
   compare against our final file.

## Reproducibility

- Collector: `work/master-run/research/collect_competitors.py`
- Raw candidates: `work/master-run/research/competitor_candidates.json`
- Final set: `work/master-run/research/competitor_final15.json`
- Selection script: `work/master-run/research/finalize_competitors.py`