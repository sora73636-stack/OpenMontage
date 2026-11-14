#!/usr/bin/env python3
"""Build Stage C (P1) Kaggle script kernels, reusing the Stage B common header."""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "audit/scripts/kaggle_environment_snapshot.py"
CFG = ROOT / "audit/config"
OUT = ROOT / "audit/kaggle/p1"

spec = importlib.util.spec_from_file_location("p0", ROOT / "audit/scripts/build_p0_notebooks.py")
P0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P0)
HEADER = P0.HEADER

REVISIONS = {
    "kokoro-82m": ("hexgrad/kokoro", "dfb907a02bba"),
    "whisper-large-v3-turbo": ("openai/whisper", "86098128c0b4"),
    "parakeet-tdt-0.6b-v3": ("NVIDIA/NeMo", "079e48770098"),
    "deepfilternet3": ("Rikorose/DeepFilterNet", "7b14b895fe7fc42cab72b4a4c1e49c982bd6404b"),
    "wan2.1-t2v-1.3b": ("Wan-Video/Wan2.1", "9737cba9c1c3"),
    "depth-anything-v2-small": ("LiheYoung/Depth-Anything", "1d03336771fe"),
    "video-depth-anything-small": ("DepthAnything/Video-Depth-Anything", "4f5ae23172ba"),
    "sdxl-base-1.0": ("Stability-AI/generative-models", "e8cd657656fa"),
}

KOKORO = r'''
def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_kokoro"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.11", "kokoro")
    tr = uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    inst = uvpip(env, uv, "kokoro soundfile", 1800)
    uvpip(env, uv, "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl", 900)
    if inst["returncode"] != 0:
        return finish("BLOCKED", "kokoro install failed", {"install": inst["stderr"][-1500:]})
    script = """
import time, torch, numpy as np, soundfile as sf, json
from kokoro import KPipeline
torch.cuda.reset_peak_memory_stats()
t0=time.time()
pipe=KPipeline(lang_code='a')
text=open(__SCRIPT__).read()
chunks=[a for _,_,a in pipe(text, voice='af_heart')]
audio=np.concatenate(chunks)
sf.write(__OUT__, audio, 24000)
peak=torch.cuda.max_memory_allocated()/2**20
print(json.dumps({'dtype':'float32','gen_s':time.time()-t0,'samples':len(audio),'sr':24000,'peak_alloc_mb':peak}))
""".replace("__SCRIPT__", repr(str(CONFIG / "science_voice_script.txt"))).replace("__OUT__", repr(str(RESULTS / "kokoro-82m/out.wav")))
    (WORK/"scripts/kokoro_run.py").write_text(script, encoding="utf-8")
    run = sh(f"{env}/bin/python {WORK/'scripts/kokoro_run.py'}", 7200)
    m = {}
    for line in run["stdout"].splitlines():
        if line.strip().startswith("{"):
            try: m = json.loads(line)
            except Exception: pass
    outs = []; save_output(RESULTS / "kokoro-82m/out.wav", outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "stderr": run["stderr"][-3000:]}, "metrics": m, "outputs": outs})
    dur = None
    import wave
    p = RESULTS / "kokoro-82m/out.wav"
    if p.exists():
        with wave.open(str(p), "rb") as w: dur = w.getnframes()/w.getframerate()
    STATE["steps"]["duration_s"] = dur
    STATE["steps"]["rtf"] = m.get("gen_s", 0)/dur if (m.get("gen_s") and dur) else None
    a = snap.collect(LOGS, "after_kokoro")
    ok = run["returncode"] == 0 and bool(outs) and dur
    return finish("PASS" if ok else "FAIL", None if ok else "kokoro inference failed",
                  {"dtype": m.get("dtype"), "runtime_seconds": m.get("gen_s"), "rtf": STATE["steps"]["rtf"],
                   "peak_vram_allocated_mb": m.get("peak_alloc_mb")})
'''

