import os
import tempfile


def write_report(directory, name, cases):
    """cases: list of (classname, test_name, status) with status passed/failed/error/skipped."""
    parts = ['<?xml version="1.0" encoding="utf-8"?>', "<testsuites><testsuite name='s'>"]
    for classname, test, status in cases:
        inner = {"failed": "<failure message='boom'/>", "error": "<error message='err'/>",
                 "skipped": "<skipped/>", "passed": ""}[status]
        parts.append(f"<testcase classname='{classname}' name='{test}' time='0.01'>{inner}</testcase>")
    parts.append("</testsuite></testsuites>")
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    return path


def tempdir():
    return tempfile.TemporaryDirectory()
