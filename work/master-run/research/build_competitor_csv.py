"""Build COMPETITOR_VIDEO_AUDIT.csv for the 10of10 requirement.

20 videos: 15 general science (public metadata) + 5 biology/evolution
(public metadata from InnerTube/oEmbed). No frames, audio or transcripts were
retrieved: YouTube player returns LOGIN_REQUIRED. Every unobserved field is
labelled NOT_ACCESSIBLE; inferred fields are labelled INFERRED.
"""

import csv
import json
from pathlib import Path

OUT = Path("/workspaces/OpenMontage/docs/research")
base = json.loads(Path("/workspaces/OpenMontage/work/master-run/research/competitor_final15.json").read_text())

BIO = [
    {"channel": "Veritasium", "title": "The Most Controversial Idea In Biology",
     "url": "https://www.youtube.com/watch?v=XX7PdJIGiCw", "duration_s": 1730,
     "views": 9209734, "published": "2025-12-25 (per source doc)",
     "chapters": "00:00 hook; 02:51 origin of life; 07:15 gene mutation; 08:01 simulating evolution; 13:25 natural selection; 16:39 inheritance; 19:40 kin selection; 22:04 selfish gene; 25:35 conclusion",
     "experts": "Jack Szostak, John Sutherland, Joanna Masel, Gerald Joyce",
     "audience": "biology/evolution documentary; 25-30 min chapters"},
    {"channel": "TierZoo", "title": "The Mammal Tier List",
     "url": "https://www.youtube.com/watch?v=7UXmUJZIH7c", "duration_s": 2728,
     "views": 3090811, "published": "2026-05-09 (per source doc)",
     "chapters": "NOT_ACCESSIBLE", "experts": "NOT_ACCESSIBLE",
     "audience": "biology/evolution with game metaphor; 45 min"},
    {"channel": "PBS Eons", "title": "When Mammals and Reptiles Split",
     "url": "https://www.youtube.com/watch?v=RY8mipBWjyw", "duration_s": 1597,
     "views": 887545, "published": "not captured",
     "chapters": "NOT_ACCESSIBLE", "experts": "NOT_ACCESSIBLE",
     "audience": "paleontology/evolution documentary; 26 min"},
    {"channel": "PBS Eons", "title": "How An Ancient Ocean Became A Texas Desert",
     "url": "https://www.youtube.com/watch?v=yGf78wc6jIU", "duration_s": 1566,
     "views": 181157, "published": "not captured",
     "chapters": "NOT_ACCESSIBLE", "experts": "NOT_ACCESSIBLE",
     "audience": "paleontology/evolution documentary; 26 min"},
    {"channel": "Kaoru GreenEmerald", "title": "The Whole History of the Earth and Life 【Finished Edition】",
     "url": "https://www.youtube.com/watch?v=NQ4CUw9RcuA", "duration_s": 3945,
     "views": 18516615, "published": "not captured",
     "chapters": "NOT_ACCESSIBLE", "experts": "NOT_ACCESSIBLE",
     "audience": "long-form timeline; 65 min"},
]

NA = "NOT_ACCESSIBLE"
rows = []
for v in base:
    rows.append({
        "channel": v["channel"], "video_title": v["title"], "url": v["url"],
        "published": v.get("published", "not captured"), "duration_s": v["duration_s"],
        "views": v["views"], "likes": NA, "metric_date": "2026-11-11",
        "audience_subgenre": "general science explainer",
        "title_promise": v["title"], "thumbnail_promise": NA,
        "first_frame_observed": NA, "first_5s": NA, "first_15s": NA, "first_30s": NA,
        "hook_type": v["hook_type_inferred"], "promise_clear_at_s": NA,
        "chapter_structure": NA, "narrative_progression": "INFERRED: premise -> anomaly -> explanation -> payoff",
        "narration_style": NA, "visual_sources": "INFERRED from channel format",
        "visual_language": "INFERRED", "motion_types": "INFERRED",
        "semantic_change_freq": NA, "music_ambience_sfx": NA,
        "captions_labels": NA, "thumbnail_analysis": NA, "sources_experts": NA,
        "adaptable_principle": "specific visual claim; one idea per beat",
        "cannot_copy_rights": "do not copy footage, brand, thumbnails, music or exact scripts",
        "strengths": "INFERRED: clear premise", "weaknesses": "INFERRED: not frame-verified",
        "confidence": "low", "evidence_class": "PUBLIC_METADATA",
    })
for v in BIO:
    rows.append({
        "channel": v["channel"], "video_title": v["title"], "url": v["url"],
        "published": v["published"], "duration_s": v["duration_s"], "views": v["views"],
        "likes": NA, "metric_date": "2026-11-11",
        "audience_subgenre": v["audience"], "title_promise": v["title"],
        "thumbnail_promise": NA, "first_frame_observed": NA, "first_5s": NA,
        "first_15s": NA, "first_30s": NA,
        "hook_type": "INFERRED: contradiction/scale" if v["channel"] != "TierZoo" else "INFERRED: game metaphor",
        "promise_clear_at_s": NA, "chapter_structure": v["chapters"],
        "narrative_progression": "INFERRED: world -> species -> change -> crisis -> payoff",
        "narration_style": NA, "visual_sources": "INFERRED: wildlife/archival/2D/3D",
        "visual_language": "INFERRED", "motion_types": "INFERRED",
        "semantic_change_freq": NA, "music_ambience_sfx": NA,
        "captions_labels": NA, "thumbnail_analysis": NA,
        "sources_experts": v["experts"],
        "adaptable_principle": "chapter-based long-form; taxonomy; timeline",
        "cannot_copy_rights": "do not copy footage, brand, thumbnails, music or exact scripts",
        "strengths": "INFERRED: strong evolutionary narrative",
        "weaknesses": "INFERRED: not frame-verified",
        "confidence": "low", "evidence_class": "PUBLIC_METADATA",
    })

cols = list(rows[0].keys())
with open(OUT / "COMPETITOR_VIDEO_AUDIT.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print("rows", len(rows), "biology", len(BIO))