WHISPER = r'''
def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_whisper"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.11", "whisper")
    uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    uvpip(env, uv, '"setuptools<81" wheel', 600)
    inst = uvpip(env, uv, "--no-build-isolation-package openai-whisper openai-whisper jiwer soundfile", 1800)
    if inst["returncode"] != 0:
        return finish("BLOCKED", "whisper install failed", {"install": inst["stderr"][-2000:]})
    data = WEIGHTS / "librispeech"
    data.mkdir(parents=True, exist_ok=True)
    arch = data / "dev-clean.tar.gz"
    if not arch.exists():
        dl = sh(f"wget -q -O {arch} https://www.openslr.org/resources/12/dev-clean.tar.gz", 1800)
        STATE["steps"]["download_librispeech"] = {"rc": dl["returncode"], "bytes": arch.stat().st_size if arch.exists() else 0}
    ex = data / "LibriSpeech"
    if not ex.exists():
        sh(f"tar xzf {arch} -C {data}", 1800)
    script = """
import os, glob, json, time, torch, soundfile as sf, numpy as np
from pathlib import Path
import whisper, jiwer
torch.cuda.reset_peak_memory_stats()
root=Path(__SEARCH__)
fls=sorted(root.rglob('*.flac'))
# keep ~40 minutes: first files until 2400 s
sel=[]; total=0.0
for f in fls:
    info=sf.info(str(f)); total+=info.duration
    sel.append(f)
    if total>=2400: break
trans={}
for t in root.rglob('*.trans.txt'):
    for line in t.read_text().splitlines():
        if ' ' in line:
            uid, txt = line.split(' ',1); trans[uid]=txt
model=whisper.load_model('large-v3-turbo', device='cuda')
hyps=[]; refs=[]; t0=time.time()
for f in sel:
    audio,sr=sf.read(str(f), dtype='float32')
    if sr!=16000:
        import librosa  # noqa
    r=model.transcribe(str(f), language='en', fp16=True, beam_size=1, verbose=False)
    hyp=r['text'].strip()
    ref=trans.get(f.stem,'')
    hyps.append(hyp); refs.append(ref)
gen=time.time()-t0
def norm(t):
    import re, string
    t=t.lower().translate(str.maketrans('', '', string.punctuation))
    return ' '.join(t.split())
wer=jiwer.wer([norm(r) for r in refs],[norm(h) for h in hyps]) if refs else None
cer=jiwer.cer([norm(r) for r in refs],[norm(h) for h in hyps]) if refs else None
out={'files':len(sel),'audio_s':total,'gen_s':gen,'rtf':gen/total if total else None,
     'wer':wer,'cer':cer,'dtype':'float16','peak_alloc_mb':torch.cuda.max_memory_allocated()/2**20}
print(json.dumps(out))
Path(__OUT__).write_text(json.dumps({'files':len(sel),'audio_s':total,'wer':wer,'cer':cer,
    'samples':[{'file':str(f),'ref':r,'hyp':h} for f,r,h in zip(sel[-10:],refs[-10:],hyps[-10:])]}, indent=2))
""".replace("__SEARCH__", repr(str(ex))).replace("__OUT__", repr(str(RESULTS / "whisper-large-v3-turbo/wers.json")))
    (WORK/"scripts/whisper_run.py").write_text(script, encoding="utf-8")
    run = sh(f"PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python {WORK/'scripts/whisper_run.py'}", 10800)
    m = {}
    for line in run["stdout"].splitlines():
        if line.strip().startswith("{"):
            try: m = json.loads(line)
            except Exception: pass
    outs = []; save_output(RESULTS / "whisper-large-v3-turbo/wers.json", outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "stderr": run["stderr"][-3000:]}, "metrics": m, "outputs": outs})
    ok = run["returncode"] == 0 and bool(outs) and m.get("wer") is not None
    return finish("PASS" if ok else "FAIL", None if ok else "whisper run failed",
                  {"dtype": m.get("dtype"), "runtime_seconds": m.get("gen_s"), "rtf": m.get("rtf"),
                   "wer": m.get("wer"), "cer": m.get("cer"), "peak_vram_allocated_mb": m.get("peak_alloc_mb")})
'''

