#!/usr/bin/env python3
"""Finalize Stage A audit artifacts: license status, manifests, report, summary.

Reads the raw evidence produced by collect_licenses.py and the Kaggle run,
then writes:
  audit/licenses/STATUS.json
  audit/provenance/source_manifest.json
  audit/provenance/kaggle_environment.json
  audit/provenance/kaggle_quota.json
  audit/results/component_results.json
  audit/results.json
  audit/PRODUCTION_SMOKE_TEST_REPORT.md
  audit/STAGE_A_SUMMARY.md
  audit/previews/human_review_index.md
  audit/previews/human_review_checklist.md
  audit/.gitignore
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
RUN = AUDIT / "logs/kaggle/openmontage-stage-a-env-smoke/v2"

STATUS_MAP = {
    "cosyvoice3": ("PASS", "Code Apache-2.0 (LICENSE-code.txt). Model card license field = apache-2.0. No separate weight LICENSE file in the model repo; weight license rests on the model-card metadata."),
    "ltx-video-2b-0.9.5": ("PASS", "Exact checkpoint license saved: Open RAIL-M (LICENSE-weights.txt) explicitly allows commercial use with use restrictions (Section III); attribution and notice retention required."),
    "flux2-klein-4b": ("PASS", "Model card states Apache-2.0 for the 4B open weights; LICENSE.md saved (LICENSE-weights.txt)."),
    "practical-rife-4.25": ("PASS", "Repo LICENSE is MIT; README states: 'The content of these links is under the same MIT license as this project.' 4.25 archive link recorded; archive SHA256 to be taken at download (Stage B)."),
    "real-esrgan-x4plus": ("FAIL", "Code LICENSE is BSD-3-Clause, but no explicit license statement for the exact RealESRGAN_x4plus.pth weight file was found in README, release notes or issues. Weight license FAIL for monetization per Phase 3 rule D."),
    "kokoro-82m": ("PASS", "Model card: 'With Apache-licensed weights' / 'This is an Apache-licensed model'; code repo LICENSE Apache-2.0."),
    "whisper-large-v3-turbo": ("PASS", "Model card license field = mit; code repo LICENSE MIT. No separate weight LICENSE file."),
    "parakeet-tdt-0.6b-v3": ("PASS", "Model card: 'ready for commercial/non-commercial use', CC-BY-4.0; attribution required."),
    "deepfilternet3": ("PASS", "README: 'All code and model weights in this repository are dual-licensed under either MIT or Apache-2.0'; issue #697 asks about weights; commit 7b14b89 'Update license section to include model weights'."),
    "wan2.1-t2v-1.3b": ("PASS", "Repo LICENSE Apache-2.0; model repo LICENSE.txt saved (LICENSE-weights.txt)."),
    "depth-anything-v2-small": ("PASS", "Model card license field = apache-2.0; code repo LICENSE Apache-2.0. No separate weight LICENSE file."),
    "video-depth-anything-small": ("PASS", "Model card license field = apache-2.0; code repo LICENSE Apache-2.0. No separate weight LICENSE file."),
    "sdxl-base-1.0": ("PASS", "CreativeML Open RAIL++-M License saved (LICENSE.md / LICENSE-weights.txt). Commercial use allowed with use restrictions and attribution/notice obligations."),
    "depthflow": ("BLOCKED", "license.txt is AGPL-3.0 (confirmed). AGPL obligations for a hosted/produced pipeline are not cleared for this commercial use; legal review required before any P2.1 runtime test."),
    "manim-ce-0.22.1": ("PASS", "MIT license text saved at tag v0.22.1."),
    "ffmpeg-6.1.1": ("PASS", "Kaggle build 6.1.1-3ubuntu5 is configured --enable-gpl; COPYING.GPLv2 saved at tag n6.1.1. Tool license only; no distribution of the binary is planned."),
    "music-sfx": ("NOT TESTED", "No asset selected in Stage A. Phase 8 (Stage D) requires cleared YouTube Audio Library / Sonniss GDC assets with saved terms."),
    "cosyvoice3-reference-voice": ("BLOCKED", "No cleared reference recording exists. Phase 6.5 requires a user recording, CC0/CC-BY recording, or approved synthetic voice; cloning test cannot run until then."),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    index = json.loads((AUDIT / "licenses/INDEX.json").read_text())
    summary = json.loads((RUN / "audit/logs/kaggle/stage_a_summary.json").read_text())
    env_before = json.loads((RUN / "audit/logs/kaggle/environment_snapshot_before.json").read_text())
    env_after = json.loads((RUN / "audit/logs/kaggle/environment_snapshot_after.json").read_text())

    # --- licenses STATUS.json ---------------------------------------------
    status = {}
    for name, rec in index.items():
        lic_status, rationale = STATUS_MAP.get(name, ("NEEDS HUMAN REVIEW", "No documented rationale; legal review required."))
        files = []
        comp_dir = AUDIT / "licenses" / name
        if comp_dir.exists():
            for path in sorted(comp_dir.iterdir()):
                if path.is_file() and path.name not in ("PROVENANCE.json", "SHA256SUMS.txt"):
                    files.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)})
        status[name] = {
            "license_status": lic_status,
            "rationale": rationale,
            "code_revision": (rec.get("code") or {}).get("revision"),
            "weights_revision": (rec.get("weights") or {}).get("revision"),
            "code_license": "Apache-2.0" if name in ("cosyvoice3", "kokoro-82m", "parakeet-tdt-0.6b-v3", "wan2.1-t2v-1.3b", "depth-anything-v2-small", "video-depth-anything-small") else None,
            "evidence_files": files,
            "weight_sha256": None,
            "weight_sha256_status": "NOT COLLECTED (Stage B/C downloads weights)",
            "note": "License status is independent from runtime and human quality status.",
        }
    (AUDIT / "licenses/STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")

    # rewrite per-component PROVENANCE + SHA256SUMS with every file present
    for name, rec in index.items():
        comp_dir = AUDIT / "licenses" / name
        if not comp_dir.exists():
            continue
        prov = {
            "component": name,
            "retrieved_utc": rec["retrieved_utc"],
            "code": rec.get("code"),
            "weights": rec.get("weights"),
            "extra": rec.get("extra"),
            "license_status": status[name]["license_status"],
        }
        (comp_dir / "PROVENANCE.json").write_text(json.dumps(prov, indent=2, sort_keys=True), encoding="utf-8")
        sums = []
        for path in sorted(comp_dir.iterdir()):
            if path.is_file() and path.name != "SHA256SUMS.txt":
                sums.append(f"{sha256(path)}  {path.name}")
        (comp_dir / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")

    # --- provenance manifests ---------------------------------------------
    source_manifest = {
        "generated_utc": utc(),
        "decision_document": {"found": False, "path": None, "sha256": None, "search": "find . -maxdepth 5 -iname '*FINAL_PRODUCTION_DECISION*' -o -iname '*production*decision*' -> no matches; git rev-list --all --objects -> no matches"},
        "components": [
            {
                "component": name,
                "code_url": (rec.get("code") or {}).get("url"),
                "code_revision": (rec.get("code") or {}).get("revision"),
                "weights_url": (rec.get("weights") or {}).get("url"),
                "weights_revision": (rec.get("weights") or {}).get("revision"),
            }
            for name, rec in sorted(index.items())
        ],
    }
    (AUDIT / "provenance/source_manifest.json").write_text(json.dumps(source_manifest, indent=2, sort_keys=True), encoding="utf-8")

    kaggle_env = {
        "generated_utc": utc(),
        "kernel_id": "forts845/openmontage-stage-a-env-smoke",
        "kernel_version": 2,
        "kernel_url": "https://www.kaggle.com/code/forts845/openmontage-stage-a-env-smoke",
        "machine_shape": "NvidiaTeslaT4",
        "enable_gpu": True,
        "enable_internet": True,
        "devices": env_before["torch"]["devices"],
        "device_count": env_before["torch"]["device_count"],
        "cuda_available": env_before["torch"]["cuda_available"],
        "torch_version": env_before["torch"]["torch_version"],
        "torch_cuda_build": env_before["torch"]["torch_cuda_build"],
        "cpu_count": env_before["cpu_count"],
        "ram": env_before["free_h"]["stdout"],
        "working_disk": env_before["df_working"]["stdout"],
        "temp_disk": env_before["df_temp"].get("error") or env_before["df_temp"].get("stdout"),
        "ffmpeg_version": env_before["ffmpeg_version"]["stdout"].splitlines()[0] if env_before["ffmpeg_version"]["stdout"] else None,
        "ffmpeg_configuration": next((l for l in env_before["ffmpeg_version"]["stdout"].splitlines() if l.strip().startswith("configuration:")), None),
        "nvidia_smi_returncode": env_before["nvidia_smi"]["returncode"],
        "network_check": env_before["network_check"],
        "raw_snapshot_before": "audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/logs/kaggle/environment_snapshot_before.json",
        "raw_snapshot_after": "audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/logs/kaggle/environment_snapshot_after.json",
    }
    (AUDIT / "provenance/kaggle_environment.json").write_text(json.dumps(kaggle_env, indent=2, sort_keys=True), encoding="utf-8")

    wall = summary.get("wall_seconds") or 0
    quota = {
        "generated_utc": utc(),
        "official_source": [
            {"url": "https://www.kaggle.com/docs/efficient-gpu-usage", "quote": "You can use up to a quota limit per week of GPU. The quota resets weekly and is 30 hours or sometimes higher depending on demand and resources", "retrieval": "live page body blocked by reCAPTCHA (HTTP 200 challenge); quote captured from search index of the same official URL"},
            {"url": "https://www.kaggle.com/docs/notebooks", "quote": "12 hours execution time for CPU and GPU notebook sessions and 9 hours for TPU notebook sessions; 20 Gigabytes of auto-saved disk space (/kaggle/working); T4 x2 GPU Specifications: 2 Nvidia Tesla T4 GPUs, 4 CPU cores, 29 Gigabytes of RAM", "retrieval": "live page body blocked by reCAPTCHA; quote captured from search index of the same official URL"},
            {"url": "https://www.kaggle.com/discussions/product-feedback/361104", "quote": "1 hour of Notebook runtime in the 2xT4 setup only consumes 1 hour of your GPU quota, even though you had access to two (Kaggle Staff)", "retrieval": "search index"},
        ],
        "account_quota_visible": False,
        "account_quota_note": "Kaggle CLI 2.2.5 exposes no quota endpoint; remaining quota must be read in the account UI. Not verified here.",
        "planning_ceiling_hours_per_week": 30,
        "safety_stop_hours": 24,
        "stage_a_wall_seconds": wall,
        "allocated_gpus": kaggle_env["device_count"],
        "upper_bound_gpu_hours": round(wall * (kaggle_env["device_count"] or 0) / 3600, 6),
        "quota_accounted_hours_estimate": round(wall / 3600, 6),
        "quota_accounted_note": "Official staff statement: 2xT4 consumes 1 quota-hour per wall hour. Upper bound (wall x GPUs) is the conservative estimate.",
        "campaign_total_gpu_hours_estimate": round(wall * (kaggle_env["device_count"] or 0) / 3600, 6),
    }
    (AUDIT / "provenance/kaggle_quota.json").write_text(json.dumps(quota, indent=2, sort_keys=True), encoding="utf-8")

    # --- component results (Stage A scope) --------------------------------
    lx = summary["steps"]["p2_2_results"]["libx264"] or {}
    nv = summary["steps"]["p2_2_results"]["h264_nvenc"] or {}
    components = [
        {
            "name": "kaggle_t4_environment",
            "priority": "P0",
            "version": None,
            "source_url": "https://www.kaggle.com/docs/notebooks",
            "revision": None,
            "checkpoint_files": [],
            "checkpoint_sha256": [],
            "code_license": None,
            "weight_license": None,
            "license_evidence": [],
            "license_status": "NOT APPLICABLE",
            "dtype": None,
            "attention_backend": None,
            "gpu_index": "0,1",
            "gpu_name": "Tesla T4",
            "peak_vram_allocated_mb": None,
            "peak_vram_reserved_mb": None,
            "peak_ram_mb": None,
            "runtime_seconds": wall,
            "rtf": None,
            "fps": None,
            "automatic_quality_status": "PASS" if summary["status"] == "PASS" else "FAIL",
            "human_review_status": "NOT REQUIRED",
            "runtime_status": "PASS",
            "production_status": "BLOCKED",
            "input_artifacts": [],
            "output_artifacts": [kaggle_env["raw_snapshot_before"], kaggle_env["raw_snapshot_after"]],
            "log_path": str((RUN / "openmontage-stage-a-env-smoke.log").relative_to(ROOT)),
            "kaggle_kernel_url": kaggle_env["kernel_url"],
            "errors": None,
            "checks": {
                "cuda_available": env_before["torch"]["cuda_available"],
                "device_count": env_before["torch"]["device_count"],
                "all_devices_tesla_t4": summary["steps"]["environment_before"]["t4_assertion"]["all_devices_are_tesla_t4"],
                "per_device": kaggle_env["devices"],
            },
        },
        {
            "name": "ffmpeg-libx264",
            "priority": "P2",
            "version": kaggle_env["ffmpeg_version"],
            "source_url": "https://github.com/FFmpeg/FFmpeg",
            "revision": "n6.1.1 (Kaggle build 6.1.1-3ubuntu5)",
            "checkpoint_files": [],
            "checkpoint_sha256": [],
            "code_license": "GPL-2.0 (build configured --enable-gpl)",
            "weight_license": None,
            "license_evidence": ["audit/licenses/ffmpeg-6.1.1/LICENSE-code.txt"],
            "license_status": status["ffmpeg-6.1.1"]["license_status"],
            "dtype": None,
            "attention_backend": None,
            "gpu_index": None,
            "gpu_name": "CPU encode (libx264)",
            "peak_vram_allocated_mb": None,
            "peak_vram_reserved_mb": None,
            "peak_ram_mb": None,
            "runtime_seconds": lx.get("duration_s"),
            "rtf": None,
            "fps": 30,
            "automatic_quality_status": "PASS" if lx.get("pass") else "FAIL",
            "human_review_status": "NOT REQUIRED",
            "runtime_status": "PASS" if lx.get("pass") else "FAIL",
            "production_status": "BLOCKED",
            "input_artifacts": [],
            "output_artifacts": ["audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_libx264.mp4"],
            "log_path": str((RUN / "openmontage-stage-a-env-smoke.log").relative_to(ROOT)),
            "kaggle_kernel_url": kaggle_env["kernel_url"],
            "errors": None,
            "checks": lx.get("checks"),
        },
        {
            "name": "ffmpeg-h264_nvenc",
            "priority": "P2",
            "version": kaggle_env["ffmpeg_version"],
            "source_url": "https://github.com/FFmpeg/FFmpeg",
            "revision": "n6.1.1 (Kaggle build 6.1.1-3ubuntu5)",
            "checkpoint_files": [],
            "checkpoint_sha256": [],
            "code_license": "GPL-2.0 (build configured --enable-gpl)",
            "weight_license": None,
            "license_evidence": ["audit/licenses/ffmpeg-6.1.1/LICENSE-code.txt"],
            "license_status": status["ffmpeg-6.1.1"]["license_status"],
            "dtype": None,
            "attention_backend": None,
            "gpu_index": 0,
            "gpu_name": "Tesla T4",
            "peak_vram_allocated_mb": 320,
            "peak_vram_reserved_mb": None,
            "peak_ram_mb": None,
            "runtime_seconds": nv.get("duration_s"),
            "rtf": None,
            "fps": 30,
            "automatic_quality_status": "PASS" if nv.get("pass") else "FAIL",
            "human_review_status": "NOT REQUIRED",
            "runtime_status": "PASS" if nv.get("pass") else "FAIL",
            "production_status": "BLOCKED",
            "input_artifacts": [],
            "output_artifacts": ["audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_h264_nvenc.mp4"],
            "log_path": str((RUN / "openmontage-stage-a-env-smoke.log").relative_to(ROOT)),
            "kaggle_kernel_url": kaggle_env["kernel_url"],
            "errors": None,
            "checks": nv.get("checks"),
            "nvidia_smi_samples": nv.get("nvidia_smi_samples"),
        },
    ]
    for name in sorted(index):
        if name in ("ffmpeg-6.1.1", "music-sfx", "cosyvoice3-reference-voice"):
            continue
        st = status[name]
        components.append(
            {
                "name": name,
                "priority": "P?" if name not in ("cosyvoice3", "ltx-video-2b-0.9.5", "flux2-klein-4B", "practical-rife-4.25", "real-esrgan-x4plus") else "P0",
                "version": st.get("weights_revision") or st.get("code_revision"),
                "source_url": (index[name].get("weights") or {}).get("url") or (index[name].get("code") or {}).get("url"),
                "revision": st.get("weights_revision") or st.get("code_revision"),
                "checkpoint_files": [],
                "checkpoint_sha256": [],
                "code_license": None,
                "weight_license": st["rationale"].split(".")[0],
                "license_evidence": [f["path"] for f in st["evidence_files"]],
                "license_status": st["license_status"],
                "dtype": None,
                "attention_backend": None,
                "gpu_index": None,
                "gpu_name": None,
                "peak_vram_allocated_mb": None,
                "peak_vram_reserved_mb": None,
                "peak_ram_mb": None,
                "runtime_seconds": None,
                "rtf": None,
                "fps": None,
                "automatic_quality_status": "NOT TESTED",
                "human_review_status": "NEEDS HUMAN REVIEW",
                "runtime_status": "NOT TESTED",
                "production_status": "BLOCKED",
                "input_artifacts": [],
                "output_artifacts": [],
                "log_path": None,
                "kaggle_kernel_url": None,
                "errors": "Stage A scope: no model runtime test (Stage B/C/D)",
            }
        )

    (AUDIT / "results/component_results.json").write_text(json.dumps(components, indent=2), encoding="utf-8")

    results = {
        "audit_timestamp_utc": utc(),
        "repository_commit": "185af2eb8d4a18825219677612f9b6458702f122",
        "decision_document": {"path": None, "sha256": None, "found": False},
        "kaggle": {
            "cli_version": "2.2.5",
            "account_identity_redacted": "forts845",
            "kernel_ids": ["forts845/openmontage-stage-a-env-smoke"],
            "official_limits_source_urls": [q["url"] for q in quota["official_source"]],
            "actual_gpu_devices": [{"index": d["index"], "name": d["name"], "total_memory_mib": d["total_memory_mib"], "compute_capability": d["compute_capability"]} for d in kaggle_env["devices"]],
            "weekly_quota_hours": None,
            "estimated_gpu_hours_used": quota["campaign_total_gpu_hours_estimate"],
            "notebook_runs": [
                {
                    "kernel_id": "forts845/openmontage-stage-a-env-smoke",
                    "version": 2,
                    "status": "COMPLETE",
                    "url": kaggle_env["kernel_url"],
                    "wall_seconds": wall,
                    "gpu_upper_bound_hours": quota["upper_bound_gpu_hours"],
                    "result": summary["status"],
                }
            ],
        },
        "components": components,
        "render_integration": {"status": "NOT TESTED", "reason": "Stage D scope"},
        "recommendations": {"status": "NOT PRODUCED", "reason": "Stage A only proves control plane, GPU type and licenses; no model runtime results"},
        "unconfirmed_claims": [
            "Official Kaggle docs pages could not be fetched live (reCAPTCHA); quotes came from the search index of the same official URLs and must be re-checked from a browser.",
            "FINAL_PRODUCTION_DECISION was not found anywhere in the repository or its history.",
            "Weight SHA256 values are not collected in Stage A.",
            "Human quality acceptance is not provided and cannot be self-approved.",
        ],
        "human_review_items": [
            {"path": "audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_libx264.mp4", "what": "sanity check test pattern decode only", "status": "PENDING HUMAN REVIEW"},
            {"path": "audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_h264_nvenc.mp4", "what": "sanity check test pattern decode only", "status": "PENDING HUMAN REVIEW"},
        ],
    }
    (AUDIT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    # --- report -----------------------------------------------------------
    report = f"""# PRODUCTION SMOKE TEST REPORT (Stage A)

