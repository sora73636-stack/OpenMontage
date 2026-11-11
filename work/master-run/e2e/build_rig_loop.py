"""Render animated Stickman Rig-1 loops (existing rig only) for the demo overlay."""

import json
import math
import subprocess
from pathlib import Path

import cairosvg
from PIL import Image

from lib.stickman_pose_library import get_pose, pose_to_frame
from lib.stickman_rig import RigProfile, emit_svg

ROOT = Path("/workspaces/OpenMontage/work/master-run/e2e")
RIG = ROOT / "rig"
RIG.mkdir(parents=True, exist_ok=True)
profile = RigProfile(rig_id="RIG-1", character_id="om-researcher")
FRAMES = 24
FPS = 12

POSES = {
    "idle": ("idle", 0.10),
    "explaining": ("explaining", 0.18),
    "pointing": ("pointing", 0.08),
    "thinking": ("thinking", 0.06),
    "examining": ("examining", 0.05),
}

manifest = []
for name, (pose_id, amp) in POSES.items():
    pose = get_pose(pose_id)
    outdir = RIG / name
    outdir.mkdir(parents=True, exist_ok=True)
    for i in range(FRAMES):
        phase = 2 * math.pi * i / FRAMES
        frame = pose_to_frame(pose_id, expression_id="neutral", view="front")
        frame.signature_detail_present = True
        base = dict(pose.get("joint_angles", {}))
        # gentle, motivated motion: right arm and head only
        base["arm_r_shoulder"] = base.get("arm_r_shoulder", 0.0) + amp * math.sin(phase)
        base["head_tilt"] = base.get("head_tilt", 0.0) + 0.05 * math.sin(phase + 1.0)
        frame.overrides = {"arm_r_shoulder": base["arm_r_shoulder"],
                           "head_tilt": base["head_tilt"]}
        svg = emit_svg(frame, pose, profile, canvas_w=300, canvas_h=420, scale=52)
        png = outdir / f"frame_{i:02d}.png"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png), output_width=300, output_height=420)
    # qtrle .mov with alpha
    mov = RIG / f"{name}.mov"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(outdir / "frame_%02d.png"),
        "-c:v", "qtrle", "-pix_fmt", "argb", str(mov)
    ], check=True, capture_output=True)
    # verify alpha
    im = Image.open(outdir / "frame_00.png").convert("RGBA")
    alpha = im.getchannel("A")
    nonzero = sum(1 for p in alpha.getdata() if p > 0)
    manifest.append({"pose": name, "mov": str(mov), "frames": FRAMES, "fps": FPS,
                     "alpha_pixels": nonzero})
    print(name, "alpha pixels", nonzero)

json.dump(manifest, open(ROOT / "rig_manifest.json", "w"), indent=2)
print("wrote", len(manifest), "loops")