PARAKEET = r'''
def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_parakeet"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.10", "parakeet")
    uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    inst = uvpip(env, uv, '"nemo_toolkit[asr]" soundfile jiwer', 10800)
    if inst["returncode"] != 0:
        return finish("BLOCKED", "nemo install failed", {"install": inst["stderr"][-2000:]})
    data = WEIGHTS / "librispeech"; data.mkdir(parents=True, exist_ok=True)
    arch = data / "dev-clean.tar.gz"
    if not arch.exists(): sh(f"wget -q -O {arch} https://www.openslr.org/resources/12/dev-clean.tar.gz", 1800)
    ex = data / "LibriSpeech"
    if not ex.exists(): sh(f"tar xzf {arch} -C {data}", 1800)
    script = """
import json, time, torch, soundfile as sf
from pathlib import Path
import jiwer
import nemo.collections.asr as nemo_asr
torch.cuda.reset_peak_memory_stats()
root=Path(__SEARCH__)
sel=[]; total=0.0
for f in sorted(root.rglob('*.flac')):
    info=sf.info(str(f)); total+=info.duration; sel.append(f)
    if total>=2400: break
trans={}
for t in root.rglob('*.trans.txt'):
    for line in t.read_text().splitlines():
        if ' ' in line:
            uid, txt = line.split(' ',1); trans[uid]=txt
model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v3")
model = model.to('cuda'); model.eval()
t0=time.time()
out = model.transcribe([str(f) for f in sel], batch_size=8)
gen=time.time()-t0
hyps=[]
for o in out:
    if hasattr(o,'text'): hyps.append(o.text)
    elif isinstance(o,(list,tuple)): hyps.append(str(o[0]))
    else: hyps.append(str(o))
refs=[trans.get(f.stem,'') for f in sel]
def norm(t):
    import string
    return ' '.join(t.lower().translate(str.maketrans('', '', string.punctuation)).split())
wer=jiwer.wer([norm(r) for r in refs],[norm(h) for h in hyps]) if refs else None
cer=jiwer.cer([norm(r) for r in refs],[norm(h) for h in hyps]) if refs else None
print(json.dumps({'files':len(sel),'audio_s':total,'gen_s':gen,'rtf':gen/total if total else None,
                  'wer':wer,'cer':cer,'peak_alloc_mb':torch.cuda.max_memory_allocated()/2**20}))
Path(__OUT__).write_text(json.dumps({'files':len(sel),'audio_s':total,'wer':wer,'cer':cer}, indent=2))
""".replace("__SEARCH__", repr(str(ex))).replace("__OUT__", repr(str(RESULTS / "parakeet-tdt-0.6b-v3/wers.json")))
    (WORK/"scripts/parakeet_run.py").write_text(script, encoding="utf-8")
    run = sh(f"PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python {WORK/'scripts/parakeet_run.py'}", 10800)
    m = {}
    for line in run["stdout"].splitlines():
        if line.strip().startswith("{"):
            try: m = json.loads(line)
            except Exception: pass
    outs = []; save_output(RESULTS / "parakeet-tdt-0.6b-v3/wers.json", outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "stderr": run["stderr"][-3000:]}, "metrics": m, "outputs": outs})
    ok = run["returncode"] == 0 and bool(outs) and m.get("wer") is not None
    return finish("PASS" if ok else "FAIL", None if ok else "parakeet run failed",
                  {"dtype": "FP16" if ok else None, "runtime_seconds": m.get("gen_s"), "rtf": m.get("rtf"),
                   "wer": m.get("wer"), "cer": m.get("cer"), "peak_vram_allocated_mb": m.get("peak_alloc_mb")})
'''

