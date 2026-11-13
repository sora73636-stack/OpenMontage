| Component | License | Runtime | dtype | Peak VRAM | Time | Log |
|---|---|---|---|---|---|---|
| LTX-Video 2B v0.9.5 | PASS (Open RAIL-M) | PASS | FP16 | 11033 MiB alloc / 11050 reserved | 62.47 s generation (49 frames) | p0-ltx/v3/ltx_logs.txt |
| FLUX.2 klein 4B | PASS (Apache-2.0) | PASS | FP16 | 7936 MiB alloc / 7948 reserved | 23.6 / 21.4 / 21.1 s per image; 66.0 s for 3 images | p0-flux/v2/flux_logs.txt |
| CosyVoice 3 | CONDITIONAL PASS (model-card metadata) | PASS | FP32 | 3589.6 MiB alloc / 4264 reserved | 594.76 s generation / 602.28 s audio (RTF 0.988) | p0-cosy/v10/cosy_logs.txt |
| Practical-RIFE 4.25 | PASS (MIT) | BLOCKED | — | — | no inference (CANCEL_ACKNOWLEDGED at ~90 s, v1/v2) | p0-rife/v2/openmontage-p0-practical-rife-4-25.log |
| Real-ESRGAN x4plus | FAIL (weight license not explicit) | PASS | FP32 | 1041 MiB (nvidia-smi) | 16.6 s / 10 images | p0-esrgan/v2/esrgan_logs.txt |
