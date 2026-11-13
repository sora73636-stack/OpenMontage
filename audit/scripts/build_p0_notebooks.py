#!/usr/bin/env python3
"""Build Stage B P0 Kaggle script kernels (one per component).

Each kernel:
  * materialises the shared Stage A helper and verifies its SHA256,
  * writes the Phase 6 fixtures,
  * creates an isolated uv environment with the component's Python version,
  * installs official repo/requirements at the pinned Stage A revision,
  * runs the official inference path in FP16/FP32 (never BF16/FA2),
  * records peak VRAM, timings, outputs, SHA256 and a JSON summary.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "audit/scripts/kaggle_environment_snapshot.py"
CFG = ROOT / "audit/config"
OUT = ROOT / "audit/kaggle/p0"

REVISIONS = {
    "cosyvoice3": ("FunAudioLLM/CosyVoice", "074ca6dc9e80"),
    "ltx-video-2b-0.9.5": ("Lightricks/LTX-Video", "50f0aef12975"),
    "practical-rife-4.25": ("hzwer/Practical-RIFE", "bbfd2ea90910"),
    "real-esrgan-x4plus": ("xinntao/Real-ESRGAN", "a4abfb2979a7"),
}

HEADER = r'''#!/usr/bin/env python3
"""OpenMontage Stage B P0 component: __COMPONENT__ (priority __PRIORITY__)."""

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
os.environ.setdefault("HF_HOME", "/tmp/audit/hf")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/audit/cache")

WORK = Path("/kaggle/working/audit")
LOGS = WORK / "logs/kaggle"
RESULTS = WORK / "results"
CONFIG = WORK / "config"
ENVS = Path("/tmp/audit/envs")
REPOS = Path("/tmp/audit/repos")
WEIGHTS = Path("/tmp/audit/weights")
for _p in (WORK, LOGS, RESULTS, CONFIG, ENVS, REPOS, WEIGHTS):
    _p.mkdir(parents=True, exist_ok=True)

COMPONENT = "__COMPONENT__"
PRIORITY = "__PRIORITY__"
KERNEL_NAME = "__KERNEL__"
REPO_URL = "__REPO_URL__"
REPO_SHA = "__REPO_SHA__"

HELPER_B64 = "__HELPER_B64__"
HELPER_SHA = "__HELPER_SHA__"
FIXTURES_B64 = __FIXTURES_JSON__

LOG = LOGS / f"{{COMPONENT}}.log"
SUMMARY = RESULTS / COMPONENT
SUMMARY.mkdir(parents=True, exist_ok=True)
STATE = {{"component": COMPONENT, "priority": PRIORITY, "kernel": KERNEL_NAME,
          "utc_start": None, "utc_end": None, "status": "UNKNOWN",
          "steps": {{}}, "errors": []}}


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    line = f"{{utc()}} {{msg}}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sh(cmd, timeout=7200, quiet=False):
    started = time.time()
    rec = {{"cmd": cmd, "returncode": None, "duration_s": None, "stdout": "", "stderr": ""}}
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        rec["returncode"] = proc.returncode
        rec["stdout"] = proc.stdout[-20000:]
        rec["stderr"] = proc.stderr[-12000:]
    except Exception as exc:  # noqa: BLE001
        rec["error"] = f"{{type(exc).__name__}}: {{exc}}"
    rec["duration_s"] = round(time.time() - started, 3)
    if not quiet:
        log(f"$ {{cmd}} -> rc={{rec['returncode']}} {{rec['duration_s']}}s")
        if rec["stdout"]:
            log("stdout tail: " + rec["stdout"][-1500:].replace("\n", " | "))
        if rec["stderr"]:
            log("stderr tail: " + rec["stderr"][-1500:].replace("\n", " | "))
    return rec


def write_fixtures():
    for name, blob in FIXTURES_B64.items():
        path = CONFIG / name
        path.write_bytes(base64.b64decode(blob))
        log(f"fixture {{path.name}} {{path.stat().st_size}} bytes sha={{sha256_file(path)}}")


def materialise_helper():
    path = WORK / "scripts/kaggle_environment_snapshot.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(HELPER_B64))
    actual = sha256_file(path)
    STATE["steps"]["helper"] = {{"path": str(path), "expected_sha256": HELPER_SHA,
                                 "actual_sha256": actual, "match": actual == HELPER_SHA}}
    log(f"helper sha256 {{actual}} match={{actual == HELPER_SHA}}")
    if actual != HELPER_SHA:
        raise RuntimeError("helper sha mismatch")
    sys.path.insert(0, str(path.parent))
    import kaggle_environment_snapshot as snap  # noqa: PLC0415
    return snap


def ensure_env(pyver, name):
    uv = shutil.which("uv")
    if not uv:
        sh("python -m pip install --user uv", 900)
        uv = str(Path.home() / ".local/bin/uv")
    env = ENVS / name
    if not (env / "bin/python").exists():
        sh(f"{{uv}} venv --python {{pyver}} {{env}}", 1800)
    return env, uv


def uvpip(env, uv, args, timeout=7200):
    py = env / "bin/python"
    return sh(f"{{uv}} pip install --python {{py}} {{args}}", timeout)


def clone(repo_url, sha, name):
    dst = REPOS / name
    if not dst.exists():
        sh(f"git clone --recursive {{repo_url}} {{dst}}", 1800)
    sh(f"git -C {{dst}} checkout -q {{sha}}", 300)
    sh(f"git -C {{dst}} submodule update --init --recursive", 1800)
    return dst


def save_output(path, outputs):
    p = Path(path)
    if p.exists() and p.stat().st_size > 0:
        outputs.append({{"path": str(p), "bytes": p.stat().st_size, "sha256": sha256_file(p)}})
        return True
    return False


def finish(status, blocker=None, extra=None):
    STATE["utc_end"] = utc()
    STATE["status"] = status
    if blocker:
        STATE["blocker"] = blocker
    if extra:
        STATE["steps"].update(extra)
    (SUMMARY / "summary.json").write_text(json.dumps(STATE, indent=2), encoding="utf-8")
    (SUMMARY / "summary.txt").write_text(json.dumps(STATE, indent=2), encoding="utf-8")
    log("FINAL " + json.dumps({{"status": status, "blocker": blocker}}))
    print(json.dumps(STATE, indent=2))
    return 0 if status == "PASS" else 3


def sample_gpu(path, seconds=60):
    cmd = (f"timeout {{seconds}} nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used "
           f"--format=csv,noheader -l 1 > {{path}} 2>&1")
    return subprocess.Popen(cmd, shell=True)


def max_gpu_mib(path):
    vals = []
    for line in Path(path).read_text(errors="replace").splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3 and parts[2].endswith("MiB"):
            try:
                vals.append(int(parts[2].replace("MiB", "")))
            except ValueError:
                pass
    return max(vals) if vals else None
'''

RIFE = r'''
def main():
    import cv2
    import numpy as np

    snap = materialise_helper()
    write_fixtures()
    STATE["utc_start"] = utc()
    before = snap.collect(LOGS, "before_rife")
    t4 = snap.assert_t4(before)
    STATE["steps"]["environment_before"] = {{"t4": t4, "devices": before["torch"]["devices"]}}
    if not t4["ok"]:
        return finish("BLOCKED", "T4 assertion failed: " + "; ".join(t4["reasons"]))

    env, uv = ensure_env("3.11", "rife")
    torch_rec = uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    STATE["steps"]["install_torch"] = {{"rc": torch_rec["returncode"], "duration_s": torch_rec["duration_s"]}}
    repo = clone(REPO_URL, REPO_SHA, "practical-rife")
    req = uvpip(env, uv, f"-r {repo}/requirements.txt", 7200)
    STATE["steps"]["install_requirements"] = {{"rc": req["returncode"], "duration_s": req["duration_s"]}}
    if req["returncode"] != 0:
        return finish("BLOCKED", "RIFE requirements install failed")

    uvpip(env, uv, "gdown", 900)
    weights_dir = WEIGHTS / "practical-rife"
    weights_dir.mkdir(parents=True, exist_ok=True)
    archive = weights_dir / "rife_4_25_download"
    g = sh(f"{env}/bin/gdown 1ZKjcbmt1hypiFprJPIKW0Tt0lr_2i7bg -O {archive} --no-cookies", 1800)
    STATE["steps"]["download_4_25"] = {{"rc": g["returncode"], "duration_s": g["duration_s"],
                                        "stderr": g["stderr"][-1000:]}}
    if not archive.exists() or archive.stat().st_size == 0:
        return finish("BLOCKED", "4.25 archive download failed")

    train_log = repo / "train_log"
    train_log.mkdir(exist_ok=True)
    kind = sh(f"file {archive}")["stdout"]
    STATE["steps"]["archive"] = {{"path": str(archive), "bytes": archive.stat().st_size,
                                  "sha256": sha256_file(archive), "file": kind}}
    if "Zip archive" in kind or "gzip" in kind:
        sh(f"unzip -o -q {archive} -d {train_log}", 600)
    else:
        shutil.copy(archive, train_log / "flownet.pkl")
    pkl = train_log / "flownet.pkl"
    if not pkl.exists():
        return finish("BLOCKED", "flownet.pkl not found after extracting 4.25 archive")

    fx = WORK / "fixtures/rife"
    fx.mkdir(parents=True, exist_ok=True)
    W, H, DUR = 640, 360, 30

    def draw(t):
        frame = np.zeros((H, W, 3), np.uint8)
        scene = int(t // 5) % 3
        frame[:] = [(20, 30, 40), (40, 30, 20), (20, 40, 30)][scene]
        x = int((W - 120) * (0.5 + 0.5 * np.sin(t * 0.9)))
        y = int((H - 120) * (0.5 + 0.5 * np.sin(t * 1.3 + 1)))
        cv2.rectangle(frame, (x, y), (x + 120, y + 120), (200, 220, 255), -1)
        cv2.circle(frame, (W // 2, H // 2), 30, (255, 180, 60), -1)
        return frame

    input_mp4 = fx / "input_24fps.mp4"
    vw = cv2.VideoWriter(str(input_mp4), cv2.VideoWriter_fourcc(*"mp4v"), 24, (W, H))
    for i in range(DUR * 24):
        vw.write(draw(i / 24))
    vw.release()
    gt_mp4 = fx / "gt_48fps.mp4"
    vw = cv2.VideoWriter(str(gt_mp4), cv2.VideoWriter_fourcc(*"mp4v"), 48, (W, H))
    for i in range(DUR * 48):
        vw.write(draw(i / 48))
    vw.release()
    STATE["steps"]["fixtures"] = {{"input": str(input_mp4), "gt": str(gt_mp4),
                                   "input_sha256": sha256_file(input_mp4), "gt_sha256": sha256_file(gt_mp4)}}

    sampler = sample_gpu(LOGS / "rife_nvidia_smi.csv", 120)
    run = sh(f"cd {repo} && {{env}}/bin/python inference_video.py --multi=2 --video={input_mp4} --model=train_log", 5400)
    try:
        sampler.wait(timeout=15)
    except Exception:  # noqa: BLE001
        sampler.kill()
    STATE["steps"]["inference"] = {{"rc": run["returncode"], "duration_s": run["duration_s"],
                                    "stderr": run["stderr"][-4000:]}}
    produced = sorted(repo.glob("*.mp4"))
    outputs = []
    out_mp4 = None
    for p in produced:
        if p.name != input_mp4.name and save_output(p, outputs):
            out_mp4 = p
    STATE["steps"]["outputs"] = outputs
    STATE["peak_vram_mib_nvidia_smi"] = max_gpu_mib(LOGS / "rife_nvidia_smi.csv")
    STATE["peak_vram_source"] = "nvidia-smi memory.used (subprocess; torch API unavailable)"

    quality = {{}}
    if out_mp4 and out_mp4.exists():
        cap = cv2.VideoCapture(str(out_mp4))
        frames = []
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            frames.append(fr)
        cap.release()
        gt = cv2.VideoCapture(str(gt_mp4))
        gts = []
        while True:
            ok, fr = gt.read()
            if not ok:
                break
            gts.append(fr)
        gt.release()
        n = min(len(frames), len(gts))
        maes, psnrs = [], []
        for i in range(n):
            diff = cv2.absdiff(frames[i], gts[i]).mean()
            maes.append(float(diff))
            mse = float(np.mean((frames[i].astype(np.float32) - gts[i].astype(np.float32)) ** 2))
            psnrs.append(99.0 if mse == 0 else float(10 * np.log10(255.0 * 255.0 / mse)))
        odd_mae = [maes[i] for i in range(1, n, 2)] or maes
        quality = {{"frames_read": len(frames), "gt_frames": len(gts), "compared": n,
                    "mae_mean": sum(maes) / len(maes) if maes else None,
                    "mae_interpolated_mean": sum(odd_mae) / len(odd_mae) if odd_mae else None,
                    "psnr_mean": sum(psnrs) / len(psnrs) if psnrs else None,
                    "output_fps": 48, "note": "metric only; no threshold invented"}}
        STATE["steps"]["quality"] = quality

    after = snap.collect(LOGS, "after_rife")
    STATE["steps"]["environment_after"] = {{"devices": after["torch"]["devices"],
                                             "working_free_gib": after["disk_usage"]["working_free_gib"]}}

    ok = run["returncode"] == 0 and out_mp4 is not None and quality.get("frames_read", 0) > 0
    if ok and STATE["peak_vram_mib_nvidia_smi"] and STATE["peak_vram_mib_nvidia_smi"] >= 15000:
        return finish("FAIL", "peak VRAM >= 15 GB", {{"quality": quality}})
    return finish("PASS" if ok else "FAIL", None if ok else "inference/output validation failed",
                  {{"dtype": "FP32 (RIFE default; no dtype flag)", "rtf": None,
                    "runtime_seconds": run["duration_s"], "fps": 48 if ok else None}})
'''

ESRGAN = r'''
def main():
    import cv2
    import numpy as np

    snap = materialise_helper()
    write_fixtures()
    STATE["utc_start"] = utc()
    before = snap.collect(LOGS, "before_esrgan")
    t4 = snap.assert_t4(before)
    STATE["steps"]["environment_before"] = {{"t4": t4, "devices": before["torch"]["devices"]}}
    if not t4["ok"]:
        return finish("BLOCKED", "T4 assertion failed: " + "; ".join(t4["reasons"]))

    env, uv = ensure_env("3.11", "esrgan")
    tr = uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    STATE["steps"]["install_torch"] = {{"rc": tr["returncode"], "duration_s": tr["duration_s"]}}
    repo = clone(REPO_URL, REPO_SHA, "real-esrgan")
    req = uvpip(env, uv, f"-r {repo}/requirements.txt", 7200)
    STATE["steps"]["install_requirements"] = {{"rc": req["returncode"], "duration_s": req["duration_s"],
                                               "stderr": req["stderr"][-1500:]}}
    if req["returncode"] != 0:
        return finish("BLOCKED", "Real-ESRGAN requirements install failed")
    inst = uvpip(env, uv, f"-e {repo}", 1800)
    STATE["steps"]["install_realesrgan"] = {{"rc": inst["returncode"], "duration_s": inst["duration_s"], "stderr": inst["stderr"][-1500:]}}

    weights = WEIGHTS / "real-esrgan"
    weights.mkdir(parents=True, exist_ok=True)
    wpath = weights / "RealESRGAN_x4plus.pth"
    wg = sh(f"wget -q -O {wpath} https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth", 1800)
    STATE["steps"]["weights"] = {{"rc": wg["returncode"], "bytes": wpath.stat().st_size if wpath.exists() else 0,
                                  "sha256": sha256_file(wpath) if wpath.exists() else None}}
    if not wpath.exists() or wpath.stat().st_size == 0:
        return finish("BLOCKED", "weight download failed")

    fx = WORK / "fixtures/esrgan/inputs"
    fx.mkdir(parents=True, exist_ok=True)
    for i in range(10):
        img = np.zeros((256, 256, 3), np.uint8)
        for y in range(256):
            img[y, :, 0] = (y * 255) // 255
        img[:, :, 1] = np.linspace(0, 255, 256, dtype=np.uint8)[None, :]
        cv2.rectangle(img, (30 + i * 8, 60), (120 + i * 8, 180), (240, 240, 240), -1)
        cv2.circle(img, (190, 90 + i * 5), 35, (80, 200, 120), -1)
        cv2.imwrite(str(fx / f"frame_{i:02d}.png"), img)
    outdir = WORK / "fixtures/esrgan/outputs"
    outdir.mkdir(parents=True, exist_ok=True)

    wrapper = WORK / "scripts/esrgan_cli.py"
    wrapper.write_text(
        "import runpy, sys, torchvision_compat\n"
        "sys.argv = ['inference_realesrgan.py'] + sys.argv[1:]\n"
        "runpy.run_path('inference_realesrgan.py', run_name='__main__')\n",
        encoding="utf-8",
    )
    shim = WORK / "scripts/torchvision_compat.py"
    shim.write_text(
        "import sys, types, torchvision.transforms.functional as F\n"
        "m = types.ModuleType('torchvision.transforms.functional_tensor')\n"
        "m.rgb_to_grayscale = F.rgb_to_grayscale\n"
        "sys.modules['torchvision.transforms.functional_tensor'] = m\n",
        encoding="utf-8",
    )
    env_on = "TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1"
    sampler = sample_gpu(LOGS / "esrgan_nvidia_smi.csv", 180)
    cmd = (f"cd {repo} && {env_on} PYTHONPATH={WORK/'scripts'} {env}/bin/python "
           f"{wrapper} -n RealESRGAN_x4plus -i {fx} -o {outdir} --outscale 4")
    run = sh(cmd, 5400)
    try:
        sampler.wait(timeout=15)
    except Exception:  # noqa: BLE001
        sampler.kill()
    STATE["steps"]["inference"] = {{"rc": run["returncode"], "duration_s": run["duration_s"],
                                    "stderr": run["stderr"][-5000:]}}
    STATE["peak_vram_mib_nvidia_smi"] = max_gpu_mib(LOGS / "esrgan_nvidia_smi.csv")
    STATE["peak_vram_source"] = "nvidia-smi memory.used (subprocess)"

    outputs = []
    valid = 0
    for p in sorted(outdir.glob("*.png")):
        img = cv2.imread(str(p))
        if img is not None and img.shape[:2] == (1024, 1024):
            valid += 1
        save_output(p, outputs)
    STATE["steps"]["outputs"] = outputs
    STATE["steps"]["validation"] = {{"files": len(outputs), "valid_1024": valid}}
    after = snap.collect(LOGS, "after_esrgan")
    STATE["steps"]["environment_after"] = {{"working_free_gib": after["disk_usage"]["working_free_gib"]}}

    ok = run["returncode"] == 0 and valid == 10 and len(outputs) == 10
    return finish("PASS" if ok else "FAIL", None if ok else "inference or output validation failed",
                  {{"dtype": "FP32 (no dtype flag)", "runtime_seconds": run["duration_s"]}})
'''

LTX = r'''
def main():
    import torch

    snap = materialise_helper()
    write_fixtures()
    STATE["utc_start"] = utc()
    before = snap.collect(LOGS, "before_ltx")
    t4 = snap.assert_t4(before)
    STATE["steps"]["environment_before"] = {{"t4": t4, "devices": before["torch"]["devices"]}}
    if not t4["ok"]:
        return finish("BLOCKED", "T4 assertion failed: " + "; ".join(t4["reasons"]))

    env, uv = ensure_env("3.10", "ltx")
    tr = uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    STATE["steps"]["install_torch"] = {{"rc": tr["returncode"], "duration_s": tr["duration_s"]}}
    repo = clone(REPO_URL, REPO_SHA, "ltx-video")
    inst = uvpip(env, uv, f"-e {repo}[inference] accelerate", 7200)
    STATE["steps"]["install_repo"] = {{"rc": inst["returncode"], "duration_s": inst["duration_s"],
                                       "stderr": inst["stderr"][-2000:]}}
    if inst["returncode"] != 0:
        return finish("BLOCKED", "LTX repo install failed")

    import json as _json
    prompts = _json.loads((CONFIG / "image_video_prompts.json").read_text())
    prompt = prompts["video_prompt"]
    seed = prompts["video_seed"]

    out_path = RESULTS / "ltx-video-2b-0.9.5/out.mp4"
    script = """
