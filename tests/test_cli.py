import contextlib
import io
import json
import unittest

from flaky_detector.cli import main
from helpers import tempdir, write_report


def invoke(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def _reports(self, d):
        return [
            write_report(d, "1.xml", [("s", "stable", "passed"), ("s", "flaky", "passed"), ("s", "broken", "failed")]),
            write_report(d, "2.xml", [("s", "stable", "passed"), ("s", "flaky", "failed"), ("s", "broken", "failed")]),
            write_report(d, "3.xml", [("s", "stable", "passed"), ("s", "flaky", "passed"), ("s", "broken", "failed")]),
        ]

    def test_text_report_lists_flaky_and_broken(self):
        with tempdir() as d:
            code, out, _ = invoke(*self._reports(d))
        self.assertEqual(code, 0)
        self.assertIn("s::flaky", out)
        self.assertIn("Always failing", out)
        self.assertNotIn("s::stable", out)

    def test_fail_on_flaky_sets_exit_code(self):
        with tempdir() as d:
            code, _, _ = invoke(*self._reports(d), "--fail-on-flaky")
        self.assertEqual(code, 1)

    def test_clean_suite_exits_zero_even_with_flag(self):
        with tempdir() as d:
            reports = [write_report(d, f"{i}.xml", [("s", "ok", "passed")]) for i in range(3)]
            code, out, _ = invoke(*reports, "--fail-on-flaky")
        self.assertEqual(code, 0)
        self.assertIn("No flaky tests found", out)

    def test_json_output_is_valid(self):
        with tempdir() as d:
            _, out, _ = invoke(*self._reports(d), "--format", "json")
        data = json.loads(out)
        self.assertEqual(data["flaky_count"], 1)
        self.assertEqual(data["flaky"][0]["history"], "PFP")

    def test_markdown_output(self):
        with tempdir() as d:
            _, out, _ = invoke(*self._reports(d), "--format", "markdown")
        self.assertIn("| Score |", out)

    def test_min_runs_filters_tests(self):
        with tempdir() as d:
            _, out, _ = invoke(*self._reports(d), "--min-runs", "4", "--format", "json")
        self.assertEqual(json.loads(out)["tests_analyzed"], 0)

    def test_missing_file_returns_error_code(self):
        code, _, err = invoke("/nonexistent/report.xml")
        self.assertEqual(code, 2)
        self.assertIn("error", err)


if __name__ == "__main__":
    unittest.main()
