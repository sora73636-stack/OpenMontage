"""Regenerate subtitles with <=42 chars/line, max 2 lines (10of10 D2 house rule)."""

import json
import textwrap
from pathlib import Path

ROOT = Path("/workspaces/OpenMontage/work/master-run/e2e")
nar = json.loads((ROOT / "narration.json").read_text())


def ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


with open(ROOT / "subtitles.srt", "w") as f:
    for i, line in enumerate(nar["timeline"], 1):
        wrapped = textwrap.wrap(line["text"], width=42, max_lines=2, placeholder="")
        f.write(f"{i}\n{ts(line['start_s'])} --> {ts(line['end_s'])}\n" + "\n".join(wrapped) + "\n\n")
print("rewrote subtitles.srt")
maxlen = 0
for line in nar["timeline"]:
    for w in textwrap.wrap(line["text"], width=42):
        maxlen = max(maxlen, len(w))
print("max line length", maxlen)