import torch, json, time
from pathlib import Path
import sys
sys.path.insert(0, __SCRIPTS__)
from diffusers import LTXPipeline
from diffusers.utils import export_to_video
torch.cuda.reset_peak_memory_stats()
t0 = time.time()
pipe = LTXPipeline.from_pretrained('Lightricks/LTX-Video-0.9.5', torch_dtype=torch.float16, low_cpu_mem_usage=True)
pipe.enable_model_cpu_offload()
model_s = time.time() - t0
dtype = next(pipe.transformer.parameters()).dtype
t1 = time.time()
video = pipe(prompt=__PROMPT__, negative_prompt='worst quality, inconsistent motion, blurry, jittery, distorted',
             width=512, height=512, num_frames=49, num_inference_steps=30,
             generator=torch.Generator(device='cuda').manual_seed(__SEED__)).frames[0]
gen_s = time.time() - t1
out = __OUT__
export_to_video(video, out, fps=24)
peak_alloc = torch.cuda.max_memory_allocated() / 2**20
peak_res = torch.cuda.max_memory_reserved() / 2**20
print(json.dumps({'dtype': str(dtype), 'load_s': model_s, 'gen_s': gen_s, 'frames': len(video),
                  'peak_alloc_mb': peak_alloc, 'peak_reserved_mb': peak_res,
                  'attn': getattr(pipe.transformer.config, '_attn_implementation', 'unknown')}))
