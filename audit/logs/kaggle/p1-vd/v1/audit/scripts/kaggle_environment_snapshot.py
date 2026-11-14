#!/usr/bin/env python3
"""Shared Kaggle environment snapshot helper for the OpenMontage audit.

This exact file must be copied unchanged into every Kaggle notebook of the
audit (Stage A..D). It records:

  * UTC timestamp, Python version/executable, pip freeze
  * torch version / CUDA build / availability / device count
  * per-device index, name, total memory, compute capability, free memory
  * full nvidia-smi output
  * GPU name / memory / driver / utilisation / process memory
  * ffmpeg -version, ffmpeg -hide_banner -encoders, ffprobe -version
  * df -h /kaggle/working, /kaggle/temp (when present), free -h
  * CPU count
  * short-timeout network check to official package/model hosts
  * free space and output-directory size

Raw command output is preserved; no command failure is silently omitted.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd, timeout: int = 120):
    """Run a command and return a structured record. Never raises."""
    started = time.time()
    record = {
        "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
        "returncode": None,
        "duration_s": None,
        "stdout": "",
        "stderr": "",
    }
    try:
        proc = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        record["returncode"] = proc.returncode
        record["stdout"] = proc.stdout[-40000:]
        record["stderr"] = proc.stderr[-16000:]
    except FileNotFoundError as exc:
        record["error"] = f"FileNotFoundError: {exc}"
    except subprocess.TimeoutExpired:
        record["error"] = f"TimeoutExpired after {timeout}s"
    except Exception as exc:  # noqa: BLE001 - audit helper must never crash the run
        record["error"] = f"{type(exc).__name__}: {exc}"
    record["duration_s"] = round(time.time() - started, 3)
    return record


def _tail(text: str, limit: int = 40000) -> str:
    return text[-limit:] if isinstance(text, str) else ""


def _pip_freeze() -> str:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            timeout=180,
        )
        return proc.stdout
    except Exception as exc:  # noqa: BLE001
        return f"pip freeze failed: {type(exc).__name__}: {exc}"


def _torch_info() -> dict:
    info = {
        "torch_imported": False,
        "torch_version": None,
        "torch_cuda_build": None,
        "cuda_available": None,
        "device_count": None,
        "devices": [],
        "errors": [],
    }
    try:
        import torch  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        info["errors"].append(f"import torch failed: {type(exc).__name__}: {exc}")
        return info

    info["torch_imported"] = True
    info["torch_version"] = getattr(torch, "__version__", None)
    info["torch_cuda_build"] = getattr(getattr(torch, "version", None), "cuda", None)
    try:
        info["cuda_available"] = bool(torch.cuda.is_available())
        info["device_count"] = int(torch.cuda.device_count())
    except Exception as exc:  # noqa: BLE001
        info["errors"].append(f"cuda query failed: {type(exc).__name__}: {exc}")
        return info

    for idx in range(info["device_count"] or 0):
        device = {"index": idx}
        try:
            props = torch.cuda.get_device_properties(idx)
            device.update(
                {
                    "name": props.name,
                    "total_memory_mib": int(props.total_memory / (1024 * 1024)),
                    "compute_capability": f"{props.major}.{props.minor}",
                    "multi_processor_count": getattr(props, "multi_processor_count", None),
                }
            )
        except Exception as exc:  # noqa: BLE001
            device["error"] = f"{type(exc).__name__}: {exc}"
        try:
            free_bytes, total_bytes = torch.cuda.mem_get_info(idx)
            device["free_memory_mib"] = int(free_bytes / (1024 * 1024))
            device["total_memory_mib_reported"] = int(total_bytes / (1024 * 1024))
        except Exception as exc:  # noqa: BLE001
            device["mem_get_info_error"] = f"{type(exc).__name__}: {exc}"
        info["devices"].append(device)
    return info


def _nvidia_smi() -> dict:
    return run_cmd(["nvidia-smi"], timeout=60)


def _network_check(hosts=None, timeout: float = 5.0) -> list:
    hosts = hosts or ["huggingface.co", "pypi.org", "github.com"]
    results = []
    for host in hosts:
        item = {"host": host, "port": 443}
        started = time.time()
        try:
            with socket.create_connection((host, 443), timeout=timeout):
                item["reachable"] = True
        except Exception as exc:  # noqa: BLE001
            item["reachable"] = False
            item["error"] = f"{type(exc).__name__}: {exc}"
        item["latency_s"] = round(time.time() - started, 3)
        results.append(item)
    return results


def _dir_size(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        return {"path": str(path), "exists": False, "bytes": None}
    total = 0
    files = 0
    try:
        for root, _dirs, names in os.walk(path):
            for name in names:
                try:
                    total += os.path.getsize(os.path.join(root, name))
                    files += 1
                except OSError:
                    continue
    except Exception as exc:  # noqa: BLE001
        return {"path": str(path), "exists": True, "error": f"{type(exc).__name__}: {exc}"}
    return {"path": str(path), "exists": True, "bytes": total, "files": files}


def collect(out_dir: str | os.PathLike, label: str) -> dict:
    """Collect a full snapshot and persist JSON + raw text. Returns the dict."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    stamp = _utc_now()

    payload = {
        "snapshot_version": SNAPSHOT_VERSION,
        "label": label,
        "utc_timestamp": stamp,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "pip_freeze": _pip_freeze(),
        "torch": _torch_info(),
        "nvidia_smi": _nvidia_smi(),
        "ffmpeg_version": run_cmd(["ffmpeg", "-version"], timeout=60),
        "ffmpeg_encoders": run_cmd(["ffmpeg", "-hide_banner", "-encoders"], timeout=120),
        "ffprobe_version": run_cmd(["ffprobe", "-version"], timeout=60),
        "df_working": run_cmd(["df", "-h", "/kaggle/working"], timeout=30),
        "df_temp": run_cmd(["df", "-h", "/kaggle/temp"], timeout=30),
        "free_h": run_cmd(["free", "-h"], timeout=30),
        "cpu_count": os.cpu_count(),
        "network_check": _network_check(),
        "output_dir_size": _dir_size(out_path),
        "disk_usage": {
            "working_free_gib": shutil.disk_usage("/kaggle/working").free / (1024**3)
            if Path("/kaggle/working").exists()
            else None
        },
    }

    json_path = out_path / f"environment_snapshot_{label}.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    raw_lines = [f"===== SNAPSHOT {label} @ {stamp} ====="]
    for key in (
        "python_version",
        "platform",
        "cpu_count",
        "nvidia_smi",
        "ffmpeg_version",
        "ffprobe_version",
        "df_working",
        "df_temp",
        "free_h",
        "network_check",
    ):
        raw_lines.append(f"--- {key} ---")
        value = payload.get(key)
        if isinstance(value, dict):
            raw_lines.append(f"returncode={value.get('returncode')}")
            raw_lines.append(value.get("stdout", ""))
            if value.get("stderr"):
                raw_lines.append("[stderr] " + value["stderr"])
            if value.get("error"):
                raw_lines.append("[error] " + str(value["error"]))
        else:
            raw_lines.append(json.dumps(value, indent=2, sort_keys=True))
    raw_lines.append("--- torch ---")
    raw_lines.append(json.dumps(payload["torch"], indent=2, sort_keys=True))
    raw_lines.append("--- pip freeze ---")
    raw_lines.append(payload["pip_freeze"])
    raw_path = out_path / f"environment_snapshot_{label}.txt"
    raw_path.write_text("\n".join(raw_lines), encoding="utf-8")

    return payload


