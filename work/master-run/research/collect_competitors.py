"""Public YouTube metadata collection via InnerTube search (no API key, no download).

Evidence class: PUBLIC_METADATA only. No frames, audio, or transcripts are
retrieved — YouTube's player endpoint returns LOGIN_REQUIRED from this
environment. Structure/hook columns are explicitly labelled INFERRED.
"""

import json
import os
import re
import subprocess

OUT = "/workspaces/OpenMontage/work/master-run/research"
RAW = f"{OUT}/competitor_raw.json"
ALL = f"{OUT}/competitor_candidates.json"
os.makedirs(OUT, exist_ok=True)

QUERIES = [
    "Veritasium science video",
    "Kurzgesagt in a nutshell",
    "PBS Space Time",
    "Mark Rober science",
    "SciShow",
    "minutephysics",
    "Real Engineering",
    "Steve Mould science",
    "Physics Girl",
    "Anton Petrov space",
    "NASA Goddard science",
    "European Space Agency",
    "TED-Ed science",
    "Jet Propulsion Laboratory",
    "Numberphile",
    "NOVA PBS science documentary",
    "BBC Earth Science",
    "Science Channel documentary",
]

BAD_CHANNELS = {
    "Toys and Colors", "Progress - Science Documentaries", "Democracy Now!",
    "Marcello Ascani", "Fire of Learning", "WUFO - Science Documentaries",
    "Spark", "Real Civil Engineer", "KPBS Arts", "StarTalk",
}
BAD_TITLE = re.compile(
    r"\b(sleep|compilation|full episode|update from|q&a|live stream|trailer|review)\b",
    re.IGNORECASE,
)


def search(query):
    body = json.dumps({
        "context": {"client": {"clientName": "WEB", "clientVersion": "2.20240401.00.00", "hl": "en"}},
        "query": query,
    })
    p = subprocess.run([
        "curl", "-sS", "--max-time", "40", "-X", "POST",
        "https://www.youtube.com/youtubei/v1/search?prettyPrint=false",
        "-H", "Content-Type: application/json",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "-H", "Origin: https://www.youtube.com",
        "-d", body,
    ], capture_output=True, text=True, timeout=60)
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return {}


def parse_duration(s):
    parts = [int(x) for x in (s or "0:00").split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def parse_views(s):
    s = (s or "").upper().replace(",", "")
    m = re.search(r"([\d.]+)\s*([KMB]?)", s)
    if not m:
        return 0
    return int(float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[m.group(2)])


def walk(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            yield obj[key]
        for v in obj.values():
            yield from walk(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v, key)


candidates = {}
for q in QUERIES:
    data = search(q)
    n = 0
    for v in walk(data, "videoRenderer"):
        vid = v.get("videoId")
        if not vid or vid in candidates:
            continue
        title = "".join(r.get("text", "") for r in v.get("title", {}).get("runs", []))
        channel = "".join(r.get("text", "") for r in v.get("ownerText", {}).get("runs", []))
        dur = parse_duration(v.get("lengthText", {}).get("simpleText"))
        views = parse_views(v.get("viewCountText", {}).get("simpleText"))
        if dur < 240 or views < 500_000:
            continue
        if channel in BAD_CHANNELS or BAD_TITLE.search(title):
            continue
        candidates[vid] = {
            "id": vid, "title": title, "channel": channel,
            "duration_s": dur, "views": views,
            "published": v.get("publishedTimeText", {}).get("simpleText", ""),
            "description": "".join(r.get("text", "") for r in v.get("descriptionSnippet", {}).get("runs", [])),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "query": q, "evidence_class": "PUBLIC_METADATA",
        }
        n += 1
    print(f"{q}: +{n} (total {len(candidates)})", flush=True)

with open(ALL, "w") as f:
    json.dump(list(candidates.values()), f, indent=2)

# one per channel, strongest first; prefer 8-30 min explainers
by_channel = {}
for v in candidates.values():
    by_channel.setdefault(v["channel"], []).append(v)

selected = []
for ch in sorted(by_channel, key=lambda c: -max(x["views"] for x in by_channel[c])):
    vids = sorted(by_channel[ch], key=lambda x: (-(300 <= x["duration_s"] <= 1900), -x["views"]))
    selected.append(vids[0])
    if len(selected) == 15:
        break
selected = selected[:15]
for i, v in enumerate(selected, 1):
    v["rank"] = i
    v["hook_type_inferred"] = (
        "question" if re.match(r"^(why|how|what|is|are|do|does|can|could|would)", v["title"].lower())
        else "number/list" if re.search(r"\d", v["title"])
        else "curiosity-gap" if ":" in v["title"] or "|" in v["title"]
        else "declarative"
    )

with open(RAW, "w") as f:
    json.dump(selected, f, indent=2)
for v in selected:
    print(f"[{v['rank']:2}] {v['channel'][:24]:24} | {v['duration_s']:4}s | {v['views']:>10} | {v['title'][:72]}", flush=True)
print(f"WROTE {RAW} ({len(selected)})")