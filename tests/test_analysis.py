import unittest

from flaky_detector.analysis import analyze
from flaky_detector.parser import FAILED, PASSED, SKIPPED, TestResult


def run(**statuses):
    return [TestResult(name, status) for name, status in statuses.items()]


class AnalysisTests(unittest.TestCase):
    def test_stable_test_is_not_flaky(self):
        stats = analyze([run(a=PASSED), run(a=PASSED), run(a=PASSED)])
        self.assertFalse(stats["a"].is_flaky)
        self.assertEqual(stats["a"].score, 0.0)

    def test_alternating_test_has_score_one(self):
        stats = analyze([run(a=PASSED), run(a=FAILED), run(a=PASSED), run(a=FAILED)])
        s = stats["a"]
        self.assertTrue(s.is_flaky)
        self.assertEqual(s.flips, 3)
        self.assertEqual(s.score, 1.0)
        self.assertEqual(s.symbols, "PFPF")

    def test_single_regression_is_low_score(self):
        stats = analyze([run(a=PASSED)] * 4 + [run(a=FAILED)])
        self.assertEqual(stats["a"].flips, 1)
        self.assertEqual(stats["a"].score, 0.25)

    def test_always_failing_is_not_flaky(self):
        stats = analyze([run(a=FAILED), run(a=FAILED)])
        self.assertTrue(stats["a"].always_fails)
        self.assertFalse(stats["a"].is_flaky)

    def test_skipped_runs_are_ignored(self):
        stats = analyze([run(a=PASSED), run(a=SKIPPED), run(a=PASSED)])
        self.assertEqual(stats["a"].runs, 2)

    def test_retry_inside_one_report_is_mixed(self):
        retry = [TestResult("a", FAILED), TestResult("a", PASSED)]
        stats = analyze([retry])
        self.assertTrue(stats["a"].is_flaky)
        self.assertEqual(stats["a"].symbols, "M")
        self.assertEqual(stats["a"].score, 1.0)

    def test_new_test_appearing_later_has_shorter_history(self):
        stats = analyze([run(a=PASSED), run(a=PASSED, b=FAILED)])
        self.assertEqual(stats["b"].runs, 1)


if __name__ == "__main__":
    unittest.main()