DFN = r'''
def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_dfn"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.11", "deepfilternet")
    uvpip(env, uv, "torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    inst = uvpip(env, uv, "deepfilternet numpy soundfile", 3600)
    if inst["returncode"] != 0:
        return finish("BLOCKED", "deepfilternet install failed", {"install": inst["stderr"][-2000:]})
    repo = clone(REPO_URL, REPO_SHA, "deepfilternet")  # pinned source, provenance only
    outdir = RESULTS / "deepfilternet3"; outdir.mkdir(parents=True, exist_ok=True)
    prep = """
import numpy as np, soundfile as sf
sr=48000; dur=30.0; t=np.arange(int(sr*dur))/sr
rng=np.random.default_rng(1234)
clean=0.1*np.sin(2*np.pi*440*t)+0.05*np.sin(2*np.pi*220*t)
noise=0.05*rng.standard_normal(clean.shape)
noisy=clean+noise
sf.write(__CLEAN__, clean.astype(np.float32), sr, subtype='PCM_16')
sf.write(__NOISY__, noisy.astype(np.float32), sr, subtype='PCM_16')
print('prep ok')
""".replace("__CLEAN__", repr(str(outdir/"clean.wav"))).replace("__NOISY__", repr(str(outdir/"noisy.wav")))
    (WORK/"scripts/dfn_prep.py").write_text(prep, encoding="utf-8")
    prep_run = sh(f"{env}/bin/python {WORK/'scripts/dfn_prep.py'}", 600)
    if prep_run["returncode"] != 0:
        return finish("BLOCKED", "dfn test signal generation failed")
    # official CLI usage (README): deepFilter path/to/noisy_audio.wav --output-dir <dir>
    cmd = f"{env}/bin/deepFilter --output-dir {outdir} {outdir/'noisy.wav'}"
    gpup = subprocess.Popen(f"timeout 3600 nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader -l 1 > {WORK}/dfn_gpu.txt", shell=True)
    t0 = time.time(); run = sh(cmd, 3600); elapsed = time.time() - t0
    gpup.terminate()
    produced = [p for p in sorted(outdir.glob("*.wav")) if p.name not in ("noisy.wav", "clean.wav")]
    m = {"gen_s": round(elapsed, 3), "in_s": 30.0, "peak_vram_mib": max_gpu_mib(WORK / "dfn_gpu.txt")}
    if produced:
        chk = """
import json, sys, soundfile as sf
i = sf.info(sys.argv[1])
print(json.dumps({'path': sys.argv[1], 'sr': i.samplerate, 'frames': i.frames,
                  'seconds': i.frames / i.samplerate, 'subtype': i.subtype, 'channels': i.channels}))
"""
        (WORK/"scripts/dfn_check.py").write_text(chk, encoding="utf-8")
        r = sh(f"{env}/bin/python {WORK/'scripts/dfn_check.py'} {produced[0]}", 300)
        for line in r["stdout"].splitlines():
            if line.strip().startswith("{"):
                try: m.update(json.loads(line))
                except Exception: pass
    if m.get("seconds"):
        m["drift_ms"] = abs(m["seconds"] - 30.0) * 1000.0
        m["rtf"] = m["gen_s"] / 30.0
    outs = []
    for p in [outdir/"clean.wav", outdir/"noisy.wav"] + produced: save_output(p, outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "stderr": run["stderr"][-3000:]}, "metrics": m, "outputs": outs})
    ok = run["returncode"] == 0 and bool(produced) and m.get("drift_ms") is not None and m["drift_ms"] < 500
    return finish("PASS" if ok else "FAIL", None if ok else "dfn run failed",
                  {"dtype": "FP32", "runtime_seconds": m.get("gen_s"), "drift_ms": m.get("drift_ms"),
                   "peak_vram_mib": m.get("peak_vram_mib"), "subtype": m.get("subtype")})
'''

WAN = r'''
def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_wan"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.10", "wan")
    uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    repo = clone(REPO_URL, REPO_SHA, "wan21")
    # flash_attn has no wheel for torch 2.6/py310 and fails to build under uv build isolation
    # (setup.py imports torch). Wan's attention falls back to PyTorch SDPA when it is absent,
    # so install the official requirements without that optional line.
    uvpip(env, uv, '"setuptools<81" wheel', 600)
    req_txt = (repo / "requirements.txt").read_text()
    kept = [l for l in req_txt.splitlines() if l.strip() and not l.strip().lower().startswith("flash")]
    filtered = WORK / "requirements_noflash.txt"
    filtered.write_text("\n".join(kept) + "\n")
    STATE["steps"]["requirements_filtered"] = {"dropped": [l for l in req_txt.splitlines() if l.strip().lower().startswith("flash")]}
    req = uvpip(env, uv, f"-r {filtered}", 7200)
    if req["returncode"] != 0:
        return finish("BLOCKED", "wan requirements failed", {"install": req["stderr"][-2000:]})
    uvpip(env, uv, "huggingface_hub", 900)
    model = WEIGHTS / "Wan2.1-T2V-1.3B"
    if not model.exists():
        hfcli = "hf" if (env / "bin/hf").exists() else "huggingface-cli"
        dl = sh(f"{env}/bin/{hfcli} download Wan-AI/Wan2.1-T2V-1.3B --local-dir {model}", 7200)
        STATE["steps"]["download_model"] = {"rc": dl["returncode"], "stderr": dl["stderr"][-1000:]}
    prompts = json.loads((CONFIG / "image_video_prompts.json").read_text())
    prompt = prompts["video_prompt"]
    cmd = (f"cd {repo} && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python generate.py "
           f"--task t2v-1.3B --size 832*480 --ckpt_dir {model} --offload_model True --t5_cpu "
           f"--sample_shift 8 --sample_guide_scale 6 --seed 424242 --prompt {json.dumps(prompt)}")
    run = sh(cmd, 10800)
    outs = []
    for p in sorted(repo.glob("*.mp4")): save_output(p, outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "stderr": run["stderr"][-4000:]}, "outputs": outs})
    ok = run["returncode"] == 0 and bool(outs)
    return finish("PASS" if ok else "FAIL", None if ok else "wan generation failed",
                  {"dtype": "FP16", "runtime_seconds": run["duration_s"], "cpu_offload": True})
'''

