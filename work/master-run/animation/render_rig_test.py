"""Render Stickman Rig-1 poses to PNG and verify the signature lens.

Uses the existing rig (lib/stickman_rig.py) and pose library
(lib/stickman_pose_library.py) — no new renderer, no second rig.
"""

import os
import re
from pathlib import Path

import cairosvg
from PIL import Image

from lib.stickman_pose_library import get_pose, list_poses, pose_to_frame
from lib.stickman_rig import RigProfile, emit_svg, rig_cache_key

OUT = Path("/workspaces/OpenMontage/work/master-run/animation")
OUT.mkdir(parents=True, exist_ok=True)
profile = RigProfile(rig_id="RIG-1", character_id="om-researcher")
print("profile issues:", profile.validate())

poses = ["idle", "walking", "running", "pointing", "explaining", "thinking", "surprised", "examining"]
views = ["front", "three_quarter", "profile", "back"]
manifest = []
for pose_id in poses:
    pose = get_pose(pose_id)
    for view in views:
        frame = pose_to_frame(pose_id, view=view)
        frame.signature_detail_present = True
        svg = emit_svg(frame, pose, profile, canvas_w=360, canvas_h=520, scale=70)
        png = OUT / f"{pose_id}_{view}.png"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png), output_width=360, output_height=520)
        # signature detail check: accent-colored circle + handle line
        accent = profile.accent_color
        lens_ok = accent in svg and svg.count("<circle") >= 2
        manifest.append({
            "pose": pose_id, "view": view, "png": str(png),
            "svg_bytes": len(svg), "signature_lens": bool(lens_ok),
            "cache_key": rig_cache_key(frame, pose)[:16],
        })
print(f"rendered {len(manifest)} frames; lens present: {sum(m['signature_lens'] for m in manifest)}/{len(manifest)}")

# contact sheet 8 rows x 4 views
imgs = [(m, Image.open(m["png"]).convert("RGB")) for m in manifest]
w, h = 360, 520
sheet = Image.new("RGB", (w * 4, h * len(poses)), "white")
from PIL import ImageDraw
d = ImageDraw.Draw(sheet)
for i, (m, im) in enumerate(imgs):
    row = poses.index(m["pose"])
    col = views.index(m["view"])
    sheet.paste(im, (col * w, row * h))
    d.text((col * w + 8, row * h + 8), f"{m['pose']}/{m['view']}", fill="black")
sheet.save(OUT / "rig_contact_sheet.jpg", quality=90)
import json
json.dump({"profile": profile.to_dict(), "frames": manifest}, open(OUT / "rig_render_manifest.json", "w"), indent=2)
print("wrote", OUT / "rig_contact_sheet.jpg")