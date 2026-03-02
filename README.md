# agentic

Reference implementation of a small planning/execution orchestration loop.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### Checks

```bash
ruff check .
ruff format --check .
mypy src
pytest
python -m build
```

## Merge requirements

All pull requests should pass the CI workflow checks before merge:

- lint (`ruff check`, `ruff format --check`)
- type-check (`mypy src`)
- tests (`pytest`)
- build (`python -m build`)

Repository admins should configure branch protection to require the `CI` workflow status check.

## Conventional commits and semantic releases

Use [Conventional Commits](https://www.conventionalcommits.org/) for all commits (e.g., `feat: ...`,
`fix: ...`, `chore: ...`).

Release automation is provided by `.github/workflows/release.yml` with
`python-semantic-release`, which:

1. infers the next semantic version from commit history,
2. creates release notes,
3. tags/releases from the `main` branch.
