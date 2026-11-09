# flaky-test-detector

[![CI](https://github.com/yazanus94-dot/flaky-test-detector/actions/workflows/ci.yml/badge.svg)](https://github.com/yazanus94-dot/flaky-test-detector/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Find unreliable tests by comparing the JUnit XML reports of several CI runs.

A test that fails once and passes on the next run wastes everyone's time and teaches the team to ignore red builds. `flaky-detect` reads the reports your test framework already produces (pytest, Maven Surefire, Jest-JUnit, Playwright, Cypress, ...), tracks every test across runs and ranks the ones whose outcome keeps changing.

- Zero runtime dependencies, standard library only
- Works with any tool that emits JUnit XML
- Separates **flaky** tests (inconsistent) from **always failing** tests (simply broken)
- Understands retries: a test that fails then passes inside one report is flagged
- Text, Markdown and JSON output, with a CI-friendly exit code

## Install

```bash
git clone https://github.com/yazanus94-dot/flaky-test-detector.git
cd flaky-test-detector
python -m pip install -e .
```

## Usage

Pass the reports **oldest run first**:

```bash
flaky-detect run1.xml run2.xml run3.xml run4.xml
```

```text
Analyzed 4 tests: 2 flaky, 1 always failing

SCORE  PASS%  HISTORY       TEST
 1.00     50  PFPF          shop.test_cart::test_checkout_timeout
 0.67     75  PPFP          shop.test_auth::test_login

Always failing (broken, not flaky):
  - shop.test_search::test_index_rebuild
```

The `examples/` folder contains the four reports used above, so you can try it immediately:

```bash
flaky-detect examples/run*.xml
```

### Options

| Option | Description |
|---|---|
| `--format text\|json\|markdown` | Output format. Markdown is handy for PR comments and job summaries. |
| `--min-runs N` | Ignore tests seen in fewer than N runs (default 2). |
| `--top N` | Only list the N flakiest tests. |
| `--fail-on-flaky` | Exit with code 1 when any flaky test is found. |

Exit codes: `0` ok, `1` flaky tests found (with `--fail-on-flaky`), `2` unreadable or invalid report.

### Use it in GitHub Actions

```yaml
- name: Check for flaky tests
  run: flaky-detect reports/*.xml --format markdown --fail-on-flaky >> "$GITHUB_STEP_SUMMARY"
```

## How the score works

Each test gets a history string: `P` passed, `F` failed, `M` mixed (passed and failed inside one report, e.g. a retry). Skipped runs are ignored.

```text
score = outcome changes between consecutive runs / (runs - 1)
```

`PFPF` scores 1.00 (changes every run), `PPPPF` scores 0.25 (one regression, probably a real bug rather than flakiness). A test is flaky when it has both passed and failed, or when a retry in a single report recovered it.

## Use as a library

```python
from flaky_detector import parse_junit, analyze

runs = [parse_junit(p) for p in ["run1.xml", "run2.xml", "run3.xml"]]
for name, stats in analyze(runs).items():
    if stats.is_flaky:
        print(name, stats.symbols, stats.score)
```

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Roadmap

- Read reports from a directory or glob with timestamps instead of argument order
- Per-test duration drift detection
- Optional GitHub Issues integration

Contributions are welcome, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) © Yazan Aljabari
