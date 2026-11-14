#!/usr/bin/env python3
"""OpenMontage Stage F: Wan2.2 TI2V-5B GGUF Q4_K_M on a single Kaggle T4.

Tests whether the quantized GGUF version (QuantStack/Wan2.2-TI2V-5B-GGUF, Q4_K_M)
runs in FP16 on one T4 and compares quality to the already-tested Wan2.1 1.3B.
Three scenes, same prompts/seeds as audit/previews/video_quality_comparison/COMPARISON.md.
"""

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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

WORK = Path("/kaggle/working/audit")
LOGS = WORK / "logs/kaggle"
RESULTS = WORK / "results"
CONFIG = WORK / "config"
ENVS = Path("/tmp/audit/envs")
REPOS = Path("/tmp/audit/repos")
WEIGHTS = Path("/tmp/audit/weights")
for _p in (WORK, LOGS, RESULTS, CONFIG, ENVS, REPOS, WEIGHTS):
    _p.mkdir(parents=True, exist_ok=True)

COMPONENT = "wan2.2-ti2v-5b-asteroid-collision"
KERNEL_NAME = "openmontage-vq-wan2-2-asteroid-collision"
LOG = LOGS / f"{COMPONENT}.log"
SUMMARY = RESULTS / COMPONENT
SUMMARY.mkdir(parents=True, exist_ok=True)
STATE = {"component": COMPONENT, "priority": "VQ", "kernel": KERNEL_NAME,
         "utc_start": None, "utc_end": None, "status": "UNKNOWN",
         "steps": {}, "errors": []}

PROMPTS = [
    {"slug": "asteroid_collision", "seed": 919191,
     "prompt": "Two asteroids colliding in deep space, dramatic high-speed impact, rock fragments and debris violently shattering and flying outward in all directions, dust and sparks, cinematic space scene"},
]

NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, watermark, text"


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    line = f"{utc()} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def sh(cmd, timeout=7200, quiet=False):
    started = time.time()
    rec = {"cmd": cmd, "returncode": None, "duration_s": None, "stdout": "", "stderr": ""}
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        rec["returncode"] = proc.returncode
        rec["stdout"] = (proc.stdout or "")[-20000:]
        rec["stderr"] = (proc.stderr or "")[-12000:]
    except Exception as exc:  # noqa: BLE001
        rec["error"] = f"{type(exc).__name__}: {exc}"
    rec["duration_s"] = round(time.time() - started, 3)
    if not quiet:
        log(f"$ {cmd} -> rc={rec['returncode']} {rec['duration_s']}s")
        if rec["stdout"]:
            log("stdout tail: " + rec["stdout"][-1500:].replace("\n", " | "))
        if rec["stderr"]:
            log("stderr tail: " + rec["stderr"][-1500:].replace("\n", " | "))
    return rec


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(p)],
                       capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    v = [s for s in j.get("streams", []) if s.get("codec_type") == "video"]
    if not v:
        return {"error": "no video stream", "stderr": (r.stderr or "")[-500:]}
    v = v[0]
    return {"width": v.get("width"), "height": v.get("height"), "fps": v.get("r_frame_rate"),
            "frames": v.get("nb_frames"), "codec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
            "duration_s": float(j.get("format", {}).get("duration", 0) or 0)}


def detect(p):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-vf",
                        "blackdetect=d=0.1:pix_th=0.10,freezedetect=n=0.003:d=1.0",
                        "-an", "-f", "null", "-"], capture_output=True, text=True)
    err = r.stderr or ""
    return {"black_segments": err.count("black_start"), "freeze_segments": err.count("freeze_start"),
            "blackdetect": "black_start" in err, "freezedetect": "freeze_start" in err,
            "stderr_tail": err[-1200:]}


def finish(status, error=None, extra=None):
    STATE["status"] = status
    STATE["utc_end"] = utc()
    if error:
        STATE["errors"].append(error)
    if extra:
        STATE["extra"] = extra
    out = SUMMARY / "summary.json"
    out.write_text(json.dumps(STATE, indent=2, default=str), encoding="utf-8")
    log(f"FINISH status={status} error={error}")
    # also dump state for the runner
    print("SUMMARY", json.dumps({"status": status, "error": error, "extra": extra or {}}, default=str))
    return 0 if status == "PASS" else 1


