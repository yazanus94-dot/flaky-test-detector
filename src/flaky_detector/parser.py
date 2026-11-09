"""Parse JUnit-style XML reports (pytest, Maven Surefire, Jest-junit, Playwright, ...)."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

PASSED = "passed"
FAILED = "failed"
SKIPPED = "skipped"


@dataclass(frozen=True)
class TestResult:
    __test__ = False  # stop test runners from collecting this class

    name: str
    status: str
    time: float = 0.0


def parse_junit(path: str) -> list[TestResult]:
    """Return every ``<testcase>`` in the report as a :class:`TestResult`.

    Raises ``ValueError`` if the file is not valid XML or has no test cases root.
    """
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"{path}: not valid XML ({exc})") from exc
    if root.tag not in ("testsuites", "testsuite"):
        raise ValueError(f"{path}: expected <testsuites> or <testsuite>, got <{root.tag}>")

    results = []
    for case in root.iter("testcase"):
        classname = case.get("classname", "")
        name = case.get("name", "")
        full = f"{classname}::{name}" if classname else name
        if case.find("failure") is not None or case.find("error") is not None:
            status = FAILED
        elif case.find("skipped") is not None:
            status = SKIPPED
        else:
            status = PASSED
        try:
            elapsed = float(case.get("time", "0") or 0)
        except ValueError:
            elapsed = 0.0
        results.append(TestResult(full, status, elapsed))
    return results