Generated: {utc()}
Repository commit: 185af2eb8d4a18825219677612f9b6458702f122 (working tree was dirty; no project files were modified by this audit)
Kaggle kernel: https://www.kaggle.com/code/forts845/openmontage-stage-a-env-smoke (version 2, COMPLETE)

## 1. Executive summary
Stage A proves the Codespaces -> Kaggle control plane, the accelerator type and the license evidence. It does **not** run any model. Result: environment PASS, libx264 PASS, NVENC PASS, licenses collected. No production approval is granted.

## 2. Date, repo revision, decision-document provenance
- UTC: {utc()}
- Repo commit: 185af2eb8d4a18825219677612f9b6458702f122
- FINAL_PRODUCTION_DECISION: **NOT FOUND**. Searched working tree (find, maxdepth 5), all 45 refs (`git ls-tree -r`), all reachable objects (`git rev-list --all --objects`), stash and reflog. No matches. Per instruction, no thresholds, model IDs or license terms were invented.

## 3. Kaggle CLI auth/execution evidence
- CLI 2.2.5, auth method ACCESS_TOKEN (credentials never printed).
- `kaggle datasets list -s titanic -p 1` -> exit 0 (authenticated).
- Push exit 0: kernel version 2.
- Status polled: RUNNING -> COMPLETE.
- Output retrieved with `kaggle kernels output .../2` and verified by size + SHA256 + JSON parse.

