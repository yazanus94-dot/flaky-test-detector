"""Render analysis results as text, Markdown or JSON."""
from __future__ import annotations

import json
from typing import Dict, List

from .analysis import TestStats


def select(stats: Dict[str, TestStats], min_runs: int = 2):
    eligible = [s for s in stats.values() if s.runs >= min_runs]
    flaky = sorted((s for s in eligible if s.is_flaky), key=lambda s: (-s.score, -s.failed, s.name))
    broken = sorted((s for s in eligible if s.always_fails), key=lambda s: s.name)
    return flaky, broken, len(eligible)


def to_dict(stats: Dict[str, TestStats], min_runs: int = 2, top: int = 0) -> dict:
    flaky, broken, total = select(stats, min_runs)
    shown = flaky[:top] if top else flaky

    def row(s: TestStats) -> dict:
        return {"name": s.name, "runs": s.runs, "passed": s.passed, "failed": s.failed,
                "mixed": s.mixed, "pass_rate": round(s.pass_rate, 3), "flips": s.flips,
                "score": s.score, "history": s.symbols}

    return {"tests_analyzed": total, "flaky_count": len(flaky),
            "always_failing_count": len(broken),
            "flaky": [row(s) for s in shown], "always_failing": [row(s) for s in broken]}


def render_text(data: dict) -> str:
    lines = [f"Analyzed {data['tests_analyzed']} tests: "
             f"{data['flaky_count']} flaky, {data['always_failing_count']} always failing", ""]
    if data["flaky"]:
        lines.append(f"{'SCORE':>5}  {'PASS%':>5}  {'HISTORY':<12}  TEST")
        for r in data["flaky"]:
            lines.append(f"{r['score']:>5.2f}  {r['pass_rate'] * 100:>5.0f}  {r['history']:<12}  {r['name']}")
    else:
        lines.append("No flaky tests found.")
    if data["always_failing"]:
        lines += ["", "Always failing (broken, not flaky):"]
        lines += [f"  - {r['name']}" for r in data["always_failing"]]
    return "\n".join(lines)


def render_markdown(data: dict) -> str:
    lines = ["## Flaky test report", "",
             f"**{data['tests_analyzed']}** tests analyzed, **{data['flaky_count']}** flaky, "
             f"**{data['always_failing_count']}** always failing.", ""]
    if data["flaky"]:
        lines += ["| Score | Pass rate | History | Test |", "|---:|---:|---|---|"]
        for r in data["flaky"]:
            lines.append(f"| {r['score']:.2f} | {r['pass_rate'] * 100:.0f}% | `{r['history']}` | `{r['name']}` |")
    else:
        lines.append("No flaky tests found. :tada:")
    if data["always_failing"]:
        lines += ["", "### Always failing", ""] + [f"- `{r['name']}`" for r in data["always_failing"]]
    return "\n".join(lines)


def render(data: dict, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data, indent=2)
    if fmt == "markdown":
        return render_markdown(data)
    return render_text(data)
