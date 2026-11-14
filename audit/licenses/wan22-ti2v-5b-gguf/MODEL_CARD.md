# Model card — QuantStack/Wan2.2-TI2V-5B-GGUF

**Source URL:** https://huggingface.co/QuantStack/Wan2.2-TI2V-5B-GGUF
**Retrieved:** 2026-11-14 (UTC)
**Revision (commit sha):** 57437632ddd08bdcbd1508c866aa22e126ed51d2
**License field (cardData):** apache-2.0
**Gated:** false
**Base model:** Wan-AI/Wan2.2-TI2V-5B (https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B)
**Quantization:** GGUF (multiple Q levels; this audit uses Q4_K_M, 3.43 GB)
**Extra component in repo:** VAE/Wan2.2_VAE.safetensors (1.41 GB)

## Raw README.md (verbatim)

```markdown
---
license: apache-2.0
base_model:
- Wan-AI/Wan2.2-TI2V-5B
library_name: gguf
pipeline_tag: text-to-video
language:
- en
- zh
tags:
- ti2v
---


This GGUF file is a direct conversion of [Wan-AI/Wan2.2-TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B)

Since this is a quantized model, all original licensing terms and usage restrictions remain in effect.

**Usage**

The model can be used with the ComfyUI custom node [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) by [city96](https://huggingface.co/city96)

Place model files in `ComfyUI/models/unet` see the GitHub readme for further installation instructions.
```

## License statement observed on the model card (rendered page)

"License: apache-2.0" (badge on the model page). The cardData JSON from the HF API reports `"license": "apache-2.0"`.

## Note on license scope

The card explicitly states: "Since this is a quantized model, all original licensing terms and usage restrictions remain in effect." The base model Wan-AI/Wan2.2-TI2V-5B is also licensed apache-2.0. There is NO separate LICENSE file in the QuantStack repo and NO additional terms beyond the Apache 2.0 reference. The GGUF conversion itself does not add restrictions.

## Files present in the repo (relevant)

- Wan2.2-TI2V-5B-Q4_K_M.gguf  (3,433,116,000 bytes)  -- used in this audit
- VAE/Wan2.2_VAE.safetensors  (1,409,400,960 bytes)
- (text encoder UMT5 is NOT in this repo; sourced from Wan-AI/Wan2.2-TI2V-5B-Diffusers, subfolder text_encoder, apache-2.0)

## License basis

license_basis = "model_card_metadata" (HF cardData license field = apache-2.0), cross-checked against the base model Wan-AI/Wan2.2-TI2V-5B (also apache-2.0). No separate LICENSE file exists in the QuantStack repo, so this is a CONDITIONAL PASS per audit convention (L6): the license is known from model-card metadata, not from a verbatim license text file. The card adds no extra terms.