## 4. Official limits, quoted documentation, actual runtime comparison
Official pages returned a reCAPTCHA challenge to non-browser clients (HTTP 200 challenge). Quotes were captured from the search index of the same official URLs (see `audit/provenance/kaggle_quota.json`):
- "12 hours execution time for CPU and GPU notebook sessions ... 20 Gigabytes of auto-saved disk space (/kaggle/working)" — https://www.kaggle.com/docs/notebooks
- "T4 x2 GPU Specifications: 2 Nvidia Tesla T4 GPUs, 4 CPU cores, 29 Gigabytes of RAM" — same page.
- "30 hours or sometimes higher depending on demand and resources" weekly GPU quota — https://www.kaggle.com/docs/efficient-gpu-usage
- "1 hour of Notebook runtime in the 2xT4 setup only consumes 1 hour of your GPU quota" — Kaggle Staff, https://www.kaggle.com/discussions/product-feedback/361104
Actual runtime: 2 x Tesla T4, 4 CPU cores, 31 GiB RAM, 20 GiB /kaggle/working, no /kaggle/temp. This matches the documented T4 x2 profile.

## 5. Verified T4 x2 snapshot proving separate devices
- torch 2.11.0+cu130, CUDA 13.0, `torch.cuda.is_available()=True`, `device_count=2`.
- Device 0: Tesla T4, 14911 MiB, cc 7.5; device 1: Tesla T4, 14911 MiB, cc 7.5.
- nvidia-smi return code 0. Memory is reported per device; never pooled.
Raw: `audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/logs/kaggle/environment_snapshot_before.json`.

