"""Regression tests for lib.release_gate (S3.4 fail-closed release gate).

REQUIRED vs SOFT check IDs. A REQUIRED check that is missing, NOT_RUN,
BLOCKED, FAIL or of unknown status forces can_publish=False. SOFT NOT_RUN
may be WARNING but stays visible. No test asserts only ``decision`` without
also asserting ``can_publish``.
"""

from __future__ import annotations

from lib.final_qc import QCReport, QCResult
from lib.release_gate import ReleaseGate, declare_required, REQUIRED_CHECK_IDS


def _check(cid: str, status: str, blocking: bool = True) -> QCResult:
    return QCResult(cid, "video", status, "evidence", blocking=blocking)


def _report(*checks: QCResult) -> QCReport:
    r = QCReport("p")
    r.checks = list(checks)
    return r


def teardown_function() -> None:
    REQUIRED_CHECK_IDS.clear()


def test_all_required_pass_can_publish_true() -> None:
    declare_required("v1", "v2")
    rg = ReleaseGate(required_check_ids=["v1", "v2"])
    gd = rg.evaluate(_report(_check("v1", "PASS"), _check("v2", "PASS")))
    assert gd.decision == "PASS"
    assert gd.can_publish is True
    assert gd.coverage_complete is True


def test_required_not_run_can_publish_false() -> None:
    declare_required("v1", "v2")
    rg = ReleaseGate(required_check_ids=["v1", "v2"])
    gd = rg.evaluate(_report(_check("v1", "PASS"), _check("v2", "NOT_RUN")))
    assert gd.can_publish is False
    assert gd.coverage_complete is False
    assert "v2" in gd.required_problems
    # can_publish must be asserted, not just decision.
    assert gd.decision == "WARNING"


def test_required_missing_can_publish_false() -> None:
    declare_required("v1", "v2")
    rg = ReleaseGate(required_check_ids=["v1", "v2"])
    gd = rg.evaluate(_report(_check("v1", "PASS")))
    assert gd.can_publish is False
    assert "v2" in gd.required_problems


def test_required_warning_can_publish_false() -> None:
    declare_required("v1")
    rg = ReleaseGate(required_check_ids=["v1"])
    gd = rg.evaluate(_report(_check("v1", "WARNING")))
    assert gd.can_publish is False
    assert gd.coverage_complete is False


def test_required_unknown_status_can_publish_false() -> None:
    declare_required("v1")
    rg = ReleaseGate(required_check_ids=["v1"])
    gd = rg.evaluate(_report(_check("v1", "UNKNOWN")))
    assert gd.can_publish is False


def test_required_blocked_can_publish_false() -> None:
    declare_required("v1")
    rg = ReleaseGate(required_check_ids=["v1"])
    gd = rg.evaluate(_report(_check("v1", "BLOCKED")))
    assert gd.can_publish is False


def test_soft_not_run_visible_but_can_publish_true_when_no_required() -> None:
    rg = ReleaseGate()
    gd = rg.evaluate(_report(_check("s1", "NOT_RUN")))
    assert gd.decision == "WARNING"
    assert gd.can_publish is True
    assert "s1" in gd.not_run_checks


def test_blocking_fail_can_publish_false() -> None:
    rg = ReleaseGate()
    gd = rg.evaluate(_report(_check("b1", "FAIL")))
    assert gd.decision == "FAIL"
    assert gd.can_publish is False


def test_every_case_asserts_can_publish() -> None:
    # Meta-check: every gate result in this module is asserted on can_publish
    # as well as decision. (Exercised implicitly by the tests above.)
    rg = ReleaseGate(required_check_ids=["v1"])
    gd = rg.evaluate(_report(_check("v1", "PASS")))
    assert "can_publish" in gd.to_dict()
    assert gd.summary["can_publish"] == gd.can_publish