"""
    script = (script.replace("__SCRIPTS__", repr(str(WORK / "scripts")))
                    .replace("__PROMPT__", repr(prompt))
                    .replace("__SEED__", str(seed))
                    .replace("__OUT__", repr(str(out_path))))
    (WORK / "scripts/ltx_run.py").write_text(script, encoding="utf-8")
    run = sh(f"PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python {WORK/'scripts/ltx_run.py'}", 7200)
    STATE["steps"]["inference"] = {{"rc": run["returncode"], "duration_s": run["duration_s"],
                                    "stdout": run["stdout"][-3000:], "stderr": run["stderr"][-4000:]}}
    metrics = {{}}
    for line in run["stdout"].splitlines():
        if line.strip().startswith("{{"):
            try:
                metrics = json.loads(line.strip())
            except Exception:  # noqa: BLE001
                pass
    STATE["steps"]["metrics"] = metrics
    outputs = []
    save_output(out_path, outputs)
    STATE["steps"]["outputs"] = outputs

    probe = sh(f"ffprobe -v error -show_streams -show_format -of json {out_path}", 120)
    STATE["steps"]["ffprobe"] = probe["stdout"][:4000]
    decode = sh(f"ffmpeg -v error -i {out_path} -f null -", 600)
    STATE["steps"]["decode_clean"] = decode["returncode"] == 0 and not decode["stderr"].strip()
    after = snap.collect(LOGS, "after_ltx")
    STATE["steps"]["environment_after"] = {{"working_free_gib": after["disk_usage"]["working_free_gib"]}}

    ok = run["returncode"] == 0 and bool(outputs) and STATE["steps"]["decode_clean"] and metrics.get("frames") == 49
    return finish("PASS" if ok else "FAIL", None if ok else "inference/decode validation failed",
                  {{"dtype": metrics.get("dtype"), "runtime_seconds": metrics.get("gen_s"),
                    "peak_vram_allocated_mb": metrics.get("peak_alloc_mb"),
                    "peak_vram_reserved_mb": metrics.get("peak_reserved_mb"),
                    "attn": metrics.get("attn")}})
'''

FLUX = r'''
def main():
    import torch

    snap = materialise_helper()
    write_fixtures()
    STATE["utc_start"] = utc()
    before = snap.collect(LOGS, "before_flux")
    t4 = snap.assert_t4(before)
    STATE["steps"]["environment_before"] = {{"t4": t4, "devices": before["torch"]["devices"]}}
    if not t4["ok"]:
        return finish("BLOCKED", "T4 assertion failed: " + "; ".join(t4["reasons"]))

    env, uv = ensure_env("3.11", "flux2")
    tr = uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    STATE["steps"]["install_torch"] = {{"rc": tr["returncode"], "duration_s": tr["duration_s"]}}
    inst = uvpip(env, uv, "git+https://github.com/huggingface/diffusers.git transformers sentencepiece accelerate safetensors", 7200)
    STATE["steps"]["install_diffusers"] = {{"rc": inst["returncode"], "duration_s": inst["duration_s"],
                                             "stderr": inst["stderr"][-2000:]}}
    if inst["returncode"] != 0:
        return finish("BLOCKED", "diffusers install failed")

    prompts = json.loads((CONFIG / "image_video_prompts.json").read_text())
    outdir = RESULTS / "flux2-klein-4b"
    outdir.mkdir(parents=True, exist_ok=True)
    script = """
