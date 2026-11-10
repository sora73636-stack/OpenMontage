"""Regression tests for zero-cost Flow/CDP guard (S3.2 cases 5 and 6).

* Case 5: a Flow/CDP route with unknown/disabled cost is BLOCKED by the
  zero-cost gate; no provider function is invoked and no network request is
  made (the conftest network guard enforces non-loopback socket blocking).
* Case 6: retry after an unknown remote status does not create a duplicate
  job — FlowJobManager.add_job rejects duplicate job_id and duplicate content.
"""

from __future__ import annotations

from lib.flow_job_manager import FlowJob, FlowJobManager
from lib.zero_cost_gate import STRICT_ZERO_COST, evaluate_call, ToolFacts


def _flow_facts(cost_usd) -> ToolFacts:
    return ToolFacts(
        tool="flow_image",
        operation="execute",
        provider="gflow",
        runtime="api",
        route="https://flow.google.com/v1/images",
        cost_usd=cost_usd,
        status="available",
    )


def test_flow_unknown_cost_blocked_no_provider_call() -> None:
    # Case 5: unknown Flow cost => BLOCKED, provider never invoked, no network.
    decision = evaluate_call(_flow_facts(None), mode=STRICT_ZERO_COST)
    assert decision.blocked is True
    assert decision.cost_usd is None
    assert "cost_usd is null" in decision.reason or "unknown" in decision.reason


def test_flow_nonzero_cost_blocked_strict() -> None:
    decision = evaluate_call(_flow_facts(0.04), mode=STRICT_ZERO_COST)
    assert decision.blocked is True


def _fresh_manager(monkeypatch) -> FlowJobManager:
    mgr = FlowJobManager()
    monkeypatch.setattr(mgr, "jobs", {})
    monkeypatch.setattr(mgr, "_persist", lambda job: None)
    return mgr


def test_retry_unknown_status_does_not_duplicate_job(monkeypatch, tmp_path) -> None:
    # Case 6: same job content submitted again (retry) must not create a
    # duplicate job; add_job raises on duplicate content.
    mgr = _fresh_manager(monkeypatch)
    job1 = mgr.add_job(
        job_id="flow-job-1",
        project="v13",
        scene="europa-ice",
        prompt="subsurface ocean cross section",
    )
    assert job1.job_id == "flow-job-1"
    assert len(mgr.jobs) == 1

    # Retry with the same content under a new job_id -> duplicate content,
    # must be rejected (no second job created).
    try:
        mgr.add_job(
            job_id="flow-job-2",
            project="v13",
            scene="europa-ice",
            prompt="subsurface ocean cross section",
        )
    except ValueError as exc:
        assert "Duplicate job content" in str(exc)
    else:
        raise AssertionError("duplicate content was not rejected")
    assert len(mgr.jobs) == 1, "retry must not create a second job"

    # Same job_id again -> duplicate job_id rejected.
    try:
        mgr.add_job(
            job_id="flow-job-1",
            project="v13",
            scene="europa-ice",
            prompt="different prompt",
        )
    except ValueError as exc:
        assert "Duplicate job_id" in str(exc)
    assert len(mgr.jobs) == 1
