"""Local CPU TTS benchmark: Kokoro-82M vs Piper lessac.

Measured: load time, generation time, audio duration, RTF, WER (faster-whisper
base.en + jiwer). Naturalness is NOT measured (no human listening).
"""

import json
import re
import subprocess
import time
from pathlib import Path

import numpy as np
import soundfile as sf

OUT = Path("/workspaces/OpenMontage/work/master-run/tts_bench")
AUDIO = OUT / "audio"
AUDIO.mkdir(parents=True, exist_ok=True)

SENTENCES = [
    "Water expands when it freezes, which is why ice floats on a lake.",
    "A light-year is the distance light travels in one year, not a measure of time.",
    "The human body contains about thirty-seven trillion cells.",
    "Sound cannot travel through the vacuum of space.",
    "Photosynthesis converts light energy into chemical energy.",
    "The Earth's core is roughly as hot as the surface of the Sun.",
    "Antibiotic resistance arises when bacteria evolve under selective pressure.",
    "A black hole's event horizon is the boundary beyond which nothing can escape.",
]


def dur(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return round(float(p.stdout.strip()), 3)


def kokoro():
    from kokoro import KPipeline
    t0 = time.time()
    pipe = KPipeline(lang_code="a", device="cpu")
    load = time.time() - t0
    files, durs, gens = [], [], []
    for i, text in enumerate(SENTENCES, 1):
        p = AUDIO / f"kokoro_{i:02d}.wav"
        t0 = time.time()
        chunks = [a for _, _, a in pipe(text, voice="af_heart", speed=1.0)]
        gen = time.time() - t0
        audio = np.concatenate([c.numpy() if hasattr(c, "numpy") else c for c in chunks])
        sf.write(p, audio, 24000)
        d = dur(p)
        files.append(str(p)); durs.append(d); gens.append(gen)
    total = sum(durs)
    return {"engine": "kokoro", "voice": "af_heart", "device": "cpu", "load_s": round(load, 2),
            "gen_s_total": round(sum(gens), 2), "gen_s_per_utt": [round(x, 3) for x in gens],
            "audio_s_total": round(total, 2), "audio_s_per_utt": durs,
            "rtf": round(sum(gens) / total, 3) if total else None, "files": files}


def piper():
    model = "/tmp/opencode/en_US-lessac-medium.onnx"
    piper_bin = "/tmp/opencode/omk/bin/piper"
    files, durs, gens = [], [], []
    for i, text in enumerate(SENTENCES, 1):
        p = AUDIO / f"piper_{i:02d}.wav"
        t0 = time.time()
        r = subprocess.run([piper_bin, "-m", model, "-f", str(p)], input=text,
                           text=True, capture_output=True)
        gen = time.time() - t0
        if r.returncode != 0:
            raise SystemExit(r.stderr[-1000:])
        d = dur(p)
        files.append(str(p)); durs.append(d); gens.append(gen)
    total = sum(durs)
    return {"engine": "piper", "voice": "en_US-lessac-medium", "device": "cpu",
            "load_s": None, "gen_s_total": round(sum(gens), 2),
            "gen_s_per_utt": [round(x, 3) for x in gens],
            "audio_s_total": round(total, 2), "audio_s_per_utt": durs,
            "rtf": round(sum(gens) / total, 3) if total else None, "files": files}


def norm(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def wer(files):
    from faster_whisper import WhisperModel
    from jiwer import wer as jiwer_wer
    t0 = time.time()
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    load = time.time() - t0
    rows = []
    for i, p in enumerate(files, 1):
        segs, _ = model.transcribe(p, beam_size=1, language="en")
        hyp = norm(" ".join(s.text for s in segs))
        ref = norm(SENTENCES[i - 1])
        score = round(jiwer_wer(ref, hyp), 4)
        rows.append({"ref": ref, "hyp": hyp, "wer": score})
    vals = [r["wer"] for r in rows]
    return {"asr_model": "faster-whisper base.en", "load_s": round(load, 2),
            "wer_per_utt": vals, "wer_mean": round(sum(vals) / len(vals), 4), "details": rows}


res = {"status": "ok", "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "runtime": {"python": "3.12", "torch": "cpu", "kokoro": "0.7.16"},
       "engines": {}, "wer": {}, "errors": []}
for name, fn in [("kokoro", kokoro), ("piper", piper)]:
    try:
        res["engines"][name] = fn()
    except Exception as exc:  # noqa: BLE001
        import traceback
        res["engines"][name] = {"status": "error", "error": traceback.format_exc()[-2000:]}
        res["errors"].append(f"{name}: {exc!r}")
try:
    res["wer"] = {"kokoro": wer(res["engines"]["kokoro"]["files"]),
                  "piper": wer(res["engines"]["piper"]["files"])}
except Exception as exc:  # noqa: BLE001
    import traceback
    res["wer"] = {"status": "error", "error": traceback.format_exc()[-2000:]}
    res["errors"].append(f"wer: {exc!r}")

json.dump(res, open(OUT / "LOCAL_TTS_BENCH.json", "w"), indent=2)
json.dump({"status": res["status"], "errors": res["errors"]}, open(OUT / "DONE.json", "w"), indent=2)
print(json.dumps({k: res[k] for k in ("engines", "wer")}, indent=2)[:5000])