import torch, json, time
from pathlib import Path
from diffusers import Flux2KleinPipeline
torch.cuda.reset_peak_memory_stats()
t0 = time.time()
pipe = Flux2KleinPipeline.from_pretrained('black-forest-labs/FLUX.2-klein-4B', torch_dtype=torch.float16, low_cpu_mem_usage=True)
pipe.enable_model_cpu_offload()
load_s = time.time() - t0
dtype = next(pipe.transformer.parameters()).dtype
records = []
for item in __PROMPTS__:
    t = time.time()
    img = pipe(prompt=item['prompt'], height=512, width=512, guidance_scale=1.0,
               num_inference_steps=4,
               generator=torch.Generator(device='cuda').manual_seed(item['seed'])).images[0]
    out = Path(__OUTDIR__) / f"flux_{{item['id']}}.png"
    img.save(out)
    records.append({{'id': item['id'], 'seed': item['seed'], 'seconds': time.time() - t, 'path': str(out)}})
peak_alloc = torch.cuda.max_memory_allocated() / 2**20
peak_res = torch.cuda.max_memory_reserved() / 2**20
print(json.dumps({{'dtype': str(dtype), 'load_s': load_s, 'images': records,
                   'peak_alloc_mb': peak_alloc, 'peak_reserved_mb': peak_res,
                   'attn': getattr(pipe.transformer.config, '_attn_implementation', 'unknown')}}))
