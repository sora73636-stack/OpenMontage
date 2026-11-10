"""Regression tests for lib.release_gate (S3.4 fail-closed release gate).

REQUIRED vs SOFT check IDs. A REQUIRED check that is missing, NOT_RUN,
BLOCKED, FAIL or of unknown status forces can_publish=False. SOFT NOT_RUN
may be WARNING but stays visible. No test asserts only ``decision`` without
also asserting ``can_publish``.

``visual_composition_budget`` (V13 C1.2) is a DEFAULT REQUIRED check, so
every ReleaseGate requires it unless the caller overrides required_check_ids.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from lib.final_qc import QCReport, QCResult  # noqa: E402
from lib.release_gate import (  # noqa: E402
    DEFAULT_REQUIRED_CHECK_IDS,
    ReleaseGate,
    declare_required,
    REQUIRED_CHECK_IDS,
)
from lib.visual_composition import check_visual_budget  # noqa: E402


def _check(cid: str, status: str, blocking: bool = True) -> QCResult:
    return QCResult(cid, "video", status, "evidence", blocking=blocking)


def _report(*checks: QCResult) -> QCReport:
    r = QCReport("p")
    r.checks = list(checks)
    return r


def teardown_function() -> None:
    REQUIRED_CHECK_IDS.clear()


def _visual_pass_check() -> QCResult:
    vc = check_visual_budget([
        {"scene_id": "S1", "visual_class": "REAL_ARCHIVE", "time_in": 0.0, "time_out": 45.0},
        {"scene_id": "S2", "visual_class": "DATA_VISUALIZATION", "time_in": 45.0, "time_out": 85.0},
        {"scene_id": "S3", "visual_class": "SCIENTIFIC_RECONSTRUCTION", "time_in": 85.0, "time_out": 100.0},
    ])
    assert vc.status == "PASS", vc.problems
    return QCResult(
        "visual_composition_budget", "visual", vc.status,
        vc.problems[0] if vc.problems else "visual budget OK",
        blocking=True, measured_value=vc.to_dict(),
    )


def test_all_required_pass_can_publish_true() -> None:
    declare_required("v1", "v2")
    rg = ReleaseGate(required_check_ids=["v1", "v2"])
    gd = rg.evaluate(_report(
        _check("v1", "PASS"), _check("v2", "PASS"), _visual_pass_check(),
    ))
    assert gd.decision == "PASS"
    assert gd.can_publish is True
    assert gd.coverage_complete is True


def test_release_gate_requires_visual_composition_by_default() -> None:
    rg = ReleaseGate()
    assert "visual_composition_budget" in rg.required_check_ids


def test_release_gate_missing_visual_check_can_publish_false() -> None:
    rg = ReleaseGate()
    report = _report(_check("ffprobe_streams", "PASS"))
    gd = rg.evaluate(report)
    assert gd.can_publish is False
    assert "visual_composition_budget" in gd.required_problems
    assert gd.coverage_complete is False


def test_required_not_run_can_publish_false() -> None:
    declare_required("v1", "v2")
    rg = ReleaseGate(required_check_ids=["v1", "v2"])
    gd = rg.evaluate(_report(
        _check("v1", "PASS"), _check("v2", "NOT_RUN"), _visual_pass_check(),
    ))
    assert gd.can_publish is False
    assert gd.coverage_complete is False
    assert "v2" in gd.required_problems
    assert gd.decision == "WARNING"


def test_required_missing_can_publish_false() -> None:
    declare_required("v1", "v2")
    rg = ReleaseGate(required_check_ids=["v1", "v2"])
    gd = rg.evaluate(_report(
        _check("v1", "PASS"), _visual_pass_check(),
    ))
    assert gd.can_publish is False
    assert "v2" in gd.required_problems


def test_required_warning_can_publish_false() -> None:
    declare_required("v1")
    rg = ReleaseGate(required_check_ids=["v1"])
    gd = rg.evaluate(_report(
        _check("v1", "WARNING"), _visual_pass_check(),
    ))
    assert gd.can_publish is False
    assert gd.coverage_complete is False


def test_required_unknown_status_can_publish_false() -> None:
    declare_required("v1")
    rg = ReleaseGate(required_check_ids=["v1"])
    gd = rg.evaluate(_report(
        _check("v1", "UNKNOWN"), _visual_pass_check(),
    ))
    assert gd.can_publish is False


def test_required_blocked_can_publish_false() -> None:
    declare_required("v1")
    rg = ReleaseGate(required_check_ids=["v1"])
    gd = rg.evaluate(_report(
        _check("v1", "BLOCKED"), _visual_pass_check(),
    ))
    assert gd.can_publish is False


def test_soft_not_run_visible_but_can_publish_true_when_visual_passes() -> None:
    # Even with NO extra required checks, visual_composition_budget is
    # DEFAULT REQUIRED; with it PASSing, a SOFT NOT_RUN stays WARNING and
    # can_publish=True.
    rg = ReleaseGate()
    gd = rg.evaluate(_report(
        _check("s1", "NOT_RUN"), _visual_pass_check(),
    ))
    assert gd.decision == "WARNING"
    assert gd.can_publish is True
    assert "s1" in gd.not_run_checks


def test_blocking_fail_can_publish_false() -> None:
    rg = ReleaseGate()
    gd = rg.evaluate(_report(
        _check("b1", "FAIL"), _visual_pass_check(),
    ))
    assert gd.decision == "FAIL"
    assert gd.can_publish is False


def test_every_case_asserts_can_publish() -> None:
    rg = ReleaseGate(required_check_ids=["v1"])
    gd = rg.evaluate(_report(_check("v1", "PASS"), _visual_pass_check()))
    assert "can_publish" in gd.to_dict()
    assert gd.summary["can_publish"] == gd.can_publish
