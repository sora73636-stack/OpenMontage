"""Regression tests for lib.visual_composition (V13 C1.2 visual budget gate).

The visual budget is measured by scene *duration*, not file count. Categories
are mutually exclusive: every scene maps to exactly one of archival /
original_diagram / ai_reconstruction. Unknown visual_class or missing
duration blocks the gate (fail-closed).

Legacy alias: ``existing_ai_reconstruction`` (used by the V12/V13 pilot
storyboard for existing AI frames) maps to ``ai_reconstruction`` and counts
toward the AI share. It is NOT treated as unknown.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from lib.visual_composition import (  # noqa: E402
    ARCHIVAL,
    AI_RECONSTRUCTION,
    ORIGINAL_DIAGRAM,
    UNKNOWN,
    category_for_visual_class,
    check_visual_budget,
    gate_decision,
)
from lib.release_gate import ReleaseGate  # noqa: E402


def _scene(scene_id: str, visual_class: str, start_s: float, end_s: float) -> dict:
    return {
        "scene_id": scene_id,
        "visual_class": visual_class,
        "time_in": start_s,
        "time_out": end_s,
    }


# ---------------------------------------------------------------------------
# category_for_visual_class
# ---------------------------------------------------------------------------


def test_category_mapping_is_mutually_exclusive() -> None:
    """Each visual_class maps to exactly one budget category; the three
    budget categories (archival / original_diagram / ai_reconstruction) are
    mutually exclusive — a scene belongs to exactly one of them."""
    expected = {
        "REAL_ARCHIVE": ARCHIVAL,
        "DATA_VISUALIZATION": ORIGINAL_DIAGRAM,
        "SCIENTIFIC_DIAGRAM": ORIGINAL_DIAGRAM,
        "SCIENTIFIC_RECONSTRUCTION": AI_RECONSTRUCTION,
        "HYPOTHETICAL_RECONSTRUCTION": AI_RECONSTRUCTION,
        "ARTISTIC_METAPHOR": AI_RECONSTRUCTION,
    }
    for vc, cat in expected.items():
        assert category_for_visual_class(vc) == cat
    # Deterministic: same input -> same single output category.
    for vc in expected:
        assert category_for_visual_class(vc) is not UNKNOWN
    assert {ARCHIVAL, ORIGINAL_DIAGRAM, AI_RECONSTRUCTION} == set(expected.values())
    assert len({ARCHIVAL, ORIGINAL_DIAGRAM, AI_RECONSTRUCTION}) == 3


def test_legacy_alias_maps_to_ai_reconstruction() -> None:
    # The pilot storyboard uses ``existing_ai_reconstruction`` for existing
    # AI frames; it must map to ai_reconstruction, NOT to unknown.
    assert category_for_visual_class("existing_ai_reconstruction") == AI_RECONSTRUCTION


def test_unknown_visual_class_maps_to_unknown() -> None:
    assert category_for_visual_class(None) is UNKNOWN
    assert category_for_visual_class("") is UNKNOWN
    assert category_for_visual_class("NOT_A_CLASS") is UNKNOWN


# ---------------------------------------------------------------------------
# check_visual_budget — happy path (sum of shares == 100%)
# ---------------------------------------------------------------------------


def test_all_within_target_passes_and_sums_to_100() -> None:
    scenes = [
        _scene("S1", "REAL_ARCHIVE", 0.0, 45.0),      # 45% archival
        _scene("S2", "DATA_VISUALIZATION", 45.0, 85.0),  # 40% orig diagram
        _scene("S3", "SCIENTIFIC_RECONSTRUCTION", 85.0, 100.0),  # 15% AI
    ]
    report = check_visual_budget(scenes)
    assert report.status == "PASS", report.problems
    assert report.unknown_scenes == []
    shares = {s.category: s.share for s in report.shares}
    assert 0.40 <= shares[ARCHIVAL] <= 0.50
    assert 0.30 <= shares[ORIGINAL_DIAGRAM] <= 0.40
    assert shares[AI_RECONSTRUCTION] <= 0.15
    # Sum of category shares == 1.0 (100%).
    assert abs(sum(shares.values()) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# check_visual_budget — 100% AI -> FAIL (current preview situation)
# ---------------------------------------------------------------------------


def test_one_hundred_percent_ai_fails() -> None:
    scenes = [
        _scene("S1", "existing_ai_reconstruction", 0.0, 90.0),
        _scene("S2", "existing_ai_reconstruction", 90.0, 180.0),
    ]
    report = check_visual_budget(scenes)
    assert report.status == "FAIL", report.problems
    by_cat = {s.category: s.share for s in report.shares}
    assert by_cat[AI_RECONSTRUCTION] == 1.0
    assert by_cat[ARCHIVAL] == 0.0
    assert by_cat[ORIGINAL_DIAGRAM] == 0.0


# ---------------------------------------------------------------------------
# check_visual_budget — threshold violations -> FAIL
# ---------------------------------------------------------------------------


def test_archival_below_min_fails() -> None:
    scenes = [
        _scene("S1", "REAL_ARCHIVE", 0.0, 30.0),   # 30% < 40%
        _scene("S2", "DATA_VISUALIZATION", 30.0, 70.0),  # 40%
        _scene("S3", "SCIENTIFIC_RECONSTRUCTION", 70.0, 100.0),  # 30% > 15%
    ]
    report = check_visual_budget(scenes)
    assert report.status == "FAIL", report.problems
    by_cat = {s.category: s.share for s in report.shares}
    assert by_cat[ARCHIVAL] < 0.40
    assert by_cat[AI_RECONSTRUCTION] > 0.15


def test_original_diagram_above_max_fails() -> None:
    scenes = [
        _scene("S1", "REAL_ARCHIVE", 0.0, 40.0),
        _scene("S2", "DATA_VISUALIZATION", 40.0, 90.0),  # 50% > 40%
        _scene("S3", "SCIENTIFIC_RECONSTRUCTION", 90.0, 100.0),  # 10%
    ]
    report = check_visual_budget(scenes)
    assert report.status == "FAIL"
    by_cat = {s.category: s.share for s in report.shares}
    assert by_cat[ORIGINAL_DIAGRAM] > 0.40


def test_ai_above_max_fails() -> None:
    scenes = [
        _scene("S1", "REAL_ARCHIVE", 0.0, 45.0),
        _scene("S2", "DATA_VISUALIZATION", 45.0, 75.0),  # 30%
        _scene("S3", "HYPOTHETICAL_RECONSTRUCTION", 75.0, 100.0),  # 25% > 15%
    ]
    report = check_visual_budget(scenes)
    assert report.status == "FAIL"
    by_cat = {s.category: s.share for s in report.shares}
    assert by_cat[AI_RECONSTRUCTION] > 0.15


# ---------------------------------------------------------------------------
# check_visual_budget — fail-closed (missing data / unknown)
# ---------------------------------------------------------------------------


def test_empty_scenes_blocked() -> None:
    report = check_visual_budget([])
    assert report.status == "BLOCKED"
    assert "no scenes" in " ".join(report.problems)


def test_unknown_visual_class_blocks() -> None:
    scenes = [
        _scene("S1", "REAL_ARCHIVE", 0.0, 40.0),
        _scene("S2", "existing_ai_reconstruction", 40.0, 100.0),  # known alias
        _scene("S3", "totally_bogus_class", 40.0, 100.0),  # truly unknown
    ]
    report = check_visual_budget(scenes)
    assert report.status == "BLOCKED"
    assert "S3" in report.unknown_scenes
    assert "S2" not in report.unknown_scenes  # legacy alias is known


def test_missing_duration_blocks() -> None:
    scenes = [
        _scene("S1", "REAL_ARCHIVE", 0.0, 40.0),
        {"scene_id": "S2", "visual_class": "DATA_VISUALIZATION"},  # no timing
    ]
    report = check_visual_budget(scenes)
    assert report.status == "BLOCKED"
    assert "S2" in report.unknown_scenes


def test_non_positive_duration_blocks() -> None:
    scenes = [
        _scene("S1", "REAL_ARCHIVE", 0.0, 40.0),
        _scene("S2", "DATA_VISUALIZATION", 40.0, 40.0),  # zero duration
    ]
    report = check_visual_budget(scenes)
    assert report.status == "BLOCKED"


# ---------------------------------------------------------------------------
# frame-based timing (start_frame/end_frame + fps)
# ---------------------------------------------------------------------------


def test_frame_based_timing_passes() -> None:
    fps = 30.0
    scenes = [
        {"scene_id": "S1", "visual_class": "REAL_ARCHIVE",
         "start_frame": 0, "end_frame": int(45 * fps)},       # 45s
        {"scene_id": "S2", "visual_class": "DATA_VISUALIZATION",
         "start_frame": int(45 * fps), "end_frame": int(85 * fps)},  # 40s
        {"scene_id": "S3", "visual_class": "SCIENTIFIC_RECONSTRUCTION",
         "start_frame": int(85 * fps), "end_frame": int(100 * fps)},  # 15s
    ]
    report = check_visual_budget(scenes, fps=fps)
    assert report.status == "PASS", report.problems


# ---------------------------------------------------------------------------
# gate_decision output shape
# ---------------------------------------------------------------------------


def test_gate_decision_has_required_fields() -> None:
    scenes = [_scene("S1", "REAL_ARCHIVE", 0.0, 50.0)]
    report = check_visual_budget(scenes)
    decision = gate_decision(report)
    assert decision["check_id"] == "visual_composition_budget"
    assert decision["blocking"] is True
    assert "status" in decision
    assert "measured_value" in decision


# ---------------------------------------------------------------------------
# ReleaseGate integration: visual_composition_budget is DEFAULT REQUIRED
# ---------------------------------------------------------------------------


def test_release_gate_requires_visual_composition_by_default() -> None:
    rg = ReleaseGate()
    assert "visual_composition_budget" in rg.required_check_ids


def test_release_gate_missing_visual_check_can_publish_false() -> None:
    rg = ReleaseGate()
    from lib.final_qc import QCReport, QCResult

    report = QCReport("p")
    report.checks = [
        QCResult("ffprobe_streams", "video", "PASS", "ok", blocking=True),
    ]
    gd = rg.evaluate(report)
    assert gd.can_publish is False
    assert "visual_composition_budget" in gd.required_problems
    assert gd.coverage_complete is False


def test_release_gate_visual_check_fail_can_publish_false() -> None:
    from lib.final_qc import QCReport, QCResult

    rg = ReleaseGate()
    vc = check_visual_budget([
        _scene("S1", "existing_ai_reconstruction", 0.0, 180.0),
    ])
    assert vc.status == "FAIL"
    report = QCReport("p")
    report.checks = [
        QCResult("ffprobe_streams", "video", "PASS", "ok", blocking=True),
        QCResult(
            "visual_composition_budget", "visual", vc.status,
            vc.problems[0] if vc.problems else "visual budget OK",
            blocking=True,
            measured_value=vc.to_dict(),
        ),
    ]
    gd = rg.evaluate(report)
    assert gd.can_publish is False
    assert "visual_composition_budget" in gd.required_problems
