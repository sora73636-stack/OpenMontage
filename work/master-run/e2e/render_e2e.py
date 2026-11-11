"""Render the 60-90 s E2E demo: scenes + zoompan + rig loop + narration + PD music + subs."""

import json
import subprocess
from pathlib import Path

ROOT = Path("/workspaces/OpenMontage/work/master-run/e2e")
CLIPS = ROOT / "clips"
CLIPS.mkdir(parents=True, exist_ok=True)
scenes = json.loads((ROOT / "scenes.json").read_text())
nar = json.loads((ROOT / "narration.json").read_text())
rig = {m["pose"]: m["mov"] for m in json.loads((ROOT / "rig_manifest.json").read_text())}
FPS = 30
TOTAL = nar["total_s"]


def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        print("CMD FAILED:", " ".join(cmd)[:500])
        print(p.stderr[-3000:])
        raise SystemExit(1)
    return p


# 1. scene clips with zoompan
for i, s in enumerate(scenes):
    dur = round(s["end_s"] - s["start_s"] + (0.55 if i < len(scenes) - 1 else 1.5), 3)
    frames = max(2, round(dur * FPS))
    out = CLIPS / f"scene_{i:02d}.mp4"
    # actual motion variety: zoom in / zoom out / pan left / pan right
    mode = i % 4
    if mode == 0:
        vf = ("zoompan=z='min(1+0.00055*on,1.10)':x='iw/2-(iw/zoom/2)':"
              "y='ih/2-(ih/zoom/2)':d=" + str(frames) + ":s=1920x1080:fps=" + str(FPS))
        move, easing, direction = "zoom_in", "linear", "in"
    elif mode == 1:
        vf = ("zoompan=z='max(1.10-0.00055*on,1.0)':x='iw/2-(iw/zoom/2)':"
              "y='ih/2-(ih/zoom/2)':d=" + str(frames) + ":s=1920x1080:fps=" + str(FPS))
        move, easing, direction = "zoom_out", "linear", "out"
    elif mode == 2:
        vf = ("zoompan=z='1.06':x='(iw-iw/zoom)*(1-on/" + str(frames) + ")':"
              "y='ih/2-(ih/zoom/2)':d=" + str(frames) + ":s=1920x1080:fps=" + str(FPS))
        move, easing, direction = "pan", "linear", "left"
    else:
        vf = ("zoompan=z='1.06':x='(iw-iw/zoom)*(on/" + str(frames) + ")':"
              "y='ih/2-(ih/zoom/2)':d=" + str(frames) + ":s=1920x1080:fps=" + str(FPS))
        move, easing, direction = "pan", "linear", "right"
    run(["ffmpeg", "-y", "-loop", "1", "-i", s["image"], "-vf", vf,
         "-frames:v", str(frames), "-r", str(FPS), "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)])
    # 2. overlay animated rig loop
    rig_mov = rig[s["pose"]]
    out2 = CLIPS / f"scene_{i:02d}_rig.mp4"
    fc = ("[1:v]scale=-1:360[rig];[0:v][rig]overlay=70:650:shortest=1")
    run(["ffmpeg", "-y", "-i", str(out), "-stream_loop", "-1", "-i", rig_mov,
         "-filter_complex", fc, "-t", str(dur), "-r", str(FPS),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", str(out2)])
    s["clip"] = str(out2)
    s["scene_duration_s"] = dur
    s["move"], s["easing"], s["direction"] = move, easing, direction
    print(f"scene {i:02d} {s['id']} {dur}s", flush=True)

json.dump(scenes, open(ROOT / "scenes_built.json", "w"), indent=2)

# 3. concat
with open(CLIPS / "concat.txt", "w") as f:
    for s in scenes:
        f.write(f"file '{s['clip']}'\n")
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(CLIPS / "concat.txt"),
     "-c", "copy", str(ROOT / "video_noaudio.mp4")])

# 4. narration track (22050 mono -> 48000 stereo)
import wave
import audioop
out = ROOT / "narration_track.wav"
with wave.open(str(out), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(22050)
    total = int((TOTAL + 1.0) * 22050)
    buf = bytearray(total * 2)
    for line in nar["timeline"]:
        with wave.open(line["file"], "rb") as r:
            data = r.readframes(r.getnframes())
        off = int(line["start_s"] * 22050) * 2
        buf[off:off + len(data)] = data
    w.writeframes(bytes(buf))
print("narration track", TOTAL)

# 5. music bed + mix + loudnorm
music = "/workspaces/OpenMontage/assets/music/ardune_red_moon.mp3"
run(["ffmpeg", "-y", "-i", str(out), "-stream_loop", "-1", "-i", music,
     "-filter_complex",
     f"[1:a]atrim=0:{TOTAL},volume=-20dB,afade=t=in:st=0:d=2,afade=t=out:st={TOTAL-3}:d=3[m];"
     f"[0:a][m]amix=inputs=2:duration=first:normalize=0,"
     f"loudnorm=I=-16:TP=-1.5:LRA=7,alimiter=limit=0.94[out]",
     "-map", "[out]", "-ar", "48000", "-ac", "2", str(ROOT / "audio_mix.wav")])
print("audio mix done")

# 6. subtitles
def ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

with open(ROOT / "subtitles.srt", "w") as f:
    for i, line in enumerate(nar["timeline"], 1):
        f.write(f"{i}\n{ts(line['start_s'])} --> {ts(line['end_s'])}\n{line['text']}\n\n")

# 7. final mux + burn subs + faststart
run(["ffmpeg", "-y", "-i", str(ROOT / "video_noaudio.mp4"), "-i", str(ROOT / "audio_mix.wav"),
     "-vf", f"subtitles={ROOT}/subtitles.srt:force_style='FontName=DejaVu Sans,FontSize=22,Outline=2,Shadow=0,MarginV=28'",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
     "-shortest", str(ROOT / "final_demo.mp4")])
print("final", ROOT / "final_demo.mp4")
subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                "format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels",
                "-of", "json", str(ROOT / "final_demo.mp4")])