# Kilo task: diagnose and fix OpenMontage V12 preview defects

You are working in `/workspaces/OpenMontage`. Treat this as a production repair task, not a request to redesign the entire factory. The reviewed artifact is `1000283079.mp4` (132.300 s, 1280x720, 30 fps, H.264, 3969 frames, 2.94 MB, video bitrate ~175 kb/s, **no audio stream**). It contains visible `OpenMontage V12 — text card` debug labels.

## Non-negotiable safety / project constraints

- First inspect the current repo, branch, status, project docs, V12 manifests, scripts, timelines, assets, and QC reports. Do not assume file paths from old handoffs still exist.
- Preserve existing final versions (especially V3/V12 artifacts). Do not overwrite a previous final MP4; create the next version using the repo's existing naming convention (e.g. V13 only if that is the next valid version).
- **Zero paid spend.** Do not invoke Google Flow, Nano Banana, paid APIs, or any job that may consume credits. Keep `--no-spend`, `GFLOW_MCP_NO_SPEND=1`, Zero-Cost Gate, Flow Job Manager and MCP Security Proxy intact. Do not reset/authenticate browser profiles or touch Flow cookies/session.
- Do not modify `yt-*` skills or unrelated project systems. Reuse the existing Remotion + FFmpeg pipeline; do not introduce a second renderer.
- No commits unless explicitly requested. Do not delete source assets or logs.
- Do not claim a fix is complete merely because tests pass. Render and inspect the actual MP4 and contact sheets.

## Phase 0 — verify which artifact this is

1. Find the V12 export matching the metadata above. Search the project for the uploaded filename or the matching 132.3 s / 1280x720 / 30 fps / ~175 kb/s export. The uploaded file may not exist in Codespaces; do not pretend you inspected it if it is absent.
2. Determine whether this is intentionally a silent low-bitrate animatic/preview or an accidentally produced final master. Inspect the render command/config and pipeline reports.
3. If the exact MP4 is not present, use the repo's matching V12 manifest/assets to diagnose and fix the source, but clearly report that the exact uploaded bytes were not re-opened in Codespaces.
4. Locate the exact source of the `OpenMontage V12 — text card` label and remove it from all production/final outputs. If useful for debug previews, put it behind an explicit debug-only option that defaults OFF in release builds.

## Confirmed defects from visual review

- 00:00–00:06: opening consists almost entirely of a dark text card. The hook line is usable, but the opening needs a strong visual reveal (Europa / icy shell / hidden ocean), not a text-only screen.
- 00:18–00:24: long English text overflows the frame and is clipped at both left and right edges.
- 00:27–00:42: Europa cross-section is held for roughly 15 s with minimal meaningful change. Labels are Russian in an English-language project; the `~29 km (±10), estimate` label has unclear referent/context; source credit sits near the edge. The diagram needs to be rebuilt as clear editable vector graphics, with sourced/qualified values and English labels.
- 00:42–00:57: Enceladus plume card repeats for roughly 15 s. Heading is clipped at top; Russian labels remain; several glyphs render as boxes. Rebuild/repair the diagram and animate an explanatory sequence (plume → particles → sampling/composition), not a static still.
- Around 01:00: Earth deep-sea/hydrothermal-ecosystem footage appears. If used, label it as an **Earth analogue**, never as actual footage from Enceladus/Europa. Verify licence and source.
- Around 01:03–01:09: a small, low-resolution composite/scientific cutaway sits inside large black margins. Replace the screenshot with a properly framed source image or native vector reconstruction. Do not upscale a tiny screenshot and call it fixed.
- Around 01:12–01:24: a very simple orange hydrothermal-vent icon/graphic is held almost unchanged. Russian labels and excessive empty space make it look like a placeholder. Separate known Earth hydrothermal systems from speculative extrapolation to Enceladus; mark hypothesis/analogy explicitly.
- Around 01:27–01:30: graph/spectral image is too small/low-resolution and its legend is not legible. Rebuild as vector chart with correct axes, units, legend, one clear takeaway, and full source attribution.
- Around 01:39–01:51: a sequence of false-colour/monochrome surface images culminates in a small propeller aircraft at about **01:48**. Identify the exact asset and sentence ID. If it is unrelated to the script, remove it and replace it with an accurate spacecraft/mission visual from a rights-cleared official source. Never leave a random aircraft image as mission footage.
- Around 01:57–02:12: ending returns to repeated text-only cards. Text again exceeds the frame edges. Replace with one visually supported concluding beat and a short readable line; keep longer narration in the voice track/subtitles.
- Throughout: Russian labels in the English-language video and missing-character tofu boxes are release blockers. Text/source credits and titles must fit within safe margins. No debug labels in final output.

## Scientific wording that must be checked

The visible end card says that Europa Clipper “arrives at Europa in 2031.” Correct the wording. NASA currently states that Europa Clipper reaches Jupiter / performs Jupiter orbit insertion in **April 2030**, and its first Europa flyby is planned for **spring 2031**. It orbits Jupiter and makes repeated flybys of Europa; it does not enter orbit around Europa. Safe wording:

> “Europa Clipper is expected to reach Jupiter in April 2030, with its first Europa flyby planned for spring 2031.”

Verify against current official NASA sources before locking the line:
- https://science.nasa.gov/mission/europa-clipper/mission-timeline/
- https://www.jpl.nasa.gov/press-kits/europa-clipper/quick-facts/

