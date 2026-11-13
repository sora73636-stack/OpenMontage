# PRODUCTION SMOKE TEST REPORT (Stage A)

Generated: 2026-11-13T04:21:09Z
Repository commit: 185af2eb8d4a18825219677612f9b6458702f122 (working tree was dirty; no project files were modified by this audit)
Kaggle kernel: https://www.kaggle.com/code/forts845/openmontage-stage-a-env-smoke (version 2, COMPLETE)

## 1. Executive summary
Stage A proves the Codespaces -> Kaggle control plane, the accelerator type and the license evidence. It does **not** run any model. Result: environment PASS, libx264 PASS, NVENC PASS, licenses collected. No production approval is granted.

## 2. Date, repo revision, decision-document provenance
- UTC: 2026-11-13T04:21:09Z
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
- Wall time: 36.147 s. Allocated GPUs: 2.
- Conservative upper bound: 0.020082 GPU-hours (wall x GPUs).
- Quota-accounted estimate: 0.010041 h (official 2xT4 = 1 h per wall hour).
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
