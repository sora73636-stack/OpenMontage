"""DeepFilterNet real denoise test: clean -> noisy -> enhanced, with WER."""

import json
import re
import time

import torch
import torchaudio
from df.enhance import init_df, enhance
from faster_whisper import WhisperModel
from jiwer import wer as jiwer_wer

ROOT = "/workspaces/OpenMontage/work/master-run/audio_dsp"
REF = "Water expands when it freezes, which is why ice floats on a lake."


def norm(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def load16k(path):
    x, sr = torchaudio.load(path)
    if sr != 16000:
        x = torchaudio.functional.resample(x, sr, 16000)
    return x.mean(0)


def asr_wer(model, path):
    segs, _ = model.transcribe(load16k(path).numpy(), beam_size=1, language="en")
    hyp = norm(" ".join(s.text for s in segs))
    return round(jiwer_wer(norm(REF), hyp), 4), hyp


model, df_state, _ = init_df(log_level="WARNING")
noisy, sr = torchaudio.load(f"{ROOT}/noisy_mild.wav")
if noisy.shape[0] > 1:
    noisy = noisy.mean(0, keepdim=True)
if sr != 48000:
    noisy = torchaudio.functional.resample(noisy, sr, 48000)
t0 = time.time()
enhanced = enhance(model, df_state, noisy)
elapsed = time.time() - t0
torchaudio.save(f"{ROOT}/enhanced.wav", enhanced.cpu(), 48000)
asr = WhisperModel("base.en", device="cpu", compute_type="int8")
res = {
    "engine": "DeepFilterNet3",
    "torch": torch.__version__,
    "torchaudio": torchaudio.__version__,
    "enhance_s": round(elapsed, 2),
    "input_s": round(noisy.shape[1] / 48000, 2),
    "rtf": round(elapsed / (noisy.shape[1] / 48000), 3),
    "wer": {},
}
for name, path in [("clean", f"/workspaces/OpenMontage/work/master-run/tts_bench/audio/kokoro_01.wav"),
                   ("noisy", f"{ROOT}/noisy_mild.wav"), ("enhanced", f"{ROOT}/enhanced.wav")]:
    score, hyp = asr_wer(asr, path)
    res["wer"][name] = {"wer": score, "hyp": hyp}
json.dump(res, open(f"{ROOT}/deepfilternet_result.json", "w"), indent=2)
print(json.dumps(res, indent=2))