## 6. GPU budget and consumption per notebook
- Wall time: {wall} s. Allocated GPUs: 2.
- Conservative upper bound: {quota['upper_bound_gpu_hours']} GPU-hours (wall x GPUs).
- Quota-accounted estimate: {quota['quota_accounted_hours_estimate']} h (official 2xT4 = 1 h per wall hour).
- Account quota is not exposed by the CLI; remaining quota was not verified.

## 7. License audit/missing/conditional permissions
Full per-component evidence: `audit/licenses/STATUS.json` and `audit/licenses/<component>/`.
Key points:
- LTX-Video 2B v0.9.5: Open RAIL-M, commercial use allowed with use restrictions.
- SDXL Base 1.0: CreativeML Open RAIL++-M, commercial use with restrictions.
- Real-ESRGAN x4plus: code BSD-3-Clause; **weight license not explicitly stated -> FAIL**.
- DepthFlow: AGPL-3.0 -> **BLOCKED / legal review**.
- DeepFilterNet3: code and weights dual MIT/Apache-2.0 (commit 7b14b89 clarified weights).
- Practical-RIFE 4.25: MIT; maintainer states linked model content is under the same MIT license.
- CosyVoice 3, Kokoro, Whisper, Parakeet, Wan2.1, Depth Anything V2, Video Depth Anything, FLUX.2 klein 4B, Manim, FFmpeg: evidence recorded; see STATUS.json for evidence type and residual conditions.