Also resolve the premise: the visible content is about Europa and Enceladus (icy moons with subsurface oceans), not a hypothetical planet with no land. Either update title/thumbnail/description to match the actual episode, or identify and restore the intended no-land-planet script. Do not blur these two concepts.

## Required repair workflow

### 1. Audit before edits
- Read `PROJECT_STATE_HANDOFF.md`, `OPENMONTAGE_MASTER_CONTEXT.md`, the current V12 creative/QC reports, and the relevant master style/production docs if present.
- Inspect the actual script and scene ledger. Map every sentence/scene ID to its visual asset, source, purpose, and timestamp.
- Identify the renderer component producing text cards, the localization source for graphic labels, the font configuration, and the asset path responsible for the aircraft image.
- Determine why the 132.3 s export has no audio. Is it an intentional animatic profile or a mux/render bug? Do not invent missing narration.

### 2. Fix text-card/layout infrastructure once
- Implement safe-area constraints for all 16:9 output: keep titles/subtitles/source credits inside a consistent 5% inset; avoid important text at the bottom edge.
- Use responsive wrapping and bounded text containers; set maximum line count and a minimum readable font size. Do not solve overflow by blindly shrinking all text.
- Add an overflow test or screenshot-based layout test so any text bounding box outside the canvas fails CI/QC.
- Use a font with all required glyphs. For this English version, localize every visible label to English. Keep Unicode support; do not let missing glyphs render as squares.
- Remove oversized sentence cards. Long narration belongs in voice-over and captions; on-screen text should be short, deliberate and readable.

### 3. Repair visual story and scene assets
- Rebuild the Europa and Enceladus diagrams as native editable SVG/Remotion graphics, not screenshots of screenshots. Make labels, units, geometry, scale and source credits legible.
- Provide progressive reveals and meaningful internal motion on scenes currently held for 9–15 s: changing layers, moving plume particles, showing the cross-section, tracing a heat/chemical pathway, or changing scale with a clear explanatory purpose.
- Label terrestrial hydrothermal footage as Earth analogue and source it. Do not imply it is observed on an icy moon.
- Remove/replace the unrelated aircraft asset around 01:48 after verifying the exact scene mapping.
- Ensure every scene matches the actual narration sentence. No decorative stock shot without a specific reason.
- Apply a controlled visual treatment across archival material, reconstruction and diagrams: coherent contrast/exposure/colour, while preserving honest distinctions between real observations and illustrative reconstructions. Do not apply one global LUT that damages scientific imagery.
- Do not regenerate every image. Retain correct, high-quality assets; replace only failed/irrelevant assets using a verified $0/licensed source or already available local model. No paid generation.

### 4. Restore audio only from approved project sources
- If an approved narration file exists, integrate it and align scenes to the actual audio. If it does not exist, run the existing Kokoro TTS pipeline from the locked script only if that pipeline is already configured and free. Do not fabricate or rewrite science claims silently.
- Ensure the final release render has a real audio stream. VO must be intelligible; add music/SFX only from existing, commercially usable assets. If no licensed music is available, deliver VO-only rather than inserting unlicensed music.
- Target 48 kHz audio in the final master. Measure integrated loudness and true peak; use the project's established targets if present, otherwise document chosen targets and do not clip.
- Keep an intentionally silent animatic as a separate preview profile; never let it be mislabelled as final master.

### 5. Render and quality-gate
- Render a new version to a new path. Keep the previous V12 output immutable.
- Final master target: 1920×1080, 16:9, 30 fps, H.264, yuv420p, square pixels (SAR 1:1), appropriate HD bitrate/CRF (e.g. x264 CRF 18–22 as a starting point; follow existing repo convention if better), and 48 kHz audio when audio is expected.
- Run ffprobe and full decode. Assert: video stream exists; audio stream exists for final master; no unexpected A/V duration mismatch; no clipping/black/blank frames; no broken frames; no text overflow; no tofu glyphs; no debug labels; subtitles are within safe areas; assets are present and mapped correctly.
- Make contact sheets from beginning/middle/end and inspect them manually. Also watch the complete exported MP4 with sound, not just keyframes or test screenshots.
- Run relevant tests and add regression tests for the defects fixed. Do not claim `CREATIVE PASS` solely from pytest/QC.

## Deliverables

1. New versioned MP4 (or clearly labelled silent preview plus a separate final master if the script/audio are not ready).
2. Updated scene ledger/manifest with asset provenance, source/licence, labels for REAL / EARTH ANALOGUE / RECONSTRUCTION / SPECULATIVE, and exact sentence/timestamp mapping.
3. `docs/PILOT_V12_REPAIR_AUDIT.md` (or next-version review report) listing root causes, changed files, fixed timestamps, remaining issues and evidence.
4. Contact sheet and short preview for manual approval.
5. Machine-readable QC report showing exact ffprobe/audio/video measurements.
6. Test results and a concise summary of what was not possible to fix without new approved assets.

## Stop conditions

- Stop before any paid call or credit use.
- Stop if an asset's licence/provenance cannot be verified; use a different free cleared source or flag it for owner approval.
- Stop if the script/source ledger is missing rather than inventing narration or science.
- Do not claim the repaired video is ready until the actual new MP4 has been inspected visually and listened to end-to-end.