DEPTHV2 = r'''
def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_depthv2"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.10", "depthv2")
    uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    inst = uvpip(env, uv, "transformers accelerate pillow numpy", 1800)
    if inst["returncode"] != 0:
        return finish("BLOCKED", "transformers install failed")
    script = """
import json, time, torch, numpy as np
from PIL import Image, ImageDraw
from transformers import pipeline
torch.cuda.reset_peak_memory_stats()
pipe=pipeline('depth-estimation', model='depth-anything/Depth-Anything-V2-Small-hf', device=0)
from pathlib import Path
out=Path(__OUT__); out.mkdir(parents=True, exist_ok=True)
W=H=640
def scene(i):
    a=np.zeros((H,W,3),np.uint8)
    im=Image.fromarray(a); d=ImageDraw.Draw(im)
    for y in range(H):  # sky gradient (far) -> ground (near)
        k=y/H
        d.line([(0,y),(W,y)], fill=(int(120+80*k), int(150+60*k), int(200+40*k)))
    d.rectangle([0,int(H*0.62),W,H], fill=(70,110,60))
    d.rectangle([80+i*6,300,240+i*6,430], fill=(180,90,70))
    d.rectangle([380,340,520,470], fill=(90,120,190))
    return im
times=[]; fin=[]; rngs=[]
for i in range(10):
    im=scene(i)
    t=time.time(); r=pipe(inputs=im); times.append(time.time()-t)
    d=np.array(r['depth']).astype(np.float32)
    fin.append(bool(np.isfinite(d).all())); rngs.append((float(d.min()),float(d.max())))
    if i < 3:
        vis=(255*(d-d.min())/(d.max()-d.min()+1e-8)).astype(np.uint8)
        Image.fromarray(vis).save(out/f'depth_{i:02d}.png')
print(json.dumps({'times':times,'finite':all(fin),'range':[min(x[0] for x in rngs),max(x[1] for x in rngs)],
                  'peak_alloc_mb':torch.cuda.max_memory_allocated()/2**20,'dtype':str(next(pipe.model.parameters()).dtype)}))
""".replace("__OUT__", repr(str(RESULTS/"depth-anything-v2-small")))
    (WORK/"scripts/depthv2_run.py").write_text(script, encoding="utf-8")
    run = sh(f"PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python {WORK/'scripts/depthv2_run.py'}", 5400)
    m = {}
    for line in run["stdout"].splitlines():
        if line.strip().startswith("{"):
            try: m = json.loads(line)
            except Exception: pass
    outs = []
    for p in sorted((RESULTS/"depth-anything-v2-small").glob("*.png")): save_output(p, outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "stderr": run["stderr"][-3000:]}, "metrics": m, "outputs": outs})
    ok = run["returncode"] == 0 and len(outs) == 3 and m.get("finite")
    return finish("PASS" if ok else "FAIL", None if ok else "depth v2 run failed",
                  {"dtype": m.get("dtype"), "runtime_seconds": sum(m.get("times") or [0]), "peak_vram_allocated_mb": m.get("peak_alloc_mb")})
'''