"""
    script = (script.replace("__PROMPTS__", json.dumps(prompts["image_prompts"]))
                    .replace("__OUTDIR__", repr(str(outdir))))
    (WORK / "scripts/flux_run.py").write_text(script, encoding="utf-8")
    run = sh(f"PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python {WORK/'scripts/flux_run.py'}", 7200)
    STATE["steps"]["inference"] = {{"rc": run["returncode"], "duration_s": run["duration_s"],
                                    "stdout": run["stdout"][-3000:], "stderr": run["stderr"][-4000:]}}
    metrics = {{}}
    for line in run["stdout"].splitlines():
        if line.strip().startswith("{{"):
            try:
                metrics = json.loads(line.strip())
            except Exception:  # noqa: BLE001
                pass
    STATE["steps"]["metrics"] = metrics
    outputs = []
    valid = 0
    for p in sorted(outdir.glob("*.png")):
        if save_output(p, outputs):
            valid += 1
    STATE["steps"]["outputs"] = outputs
    STATE["steps"]["validation"] = {{"images": valid}}
    after = snap.collect(LOGS, "after_flux")
    STATE["steps"]["environment_after"] = {{"working_free_gib": after["disk_usage"]["working_free_gib"]}}

    ok = run["returncode"] == 0 and valid == 3 and metrics.get("images")
    return finish("PASS" if ok else "FAIL", None if ok else "inference/output validation failed",
                  {{"dtype": metrics.get("dtype"),
                    "runtime_seconds": (metrics.get("images") or [{{}}])[0].get("seconds") if metrics.get("images") else None,
                    "peak_vram_allocated_mb": metrics.get("peak_alloc_mb"),
                    "peak_vram_reserved_mb": metrics.get("peak_reserved_mb"),
                    "attn": metrics.get("attn")}})
'''

COSY = r'''
def main():
    snap = materialise_helper()
    write_fixtures()
    STATE["utc_start"] = utc()
    before = snap.collect(LOGS, "before_cosyvoice")
    t4 = snap.assert_t4(before)
    STATE["steps"]["environment_before"] = {{"t4": t4, "devices": before["torch"]["devices"]}}
    if not t4["ok"]:
        return finish("BLOCKED", "T4 assertion failed: " + "; ".join(t4["reasons"]))

    env, uv = ensure_env("3.10", "cosyvoice")
    tr = uvpip(env, uv, "torch==2.3.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121", 7200)
    STATE["steps"]["install_torch"] = {{"rc": tr["returncode"], "duration_s": tr["duration_s"]}}
    repo = clone(REPO_URL, REPO_SHA, "cosyvoice")

    filtered = []
    skip = ("deepspeed", "tensorrt", "onnxruntime-gpu", "gradio", "fastapi", "fastapi-cli",
            "uvicorn", "tensorboard", "grpcio", "grpcio-tools", "openai-whisper")
    for line in (repo / "requirements.txt").read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("--"):
            continue
        if any(s.lower().startswith(k) for k in skip):
            continue
        filtered.append(s)
    uvpip(env, uv, '"setuptools<81" wheel', 600)
    whisper_inst = uvpip(env, uv, "--no-build-isolation-package openai-whisper openai-whisper==20231117", 1800)
    STATE["steps"]["install_openai_whisper"] = {{"rc": whisper_inst["returncode"], "duration_s": whisper_inst["duration_s"], "stderr": whisper_inst["stderr"][-1500:]}}
    if whisper_inst["returncode"] != 0:
        return finish("BLOCKED", "openai-whisper build failed")
    req_file = WORK / "scripts/cosyvoice_requirements_filtered.txt"
    req_file.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    STATE["steps"]["requirements_filter"] = {{"omitted": skip, "kept": len(filtered)}}
    inst = uvpip(env, uv, f"-r {req_file}", 7200)
    STATE["steps"]["install_requirements"] = {{"rc": inst["returncode"], "duration_s": inst["duration_s"],
                                               "stderr": inst["stderr"][-3000:]}}
    if inst["returncode"] != 0:
        return finish("BLOCKED", "CosyVoice filtered requirements install failed")
    ort = uvpip(env, uv, "onnxruntime", 1200)
    STATE["steps"]["install_onnxruntime"] = {{"rc": ort["returncode"], "duration_s": ort["duration_s"], "stderr": ort["stderr"][-1000:]}}

    from huggingface_hub import snapshot_download
    model_dir = WEIGHTS / "cosyvoice3/Fun-CosyVoice3-0.5B"
    snapshot_download("FunAudioLLM/Fun-CosyVoice3-0.5B-2512", local_dir=str(model_dir))
    STATE["steps"]["model_download"] = {{"path": str(model_dir), "bytes": sum(p.stat().st_size for p in model_dir.rglob('*') if p.is_file())}}

    # reference voice: Kokoro (allowed by Phase 6.5a) if it starts
    ref = WEIGHTS / "cosyvoice3/reference"
    ref.mkdir(parents=True, exist_ok=True)
    espeak = sh("which espeak-ng || which espeak", 30)
    kokoro_ok = False
    try:
        uvpip(env, uv, "kokoro soundfile", 1800)
        uvpip(env, uv, "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl", 900)
        kscript = """
