# Contributing Guide

Thank you for contributing to FrameWork! This guide covers everything you need to know.

## Quick Start for Contributors

```bash
# 1. Fork the repo on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Frame-work.git
cd Frame-work

# 3. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 4. Install in development mode with all tools
pip install -e .[desktop,mobile,dev,docs]

# 5. Install pre-commit hooks
pre-commit install

# 6. Run the app
streamlit run app.py
```

## Ways to Contribute

### 📝 Add a Protocol

See [Adding Protocols](../protocol-database/adding-protocols.md) for complete guide.

1. Edit `build_data.py` — add `add(...)` call
2. Run `python build_data.py`
3. Run tests: `python build_scripts/check_data.py && python build_scripts/check_logic.py`
4. Verify in app: `streamlit run app.py`
5. Submit PR

### 🐛 Fix a Bug

1. Check [existing issues](https://github.com/KSHNKMRJHA/Frame-work/issues)
2. Create minimal reproduction
3. Fix with test if applicable
4. Run full validation: `./validate-all.sh`
5. Submit PR

### 📚 Improve Documentation

- Fix typos, clarify explanations
- Add examples to API docs
- Write new ADRs for significant changes
- Update README.md for user-facing changes

### ⚡ Performance / Refactoring

- Profile before optimizing
- Maintain backward compatibility
- Run benchmarks if changing hot paths

---

## Development Workflow

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/short-description` | `feat/add-mipi-dphy` |
| Bugfix | `fix/short-description` | `fix/uart-crc-calculator` |
| Docs | `docs/short-description` | `docs/update-api-reference` |
| Refactor | `refactor/short-description` | `refactor/quiz-engine` |
| Chore | `chore/short-description` | `chore/update-dependencies` |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

Examples:
```
feat(protocols): add MIPI D-PHY v2.0 protocol
fix(science): correct CAN bit timing sample point calculation
docs(api): add science module reference
refactor(quiz): extract puzzle generators to separate module
```

### Pull Request Process

1. **Title**: Use conventional commit format
2. **Description**: What, why, how to test
3. **Checks**: All CI must pass
4. **Review**: At least one approval required
5. **Merge**: Squash and merge (default)

---

## Code Standards

### Python Style

- **Formatter**: Ruff (configured in `ruff.toml`)
- **Line length**: 100 characters
- **Target version**: Python 3.10
- **Import order**: stdlib → third-party → local

```bash
# Format
ruff format .

# Lint
ruff check .

# Fix auto-fixable
ruff check --fix .
```

### Type Hints

- Required for public functions
- Use `from __future__ import annotations`
- Prefer `list[str]` over `List[str]` (Python 3.9+)

```python
def generate_quiz(
    protocols: list[dict],
    n: int = 10,
    seed: int | None = None,
) -> list[dict]:
    ...
```

### Docstrings

Google style (configured for mkdocstrings):

```python
def uart_bit_timing(f_clk: int, baud: int, oversampling: int = 16) -> dict:
    """Calculate UART baud rate divisor and error.
    
    Args:
        f_clk: Clock frequency in Hz.
        baud: Target baud rate.
        oversampling: Oversampling factor (default 16).
        
    Returns:
        Dict with divisor, actual_baud, error_pct, acceptable.
        
    Raises:
        ValueError: If inputs are invalid.
    """
```

### Testing

- **Unit tests**: `build_scripts/check_logic.py`
- **Data integrity**: `build_scripts/check_data.py`
- **Property-based**: Add Hypothesis tests for generators
- **Run all**: `python build_scripts/check_data.py && python build_scripts/check_logic.py`

### Adding Tests

For new calculator/validator/generator:

1. Add test function to `check_logic.py` or `check_data.py`
2. Add to `tests` list in `main()`
3. Verify it fails before fix, passes after

---

## Protocol Contribution Checklist

Before submitting a new protocol PR:

- [ ] `build_data.py` entry follows [schema](../protocol-database/schema.md)
- [ ] All 20+ required fields populated
- [ ] `electrical` has all 8 sub-fields with real values
- [ ] `frame.fields` ordered, unique names, realistic bit widths
- [ ] `related_protocols` references existing IDs only
- [ ] `category` is canonical
- [ ] `difficulty` justified
- [ ] `year` is invention/standardization year
- [ ] `run python build_data.py` — no errors
- [ ] `run python build_scripts/check_data.py` — passes
- [ ] `run python build_scripts/check_logic.py` — passes
- [ ] `run python build_scripts/sync_mobile.py` — no diff
- [ ] `streamlit run app.py` — protocol appears, diagrams render, quiz works
- [ ] Added to `technical_profiles.py` if calculator-relevant

---

## CI/CD Pipeline

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR:

1. **Python 3.10 & 3.11** matrix
2. **Install deps**
3. **Reproducibility**: `protocols.json` matches `build_data.py`
4. **Mobile sync**: `kivy_mobile/` matches desktop
5. **Syntax check**: All `.py` files compile
6. **Data integrity**: `check_data.py`
7. **Logic tests**: `check_logic.py`
8. **Lint**: `ruff check`

---

## Release Process

Maintainers only:

```bash
# 1. Update VERSION in utils/branding.py
# 2. Update CHANGELOG.md
# 3. Commit: "chore: release v1.1.0"
# 4. Tag: git tag v1.1.0
# 5. Push: git push origin main --tags
# 6. GitHub Actions builds desktop/mobile artifacts
# 7. Create GitHub Release with artifacts
# 8. Streamlit Cloud auto-deploys
```

See [Releases: Build Process](../releases/build-process.md).

---

## Getting Help

- **Questions**: [GitHub Discussions](https://github.com/KSHNKMRJHA/Frame-work/discussions)
- **Bugs**: [GitHub Issues](https://github.com/KSHNKMRJHA/Frame-work/issues)
- **Security**: Email maintainer (see README.md)
- **Discord**: Not available yet

---

## Code of Conduct

Be respectful, inclusive, and constructive. This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

---

## License

By contributing, you agree your contributions are licensed under the MIT License (same as project).

---

## See Also

- [Code Style](code-style.md)
- [Testing](testing.md)
- [CI/CD](ci-cd.md)
- [Pre-commit](pre-commit.md)
- [Protocol Database](../protocol-database/adding-protocols.md)