def assert_t4(payload: dict) -> dict:
    """Return a T4 verification record. Never raises; caller decides to stop."""
    torch_info = payload.get("torch", {})
    devices = torch_info.get("devices", [])
    record = {
        "cuda_available": torch_info.get("cuda_available"),
        "device_count": torch_info.get("device_count"),
        "all_devices_are_tesla_t4": False,
        "per_device": [],
        "ok": False,
        "reasons": [],
    }
    if not torch_info.get("cuda_available"):
        record["reasons"].append("torch.cuda.is_available() is false")
    if not torch_info.get("device_count") in (1, 2):
        record["reasons"].append(
            f"device_count={torch_info.get('device_count')!r} is not 1 or 2"
        )
    for device in devices:
        item = {
            "index": device.get("index"),
            "name": device.get("name"),
            "total_memory_mib": device.get("total_memory_mib"),
            "compute_capability": device.get("compute_capability"),
            "free_memory_mib": device.get("free_memory_mib"),
        }
        name = (device.get("name") or "").upper()
        if "TESLA T4" not in name:
            record["reasons"].append(f"device {device.get('index')} is not a Tesla T4: {device.get('name')!r}")
        if device.get("compute_capability") not in ("7.5", None):
            record["reasons"].append(
                f"device {device.get('index')} compute capability {device.get('compute_capability')} != 7.5"
            )
        record["per_device"].append(item)
    record["all_devices_are_tesla_t4"] = all(
        "TESLA T4" in (d.get("name") or "").upper() for d in devices
    ) and bool(devices)
    record["ok"] = record["all_devices_are_tesla_t4"] and not record["reasons"]
    return record


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kaggle environment snapshot")
    parser.add_argument("--out", default="/kaggle/working/audit/logs/kaggle")
    parser.add_argument("--label", default="manual")
    args = parser.parse_args()
    result = collect(args.out, args.label)
    print(json.dumps({"label": args.label, "torch": result["torch"], "t4": assert_t4(result)}, indent=2))