VIDEODEPTH = r'''
def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_videodepth"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.10", "videodepth")
    uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    repo = clone(REPO_URL, REPO_SHA, "videodepth")
    # requirements.txt pins torch==2.1.1 / xformers==0.0.23 / OpenEXR==3.3.1 which conflict with the
    # torch 2.6 cu126 env; install only the runtime deps the official run.py actually needs
    # (xformers/decord/OpenEXR are optional, guarded by try/except in the repo).
    inst = uvpip(env, uv, "opencv-python-headless pillow imageio imageio-ffmpeg einops easydict tqdm matplotlib", 1800)
    if inst["returncode"] != 0:
        return finish("BLOCKED", "videodepth requirements failed", {"install": inst["stderr"][-2000:]})
    uvpip(env, uv, "huggingface_hub", 900)
    (repo / "checkpoints").mkdir(parents=True, exist_ok=True)
    ckpt = repo / "checkpoints/video_depth_anything_vits.pth"
    if not ckpt.exists():
        model = WEIGHTS / "Video-Depth-Anything-Small"
        hfcli = "hf" if (env / "bin/hf").exists() else "huggingface-cli"
        dl = sh(f"{env}/bin/{hfcli} download depth-anything/Video-Depth-Anything-Small video_depth_anything_vits.pth --local-dir {model}", 7200)
        STATE["steps"]["download_model"] = {"rc": dl["returncode"], "stderr": dl["stderr"][-1000:]}
        src = model / "video_depth_anything_vits.pth"
        if src.exists():
            import shutil as _sh; _sh.copy2(src, ckpt)
    if not ckpt.exists():
        return finish("BLOCKED", "vits checkpoint missing")
    # deterministic 2 s 640x480 24 fps test clip with real depth structure
    vid = WORK / "fixtures/videodepth/input.mp4"; vid.parent.mkdir(parents=True, exist_ok=True)
    gen = """
import cv2, numpy as np
W,H,F,D=640,480,24,2
vw=cv2.VideoWriter(__OUT__,cv2.VideoWriter_fourcc(*'mp4v'),F,(W,H))
for i in range(F*D):
    f=np.zeros((H,W,3),np.uint8)
    for y in range(H):
        k=y/H; f[y,:]=(int(120+80*k), int(150+60*k), int(200+40*k))
    f[int(H*0.62):,:]=(60,110,60)
    cv2.rectangle(f,(80+i*4,300),(240+i*4,430),(70,90,180),-1)
    cv2.rectangle(f,(380,340),(520,470),(190,120,90),-1)
    vw.write(f)
vw.release()
""".replace("__OUT__", repr(str(vid)))
    (WORK/"scripts/vd_gen.py").write_text(gen, encoding="utf-8"); sh(f"{env}/bin/python {WORK/'scripts/vd_gen.py'}", 600)
    outdir = RESULTS / "video-depth-anything-small"; outdir.mkdir(parents=True, exist_ok=True)
    # official example: python3 run.py --input_video <video> --output_dir <dir> --encoder vits
    cmd = (f"cd {repo} && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python run.py "
           f"--input_video {vid} --output_dir {outdir} --encoder vits --max_len 48 --target_fps 12")
    gpup = subprocess.Popen(f"timeout 3600 nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader -l 1 > {WORK}/vd_gpu.txt", shell=True)
    run = sh(cmd, 10800)
    gpup.terminate()
    peak_mib = max_gpu_mib(WORK / "vd_gpu.txt")
    outs = []
    for p in sorted(outdir.rglob("*_vis.mp4")): save_output(p, outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "stderr": run["stderr"][-4000:]}, "outputs": outs})
    ok = run["returncode"] == 0 and bool(outs)
    return finish("PASS" if ok else "FAIL", None if ok else "video depth run failed",
                  {"dtype": "FP16", "runtime_seconds": run["duration_s"], "peak_vram_mib": peak_mib})
'''

