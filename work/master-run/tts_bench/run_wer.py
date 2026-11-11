"""WER-only pass for the local TTS benchmark (faster-whisper with numpy input)."""

import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

OUT = Path("/workspaces/OpenMontage/work/master-run/tts_bench")
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


def norm(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def load16k(path):
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != 16000:
        x = resample_poly(x, 16000, sr)
    return x


def wer(files):
    from faster_whisper import WhisperModel
    from jiwer import wer as jiwer_wer
    import time
    t0 = time.time()
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    load = time.time() - t0
    rows = []
    for i, p in enumerate(files, 1):
        segs, _ = model.transcribe(load16k(p), beam_size=1, language="en")
        hyp = norm(" ".join(s.text for s in segs))
        ref = norm(SENTENCES[i - 1])
        rows.append({"ref": ref, "hyp": hyp, "wer": round(jiwer_wer(ref, hyp), 4)})
    vals = [r["wer"] for r in rows]
    return {"asr_model": "faster-whisper base.en", "load_s": round(load, 2),
            "wer_per_utt": vals, "wer_mean": round(sum(vals) / len(vals), 4), "details": rows}


d = json.load(open(OUT / "LOCAL_TTS_BENCH.json"))
d["wer"] = {"kokoro": wer(d["engines"]["kokoro"]["files"]),
            "piper": wer(d["engines"]["piper"]["files"])}
d["errors"] = [e for e in d.get("errors", []) if not e.startswith("wer:")]
json.dump(d, open(OUT / "LOCAL_TTS_BENCH.json", "w"), indent=2)
json.dump({"status": d["status"], "errors": d["errors"]}, open(OUT / "DONE.json", "w"), indent=2)
print(json.dumps({k: {"wer_mean": v["wer_mean"], "wer": v["wer_per_utt"]} for k, v in d["wer"].items()}, indent=2))
for r in d["wer"]["kokoro"]["details"]:
    print("K", r["wer"], "|", r["hyp"][:80])
for r in d["wer"]["piper"]["details"]:
    print("P", r["wer"], "|", r["hyp"][:80])