import soundfile as sf
from kokoro import KPipeline
pipe = KPipeline(lang_code='a')
text = 'The mitochondrion is the powerhouse of the cell, and it carries out aerobic respiration.'
chunks = [a for _, _, a in pipe(text, voice='af_heart')]
import numpy as np
audio = np.concatenate(chunks)
sf.write(__REF__, audio, 24000)
print('OK', len(audio)/24000)
""".replace("__REF__", repr(str(ref / "reference_10s.wav")))
        (WORK / "scripts/kokoro_ref.py").write_text(kscript, encoding="utf-8")
        kr = sh(f"{env}/bin/python {WORK/'scripts/kokoro_ref.py'}", 1800)
        STATE["steps"]["kokoro_reference"] = {{"rc": kr["returncode"], "stdout": kr["stdout"][-1000:], "stderr": kr["stderr"][-2000:]}}
        kokoro_ok = kr["returncode"] == 0 and (ref / "reference_10s.wav").exists()
    except Exception as exc:  # noqa: BLE001
        STATE["steps"]["kokoro_reference"] = {{"error": f"{{type(exc).__name__}}: {{exc}}"}}
    if kokoro_ok:
        (ref / "TRANSCRIPT.txt").write_text("The mitochondrion is the powerhouse of the cell, and it carries out aerobic respiration.", encoding="utf-8")
        (ref / "LICENSE.txt").write_text("Kokoro-82M model weights: Apache-2.0 (model card). Generated with Kokoro voice af_heart; synthetic reference.", encoding="utf-8")
        STATE["steps"]["reference_voice"] = {{"path": str(ref/'reference_10s.wav'), "sha256": sha256_file(ref/'reference_10s.wav'),
                                              "license_basis": "model_card_metadata", "license_status": "CONDITIONAL PASS"}}

    script_text = (CONFIG / "science_voice_script.txt").read_text()
    import re
    text_flat = " ".join(script_text.split())
    chunks = [c.strip() for c in re.split(r'(?<=[.!?])\s+', text_flat) if c.strip()]
    grouped, cur = [], ""
    for c in chunks:
        if len(cur) + len(c) + 1 <= 300:
            cur = (cur + " " + c).strip()
        else:
            if cur:
                grouped.append(cur)
            cur = c
    if cur:
        grouped.append(cur)
    STATE["steps"]["chunking"] = {{"chunks": len(grouped), "max_chars": max(len(c) for c in grouped)}}

    cscript = """
