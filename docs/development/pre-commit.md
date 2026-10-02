# Pre-commit Hooks

Automated checks that run before every commit.

## Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks in .git/hooks/
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## Configuration

`.pre-commit-config.yaml`:

```yaml
repos:
  # Ruff: formatting + linting (replaces black, isort, flake8, pyupgrade)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        name: Ruff (lint + fix)
      - id: ruff-format
        name: Ruff (format)

  # Check for merge conflicts, debug statements, large files
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-merge-conflict
      - id: debug-logger
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-json

  # Validate JSON Schema for protocols.json (if schema file exists)
  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.28.0
    hooks:
      - id: check-jsonschema
        files: "data/protocols\.json$"
        args: ["--schemafile", "docs/protocol-database/schema.json"]

  # Prevent secrets in commits
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
        exclude: "data/protocols\.json$"
```

## Hook Behavior

| Hook | Runs On | Fixes |
|------|---------|-------|
| Ruff (lint) | Modified `.py` files | Yes (`--fix`) |
| Ruff (format) | Modified `.py` files | Yes |
| Merge conflict check | All files | No |
| Debug logger | Modified `.py` files | No |
| Large files | All files | No |
| Trailing whitespace | All files | Yes |
| End of file fixer | All files | Yes |
| YAML/TOML/JSON syntax | Modified config files | No |
| JSON Schema validation | `data/protocols.json` | No |
| Detect secrets | All files | No |

## Skip Hooks (Emergency Only)

```bash
# Skip all hooks for this commit
git commit --no-verify -m "emergency fix"

# Skip specific hook
SKIP=ruff git commit -m "skip ruff"
```

## Updating Hooks

```bash
# Update to latest hook versions
pre-commit autoupdate

# Review changes in .pre-commit-config.yaml
git diff .pre-commit-config.yaml
```

## CI Integration

Pre-commit also runs in CI as a safety net:

```yaml
# .github/workflows/pre-commit.yml
name: Pre-commit

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: pre-commit/action@v3.0.0
```

---

## Troubleshooting

### "Ruff made changes" — commit again

```bash
# Ruff auto-fixed files, stage them and commit
git add -u
git commit -m "style: ruff auto-fixes"
```

### "File too large" — use Git LFS

```bash
git lfs track "*.apk"
git add .gitattributes
git add large-file.apk
git commit -m "add large binary"
```

### "Secrets detected" — false positive

```bash
# Update baseline
detect-secrets scan --baseline .secrets.baseline
# Or add to allowlist in .secrets.baseline
```

---

## See Also

- [Code Style](code-style.md)
- [Testing](testing.md)
- [CI/CD](ci-cd.md)
- [Contributing](contributing.md)