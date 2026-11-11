"""OpenMontage TTS benchmark — Kaggle kernel.

Real, measured comparison of two local, $0 TTS runtimes:
  - Kokoro-82M (af_heart)  [CORE candidate]
  - Piper (en_US-lessac-medium) [FALLBACK candidate]

Metrics: load time, per-utterance generation time, audio duration, RTF,
WER via faster-whisper base.en + jiwer. Naturalness is NOT measurable here;
it is recorded as NOT_MEASURED (no human listening in a kernel).

Writes TTS_BENCH.json, DONE.json and WAVs to /kaggle/working.
"""

import json
import os
import re
import subprocess
import sys
import time
import traceback

OUT = "/kaggle/working"
os.makedirs(f"{OUT}/audio", exist_ok=True)
RESULT = {
    "status": "ok",
    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "runtime": {"python": sys.version, "torch": None, "cuda": None},
    "engines": {},
    "wer": {},
    "errors": [],
}

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


def pip(cmd, timeout=900):
    print("+", " ".join(cmd), flush=True)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        print(p.stdout[-2000:], p.stderr[-3000:], flush=True)
        raise RuntimeError(f"command failed: {cmd[:3]}")


def sh(cmd, timeout=600):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout.strip(), p.stderr.strip()[-1000:]


def audio_duration(path):
    rc, out, _ = sh(f"ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 {path}")
    try:
        return float(out)
    except ValueError:
        return 0.0


def install():
    pip([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "pip"])
    # Keep Kaggle's torch; install only what is missing.
    pip([sys.executable, "-m", "pip", "install", "-q",
         "numpy==1.26.4", "scipy", "soundfile", "misaki[en]", "kokoro",
         "faster-whisper", "jiwer", "piper-tts"])
    rc, out, err = sh("python -m piper.download_voices en_US-lessac-medium", timeout=600)
    print("piper voice download:", rc, out[-300:], err[-300:], flush=True)


def run_kokoro():
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline

    t0 = time.time()
    pipe = KPipeline(lang_code="a", device="cpu")
    load_s = time.time() - t0
    files, durations, gen_s = [], [], []
    for i, text in enumerate(SENTENCES, 1):
        path = f"{OUT}/audio/kokoro_{i:02d}.wav"
        t0 = time.time()
        chunks = [a for _, _, a in pipe(text, voice="af_heart", speed=1.0)]
        gen = time.time() - t0
        audio = np.concatenate([c.numpy() if hasattr(c, "numpy") else c for c in chunks])
        sf.write(path, audio, 24000)
        dur = audio_duration(path)
        files.append(path)
        durations.append(round(dur, 3))
        gen_s.append(round(gen, 3))
    total_audio = sum(durations)
    return {
        "voice": "af_heart",
        "device": "cpu",
        "load_s": round(load_s, 2),
        "generation_s_total": round(sum(gen_s), 2),
        "generation_s_per_utt": gen_s,
        "audio_s_total": round(total_audio, 2),
        "audio_s_per_utt": durations,
        "rtf": round(sum(gen_s) / total_audio, 3) if total_audio else None,
        "files": files,
    }


def run_piper():
    voice = "en_US-lessac-medium"
    model = f"{voice}.onnx"
    if not os.path.exists(model):
        rc, out, err = sh(f"python -m piper.download_voices {voice}", timeout=600)
        print("download:", rc, out[-200:], err[-200:], flush=True)
    files, durations, gen_s = [], [], []
    for i, text in enumerate(SENTENCES, 1):
        path = f"{OUT}/audio/piper_{i:02d}.wav"
        t0 = time.time()
        rc, out, err = sh(f'echo {json.dumps(text)} | piper -m {model} -f {path}', timeout=300)
        gen = time.time() - t0
        if rc != 0 or not os.path.exists(path):
            raise RuntimeError(f"piper failed: {err}")
        dur = audio_duration(path)
        files.append(path)
        durations.append(round(dur, 3))
        gen_s.append(round(gen, 3))
    total_audio = sum(durations)
    return {
        "voice": voice,
        "device": "cpu",
        "generation_s_total": round(sum(gen_s), 2),
        "generation_s_per_utt": gen_s,
        "audio_s_total": round(total_audio, 2),
        "audio_s_per_utt": durations,
        "rtf": round(sum(gen_s) / total_audio, 3) if total_audio else None,
        "files": files,
    }


def norm(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def wer_all(engine, files):
    from faster_whisper import WhisperModel
    from jiwer import wer

    t0 = time.time()
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    load_s = time.time() - t0
    rows = []
    for i, path in enumerate(files, 1):
        segments, _ = model.transcribe(path, beam_size=1, language="en")
        hyp = norm(" ".join(s.text for s in segments))
        ref = norm(SENTENCES[i - 1])
        try:
            score = round(wer(ref, hyp), 4)
        except ZeroDivisionError:
            score = None
        rows.append({"ref": ref, "hyp": hyp, "wer": score})
        print(f"{engine} utt{i} WER={score}", flush=True)
    return {
        "asr_model": "faster-whisper base.en",
        "asr_load_s": round(load_s, 2),
        "wer_per_utt": [r["wer"] for r in rows],
        "wer_mean": round(sum(r["wer"] for r in rows if r["wer"] is not None) / len(rows), 4),
        "details": rows,
    }


try:
    import torch
    RESULT["runtime"]["torch"] = torch.__version__
    RESULT["runtime"]["cuda"] = torch.cuda.is_available()
except Exception as exc:  # noqa: BLE001
    RESULT["errors"].append(f"torch import: {exc!r}")

try:
    install()
except Exception:
    RESULT["status"] = "error"
    RESULT["errors"].append(traceback.format_exc()[-3000:])
    json.dump(RESULT, open(f"{OUT}/TTS_BENCH.json", "w"), indent=2)
    json.dump({"status": "error", "errors": RESULT["errors"]}, open(f"{OUT}/DONE.json", "w"), indent=2)
    raise

for name, fn in [("kokoro", run_kokoro), ("piper", run_piper)]:
    try:
        RESULT["engines"][name] = fn()
    except Exception:
        RESULT["engines"][name] = {"status": "error", "error": traceback.format_exc()[-2500:]}
        RESULT["errors"].append(f"{name}: failed")

try:
    RESULT["wer"] = {
        "kokoro": wer_all("kokoro", RESULT["engines"].get("kokoro", {}).get("files", [])),
        "piper": wer_all("piper", RESULT["engines"].get("piper", {}).get("files", [])),
    }
except Exception:
    RESULT["wer"] = {"status": "error", "error": traceback.format_exc()[-2500:]}
    RESULT["errors"].append("WER failed")

json.dump(RESULT, open(f"{OUT}/TTS_BENCH.json", "w"), indent=2)
json.dump({"status": RESULT["status"], "errors": RESULT["errors"]}, open(f"{OUT}/DONE.json", "w"), indent=2)
print(json.dumps({k: RESULT[k] for k in ("engines", "wer")}, indent=2)[:6000])