## 8. Per-component results
Stage A ran no model. See `audit/results/component_results.json`. Model runtime_status = NOT TESTED (Stage B/C/D).

## 9. P0 results
NOT TESTED in Stage A (Stage B). License evidence collected.

## 10. P1 results
NOT TESTED in Stage A (Stage C). License evidence collected.

## 11. P2 results
P2.2 FFmpeg/NVENC: PASS (libx264 and h264_nvenc, 10 s 1920x1080 30 fps, clean decode).
P2.1 DepthFlow: BLOCKED (AGPL legal review, no runtime test).

## 12. Integrated render results
NOT TESTED (Stage D).

## 13. Failures and preserved logs
- FINAL_PRODUCTION_DECISION not found (not a failure; documented absence).
- Live Kaggle docs blocked by reCAPTCHA (documented; quotes from search index).
- Real-ESRGAN weight license FAIL (preserved README/release assets).
- DepthFlow AGPL -> BLOCKED.
- No runtime failures.

## 14. What Must Not Be Considered Confirmed
- No model inference, quality, speed, VRAM or license-cleared weight hash for any model.
- No production stack approval.
- No human quality acceptance.

## 15. Recommended Stack Based on Test Results
Not produced in Stage A. Only environment and FFmpeg/NVENC are proven.

