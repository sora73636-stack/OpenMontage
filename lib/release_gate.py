"""Release Gate — P5 final publish decision for OpenMontage Factory.

Takes a QCReport (from lib.final_qc.FinalQC) and produces a GateDecision:

  * PASS  — all blocking checks PASS; no WARNINGS; release allowed.
  * WARNING — all blocking checks PASS, but one or more WARNING-level
    issues exist; release allowed but flagged for human review.
  * FAIL  — any blocking check FAIL or BLOCKED; release NOT allowed.

The gate never auto-publishes on FAIL.  It is the final hard stop before
package_draft / upload preparation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from lib.final_qc import QCReport

# Checks whose status must be PASS for the release to be publishable. A
# REQUIRED check that is missing, NOT_RUN, BLOCKED, FAIL or has an unknown
# status makes coverage incomplete and forces can_publish=False. SOFT checks
# (all others) may be NOT_RUN -> WARNING while staying visible in the summary.
REQUIRED_CHECK_IDS: set[str] = set()

# Default REQUIRED checks enforced by every ReleaseGate unless overridden.
# The visual composition budget (C1.2) is a hard gate: the visual mix must
# satisfy the archival / original-diagram / AI-reconstruction share targets
# before a release may be published.
DEFAULT_REQUIRED_CHECK_IDS: frozenset[str] = frozenset({"visual_composition_budget"})


def declare_required(*check_ids: str) -> None:
    """Register check IDs that MUST pass for ``can_publish=True``.

    Callable by pipeline manifests / stage code to declare which QC checks
    are REQUIRED (vs SOFT). A REQUIRED check that is missing, NOT_RUN,
    BLOCKED, FAIL or of unknown status forces ``can_publish=False``.
    """
    REQUIRED_CHECK_IDS.update(check_ids)


@dataclass
class GateDecision:
    """Outcome of the release gate evaluation."""

    decision: str  # PASS | WARNING | FAIL
    can_publish: bool
    blocking_checks: list[str] = field(default_factory=list)
    warning_checks: list[str] = field(default_factory=list)
    not_run_checks: list[str] = field(default_factory=list)
    required_problems: list[str] = field(default_factory=list)
    coverage_complete: bool = True
    summary: dict[str, Any] = field(default_factory=dict)
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReleaseGate:
    """Evaluate a QCReport and decide whether the project may proceed to
    publication preparation (package_draft)."""

    VALID_DECISIONS = ("PASS", "WARNING", "FAIL")

    def __init__(
        self,
        *,
        require_all_blocking_pass: bool = True,
        required_check_ids: Optional[Iterable[str]] = None,
    ) -> None:
        self.require_all_blocking_pass = require_all_blocking_pass
        self.required_check_ids: set[str] = set(required_check_ids or [])
        self.required_check_ids |= set(REQUIRED_CHECK_IDS)
        self.required_check_ids |= set(DEFAULT_REQUIRED_CHECK_IDS)

    def evaluate(self, report: QCReport) -> GateDecision:
        """Evaluate the report and return a GateDecision.

        Logic:
          * FAIL: any blocking check has status FAIL or BLOCKED.
          * REQUIRED check missing / NOT_RUN / BLOCKED / FAIL / unknown or
            WARNING status => coverage incomplete, can_publish=False.
          * WARNING: no blocking failures, all REQUIRED checks PASS, but at
            least one SOFT WARNING-level or NOT_RUN check exists.
            can_publish=True; the check stays visible in the summary.
          * PASS: all blocking checks PASS, all REQUIRED checks PASS, no
            warnings, coverage complete.
        """
        check_by_id = {c.check_id: c for c in report.checks}
        required = self.required_check_ids
        required_problems: list[str] = []
        for cid in sorted(required):
            c = check_by_id.get(cid)
            if c is None or c.status != "PASS":
                required_problems.append(cid)
        coverage_complete = not required_problems

        blocking_failures = report.blocking_failures
        warnings = report.warnings
        not_run = [c for c in report.checks if c.status == "NOT_RUN"]

        if blocking_failures:
            decision = "FAIL"
            can_publish = False
            reason = (
                f"{len(blocking_failures)} blocking check(s) failed: "
                + "; ".join(c.check_id for c in blocking_failures[:5])
            )
        elif required_problems:
            decision = "WARNING"
            can_publish = False
            reason = (
                f"{len(required_problems)} REQUIRED check(s) not PASS "
                "(missing / NOT_RUN / unknown / WARNING / FAIL): "
                + "; ".join(required_problems[:5])
                + f"; coverage complete={coverage_complete}"
            )
        elif warnings:
            decision = "WARNING"
            can_publish = True
            reason = (
                f"{len(warnings)} warning check(s); release allowed but "
                + "human review recommended: "
                + "; ".join(c.check_id for c in warnings[:5])
            )
        elif not_run:
            decision = "WARNING"
            can_publish = True
            reason = (
                f"{len(not_run)} check(s) could not run; release allowed "
                + "but coverage is incomplete: "
                + "; ".join(c.check_id for c in not_run[:5])
            )
        else:
            decision = "PASS"
            can_publish = True
            reason = "all blocking checks passed; no warnings"

        return GateDecision(
            decision=decision,
            can_publish=can_publish,
            blocking_checks=[c.check_id for c in blocking_failures],
            warning_checks=[c.check_id for c in warnings],
            not_run_checks=[c.check_id for c in not_run],
            required_problems=required_problems,
            coverage_complete=coverage_complete,
            summary={
                "total_checks": len(report.checks),
                "pass": sum(1 for c in report.checks if c.status == "PASS"),
                "warning": sum(1 for c in report.checks if c.status == "WARNING"),
                "fail": sum(1 for c in report.checks if c.status == "FAIL"),
                "blocked": sum(1 for c in report.checks if c.status == "BLOCKED"),
                "not_run": sum(1 for c in report.checks if c.status == "NOT_RUN"),
                "blocking_failures": len(blocking_failures),
                "warnings": len(warnings),
                "required_problems": len(required_problems),
                "coverage_complete": coverage_complete,
                "can_publish": can_publish,
            },
            reason=reason,
        )

    def gate_report_path(self, report: QCReport, output_path: str) -> None:
        """Write the gate decision as JSON to output_path (side effect)."""
        decision = self.evaluate(report)
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(decision.to_dict(), indent=2), encoding="utf-8")
