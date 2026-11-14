#!/usr/bin/env python3
"""Build the two video-quality comparison kernels (LTX-Video 2B 0.9.5 vs Wan2.1 T2V 1.3B).

Same prompts, same seeds, same 832x480 / 24 fps / 193 frames for both models.
Reuses the Stage B kernel HEADER (env snapshot helper, uv helpers, logging).
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "audit/scripts/kaggle_environment_snapshot.py"
CFG = ROOT / "audit/config"
OUT = ROOT / "audit/kaggle/vq"

spec = importlib.util.spec_from_file_location("p0", ROOT / "audit/scripts/build_p0_notebooks.py")
P0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P0)
HEADER = P0.HEADER

PROMPTS = [
    {"slug": "europa_flyby", "seed": 424242,
     "prompt": "A slow cinematic flyby of Jupiter's moon Europa, showing its icy cracked surface, "
               "subsurface ocean implied beneath, realistic space lighting, documentary style, no text, no watermark."},
    {"slug": "saturn_solar", "seed": 202607,
     "prompt": "A scientifically accurate visualization of a spacecraft deploying solar panels in orbit around Saturn, "
               "with Saturn's rings visible in the background, realistic engineering detail, no text, no watermark."},
    {"slug": "enceladus_plumes", "seed": 271828,
     "prompt": "A slow zoom into a cross-section diagram style view of Enceladus showing water plumes erupting "
               "from its south pole into space, realistic lighting, documentary visual style, no text, no watermark."},
]

LT = r'''
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, watermark, text"


def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_vq_ltx"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.10", "vqltx")
    uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    inst = uvpip(env, uv, "diffusers transformers accelerate safetensors imageio imageio-ffmpeg sentencepiece protobuf", 3600)
    if inst["returncode"] != 0:
        return finish("BLOCKED", "diffusers install failed", {"install": inst["stderr"][-2000:]})
    outdir = RESULTS / "vq/ltx"; outdir.mkdir(parents=True, exist_ok=True)
    script = """
import json, time, torch, subprocess
from pathlib import Path
from diffusers import LTXPipeline
from diffusers.utils import export_to_video
torch.cuda.reset_peak_memory_stats()
t0 = time.time()
pipe = LTXPipeline.from_pretrained('Lightricks/LTX-Video-0.9.5', torch_dtype=torch.float16, low_cpu_mem_usage=True)
pipe.enable_model_cpu_offload()
load_s = time.time() - t0
dtype = str(next(pipe.transformer.parameters()).dtype)
attn = getattr(pipe.transformer.config, '_attn_implementation', 'unknown')
scheduler = type(pipe.scheduler).__name__
import json as _json0, subprocess as _sp0
def probe(p):
    r = _sp0.run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(p)], capture_output=True, text=True)
    j = _json0.loads(r.stdout or "{}")
    v = [s for s in j.get("streams", []) if s.get("codec_type") == "video"]
    if not v: return {"error": "no video stream", "stderr": r.stderr[-500:]}
    v = v[0]
    return {"width": v.get("width"), "height": v.get("height"), "fps": v.get("r_frame_rate"),
            "frames": v.get("nb_frames"), "codec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
            "duration_s": float(j.get("format", {}).get("duration", 0) or 0)}
def detect(p):
    r = _sp0.run(["ffmpeg","-hide_banner","-nostats","-i",str(p),"-vf",
                  "blackdetect=d=0.1:pix_th=0.10,freezedetect=n=0.003:d=1.0",
                  "-an","-f","null","-"], capture_output=True, text=True)
    err = r.stderr
    return {"black_segments": err.count("black_start"), "freeze_segments": err.count("freeze_start"),
            "blackdetect": "black_start" in err, "freezedetect": "freeze_start" in err,
            "stderr_tail": err[-1200:]}
