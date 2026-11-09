"""Command line interface: ``flaky-detect run1.xml run2.xml run3.xml``."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .analysis import analyze
from .parser import parse_junit
from .report import render, select, to_dict


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="flaky-detect",
        description="Detect flaky tests by comparing JUnit XML reports from several runs "
                    "(pass them oldest first).")
    p.add_argument("reports", nargs="+", help="JUnit XML files, oldest run first")
    p.add_argument("--min-runs", type=int, default=2, help="ignore tests seen in fewer runs (default: 2)")
    p.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    p.add_argument("--top", type=int, default=0, help="only list the N flakiest tests")
    p.add_argument("--fail-on-flaky", action="store_true", help="exit with code 1 if any flaky test is found")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        runs = [parse_junit(path) for path in args.reports]
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    stats = analyze(runs)
    print(render(to_dict(stats, args.min_runs, args.top), args.format))
    flaky, _, _ = select(stats, args.min_runs)
    return 1 if (args.fail_on_flaky and flaky) else 0


if __name__ == "__main__":
    sys.exit(main())