import sys, json, time, torch, torchaudio
import numpy as np
sys.path.insert(0, __REPO__)
sys.path.insert(0, __MATCHA__)
from cosyvoice.cli.cosyvoice import AutoModel
torch.cuda.reset_peak_memory_stats()
model = AutoModel(model_dir=__MODEL_DIR__)
try:
    dtype = next(model.model.llm.parameters()).dtype
except Exception:
    dtype = 'unknown'
print('dtype', dtype)
ref = __REF__ if __KOKORO_OK__ else None
prompt = 'You are a helpful assistant.<|endofprompt|>The mitochondrion is the powerhouse of the cell, and it carries out aerobic respiration.'
groups = __GROUPS__
sr = getattr(model, 'sample_rate', 24000)
pieces = []
t0 = time.time()
for g in groups:
    for out in model.inference_zero_shot(g, prompt, ref, stream=False):
        pieces.append(out['tts_speech'].float().cpu())
gen_s = time.time() - t0
audio = torch.cat(pieces, dim=1) if pieces else None
peak_alloc = torch.cuda.max_memory_allocated() / 2**20
peak_res = torch.cuda.max_memory_reserved() / 2**20
print(json.dumps({'dtype': str(dtype), 'gen_s': gen_s, 'samples': 0 if audio is None else audio.shape[-1],
                  'sr': sr, 'peak_alloc_mb': peak_alloc, 'peak_reserved_mb': peak_res}))
if audio is not None:
    torchaudio.save(__OUT__, audio, sr, encoding='PCM_S', bits_per_sample=16)