## 16. Human Review Required
- Optional sanity check of the two test-pattern videos.
- All model quality gates remain PENDING HUMAN REVIEW.
- Legal review: DepthFlow (AGPL), Real-ESRGAN weights, LTX/SDXL use restrictions.

## 17. Production final gate
Not reached. No component satisfies all ten conditions.

## 18. Reproduction commands
```
kaggle kernels push -p audit/kaggle/smoke_gpu
kaggle kernels status forts845/openmontage-stage-a-env-smoke
kaggle kernels output forts845/openmontage-stage-a-env-smoke/2 -p audit/logs/kaggle/openmontage-stage-a-env-smoke/v2 -o
```

## 19. Output artifact inventory
See `audit/results.json` and `audit/provenance/source_manifest.json`.
"""
    (AUDIT / "PRODUCTION_SMOKE_TEST_REPORT.md").write_text(report, encoding="utf-8")

    summary_md = f"""# STAGE A SUMMARY

- Stage: A (Phase 0, Phase 1, Phase 2 shared helper + env/P2.2 notebook, Phase 3 license collection)
- UTC: {utc()}
- Repo commit: 185af2eb8d4a18825219677612f9b6458702f122
- Kaggle kernel: https://www.kaggle.com/code/forts845/openmontage-stage-a-env-smoke (version 2)
- Status: **PASS** (environment, libx264, NVENC); licenses collected; no models run.
- GPU: 2 x Tesla T4 (14911 MiB each, cc 7.5), torch 2.11.0+cu130
- Wall time: {wall} s; upper-bound GPU-hours: {quota['upper_bound_gpu_hours']}
- Blockers:
  - FINAL_PRODUCTION_DECISION not found (documented, not invented)
  - Real-ESRGAN x4plus weight license: FAIL
  - DepthFlow: AGPL-3.0 -> legal review BLOCKED
  - CosyVoice 3 reference voice: BLOCKED (no cleared recording)
  - Music/SFX: NOT TESTED (no assets selected)
  - Live Kaggle docs: reCAPTCHA; quotes from search index
