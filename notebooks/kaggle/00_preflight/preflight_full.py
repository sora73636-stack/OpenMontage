"""OpenMontage preflight — full Phase 1 artifact set (Kaggle kernel)."""

import json
import os
import platform
import shutil
import subprocess
import sys
import time

OUT = "/kaggle/working"
R = {"status": "ok", "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
     "python": sys.version, "platform": platform.platform(), "cpu_count": os.cpu_count(),
     "ram_gb": None, "disk": {}, "gpu": [], "cuda": {}, "torch": {}, "internet": {},
     "packages": {}, "attention": {}, "errors": []}


def sh(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr[-1500:]
    except Exception as exc:  # noqa: BLE001
        return None, "", repr(exc)


def w(name, text):
    with open(f"{OUT}/{name}", "w", encoding="utf-8") as f:
        f.write(text)


try:
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                R["ram_gb"] = round(int(line.split()[1]) / 1024 / 1024, 2)
except Exception as exc:  # noqa: BLE001
    R["errors"].append(f"meminfo: {exc!r}")

for path in ("/kaggle/working", "/kaggle/temp", "/kaggle/input"):
    try:
        u = shutil.disk_usage(path)
        R["disk"][path] = {"free_gb": round(u.free / 1024**3, 2), "total_gb": round(u.total / 1024**3, 2)}
    except Exception as exc:  # noqa: BLE001
        R["disk"][path] = {"error": repr(exc)}

rc, out, err = sh(["nvidia-smi"])
w("nvidia_smi.txt", out + ("\nSTDERR\n" + err if err else ""))
rc2, q, _ = sh(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
if rc2 == 0 and q:
    for line in q.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 2:
            R["gpu"].append({"name": parts[0], "vram": parts[1], "driver": parts[2] if len(parts) > 2 else None})

rc, out, err = sh(["nvcc", "--version"])
R["cuda"]["nvcc"] = out.strip().splitlines()[-1] if rc == 0 and out else None

try:
    import torch
    R["torch"] = {"version": torch.__version__, "cuda_available": torch.cuda.is_available(),
                  "cuda_version": torch.version.cuda, "device_count": torch.cuda.device_count(),
                  "capabilities": [torch.cuda.get_device_capability(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else [],
                  "devices": [{"index": i, "name": torch.cuda.get_device_name(i),
                               "vram_gb": round(torch.cuda.get_device_properties(i).total_memory / 1024**3, 2)} for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else []}
    R["attention"] = {"sdpa": hasattr(torch.nn.functional, "scaled_dot_product_attention"),
                      "flash_sdp_enabled": torch.backends.cuda.flash_sdp_enabled() if torch.cuda.is_available() else False,
                      "mem_efficient_sdp_enabled": torch.backends.cuda.mem_efficient_sdp_enabled() if torch.cuda.is_available() else False}
except Exception as exc:  # noqa: BLE001
    R["torch"] = {"import_error": repr(exc)}
    R["errors"].append(f"torch: {exc!r}")

for pkg in ["transformers", "diffusers", "kokoro", "misaki", "soundfile", "librosa", "manim", "cv2", "yt_dlp"]:
    try:
        m = __import__(pkg)
        R["packages"][pkg] = getattr(m, "__version__", "present")
    except Exception as exc:  # noqa: BLE001
        R["packages"][pkg] = f"missing ({type(exc).__name__})"

for name, url in [("huggingface", "https://huggingface.co"), ("pypi", "https://pypi.org/simple/"), ("github", "https://github.com")]:
    rc, out, err = sh(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "15", "-I", url], timeout=25)
    R["internet"][name] = out or err

rc, ff, _ = sh(["ffmpeg", "-version"])
w("ffmpeg_version.txt", ff)
rc, fp, _ = sh(["ffprobe", "-version"])
w("ffprobe_version.txt", fp)
rc, enc, _ = sh(["ffmpeg", "-hide_banner", "-encoders"])
w("ffmpeg_encoders.txt", "\n".join(l for l in enc.splitlines() if any(k in l.lower() for k in ("264", "265", "aac", "nvenc", "libx264", "libx265"))))
rc, freeze, _ = sh(["pip", "freeze"])
w("pip_freeze.txt", freeze)

w("disk_report.txt", "\n".join(f"{p}: {v}" for p, v in R["disk"].items()) + "\n\n" + sh(["df", "-h"])[1])
w("kaggle_quota.txt", "NOT_AVAILABLE_IN_KERNEL: Kaggle token is intentionally not passed into the kernel.\n"
                        "Observed on the controller (Codespaces): GPU 30.00h total / 29.99h remaining / 0.01h used, refresh 2026-11-14T00:00:00Z.\n")
w("kaggle_environment_report.json", json.dumps(R, indent=2))
w("DONE.json", json.dumps({"status": R["status"], "errors": R["errors"]}, indent=2))
print(json.dumps(R, indent=2)[:4000])