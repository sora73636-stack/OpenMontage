"""OpenMontage Factory preflight — Kaggle kernel.

Reports only observed facts. Writes PREFLIGHT.json and DONE.json to
/kaggle/working. No model downloads happen here by design.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import time

OUT = "/kaggle/working"
RESULT = {
    "status": "ok",
    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "platform": platform.platform(),
    "python": sys.version,
    "cpu_count": os.cpu_count(),
    "ram_gb": None,
    "disk_gb_free": None,
    "gpu": [],
    "cuda": {},
    "torch": {},
    "internet": {},
    "packages": {},
    "errors": [],
}


def run(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()[-2000:]}
    except Exception as exc:  # noqa: BLE001
        return {"returncode": None, "error": repr(exc)}


try:
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                RESULT["ram_gb"] = round(int(line.split()[1]) / 1024 / 1024, 2)
                break
except Exception as exc:  # noqa: BLE001
    RESULT["errors"].append(f"meminfo: {exc!r}")

try:
    usage = shutil.disk_usage(OUT)
    RESULT["disk_gb_free"] = round(usage.free / 1024**3, 2)
    RESULT["disk_gb_total"] = round(usage.total / 1024**3, 2)
except Exception as exc:  # noqa: BLE001
    RESULT["errors"].append(f"disk: {exc!r}")

# GPU: nvidia-smi is the ground truth
smi = run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
RESULT["gpu_smi"] = smi
if smi["returncode"] == 0 and smi["stdout"]:
    for line in smi["stdout"].splitlines():
        parts = [p.strip() for p in line.split(",")]
        RESULT["gpu"].append({"name": parts[0], "vram": parts[1], "driver": parts[2] if len(parts) > 2 else None})

# CUDA toolkit
RESULT["cuda"]["nvcc"] = run(["nvcc", "--version"])["stdout"].splitlines()[-1] if run(["nvcc", "--version"])["returncode"] == 0 else None

# Torch
try:
    import torch  # noqa: PLC0415

    RESULT["torch"] = {
        "version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_version": torch.version.cuda,
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "devices": [
            {"index": i, "name": torch.cuda.get_device_name(i),
             "vram_gb": round(torch.cuda.get_device_properties(i).total_memory / 1024**3, 2)}
            for i in range(torch.cuda.device_count())
        ] if torch.cuda.is_available() else [],
    }
except Exception as exc:  # noqa: BLE001
    RESULT["torch"] = {"import_error": repr(exc)}
    RESULT["errors"].append(f"torch: {exc!r}")

# Package presence (no install here)
for pkg in ["transformers", "diffusers", "kokoro", "misaki", "soundfile", "librosa", "yt_dlp"]:
    try:
        mod = __import__(pkg)
        RESULT["packages"][pkg] = getattr(mod, "__version__", "present")
    except Exception as exc:  # noqa: BLE001
        RESULT["packages"][pkg] = f"missing ({type(exc).__name__})"

# Internet reachability (HEAD requests, no downloads)
for name, url in [
    ("huggingface", "https://huggingface.co"),
    ("pypi", "https://pypi.org/simple/"),
    ("github", "https://github.com"),
]:
    r = run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "15", "-I", url], timeout=25)
    RESULT["internet"][name] = r.get("stdout") or r.get("error")

with open(f"{OUT}/PREFLIGHT.json", "w") as f:
    json.dump(RESULT, f, indent=2)

RESULT["status"] = "ok" if not [e for e in RESULT["errors"] if e.startswith(("torch", "meminfo", "disk"))] else "error"
with open(f"{OUT}/DONE.json", "w") as f:
    json.dump({"status": RESULT["status"], "errors": RESULT["errors"]}, f, indent=2)
print(json.dumps(RESULT, indent=2))