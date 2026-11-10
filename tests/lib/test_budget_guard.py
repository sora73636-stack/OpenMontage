"""Regression tests for lib.budget_guard (S3.2 zero-cost enforcement).

Budget is hard $0. Unknown cost (None) is never treated as free: only an
explicit estimated_usd == 0.0 for a known free route is allowed.
"""

from __future__ import annotations

from lib.budget_guard import BudgetGuard, guard


def _decision(**kwargs) -> dict:
    return BudgetGuard().guard(kwargs.pop("kind"), kwargs.pop("est", None), **kwargs)


def test_unknown_cost_none_is_blocked_not_free() -> None:
    d = BudgetGuard().guard("image_generation", None)
    assert d.allowed is False
    assert d.status == "fallback_used"
    assert "None (unknown)" in d.reason or "BLOCKED, not free" in d.reason


def test_default_arg_is_none_and_blocked() -> None:
    # guard(kind) with no estimated_usd => unknown => blocked.
    d = guard("tts")
    assert d["allowed"] is False
    assert d["status"] == "fallback_used"


def test_explicit_zero_local_route_allowed() -> None:
    d = BudgetGuard().guard("ffmpeg_render", 0.0)
    assert d.allowed is True
    assert d.status == "success"


def test_nonzero_cost_blocked() -> None:
    d = BudgetGuard().guard("api_call", 2.5)
    assert d.allowed is False
    assert d.status == "fallback_used"


def test_nonzero_cost_blocked_even_if_caller_would_approve() -> None:
    # BudgetGuard has no approval parameter: any spend estimate > 0 is
    # refused under the $0 ceiling, approval cannot turn it free.
    d = BudgetGuard().guard("flow_generation", 0.02)
    assert d.allowed is False


def test_spend_stays_zero() -> None:
    g = BudgetGuard()
    g.guard("x", 0.0)
    g.record_spend(0.0)
    assert g.spent_usd == 0.0


def test_module_level_guard_blocks_none() -> None:
    d = guard("download", None)
    assert d["allowed"] is False
    assert d["status"] == "fallback_used"


def test_module_level_guard_allows_zero() -> None:
    d = guard("ffmpeg_render", 0.0)
    assert d["allowed"] is True
    assert d["status"] == "success"
