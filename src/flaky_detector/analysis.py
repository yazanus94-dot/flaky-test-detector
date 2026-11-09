"""Turn several test runs into per-test reliability statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .parser import FAILED, PASSED, SKIPPED, TestResult

MIXED = "mixed"  # the same test passed *and* failed inside one report (a retry)


@dataclass
class TestStats:
    __test__ = False

    name: str
    history: List[str] = field(default_factory=list)  # one of passed/failed/mixed per run

    @property
    def runs(self) -> int:
        return len(self.history)

    @property
    def passed(self) -> int:
        return self.history.count(PASSED)

    @property
    def failed(self) -> int:
        return self.history.count(FAILED)

    @property
    def mixed(self) -> int:
        return self.history.count(MIXED)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.runs if self.runs else 0.0

    @property
    def flips(self) -> int:
        """Number of times the outcome changed between consecutive runs."""
        return sum(1 for a, b in zip(self.history, self.history[1:]) if a != b or a == MIXED)

    @property
    def is_flaky(self) -> bool:
        return self.mixed > 0 or (self.passed > 0 and self.failed > 0)

    @property
    def always_fails(self) -> bool:
        return self.runs > 0 and self.failed == self.runs

    @property
    def score(self) -> float:
        """0.0 = stable, 1.0 = the outcome changes on every single run."""
        if self.runs > 1:
            return round(self.flips / (self.runs - 1), 3)
        return 1.0 if self.mixed else 0.0

    @property
    def symbols(self) -> str:
        return "".join({PASSED: "P", FAILED: "F", MIXED: "M"}[h] for h in self.history)


def _collapse(attempts: List[str]) -> str:
    executed = [a for a in attempts if a != SKIPPED]
    if not executed:
        return SKIPPED
    if all(a == PASSED for a in executed):
        return PASSED
    if all(a == FAILED for a in executed):
        return FAILED
    return MIXED


def analyze(runs: List[List[TestResult]]) -> Dict[str, TestStats]:
    """Aggregate ``runs`` (oldest first) into stats keyed by test name.

    Skipped tests are ignored for that run. A test that appears several times in
    one report (retries) and has both outcomes is recorded as ``mixed``.
    """
    stats: Dict[str, TestStats] = {}
    for run in runs:
        per_test: Dict[str, List[str]] = {}
        for result in run:
            per_test.setdefault(result.name, []).append(result.status)
        for name, attempts in per_test.items():
            outcome = _collapse(attempts)
            if outcome == SKIPPED:
                continue
            stats.setdefault(name, TestStats(name)).history.append(outcome)
    return stats