recs = []
for item in __PROMPTS__:
    out = Path(__OUT__) / ("ltx_%s_%d.mp4" % (item['slug'], item['seed']))
    t = time.time()
    frames = pipe(prompt=item['prompt'], negative_prompt=__NEG__, width=832, height=480,
                  num_frames=193, num_inference_steps=30, guidance_scale=3.0,
                  generator=torch.Generator(device='cuda').manual_seed(item['seed'])).frames[0]
    gen = time.time() - t
    export_to_video(frames, str(out), fps=24)
    rec = {"model": "LTX-Video-2B-0.9.5", "slug": item["slug"], "prompt": item["prompt"],
           "seed": item["seed"], "dtype": dtype, "attn": attn, "scheduler": scheduler,
           "steps": 30, "guidance_scale": 3.0, "width": 832, "height": 480,
           "num_frames": len(frames), "fps": 24, "gen_s": round(gen, 3),
           "peak_alloc_mb": round(torch.cuda.max_memory_allocated()/2**20, 1),
           "peak_reserved_mb": round(torch.cuda.max_memory_reserved()/2**20, 1),
           "file": str(out), "bytes": out.stat().st_size if out.exists() else 0}
    rec["ffprobe"] = probe(out)
    rec["checks"] = detect(out)
    recs.append(rec); print("CLIP", json.dumps(rec), flush=True)
print("SUMMARY", json.dumps({"dtype": dtype, "attn": attn, "scheduler": scheduler,
                             "load_s": round(load_s, 3), "clips": recs}))
""".replace("__NEG__", json.dumps(NEG)).replace("__OUT__", repr(str(outdir)))
    (WORK / "scripts/vq_ltx_run.py").write_text(script, encoding="utf-8")
    t = time.time()
    run = sh(f"PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python {WORK/'scripts/vq_ltx_run.py'}", 14400)
    m = {"wall_s": round(time.time() - t, 1), "rc": run["returncode"], "stderr": run["stderr"][-4000:]}
    for line in run["stdout"].splitlines():
        if line.startswith("SUMMARY "):
            try: m.update(json.loads(line[8:]))
            except Exception: pass
    outs = []
    for p in sorted(outdir.glob("*.mp4")): save_output(p, outs)
    STATE["steps"].update({"inference": {"rc": run["returncode"], "duration_s": run["duration_s"],
                                          "stdout": run["stdout"][-6000:], "stderr": run["stderr"][-4000:]},
                            "metrics": m, "outputs": outs})
    ok = run["returncode"] == 0 and len(outs) == 3
    return finish("PASS" if ok else "FAIL", None if ok else "ltx vq run failed", m)
'''

WAN = r'''
VQ_FRAMES = 33
VQ_STEPS = 6
VQ_ONLY = ("europa_flyby",)


def run():
    snap = materialise_helper(); write_fixtures(); STATE["utc_start"] = utc()
    b = snap.collect(LOGS, "before_vq_wan"); t4 = snap.assert_t4(b)
    if not t4["ok"]: return finish("BLOCKED", "T4 assertion failed")
    env, uv = ensure_env("3.10", "vqwan")
    uvpip(env, uv, "torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126", 7200)
    repo = clone(REPO_URL, REPO_SHA, "wan21")
    uvpip(env, uv, '"setuptools<81" wheel', 600)
    kept = [l for l in (repo / "requirements.txt").read_text().splitlines()
            if l.strip() and not l.strip().lower().startswith("flash")]
    filtered = WORK / "requirements_noflash.txt"; filtered.write_text("\n".join(kept) + "\n")
    req = uvpip(env, uv, f"-r {filtered} einops", 7200)
    if req["returncode"] != 0:
        return finish("BLOCKED", "wan requirements failed", {"install": req["stderr"][-2000:]})
    uvpip(env, uv, "huggingface_hub", 900)
    model = WEIGHTS / "Wan2.1-T2V-1.3B"
    if not model.exists():
        hfcli = "hf" if (env / "bin/hf").exists() else "huggingface-cli"
        dl = sh(f"{env}/bin/{hfcli} download Wan-AI/Wan2.1-T2V-1.3B --local-dir {model}", 7200)
        STATE["steps"]["download_model"] = {"rc": dl["returncode"], "stderr": dl["stderr"][-800:]}
    # official generate.py with one documented patch: fp16 instead of the shipped bf16 config
    gen_src = (repo / "generate.py").read_text()
    marker = "args = parser.parse_args()"
    assert marker in gen_src, "generate.py layout changed"
    line_start = gen_src.rfind("\n", 0, gen_src.index(marker)) + 1
    indent = gen_src[line_start:gen_src.index(marker)]
    assert indent.strip() == "", f"unexpected prefix before marker: {indent!r}"
    patched = gen_src.replace(
        marker,
        marker + f"\n{indent}WAN_CONFIGS[args.task].param_dtype = torch.float16  # audit: T4 has no bf16 tensor cores",
        1)
    (repo / "vq_generate.py").write_text(patched, encoding="utf-8")
    # Wan 2.1 asserts FLASH_ATTN_2_AVAILABLE; T4 is sm_75 and the audit forbids FA2 -> torch SDPA
    att_path = repo / "wan/modules/attention.py"
    att = att_path.read_text()
    att_marker = ("    half_dtypes = (torch.float16, torch.bfloat16)\n"
                  "    assert dtype in half_dtypes\n"
                  "    assert q.device.type == 'cuda' and q.size(-1) <= 256\n")
    assert att_marker in att, "attention.py layout changed"
    att_fallback = att_marker + """
    if not (FLASH_ATTN_3_AVAILABLE or FLASH_ATTN_2_AVAILABLE):
        # audit: no FlashAttention on T4 (sm_75); torch SDPA, batch-level padded, no varlen
        if q_scale is not None:
            q = q * q_scale
        out = torch.nn.functional.scaled_dot_product_attention(
            q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2),
            dropout_p=dropout_p, is_causal=causal, scale=softmax_scale)
        return out.transpose(1, 2).contiguous()