def env_snapshot():
    b = {}
    try:
        import torch
        b["torch"] = torch.__version__
        b["cuda_available"] = torch.cuda.is_available()
        b["device_count"] = torch.cuda.device_count() if torch.cuda.is_available() else 0
        if torch.cuda.is_available():
            b["gpu_name"] = torch.cuda.get_device_name(0)
            b["total_vram_mib"] = round(torch.cuda.get_device_properties(0).total_memory / 2**20, 1)
            b["compute_capability"] = ".".join(str(x) for x in torch.cuda.get_device_capability(0))
    except Exception as e:
        b["torch_error"] = str(e)
    # ffmpeg
    r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    b["ffmpeg_version"] = (r.stdout or "").splitlines()[0] if r.returncode == 0 else None
    return b


def main():
    STATE["utc_start"] = utc()
    log("=== Wan2.2 TI2V-5B GGUF Q4_K_M audit start ===")

    # ---- Step 0: env snapshot + T4 assertion ----
    snap = env_snapshot()
    STATE["steps"]["env_before"] = snap
    log(json.dumps(snap))
    if not snap.get("cuda_available"):
        return finish("BLOCKED", "CUDA not available")
    if "T4" not in str(snap.get("gpu_name", "")):
        log("WARNING: GPU is not a T4; proceeding anyway but recording device")
    if snap.get("compute_capability") != "7.5":
        log(f"NOTE: compute capability {snap.get('compute_capability')} (T4 is 7.5)")

    # ---- Step 1: install dependencies ----
    log("Using Kaggle pre-installed torch; pinning compatible diffusers/transformers...")
    r = sh("pip install --quiet --upgrade pip", 300)
    # Do NOT override torch: Kaggle ships torch 2.11+cu130 on py3.13. Pin diffusers/transformers to versions
    # compatible with that torch (avoid transformers 5.x which needs torch._dynamo.skip_code).
    r = sh("pip install --quiet 'diffusers==0.35.2' 'transformers==4.51.3' 'gguf' 'accelerate' 'safetensors' 'imageio' 'imageio-ffmpeg' 'sentencepiece' 'protobuf' 'huggingface_hub' 'ftfy'", 3600)
    if r["returncode"] != 0:
        return finish("BLOCKED", "deps install failed", {"stderr": r["stderr"][-2000:]})

    # ffmpeg (should already be there on Kaggle)
    r = sh("which ffmpeg", 60, quiet=True)
    if r["returncode"] != 0:
        sh("apt-get install -y -qq ffmpeg", 300)

    # record versions
    import importlib
    ver = {}
    for m in ("torch", "diffusers", "gguf", "transformers", "accelerate"):
        try:
            mod = importlib.import_module(m)
            ver[m] = getattr(mod, "__version__", "unknown")
        except Exception as e:
            ver[m] = f"ERR {e}"
    STATE["steps"]["versions"] = ver
    log(json.dumps(ver))

    # attention backend check: flash_attn must NOT be importable; we use SDPA
    flash = None
    try:
        import flash_attn  # noqa: F401
        flash = flash_attn.__version__
    except Exception:
        flash = None
    STATE["steps"]["flash_attn_available"] = flash
    log(f"flash_attn available: {flash} (expected None on T4)")

    # ---- Step 2: download weights ----
    from huggingface_hub import hf_hub_download
    outdir = WEIGHTS
    model_dir = outdir / "wan22-ti2v-5b-gguf"
    model_dir.mkdir(parents=True, exist_ok=True)

    log("Downloading GGUF Q4_K_M...")
    t = time.time()
    gguf_path = hf_hub_download(repo_id="QuantStack/Wan2.2-TI2V-5B-GGUF",
                                filename="Wan2.2-TI2V-5B-Q4_K_M.gguf",
                                local_dir=str(model_dir))
    dl_gguf = round(time.time() - t, 1)
    log(f"GGUF downloaded: {gguf_path} in {dl_gguf}s")

    log("Downloading VAE...")
    t = time.time()
    vae_path = hf_hub_download(repo_id="QuantStack/Wan2.2-TI2V-5B-GGUF",
                               filename="VAE/Wan2.2_VAE.safetensors",
                               local_dir=str(model_dir))
    dl_vae = round(time.time() - t, 1)
    log(f"VAE downloaded: {vae_path} in {dl_vae}s")

    # Text encoder + config from diffusers repo (UMT5). We only need config + text_encoder + vae.
    # Download the whole diffusers repo is huge; instead use from_pretrained with local cache for
    # config/vae/text_encoder by snapshot_download of just needed subfolders.
    log("Downloading diffusers repo config/vae/text_encoder/tokenizer/scheduler...")
    t = time.time()
    from huggingface_hub import snapshot_download
    diffusers_dir = snapshot_download(
        repo_id="Wan-AI/Wan2.2-TI2V-5B-Diffusers",
        local_dir=str(model_dir / "diffusers"),
        allow_patterns=["config.json", "model_index.json",
                        "scheduler/*", "tokenizer/*", "text_encoder/*", "vae/*", "transformer/config.json"],
        ignore_patterns=["*.safetensors.index.json.tmp"],
    )
    dl_diff = round(time.time() - t, 1)
    log(f"diffusers subset downloaded in {dl_diff}s: {diffusers_dir}")

    # disk usage
    def dir_size_mb(p):
        total = 0
        for root, _, files in os.walk(p):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
        return round(total / 2**20, 1)
    disk_mb = dir_size_mb(str(model_dir))
    STATE["steps"]["disk_usage_mb"] = disk_mb
    log(f"disk usage (model_dir): {disk_mb} MiB")

    STATE["steps"]["downloads"] = {
        "gguf_path": gguf_path, "gguf_seconds": dl_gguf,
        "vae_path": vae_path, "vae_seconds": dl_vae,
        "diffusers_dir": diffusers_dir, "diffusers_seconds": dl_diff,
        "disk_usage_mb": disk_mb,
    }

    # ---- Step 3: load pipeline in FP16 with SDPA ----
    import torch
    dtype = torch.float16
    text_encoder_dtype = torch.float16  # try FP16; fallback to bf16 if needed
    vae_dtype = torch.float32  # VAE stays fp32 for stability (known limitation candidate)

    from diffusers import WanPipeline, AutoencoderKLWan, WanTransformer3DModel, GGUFQuantizationConfig

    log("Loading transformer from GGUF (FP16 compute dtype)...")
    t0 = time.time()
    try:
        transformer = WanTransformer3DModel.from_single_file(
            gguf_path,
            quantization_config=GGUFQuantizationConfig(compute_dtype=dtype),
            config=str(model_dir / "diffusers"),
            subfolder="transformer",
            torch_dtype=dtype,
        )
        load_tr = round(time.time() - t0, 1)
        log(f"transformer loaded in {load_tr}s")
    except Exception as e:
        tb = traceback.format_exc()
        log("TRANSFORMER LOAD FAILED: " + tb[-3000:])
        STATE["steps"]["transformer_load_error"] = tb[-3000:]
        return finish("BLOCKED", "transformer load failed", {"traceback": tb[-3000:]})

    # attention backend: force SDPA
    attn_backend_used = "default"
    try:
        # diffusers >= 0.35 exposes set_attention_backend on the transformer
        if hasattr(transformer, "set_attention_backend"):
            transformer.set_attention_backend("sdpa")
            attn_backend_used = "sdpa (set_attention_backend)"
        log(f"attention backend set: {attn_backend_used}")
    except Exception as e:
        log(f"set_attention_backend failed: {e}; relying on default (no flash_attn installed -> SDPA)")
        attn_backend_used = "default (flash_attn absent -> SDPA)"

    log("Loading VAE (fp32)...")
    t0 = time.time()
    try:
        vae = AutoencoderKLWan.from_pretrained(str(model_dir / "diffusers"), subfolder="vae", torch_dtype=vae_dtype)
        load_vae = round(time.time() - t0, 1)
        log(f"vae loaded in {load_vae}s")
    except Exception as e:
        tb = traceback.format_exc()
        log("VAE LOAD FAILED: " + tb[-3000:])
        return finish("BLOCKED", "vae load failed", {"traceback": tb[-3000:]})

    log("Loading pipeline...")
    t0 = time.time()
    dtype_mixed = False
    try:
        pipe = WanPipeline.from_pretrained(
            str(model_dir / "diffusers"),
            transformer=transformer,
            vae=vae,
            torch_dtype=dtype,
        )
        # try to force text encoder to FP16 if it loaded in bf16
        if hasattr(pipe, "text_encoder") and pipe.text_encoder is not None:
            try:
                pipe.text_encoder = pipe.text_encoder.to(dtype)
                # verify
                te_dtype = next(pipe.text_encoder.parameters()).dtype
                log(f"text_encoder dtype after .to(fp16): {te_dtype}")
                if te_dtype != dtype:
                    dtype_mixed = True
            except Exception as e:
                log(f"text_encoder .to(fp16) failed: {e}; leaving as-is")
                dtype_mixed = True
        pipe.enable_model_cpu_offload()
        load_pipe = round(time.time() - t0, 1)
        log(f"pipeline loaded in {load_pipe}s")
    except Exception as e:
        tb = traceback.format_exc()
        log("PIPELINE LOAD FAILED: " + tb[-3000:])
        return finish("BLOCKED", "pipeline load failed", {"traceback": tb[-3000:]})

    # record component dtypes
    comp_dtype = {
        "transformer": str(next(transformer.parameters()).dtype),
        "vae": str(next(vae.parameters()).dtype),
        "text_encoder": str(next(pipe.text_encoder.parameters()).dtype) if getattr(pipe, "text_encoder", None) is not None else None,
        "pipeline_torch_dtype": str(dtype),
    }
    STATE["steps"]["component_dtypes"] = comp_dtype
    STATE["steps"]["dtype_mixed"] = dtype_mixed
    STATE["steps"]["attention_backend"] = attn_backend_used
    log("component dtypes: " + json.dumps(comp_dtype))
    log(f"dtype_mixed: {dtype_mixed}")

    # ---- Step 4: generate three clips ----
    from diffusers.utils import export_to_video
    outdir_clips = RESULTS / "clips"
    outdir_clips.mkdir(parents=True, exist_ok=True)
    recs = []
    for item in PROMPTS:
        out = outdir_clips / "wan22_asteroid_collision_919191_MOTION.mp4"
        torch.cuda.reset_peak_memory_stats()
        t = time.time()
        try:
            output = pipe(
                prompt=item["prompt"],
                negative_prompt=NEG,
                height=480,
                width=832,
                num_frames=49,
                guidance_scale=5.0,
                num_inference_steps=20,
                generator=torch.Generator(device="cuda").manual_seed(item["seed"]),
            ).frames[0]
            gen = round(time.time() - t, 3)
            export_to_video(output, str(out), fps=24)
            peak_alloc = round(torch.cuda.max_memory_allocated() / 2**20, 1)
            peak_reserved = round(torch.cuda.max_memory_reserved() / 2**20, 1)
            rec = {"slug": item["slug"], "seed": item["seed"], "prompt": item["prompt"],
                   "gen_s": gen, "peak_alloc_mb": peak_alloc, "peak_reserved_mb": peak_reserved,
                   "file": str(out), "bytes": out.stat().st_size if out.exists() else 0,
                   "height": 480, "width": 832, "num_frames": len(output), "fps": 24,
                   "steps": 20, "guidance_scale": 5.0}
            rec["ffprobe"] = probe(out)
            rec["checks"] = detect(out)
            recs.append(rec)
            log("CLIP " + json.dumps(rec))
            print("CLIP", json.dumps(rec), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            log("CLIP FAILED " + item["slug"] + ": " + tb[-3000:])
            recs.append({"slug": item["slug"], "seed": item["seed"], "error": str(e),
                         "traceback": tb[-3000:], "file": str(out)})
            STATE["errors"].append(f"clip {item['slug']} failed: {e}")
            # continue to next clip
    STATE["steps"]["clips"] = recs

    # ---- Step 5: save outputs to /kaggle/working for fetch ----
    # copy clips to a top-level outputs dir too
    top = Path("/kaggle/working/outputs")
    top.mkdir(parents=True, exist_ok=True)
    for r in recs:
        f = Path(r.get("file", ""))
        if f.exists():
            shutil.copy2(f, top / f.name)

    # overall status
    ok = len(recs) == len(PROMPTS) and all("error" not in r for r in recs) and all(Path(r.get("file","")).exists() for r in recs)
    if ok:
        return finish("PASS", None, {"clips": recs, "dtype_mixed": dtype_mixed,
                                    "peak_vram_allocated_mb_max": max(r.get("peak_alloc_mb", 0) for r in recs),
                                    "disk_usage_mb": disk_mb, "attention_backend": attn_backend_used,
                                    "component_dtypes": comp_dtype})
    else:
        return finish("FAIL", "one or more clips failed", {"clips": recs})


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        print(tb)
        log("UNHANDLED " + tb[-3000:])
        finish("FAIL", "unhandled exception", {"traceback": tb[-3000:]})
        raise SystemExit(4)