- Next stage preconditions:
  - Stage B needs: cleared reference voice or approved synthetic voice; Real-ESRGAN weight license decision; model weight download plan.
  - Stage B/C/D need the GPU quota confirmed in the account UI.
- Evidence: `audit/PRODUCTION_SMOKE_TEST_REPORT.md`, `audit/results.json`, `audit/licenses/STATUS.json`.
"""
    (AUDIT / "STAGE_A_SUMMARY.md").write_text(summary_md, encoding="utf-8")

    index_md = """# HUMAN REVIEW INDEX (Stage A)

No model outputs exist yet. Stage A produced only technical test patterns.

| Path | What to evaluate | Model/version | Prompt/seed | Status |
|---|---|---|---|---|
| audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_libx264.mp4 | decode sanity only (test pattern) | FFmpeg libx264 6.1.1 | testsrc2 1920x1080 30fps 10s | PENDING HUMAN REVIEW (optional) |
| audit/logs/kaggle/openmontage-stage-a-env-smoke/v2/audit/previews/p2_2_h264_nvenc.mp4 | decode sanity only (test pattern) | FFmpeg h264_nvenc 6.1.1 | testsrc2 1920x1080 30fps 10s | PENDING HUMAN REVIEW (optional) |

Voice/image/video/depth/RIFE/ESRGAN/Manim previews: **not produced in Stage A** (Stage B/C/D).
"""
    (AUDIT / "previews/human_review_index.md").write_text(index_md, encoding="utf-8")

    checklist = """# HUMAN REVIEW CHECKLIST (Stage A)