"""
    att_path.write_text(att.replace(att_marker, att_fallback, 1))
    STATE["steps"]["attention_patch"] = {"file": str(att_path), "fallback": "torch_sdpa"}
    outdir = RESULTS / "vq/wan"; outdir.mkdir(parents=True, exist_ok=True)
    recs = []
    for item in __PROMPTS__:
        raw = outdir / ("wan_%s_%d_raw16.mp4" % (item["slug"], item["seed"]))
        final = outdir / ("wan_%s_%d.mp4" % (item["slug"], item["seed"]))
        cmd = (f"cd {repo} && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True {env}/bin/python vq_generate.py "
               f"--task t2v-1.3B --size 832*480 --frame_num {VQ_FRAMES} --ckpt_dir {model} "
               f"--offload_model True --t5_cpu --base_seed {item['seed']} "
               f"--sample_solver unipc --sample_steps {VQ_STEPS} --sample_shift 8 --sample_guide_scale 6 "
               f"--prompt {json.dumps(item['prompt'])} --save_file {raw}")
        t = time.time(); r = sh(cmd, 14400); gen = round(time.time() - t, 3)
        # Wan samples at 16 fps; re-time to the comparison fps without changing the frame count
        enc = sh(f"ffmpeg -y -loglevel error -i {raw} -r 24 -c:v libx264 -crf 18 -pix_fmt yuv420p {final}", 1800)
        rec = {"model": "Wan2.1-T2V-1.3B", "slug": item["slug"], "prompt": item["prompt"],
               "seed": item["seed"], "dtype": "float16 (patched from bf16 config; T5 stays bf16 on CPU)",
               "scheduler": "unipc", "steps": VQ_STEPS, "guidance_scale": 6.0, "sample_shift": 8,
               "width": 832, "height": 480, "num_frames": VQ_FRAMES, "fps": 24,
               "native_sample_fps": 16, "gen_s": gen, "gen_rc": r["returncode"],
               "encode_rc": enc["returncode"], "file": str(final),
               "bytes": final.stat().st_size if final.exists() else 0}
        rec["ffprobe"] = probe(final)
        rec["checks"] = detect(final)
        recs.append(rec); STATE["steps"][f"wan_{item['slug']}"] = {"rc": r["returncode"],
                                                                  "gen_s": gen, "stderr": r["stderr"][-1500:]}
        print("CLIP", json.dumps(rec), flush=True)
    m = {"clips": recs}
    outs = []
    for p in sorted(outdir.glob("*.mp4")):
        if not p.name.endswith("_raw16.mp4"): save_output(p, outs)
    STATE["steps"].update({"metrics": m, "outputs": outs})
    ok = all(r["gen_rc"] == 0 and r["ffprobe"].get("frames") for r in recs) and len(recs) == len(VQ_ONLY)
    return finish("PASS" if ok else "FAIL", None if ok else "wan vq run failed", m)
'''

PROBE_SRC = r'''
import json, subprocess
def probe(p):
    r = subprocess.run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(p)],
                       capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    v = [s for s in j.get("streams", []) if s.get("codec_type") == "video"]
    if not v: return {"error": "no video stream", "stderr": r.stderr[-500:]}
    v = v[0]
    return {"width": v.get("width"), "height": v.get("height"), "fps": v.get("r_frame_rate"),
            "frames": v.get("nb_frames"), "codec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
            "duration_s": float(j.get("format", {}).get("duration", 0) or 0)}
def detect(p):
    r = subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",str(p),"-vf",
                        "blackdetect=d=0.1:pix_th=0.10,freezedetect=n=0.003:d=1.0",
                        "-an","-f","null","-"], capture_output=True, text=True)
    err = r.stderr
    return {"black_segments": err.count("black_start"), "freeze_segments": err.count("freeze_start"),
            "blackdetect": "black_start" in err, "freezedetect": "freeze_start" in err,
            "stderr_tail": err[-1200:]}
'''

CODES = {"ltx": LT, "wan": WAN}
REVS = {"ltx": ("Lightricks/LTX-Video", "50f0aef12975"), "wan": ("Wan-Video/Wan2.1", "9737cba9c1c3")}


def main() -> None:
    helper_raw = HELPER.read_bytes(); helper_sha = hashlib.sha256(helper_raw).hexdigest()
    fixtures = {n: base64.b64encode((CFG / n).read_bytes()).decode()
                for n in ("science_voice_script.txt", "science_terms.json", "image_video_prompts.json")}
    for comp, code in CODES.items():
        repo, sha = REVS[comp]
        body = HEADER
        body = (body.replace("__COMPONENT__", f"vq-{comp}").replace("__PRIORITY__", "VQ")
                    .replace("__KERNEL__", f"openmontage-vq-{comp}")
                    .replace("__REPO_URL__", f"https://github.com/{repo}")
                    .replace("__REPO_SHA__", sha)
                    .replace("__HELPER_B64__", base64.b64encode(helper_raw).decode())
                    .replace("__HELPER_SHA__", helper_sha)
                    .replace("__FIXTURES_JSON__", json.dumps(fixtures)))
        body += "\n" + PROBE_SRC + "\n" + code + "\n\nif __name__ == '__main__':\n    try:\n        raise SystemExit(run())\n    except SystemExit:\n        raise\n    except Exception:\n        tb = traceback.format_exc(); print(tb); log('UNHANDLED ' + tb[-3000:]); finish('FAIL', 'unhandled exception'); raise SystemExit(4)\n"
        body = body.replace("__PROMPTS__", json.dumps(PROMPTS))
        body = body.replace("{{", "{").replace("}}", "}")
        d = OUT / comp; d.mkdir(parents=True, exist_ok=True)
        (d / "notebook.py").write_text(body, encoding="utf-8")
        meta = {"id": f"forts845/openmontage-vq-{comp}", "title": f"OpenMontage VQ {comp}",
                "code_file": "notebook.py", "language": "python", "kernel_type": "script",
                "is_private": "true", "enable_gpu": "true", "enable_tpu": "false",
                "enable_internet": "true", "machine_shape": "NvidiaTeslaT4",
                "dataset_sources": [], "competition_sources": [], "kernel_sources": [], "model_sources": []}
        (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print("wrote", d / "notebook.py", len(body))


if __name__ == "__main__":
    main()