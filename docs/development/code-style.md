# Code Style

FrameWork uses **Ruff** for formatting and linting. Configuration in `ruff.toml`.

## Quick Commands

```bash
# Format all files
ruff format .

# Check lint (no changes)
ruff check .

# Auto-fix lint issues
ruff check --fix .

# Check specific file
ruff check utils/data_loader.py
```

## Ruff Configuration (`ruff.toml`)

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
src = ["utils", "pages", "build_scripts", "kivy_mobile", "app.py", "build_data.py"]

[tool.ruff.format]
quote-style = "single"
indent-style = "space"
skip-magic-trailing-comma = false
docstring-code-format = true

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
    "T20", # flake8-print (no print in prod)
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults (acceptable)
    "SIM113", # use itertools (not always clearer)
]
per-file-ignores = {
    "build_data.py": ["T201"],  # print allowed in build script
    "build_scripts/*.py": ["T201"],
    "kivy_mobile/*.py": ["T201"],
}
```

## Key Style Rules

### Imports

```python
# Standard library
import json
import os
from pathlib import Path
from typing import Optional

# Third-party
import streamlit as st
import pandas as pd
import numpy as np

# Local
from utils.data_loader import load_protocols
from utils import branding
```

### Type Hints

```python
# Modern syntax (Python 3.10+)
def search_protocols(
    protocols: list[dict],
    query: str,
    limit: int = 50
) -> list[dict]:
    ...

# Union types
def get_protocol(protocols: list[dict], protocol_id: str) -> dict | None:
    ...

# Complex types
from typing import TypedDict

class QuizQuestion(TypedDict):
    question: str
    options: list[str]
    answer: str
    explain: str
    category: str
    difficulty: str
    protocol_id: str
```

### Docstrings (Google Style)

```python
def generate_quiz(
    protocols: list[dict],
    n: int = 10,
    seed: int | None = None,
) -> list[QuizQuestion]:
    """Generate n unique multiple-choice questions from protocol database.
    
    Args:
        protocols: Full protocol list from load_protocols().
        n: Number of questions to generate.
        seed: Random seed for reproducibility.
        
    Returns:
        List of question dicts with keys: question, options, answer, explain,
        category, difficulty, protocol_id.
        
    Raises:
        ValueError: If n <= 0 or protocols list is empty.
    """
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `data_loader.py` |
| Classes | PascalCase | `QuizEngine` |
| Functions | snake_case | `generate_quiz` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_STATE` |
| Variables | snake_case | `protocol_count` |
| Private | `_leading_underscore` | `_internal_helper` |

### Error Handling

```python
# Raise ValueError for invalid arguments (not ZeroDivisionError)
def uart_bit_timing(f_clk: int, baud: int, oversampling: int = 16) -> dict:
    if f_clk <= 0:
        raise ValueError("f_clk must be positive")
    if baud <= 0:
        raise ValueError("baud must be positive")
    # ...

# Use specific exceptions
try:
    with open(path) as f:
        data = json.load(f)
except (OSError, json.JSONDecodeError) as e:
    logger.error(f"Failed to load {path}: {e}")
    return DEFAULT_STATE
```

### Async/Await

Not used in current codebase (Streamlit is synchronous). If needed:
- Use `asyncio` for I/O
- Keep Streamlit callbacks sync

### Streamlit Patterns

```python
# Cache expensive operations
@st.cache_data
def load_protocols() -> list[dict]:
    ...

# Session state for user data
if "user_state" not in st.session_state:
    st.session_state.user_state = load_state()

# Columns for layout
col1, col2 = st.columns([2, 1])

# Expanders for progressive disclosure
with st.expander("Advanced Options"):
    ...

# Form for batch input
with st.form("quiz_config"):
    ...
    submitted = st.form_submit_button("Start Quiz")
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Something unexpected but handled")
logger.error("Error occurred", exc_info=True)
```

Configured in `app.py`:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

---

## Pre-commit Hooks

Installed via `pre-commit install`. Runs on every commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

Run manually: `pre-commit run --all-files`

---

## IDE Setup

### VS Code (`.vscode/settings.json`)

```json
{
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.testing.pytestEnabled": false,
    "files.insertFinalNewline": true,
    "files.trimTrailingWhitespace": true
}
```

### PyCharm

- Enable Ruff: Settings → Tools → Ruff
- Set as formatter and linter
- Configure line length: 100

---

## See Also

- [Contributing](contributing.md)
- [Testing](testing.md)
- [CI/CD](ci-cd.md)
- [Pre-commit](pre-commit.md)
- [Ruff Documentation](https://docs.astral.sh/ruff/)