SDXL = r'''
def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_sdxl"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.10", "sdxl")
    uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    inst = uvpip(env, uv, "diffusers transformers accelerate safetensors", 1800)
    if inst["returncode"] != 0:
        return finish("BLOCKED", "diffusers install failed")
    prompts = json.loads((CONFIG / "image_video_prompts.json").read_text())
    script = """
import json, time, torch
from diffusers import StableDiffusionXLPipeline
torch.cuda.reset_peak_memory_stats()
pipe=StableDiffusionXLPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0', torch_dtype=torch.float16, use_safetensors=True, variant='fp16', low_cpu_mem_usage=True)
pipe.enable_model_cpu_offload()
from pathlib import Path
out=Path(__OUT__); out.mkdir(parents=True, exist_ok=True); recs=[]
for it in __PROMPTS__:
    t=time.time()
    im=pipe(prompt=it['prompt'], height=512, width=512, num_inference_steps=25,
            generator=torch.Generator(device='cuda').manual_seed(it['seed'])).images[0]
    p=out/f"sdxl_{it['id']}.png"; im.save(p); recs.append({'id':it['id'],'s':time.time()-t})
print(json.dumps({'images':recs,'peak_alloc_mb':torch.cuda.max_memory_allocated()/2**20,'dtype':str(next(pipe.unet.parameters()).dtype)}))
""".replace("__OUT__", repr(str(RESULTS/"sdxl-base-1.0"))).replace("__PROMPTS__", json.dumps(prompts["image_prompts"]))
    (WORK/"scripts/sdxl_run.py").write_text(script, encoding="utf-8")
    run = sh(f"PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python {WORK/'scripts/sdxl_run.py'}", 7200)
    m = {}
    for line in run["stdout"].splitlines():
        if line.strip().startswith("{"):
            try: m = json.loads(line)
            except Exception: pass
    outs = []
    for p in sorted((RESULTS/"sdxl-base-1.0").glob("*.png")): save_output(p, outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "stderr": run["stderr"][-3000:]}, "metrics": m, "outputs": outs})
    ok = run["returncode"] == 0 and len(outs) == 3
    return finish("PASS" if ok else "FAIL", None if ok else "sdxl run failed",
                  {"dtype": m.get("dtype"), "runtime_seconds": sum(x.get("s",0) for x in m.get("images") or []),
                   "peak_vram_allocated_mb": m.get("peak_alloc_mb")})
'''

CODES = {
    "kokoro-82m": KOKORO,
    "whisper-large-v3-turbo": WHISPER,
    "parakeet-tdt-0.6b-v3": PARAKEET,
    "deepfilternet3": DFN,
    "wan2.1-t2v-1.3b": WAN,
    "depth-anything-v2-small": DEPTHV2,
    "video-depth-anything-small": VIDEODEPTH,
    "sdxl-base-1.0": SDXL,
}


def main() -> None:
    helper_raw = HELPER.read_bytes(); helper_sha = hashlib.sha256(helper_raw).hexdigest()
    fixtures = {n: base64.b64encode((CFG / n).read_bytes()).decode() for n in ("science_voice_script.txt", "science_terms.json", "image_video_prompts.json")}
    for comp, code in CODES.items():
        repo, sha = REVISIONS[comp]
        body = HEADER
        body = (body.replace("__COMPONENT__", comp).replace("__PRIORITY__", "P1")
                    .replace("__KERNEL__", "openmontage-p1-" + comp.replace(".", "-"))
                    .replace("__REPO_URL__", f"https://github.com/{repo}")
                    .replace("__REPO_SHA__", sha)
                    .replace("__HELPER_B64__", base64.b64encode(helper_raw).decode())
                    .replace("__HELPER_SHA__", helper_sha)
                    .replace("__FIXTURES_JSON__", json.dumps(fixtures)))
        body += "\n" + code.replace("def run():", "def run():") + "\n\nif __name__ == '__main__':\n    try:\n        raise SystemExit(run())\n    except SystemExit:\n        raise\n    except Exception:\n        tb = traceback.format_exc(); print(tb); log('UNHANDLED ' + tb[-3000:]); finish('FAIL', 'unhandled exception'); raise SystemExit(4)\n"
        body = body.replace("{{", "{").replace("}}", "}")
        d = OUT / comp; d.mkdir(parents=True, exist_ok=True)
        (d / "notebook.py").write_text(body, encoding="utf-8")
        meta = {"id": f"forts845/openmontage-p1-{comp.replace('.', '-')}", "title": f"OpenMontage P1 {comp}",
                "code_file": "notebook.py", "language": "python", "kernel_type": "script", "is_private": "true",
                "enable_gpu": "true", "enable_tpu": "false", "enable_internet": "true", "machine_shape": "NvidiaTeslaT4",
                "dataset_sources": [], "competition_sources": [], "kernel_sources": [], "model_sources": []}
        (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print("wrote", d / "notebook.py", len(body))


if __name__ == "__main__":
    main()