# V13 QC Report (preview)

Video: `/workspaces/OpenMontage/work/v13/render/v13_preview.mp4`
SHA256: 991223b683234b7a38ee8309e4323d7a259a1e339d0c7b226f92d02bdac2c192
Created: 2026-11-10T12:21:14.073037+00:00
Overall status: **WARNING**

## Summary

- total checks: 12
- PASS: 9
- WARNING: 1
- FAIL: 0
- BLOCKED: 0
- NOT_RUN: 2

## Checks

- [PASS] ffprobe (video) — video+audio; 1920x1080@30/1; sar= dar=; 178.733s; 24.48 MB
  - measured: {'w': 1920, 'h': 1080, 'fps': '30/1', 'codec_v': 'h264', 'codec_a': 'aac', 'sar': '', 'dar': '', 'duration': 178.733333, 'size_mb': 24.48}
- [PASS] full_decode (video) — full decode: no errors
  - measured: {'bytes': 25665530}
- [WARNING] audio_loudness (audio) — music-only preview: I=-70.00 LUFS, TP=None dBTP (narration loudness target not applicable)
  - measured: {'lufs': -70.0, 'true_peak': None}
  - threshold: I=-16.0±1.5 LUFS, TP<=-1.5 dBTP
- [PASS] black_frames (video) — no black segments
  - measured: {'count': 0, 'ratio': 0.0}
  - threshold: 0.05
- [PASS] audio_silence (audio) — silence ratio 0.000, longest run 0.00s
  - measured: {'ratio': 0.0, 'longest_run_s': 0.0}
  - threshold: ratio<=0.10, run<=3s
- [PASS] frozen_segments (video) — no frozen segments
  - measured: {'count': 0}
  - threshold: max 2s
- [NOT_RUN] scene_cuts (video) — scdet did not emit NBSCENES; sampled-frame proxy used
  - measured: {'sampled_frames_1fps': 179}
- [PASS] frame_count (video) — decoded 5362 frames vs expected 5362
  - measured: {'decoded': 5362, 'expected': 5362, 'drift': 0}
- [PASS] av_sync (audio) — audio 178.731s vs video 178.733s, delta 0.003s
  - measured: {'audio_dur': 178.73066666666668, 'video_dur': 178.733333, 'delta_s': 0.0026663333333090122}
  - threshold: <=0.10s
- [NOT_RUN] subtitles (visual) — no burned-in subtitles in this preview (narration BLOCKED; SRT not produced)
  - measured: {'burned': False}
- [PASS] integrity_hash (structural) — SHA256=991223b683234b7a38ee8309e4323d7a259a1e339d0c7b226f92d02bdac2c192; sampled 10 frame aHashes recorded
  - measured: {'sha256': '991223b683234b7a38ee8309e4323d7a259a1e339d0c7b226f92d02bdac2c192', 'frame_ahash_sample': ['00f0fc0fffdf6000', '00f0fc0fffdf6400', '00f0fc0fffdf6400', '00f0fc0fff9b6400', '00f0fc0fff9b6400']}
- [PASS] scene_count_match (structural) — EDL scenes=12 = render scenes=12 = storyboard scenes=12
  - measured: {'edl': 12, 'render': 12, 'storyboard': 12}

## Note
This is a low-res preview from the EDL, not a compliant V13 master:
- narration is BLOCKED (Kokoro `af_heart` package/weights not installed),
- 100% of frames are existing AI reconstructions (S1.2 AI cap is 0-15%),
- no subtitles burned (SRT not produced).
Owner must install Kokoro `af_heart`, supply compliant archive/original-diagram assets,
and approve narrative framing before a final V13 master can be READY_FOR_OWNER_REVIEW.