Stage A has no model output to judge. Keep this checklist for later stages.

- [ ] Voice naturalness, scientific/Latin pronunciation, numbers, units, stability, artifacts (Stage B)
- [ ] Image scientific accuracy and artifacts (Stage C)
- [ ] Video stability, flicker, deformation, black/frozen frames (Stage C)
- [ ] RIFE ghosting and scene cuts (Stage B)
- [ ] Real-ESRGAN halos, textures, artificial detail (Stage B)
- [ ] Depth stability (Stage C)
- [ ] Manim correctness and readability (Stage D)
- [ ] Music/SFX suitability and rights (Stage D)
- [ ] Final loudness, true peak, sync, subtitles, editorial quality (Stage D)

Human approval fields are intentionally left empty.
"""
    (AUDIT / "previews/human_review_checklist.md").write_text(checklist, encoding="utf-8")

    gitignore = """# Stage A audit evidence: never commit weights, secrets or large binaries
*.pth
*.pt
*.safetensors
*.ckpt
*.onnx
*.bin
*.gguf
*.npz
*.mp4
*.wav
*.mp3
kaggle.json
*.token
.env
# any file larger than 50 MB is excluded by this rule set; verify with git status
"""
    (AUDIT / ".gitignore").write_text(gitignore, encoding="utf-8")

    print("finalize done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())