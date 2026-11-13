#!/usr/bin/env python3
"""Phase 3 license/provenance collector (CPU/network only, no GPU).

Resolves, for every approved component:
  * canonical code repository + immutable revision (git ls-remote / HF API)
  * code LICENSE text at that revision
  * official model card / README at that revision
  * model repo metadata (HF cardData.license where present)
  * SHA256 for every saved file

No weights are downloaded in Stage A; weight SHA256 is recorded as
NOT COLLECTED (Stage B/C downloads them). Nothing is guessed: when a source
cannot be resolved or fetched, the component is marked BLOCKED with the exact
HTTP error.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit/licenses"
LOG = ROOT / "audit/logs/codespaces/license_collection.log"
UA = "openmontage-audit/1.0 (license-provenance; +https://github.com/OpenMontageInc/OpenMontage)"


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{utc()} {msg}\n")
    print(msg)


def http(url: str, timeout: int = 45, accept_json: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json" if accept_json else "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()[:2000], dict(exc.headers or {})
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}".encode(), {}


def save(path: Path, data: bytes) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": str(path.relative_to(ROOT)), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def gh_head(repo: str, ref: str = "HEAD") -> dict:
    out = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{repo}", ref],
        capture_output=True, text=True, timeout=90,
    )
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    if out.returncode != 0 or not lines:
        return {"ok": False, "error": (out.stderr or "no ref").strip()[:500]}
    sha, name = lines[0].split("\t", 1)
    return {"ok": True, "sha": sha, "ref": name}


def gh_tags(repo: str, wanted: str) -> dict:
    out = subprocess.run(
        ["git", "ls-remote", "--tags", f"https://github.com/{repo}"],
        capture_output=True, text=True, timeout=90,
    )
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1].endswith(wanted):
            return {"ok": True, "sha": parts[0], "ref": parts[1]}
    return {"ok": False, "error": f"tag {wanted} not found"}


def fetch_text_sources(base_url: str, revision: str, names: list[str]) -> dict:
    found = {}
    for name in names:
        url = f"{base_url}/{revision}/{name}"
        status, body, _ = http(url)
        if status == 200 and body:
            found[name] = body
            break
    return found


def hf_model(model_id: str) -> dict:
    status, body, _ = http(f"https://huggingface.co/api/models/{model_id}", accept_json=True)
    if status != 200:
        return {"ok": False, "http": status, "error": body[:400].decode("utf-8", "replace")}
    data = json.loads(body)
    return {
        "ok": True,
        "sha": data.get("sha"),
        "license": (data.get("cardData") or {}).get("license"),
        "cardData": data.get("cardData") or {},
        "lastModified": data.get("lastModified"),
        "gated": data.get("gated"),
    }


def hf_files(model_id: str, revision: str, names: list[str]) -> dict:
    out = {}
    for name in names:
        status, body, _ = http(f"https://huggingface.co/{model_id}/raw/{revision}/{name}")
        if status == 200 and body:
            out[name] = body
    return out


def component_record(
    name: str,
    priority: str,
    code: dict | None,
    weights: dict | None,
    extra: dict | None = None,
) -> dict:
    return {
        "component": name,
        "priority": priority,
        "retrieved_utc": utc(),
        "code": code or {"type": "NONE", "note": "no canonical code repository resolved"},
        "weights": weights or {"type": "NONE", "note": "no model repository resolved"},
        "extra": extra or {},
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    log("license collection start")
    records = {}

    # --- GitHub code repos -------------------------------------------------
    gh_components = {
        "cosyvoice3": ("FunAudioLLM/CosyVoice", None),
        "ltx-video-2b-0.9.5": ("Lightricks/LTX-Video", None),
        "practical-rife-4.25": ("hzwer/Practical-RIFE", None),
        "real-esrgan-x4plus": ("xinntao/Real-ESRGAN", None),
        "kokoro-82m": ("hexgrad/kokoro", None),
        "whisper-large-v3-turbo": ("openai/whisper", None),
        "parakeet-tdt-0.6b-v3": ("NVIDIA/NeMo", None),
        "deepfilternet3": ("Rikorose/DeepFilterNet", None),
        "wan2.1-t2v-1.3b": ("Wan-Video/Wan2.1", None),
        "depth-anything-v2-small": ("LiheYoung/Depth-Anything", None),
        "video-depth-anything-small": ("DepthAnything/Video-Depth-Anything", None),
        "sdxl-base-1.0": ("Stability-AI/generative-models", None),
        "flux2-klein-4b": ("black-forest-labs/flux2", None),
        "depthflow": ("BrokenSource/DepthFlow", None),
        "manim-ce-0.22.1": ("ManimCommunity/manim", "v0.22.1"),
        "ffmpeg-6.1.1": ("FFmpeg/FFmpeg", "n6.1.1"),
    }

    for name, (repo, tag) in gh_components.items():
        if tag:
            rev = gh_tags(repo, tag)
        else:
            rev = gh_head(repo)
        if not rev.get("ok"):
            log(f"{name}: BLOCKED resolving revision ({rev.get('error')})")
            records[name] = component_record(name, "P?", {"type": "github", "url": f"https://github.com/{repo}", "resolved": False, "error": rev.get("error")}, None)
            continue

        sha = rev["sha"]
        comp_dir = OUT / name
        texts = fetch_text_sources(
            f"https://raw.githubusercontent.com/{repo}",
            sha,
            ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md", "LICENSE-CODE"],
        )
        saved_license = None
        if texts:
            lname, ldata = next(iter(texts.items()))
            saved_license = save(comp_dir / "LICENSE-code.txt", ldata)
        readme = fetch_text_sources(
            f"https://raw.githubusercontent.com/{repo}",
            sha,
            ["README.md", "README.rst", "MODEL_CARD.md"],
        )
        saved_readme = None
        if readme:
            rname, rdata = next(iter(readme.items()))
            saved_readme = save(comp_dir / "MODEL_CARD.md", rdata)

        records[name] = component_record(
            name,
            "P?",
            {
                "type": "github",
                "url": f"https://github.com/{repo}",
                "revision": sha,
                "ref": rev.get("ref"),
                "license_file": saved_license,
                "readme_file": saved_readme,
                "license_fetch_status": "OK" if texts else "NO LICENSE FILE AT TOP LEVEL",
            },
            None,
        )
        log(f"{name}: github {repo}@{sha[:12]} license={'OK' if saved_license else 'MISSING'}")

    # --- Hugging Face model repos -----------------------------------------
    hf_components = {
        "cosyvoice3": "FunAudioLLM/Fun-CosyVoice3-0.5B-2512",
        "ltx-video-2b-0.9.5": "Lightricks/LTX-Video-0.9.5",
        "flux2-klein-4b": "black-forest-labs/FLUX.2-klein-4B",
        "kokoro-82m": "hexgrad/Kokoro-82M",
        "whisper-large-v3-turbo": "openai/whisper-large-v3-turbo",
        "parakeet-tdt-0.6b-v3": "nvidia/parakeet-tdt-0.6b-v3",
        "wan2.1-t2v-1.3b": "Wan-AI/Wan2.1-T2V-1.3B",
        "depth-anything-v2-small": "depth-anything/Depth-Anything-V2-Small",
        "video-depth-anything-small": "depth-anything/Video-Depth-Anything-Small",
        "sdxl-base-1.0": "stabilityai/stable-diffusion-xl-base-1.0",
    }

    for name, model_id in hf_components.items():
        meta = hf_model(model_id)
        if not meta.get("ok"):
            log(f"{name}: BLOCKED HF metadata {meta.get('http')} {meta.get('error')}")
            rec = records.setdefault(name, component_record(name, "P?", None, None))
            rec["weights"] = {"type": "huggingface", "url": f"https://huggingface.co/{model_id}", "resolved": False, "http": meta.get("http"), "error": meta.get("error")}
            continue

        rev = meta["sha"]
        comp_dir = OUT / name
        files = hf_files(
            model_id,
            rev,
            ["README.md", "LICENSE", "LICENSE.txt", "NOTICE", "MODEL_CARD.md"],
        )
        saved = []
        for fname, data in files.items():
            target = "MODEL_CARD.md" if fname.upper().startswith("README") else f"{fname}"
            saved.append(save(comp_dir / target, data))

        rec = records.setdefault(name, component_record(name, "P?", None, None))
        rec["weights"] = {
            "type": "huggingface",
            "url": f"https://huggingface.co/{model_id}",
            "revision": rev,
            "api_license": meta.get("license"),
            "cardData_license": (meta.get("cardData") or {}).get("license"),
            "gated": meta.get("gated"),
            "files": saved,
            "weights_downloaded": False,
            "weight_sha256": None,
        }
        log(f"{name}: hf {model_id}@{rev[:12]} license={meta.get('license')} files={len(saved)}")

    # --- special checks ----------------------------------------------------
    extra = {}

    # A. DeepFilterNet issue #697 and commit 7b14b89
    try:
        status, body, _ = http("https://api.github.com/repos/Rikorose/DeepFilterNet/issues/697", accept_json=True)
        issue = json.loads(body) if status == 200 else {"http": status, "body": body[:500].decode("utf-8", "replace")}
        extra["deepfilternet_issue_697"] = {
            "url": "https://github.com/Rikorose/DeepFilterNet/issues/697",
            "http": status,
            "title": issue.get("title"),
            "state": issue.get("state"),
            "body_sha256": hashlib.sha256(json.dumps(issue.get("body") or "").encode()).hexdigest(),
            "body_excerpt": (issue.get("body") or "")[:2000],
        }
        save(OUT / "deepfilternet3/ISSUE-697.json", json.dumps(issue, indent=2).encode())
    except Exception as exc:  # noqa: BLE001
        extra["deepfilternet_issue_697"] = {"error": f"{type(exc).__name__}: {exc}"}

    try:
        status, body, _ = http("https://api.github.com/repos/Rikorose/DeepFilterNet/commits/7b14b89", accept_json=True)
        commit = json.loads(body) if status == 200 else {"http": status}
        extra["deepfilternet_commit_7b14b89"] = {
            "url": "https://github.com/Rikorose/DeepFilterNet/commit/7b14b89",
            "http": status,
            "sha": commit.get("sha"),
            "message": (commit.get("commit") or {}).get("message", "")[:1000],
            "files": [f.get("filename") for f in (commit.get("files") or [])][:50],
        }
        save(OUT / "deepfilternet3/COMMIT-7b14b89.json", json.dumps(commit, indent=2).encode())
    except Exception as exc:  # noqa: BLE001
        extra["deepfilternet_commit_7b14b89"] = {"error": f"{type(exc).__name__}: {exc}"}

    # D. Real-ESRGAN release assets (exact weight file + any license statement)
    try:
        status, body, _ = http("https://api.github.com/repos/xinntao/Real-ESRGAN/releases", accept_json=True)
        releases = json.loads(body) if status == 200 else []
        assets = []
        for rel in releases if isinstance(releases, list) else []:
            for a in rel.get("assets", []):
                assets.append({"tag": rel.get("tag_name"), "name": a.get("name"), "url": a.get("browser_download_url"), "size": a.get("size")})
        extra["real_esrgan_release_assets"] = {"http": status, "assets": assets}
        save(OUT / "real-esrgan-x4plus/RELEASE_ASSETS.json", json.dumps(extra["real_esrgan_release_assets"], indent=2).encode())
    except Exception as exc:  # noqa: BLE001
        extra["real_esrgan_release_assets"] = {"error": f"{type(exc).__name__}: {exc}"}

    # E. Practical-RIFE release assets (4.25 archive)
    try:
        status, body, _ = http("https://api.github.com/repos/hzwer/Practical-RIFE/releases", accept_json=True)
        releases = json.loads(body) if status == 200 else []
        assets = []
        for rel in releases if isinstance(releases, list) else []:
            for a in rel.get("assets", []):
                assets.append({"tag": rel.get("tag_name"), "name": a.get("name"), "url": a.get("browser_download_url"), "size": a.get("size")})
        extra["practical_rife_release_assets"] = {"http": status, "assets": assets}
        save(OUT / "practical-rife-4.25/RELEASE_ASSETS.json", json.dumps(extra["practical_rife_release_assets"], indent=2).encode())
    except Exception as exc:  # noqa: BLE001
        extra["practical_rife_release_assets"] = {"error": f"{type(exc).__name__}: {exc}"}

    records.setdefault("deepfilternet3", component_record("deepfilternet3", "P1", None, None))["extra"].update(extra)
    records.setdefault("real-esrgan-x4plus", component_record("real-esrgan-x4plus", "P0", None, None))["extra"]["release_assets"] = extra.get("real_esrgan_release_assets")
    records.setdefault("practical-rife-4.25", component_record("practical-rife-4.25", "P0", None, None))["extra"]["release_assets"] = extra.get("practical_rife_release_assets")

    # F. music/SFX: no cleared assets in Stage A
    records["music-sfx"] = component_record(
        "music-sfx",
        "P2",
        {"type": "NONE", "note": "assets selected in Phase 8 (Stage D); none downloaded in Stage A"},
        None,
        {"status": "NOT TESTED", "reason": "no asset selected yet; Phase 8 requires cleared YouTube Audio Library / Sonniss GDC assets"},
    )
    records["cosyvoice3-reference-voice"] = component_record(
        "cosyvoice3-reference-voice",
        "P0",
        None,
        None,
        {"status": "BLOCKED", "reason": "no cleared reference recording available; Phase 6.5 requires user/CC0/CC-BY or approved synthetic voice"},
    )

    index = OUT / "INDEX.json"
    index.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    log(f"license collection done: {len(records)} records -> {index}")

    # per-component PROVENANCE.json + SHA256SUMS.txt
    for name, rec in records.items():
        comp_dir = OUT / name
        comp_dir.mkdir(parents=True, exist_ok=True)
        prov = {
            "component": name,
            "retrieved_utc": rec["retrieved_utc"],
            "code": rec.get("code"),
            "weights": rec.get("weights"),
            "extra": rec.get("extra"),
        }
        (comp_dir / "PROVENANCE.json").write_text(json.dumps(prov, indent=2, sort_keys=True), encoding="utf-8")
        sums = []
        for path in sorted(comp_dir.glob("*")):
            if path.is_file() and path.name not in ("PROVENANCE.json", "SHA256SUMS.txt"):
                sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
        (comp_dir / "SHA256SUMS.txt").write_text("\n".join(sums) + ("\n" if sums else ""), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:  # noqa: BLE001
        import traceback

        traceback.print_exc()
        log("license collection FAILED")
        raise SystemExit(1)