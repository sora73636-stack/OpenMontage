"""Visual composition budget gate (C1.2) — fail-closed visual share verification.

Verifies that the visual budget of a storyboard/EDL complies with the V13
targets (VIDEO_BUILD_TASK_V13.md S1.2), measured by *screen duration* of
scenes, not by file count:

  * NASA/ESA archival (REAL_ARCHIVE)            : 40–50%
  * Original diagrams / data / maps (PIL etc.)   : 30–40%
    (DATA_VISUALIZATION + SCIENTIFIC_DIAGRAM)
  * AI reconstructions                            : 0–15%
    (SCIENTIFIC_RECONSTRUCTION + HYPOTHETICAL_RECONSTRUCTION + ARTISTIC_METAPHOR)

Categories are mutually exclusive: every scene maps to exactly one category.
A scene with an unknown visual_class (or missing duration) blocks the gate.

Usage:
    from lib.visual_composition import check_visual_budget
    report = check_visual_budget(scenes)   # scenes: list of dicts with
                                           #   visual_class, time_in/time_out
                                           #   (or start_frame/end_frame + fps)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from lib.storyboard import VISUAL_CLASSES

# ---------------------------------------------------------------------------
# Budget categories — mutually exclusive.
# ---------------------------------------------------------------------------

ARCHIVAL = "archival"            # REAL_ARCHIVE  (NASA/JPL/ESA archive)
ORIGINAL_DIAGRAM = "original_diagram"  # DATA_VISUALIZATION + SCIENTIFIC_DIAGRAM
AI_RECONSTRUCTION = "ai_reconstruction"  # SCIENTIFIC_RECONSTRUCTION +
                                         # HYPOTHETICAL_RECONSTRUCTION +
                                         # ARTISTIC_METAPHOR
UNKNOWN = "unknown"

_CATEGORY_OF_CLASS: Mapping[str, str] = {
    "REAL_ARCHIVE": ARCHIVAL,
    "DATA_VISUALIZATION": ORIGINAL_DIAGRAM,
    "SCIENTIFIC_DIAGRAM": ORIGINAL_DIAGRAM,
    "SCIENTIFIC_RECONSTRUCTION": AI_RECONSTRUCTION,
    "HYPOTHETICAL_RECONSTRUCTION": AI_RECONSTRUCTION,
    "ARTISTIC_METAPHOR": AI_RECONSTRUCTION,
    # Legacy alias used by the V12/V13 pilot storyboard: existing AI frames
    # that were generated in a previous pilot run (not newly generated in V13).
    # They count toward the AI share; they are NOT newly generated.
    "existing_ai_reconstruction": AI_RECONSTRUCTION,
}

# Target shares (fraction of total duration), per V13 S1.2.
TARGET_SHARES: Mapping[str, tuple[float, float]] = {
    ARCHIVAL: (0.40, 0.50),
    ORIGINAL_DIAGRAM: (0.30, 0.40),
    AI_RECONSTRUCTION: (0.00, 0.15),
}

CATEGORY_LABELS: Mapping[str, str] = {
    ARCHIVAL: "NASA/ESA archival",
    ORIGINAL_DIAGRAM: "original diagrams/data/maps (PIL etc.)",
    AI_RECONSTRUCTION: "AI reconstructions",
}


def category_for_visual_class(visual_class: str | None) -> str:
    """Map a ``visual_class`` to its mutually exclusive budget category.

    Returns ``UNKNOWN`` for any class not in ``VISUAL_CLASSES`` — including
    ``None`` and legacy strings such as ``"existing_ai_reconstruction"``.
    """
    if visual_class is None:
        return UNKNOWN
    return _CATEGORY_OF_CLASS.get(visual_class, UNKNOWN)


def _scene_duration_seconds(scene: Mapping[str, Any], fps: float = 30.0) -> float | None:
    """Duration of one scene in seconds.

    Prefers explicit ``time_in``/``time_out`` (seconds). Falls back to
    ``start_frame``/``end_frame`` converted with ``fps``. Returns ``None``
    when no usable timing information is present.
    """
    try:
        if scene.get("time_in") is not None and scene.get("time_out") is not None:
            return float(scene["time_out"]) - float(scene["time_in"])
    except (TypeError, ValueError):
        return None
    start = scene.get("start_frame")
    end = scene.get("end_frame")
    if start is not None and end is not None and end > start:
        return (int(end) - int(start)) / fps
    return None


@dataclass
class VisualShare:
    category: str
    label: str
    duration_s: float
    share: float
    target_min: float
    target_max: float
    scene_count: int
    within_target: bool


@dataclass
class VisualCompositionReport:
    """Result of the visual composition budget check."""

    total_duration_s: float
    scene_count: int
    shares: list[VisualShare] = field(default_factory=list)
    unknown_scenes: list[str] = field(default_factory=list)
    status: str = "NOT_RUN"  # PASS | WARNING | FAIL | BLOCKED
    problems: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_duration_s": self.total_duration_s,
            "scene_count": self.scene_count,
            "shares": [
                {
                    "category": s.category,
                    "label": s.label,
                    "duration_s": s.duration_s,
                    "share": round(s.share, 4),
                    "share_percent": round(s.share * 100, 2),
                    "target_min": s.target_min,
                    "target_max": s.target_max,
                    "target_min_percent": round(s.target_min * 100, 1),
                    "target_max_percent": round(s.target_max * 100, 1),
                    "scene_count": s.scene_count,
                    "within_target": s.within_target,
                }
                for s in self.shares
            ],
            "unknown_scenes": list(self.unknown_scenes),
            "status": self.status,
            "problems": list(self.problems),
        }


def check_visual_budget(
    scenes: list[Mapping[str, Any]],
    *,
    fps: float = 30.0,
) -> VisualCompositionReport:
    """Verify visual budget shares against the V13 C1.2 targets.

    Fail-closed: empty input, missing durations, or unknown visual classes
    produce ``BLOCKED``/``FAIL``, never ``PASS``.
    """
    report = VisualCompositionReport(total_duration_s=0.0, scene_count=len(scenes))

    if not scenes:
        report.status = "BLOCKED"
        report.problems.append("no scenes provided — cannot compute visual shares")
        return report

    # Classify every scene; unknown classes block immediately.
    category_durations: dict[str, float] = {ARCHIVAL: 0.0, ORIGINAL_DIAGRAM: 0.0, AI_RECONSTRUCTION: 0.0}
    category_counts: dict[str, int] = {ARCHIVAL: 0, ORIGINAL_DIAGRAM: 0, AI_RECONSTRUCTION: 0}
    total_duration = 0.0

    for scene in scenes:
        scene_id = str(scene.get("scene_id", "?"))
        visual_class = scene.get("visual_class")
        category = category_for_visual_class(visual_class)
        if category == UNKNOWN:
            report.unknown_scenes.append(scene_id)
            continue
        dur = _scene_duration_seconds(scene, fps=fps)
        if dur is None or dur <= 0:
            report.unknown_scenes.append(scene_id)
            report.problems.append(
                f"{scene_id}: missing or non-positive duration "
                f"(visual_class={visual_class!r})"
            )
            continue
        category_durations[category] += dur
        category_counts[category] += 1
        total_duration += dur

    if report.unknown_scenes:
        report.status = "BLOCKED"
        report.total_duration_s = total_duration
        report.problems.append(
            f"{len(report.unknown_scenes)} scene(s) have unknown visual_class "
            f"or missing duration: {report.unknown_scenes[:5]}"
        )
        # Still compute shares for the known scenes so the report is useful,
        # but keep status BLOCKED.
        report.scene_count = len(scenes)

    report.total_duration_s = total_duration

    for category in (ARCHIVAL, ORIGINAL_DIAGRAM, AI_RECONSTRUCTION):
        dur = category_durations[category]
        share = dur / total_duration if total_duration > 0 else 0.0
        t_min, t_max = TARGET_SHARES[category]
        within = t_min <= share <= t_max
        report.shares.append(
            VisualShare(
                category=category,
                label=CATEGORY_LABELS[category],
                duration_s=round(dur, 3),
                share=round(share, 6),
                target_min=t_min,
                target_max=t_max,
                scene_count=category_counts[category],
                within_target=within,
            )
        )

    # Final verdict.
    if report.unknown_scenes:
        report.status = "BLOCKED"
    elif total_duration <= 0:
        report.status = "FAIL"
        report.problems.append("total duration is zero — no valid scene timing")
    elif not all(s.within_target for s in report.shares):
        problems = []
        for s in report.shares:
            if not s.within_target:
                problems.append(
                    f"{s.label}: {s.share*100:.1f}% not in "
                    f"{s.target_min*100:.0f}–{s.target_max*100:.0f}%"
                )
        report.status = "FAIL"
        report.problems.extend(problems)
    else:
        report.status = "PASS"

    return report


def gate_decision(report: VisualCompositionReport) -> dict[str, Any]:
    """Convert a :class:`VisualCompositionReport` into a release-gate check dict.

    Suitable for inclusion as a REQUIRED check in a QCReport.
    """
    return {
        "check_id": "visual_composition_budget",
        "category": "visual",
        "status": report.status,
        "evidence": "; ".join(report.problems)
        if report.problems
        else f"visual budget OK: " + ", ".join(
            f"{s.label} {s.share_percent:.1f}% (target "
            f"{s.target_min_percent:.0f}–{s.target_max_percent:.0f}%)"
            for s in report.shares
        ),
        "measured_value": report.to_dict(),
        "blocking": True,
    }
