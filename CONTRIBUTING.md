# Contributing to flaky-test-detector

Thanks for your interest! Bug reports, ideas and pull requests are welcome.

## Getting started

```bash
git clone https://github.com/yazanus94-dot/flaky-test-detector.git
cd flaky-test-detector
python -m venv .venv && source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Pull request checklist

- Open an issue first for larger changes so we can agree on the approach.
- Add or update tests for every behavior change.
- Keep the project free of third-party runtime dependencies.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages (`feat:`, `fix:`, `docs:` ...).
- Make sure the full test suite passes on Python 3.9+.