"""
    out_path = RESULTS / "cosyvoice3/out.wav"
    cscript = (cscript.replace("__REPO__", repr(str(repo)))
                      .replace("__MATCHA__", repr(str(repo / "third_party/Matcha-TTS")))
                      .replace("__MODEL_DIR__", repr(str(model_dir)))
                      .replace("__REF__", repr(str(ref / "reference_10s.wav")))
                      .replace("__KOKORO_OK__", repr(kokoro_ok))
                      .replace("__GROUPS__", json.dumps(grouped))
                      .replace("__OUT__", repr(str(out_path))))
    (WORK / "scripts/cosy_run.py").write_text(cscript, encoding="utf-8")
    run = sh(f"{env}/bin/python {WORK/'scripts/cosy_run.py'}", 7200)
    STATE["steps"]["inference"] = {{"rc": run["returncode"], "duration_s": run["duration_s"],
                                    "stdout": run["stdout"][-3000:], "stderr": run["stderr"][-5000:]}}
    metrics = {{}}
    for line in run["stdout"].splitlines():
        if line.strip().startswith("{{"):
            try:
                metrics = json.loads(line.strip())
            except Exception:  # noqa: BLE001
                pass
    STATE["steps"]["metrics"] = metrics
    outputs = []
    save_output(out_path, outputs)
    STATE["steps"]["outputs"] = outputs
    duration = None
    if out_path.exists():
        import wave
        with wave.open(str(out_path), "rb") as wf:
            duration = wf.getnframes() / wf.getframerate()
    STATE["steps"]["audio_duration_s"] = duration
    STATE["steps"]["rtf"] = (metrics.get("gen_s") / duration) if (duration and metrics.get("gen_s")) else None
    after = snap.collect(LOGS, "after_cosyvoice")
    STATE["steps"]["environment_after"] = {{"working_free_gib": after["disk_usage"]["working_free_gib"]}}

    ok = run["returncode"] == 0 and bool(outputs) and duration and metrics
    return finish("PASS" if ok else "FAIL", None if ok else "inference/output validation failed",
                  {{"dtype": metrics.get("dtype"), "runtime_seconds": metrics.get("gen_s"),
                    "rtf": STATE["steps"]["rtf"],
                    "peak_vram_allocated_mb": metrics.get("peak_alloc_mb"),
                    "peak_vram_reserved_mb": metrics.get("peak_reserved_mb"),
                    "cloning_reference": "Kokoro af_heart" if kokoro_ok else "BLOCKED (no cleared reference)"}})
'''

CODES = {
    "cosyvoice3": COSY,
    "ltx-video-2b-0.9.5": LTX,
    "flux2-klein-4b": FLUX,
    "practical-rife-4.25": RIFE,
    "real-esrgan-x4plus": ESRGAN,
}


def main() -> None:
    helper_raw = HELPER.read_bytes()
    helper_sha = hashlib.sha256(helper_raw).hexdigest()
    helper_b64 = base64.b64encode(helper_raw).decode()
    fixtures = {}
    for name in ("science_voice_script.txt", "science_terms.json", "image_video_prompts.json"):
        fixtures[name] = base64.b64encode((CFG / name).read_bytes()).decode()
    fixtures_json = json.dumps(fixtures)

    for comp, code in CODES.items():
        repo, sha = REVISIONS.get(comp, ("", ""))
        body = HEADER
        body = body.replace("__COMPONENT__", comp)
        body = body.replace("__PRIORITY__", "P0")
        body = body.replace("__KERNEL__", f"openmontage-p0-{comp.replace('.', '-')}")
        body = body.replace("__REPO_URL__", f"https://github.com/{repo}" if repo else "")
        body = body.replace("__REPO_SHA__", sha)
        body = body.replace("__HELPER_B64__", helper_b64)
        body = body.replace("__HELPER_SHA__", helper_sha)
        body = body.replace("__FIXTURES_JSON__", fixtures_json)
        code = code.replace("def main():", "def run():")
        body += "\n" + code + "\n\nif __name__ == '__main__':\n    try:\n        raise SystemExit(run())\n    except SystemExit:\n        raise\n    except Exception:\n        tb = traceback.format_exc()\n        print(tb)\n        log('UNHANDLED ' + tb[-3000:])\n        finish('FAIL', 'unhandled exception')\n        raise SystemExit(4)\n"
        body = body.replace("{{", "{").replace("}}", "}")
        d = OUT / comp
        d.mkdir(parents=True, exist_ok=True)
        (d / "notebook.py").write_text(body, encoding="utf-8")
        meta = {
            "id": f"forts845/openmontage-p0-{comp.replace('.', '-')}",
            "title": f"OpenMontage P0 {comp}",
            "code_file": "notebook.py",
            "language": "python",
            "kernel_type": "script",
            "is_private": "true",
            "enable_gpu": "true",
            "enable_tpu": "false",
            "enable_internet": "true",
            "machine_shape": "NvidiaTeslaT4",
            "dataset_sources": [],
            "competition_sources": [],
            "kernel_sources": [],
            "model_sources": [],
        }
        (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print("wrote", d / "notebook.py", len(body), "bytes")


if __name__ == "__main__":
    main()