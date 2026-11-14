# Stage G Summary — Motion-dependent scene: AI video-gen vs Ken Burns baseline

**Date:** 2026-11-14 (UTC)
**Branch:** audit/kaggle-t4
**HEAD SHA (start):** f30d1793a3949fcc3840d3ad9ebf6e2cb1e4ad70
**Kernel:** forts845/openmontage-vq-wan2-2-asteroid-collision (v1, COMPLETE)

## What was done
- Generated one MOTION clip with the fixed scene "Two asteroids colliding in deep space..." (seed 919191) using the exact Stage F config (diffusers 0.35.2, GGUF Q4_K_M, fp16 compute, VAE fp32, UMT5 fp16, SDPA, 832×480, 49 frames, 24 fps, 20 steps). Saved as `audit/previews/video_quality_comparison/wan22_asteroid_collision_919191_MOTION.mp4`.
- Extracted frame 0 from the MOTION clip as PNG and produced a Ken Burns clip of identical duration (49 frames, 24 fps) via ffmpeg zoompan. Saved as `audit/previews/video_quality_comparison/wan22_asteroid_collision_919191_KENBURNS.mp4`. Generation took ~1.1 s, CPU only, no GPU.
- Ran ffprobe + blackdetect + freezedetect on both: 0 black, 0 freeze on both.
- Updated COMPARISON.md (Stage G section) and results.json / component_results.json with entry `wan22-ti2v-5b-vs-kenburns-asteroid-919191`.

## Metrics
- MOTION: gen_time 365.0 s, peak VRAM 13863.3 MiB, 49 frames, 832×480, 2.04 s, blackdetect 0, freezedetect 0.
- KENBURNS: gen_time 1.1 s, GPU used false, 49 frames, 832×480, 2.04 s, blackdetect 0, freezedetect 0.

## production_status
BLOCKED — pending human review (`human_review_status = PENDING_HUMAN_REVIEW` for both). The MOTION clip contains real model-generated motion/destruction; the KENBURNS clip is a programmed zoom of a single static frame. Which is preferable is a human visual decision; no automated quality verdict was made.

## Scope note
Only this one scene was tested. No other scenes/models were touched.
EOF
echo done