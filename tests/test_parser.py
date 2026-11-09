import os
import unittest

from flaky_detector.parser import FAILED, PASSED, SKIPPED, parse_junit
from helpers import tempdir, write_report


class ParserTests(unittest.TestCase):
    def test_statuses_and_names(self):
        with tempdir() as d:
            path = write_report(d, "r.xml", [("a.Login", "ok", "passed"), ("a.Login", "bad", "failed"),
                                             ("a.Login", "crash", "error"), ("a.Login", "skip", "skipped")])
            got = {r.name: r.status for r in parse_junit(path)}
        self.assertEqual(got, {"a.Login::ok": PASSED, "a.Login::bad": FAILED,
                               "a.Login::crash": FAILED, "a.Login::skip": SKIPPED})

    def test_testcase_without_classname(self):
        with tempdir() as d:
            path = write_report(d, "r.xml", [("", "plain", "passed")])
            self.assertEqual(parse_junit(path)[0].name, "plain")

    def test_invalid_xml_raises(self):
        with tempdir() as d:
            bad = os.path.join(d, "bad.xml")
            with open(bad, "w") as fh:
                fh.write("<not-closed")
            with self.assertRaises(ValueError):
                parse_junit(bad)

    def test_wrong_root_raises(self):
        with tempdir() as d:
            bad = os.path.join(d, "other.xml")
            with open(bad, "w") as fh:
                fh.write("<html></html>")
            with self.assertRaises(ValueError):
                parse_junit(bad)


if __name__ == "__main__":
    unittest.main()
