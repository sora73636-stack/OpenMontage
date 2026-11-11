"""Select the final 15-video competitor set and compute public-data statistics."""

import json
import re
import statistics
from pathlib import Path

OUT = Path("/workspaces/OpenMontage/work/master-run/research")
cands = json.loads((OUT / "competitor_candidates.json").read_text())

PICKS = [
    ("Mark Rober", "Carnival Scam Science"),
    ("Veritasium", "The Most Misunderstood Concept in Physics"),
    ("Kurzgesagt", "The Black Hole Bomb"),
    ("Steve Mould", "NASA tested my chain theory"),
    ("NOVA PBS", "Atomic Clocks Prove Reality"),
    ("Physics Girl", "Crazy pool vortex"),
    ("TED-Ed", "three-body problem"),
    ("Real Engineering", "The Insane Engineering of the X-15"),
    ("NASA Jet Propulsion", "7 Minutes of Terror"),
    ("PBS Space Time", "Black Hole Star"),
    ("SciShow", "First Ancient City"),
    ("Numberphile", "Equally sharing a cake"),
    ("Anton Petrov", "Only Intelligent Life"),
    ("BBC Earth Science", "Giant Space Magnet"),
    ("European Space Agency", "cosmic views with James Webb"),
]


def find(channel_part, title_part):
    matches = [v for v in cands if channel_part.lower() in v["channel"].lower()
               and title_part.lower() in v["title"].lower()]
    if not matches:
        raise SystemExit(f"NOT FOUND: {channel_part} / {title_part}")
    matches.sort(key=lambda x: -x["views"])
    return matches[0]


selected = []
for i, (ch, ti) in enumerate(PICKS, 1):
    v = dict(find(ch, ti))
    v["rank"] = i
    v["hook_type_inferred"] = (
        "question" if re.match(r"^(why|how|what|is|are|do|does|can|could|would)", v["title"].lower())
        else "number/list" if re.search(r"\d", v["title"])
        else "curiosity-gap" if ":" in v["title"] or "|" in v["title"] or "..." in v["title"]
        else "declarative"
    )
    selected.append(v)

(OUT / "competitor_final15.json").write_text(json.dumps(selected, indent=2))
durs = [v["duration_s"] for v in selected]
views = [v["views"] for v in selected]
print("n", len(selected))
print("duration min/median/max", min(durs), statistics.median(durs), max(durs))
print("views min/median/max", min(views), statistics.median(views), max(views))
from collections import Counter
print("hook types", Counter(v["hook_type_inferred"] for v in selected))
for v in selected:
    print(v["rank"], v["channel"], v["duration_s"], v["views"], v["hook_type_inferred"], v["title"][:70])