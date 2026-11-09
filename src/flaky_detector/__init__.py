"""flaky-test-detector: find unreliable tests by comparing JUnit XML reports."""
from .parser import TestResult, parse_junit
from .analysis import TestStats, analyze

__all__ = ["TestResult", "parse_junit", "TestStats", "analyze"]
__version__ = "0.1.0"
