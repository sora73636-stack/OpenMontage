# V13 Watch Notes (preview) — 2026-11-10T12:22:21.880427+00:00
## Source
- Video: `work/v13/render/v13_preview.mp4` (SHA256 recorded in v13_qc.json)
- Duration: 178.73s (target 170-190s)
- Resolution/codec: 1920x1080, H.264, yuv420p, 30fps; AAC 48kHz

## What works (technical)
- FFprobe: 1 video + 1 audio stream, 1920x1080@30, H.264/AAC
- Full decode: no errors
- Frame count: decoded 5362 = expected 5362 (exact)
- A/V delta: 0.003s (<=0.10s)
- No black segments, no frozen segments, silence ratio 0.000
- SHA256 + per-frame aHash recorded

## Blockers (owner action required)
- VOICE BLOCKED: Kokoro `af_heart` package/weights not installed. No placeholder WAV created.
  Owner must install Kokoro and re-synthesize narration.
- No narration / SRT → subtitles NOT_RUN, audio_loudness target not applicable.
- Visual budget off-spec: 100% existing AI reconstructions (S1.2 cap 0-15%).
  Owner must supply NASA/archive (~40-50%) and/or original PIL diagrams (~30-40%).
- Scene count 12, below the 24-32 target (count is not a standalone quality indicator).

## Recommendation
Do NOT promote this preview to READY_FOR_OWNER_REVIEW as a final V13 master.
It validates the FFmpeg/PIL render + QC pipeline. Final narrated master requires
owner-approved script + Kokoro voice + compliant visual mix.
