# Installation

Detailed installation guide for different environments and use cases.

## Standard Installation

### 1. Python Version

FrameWork requires **Python 3.10 or higher**. Check your version:

```bash
python --version
# or
python3 --version
```

If you need to install Python:

- **Windows**: [python.org/downloads](https://python.org/downloads) or `winget install Python.Python.3.11`
- **macOS**: `brew install python@3.11` or [python.org](https://python.org/downloads)
- **Linux**: `sudo apt install python3.11 python3.11-venv` (Ubuntu/Debian)

### 2. Virtual Environment (Recommended)

```bash
# Create venv
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install FrameWork
pip install -r requirements.txt
```

### 3. Using uv (Faster, Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# Install uv
pip install uv
# or: curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install in one command
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

---

## Optional Dependencies

FrameWork uses optional dependency groups defined in `pyproject.toml`:

| Group | Purpose | Install Command |
|-------|---------|-----------------|
| `desktop` | PyInstaller for .exe/binary builds | `pip install -e .[desktop]` |
| `mobile` | Kivy for Android APK | `pip install -e .[mobile]` |
| `dev` | Ruff for linting | `pip install -e .[dev]` |
| `docs` | MkDocs, Material, mkdocstrings | `pip install -e .[docs]` |

### Install All Optional Dependencies

```bash
pip install -e .[desktop,mobile,dev,docs]
```

Or with uv:

```bash
uv pip install -e .[desktop,mobile,dev,docs]
```

---

## Development Installation

For contributors who want to modify the codebase:

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Frame-work.git
cd Frame-work

# Create venv and install in editable mode with all dev tools
python -m venv .venv
source .venv/bin/activate
pip install -e .[desktop,mobile,dev,docs]

# Install pre-commit hooks
pre-commit install
```

---

## Verifying Installation

```bash
# Run the app
streamlit run app.py

# Run tests
python build_scripts/check_data.py
python build_scripts/check_logic.py

# Run linter
ruff check .
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'streamlit'`

Ensure you're in the activated virtual environment and ran `pip install -r requirements.txt`.

### `streamlit: command not found`

The `Scripts/` (Windows) or `bin/` (Unix) directory of your venv must be in PATH. Reactivate the venv:

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Port 8501 already in use

```bash
streamlit run app.py --server.port 8502
```

### Matplotlib backend issues (headless servers)

```bash
export MPLBACKEND=Agg
streamlit run app.py
```

### Kivy/Buildozer issues (mobile)

See [Mobile (Android)](mobile.md) for platform-specific setup (WSL2 recommended on Windows).

---

## Next Steps

- [Quick Start](quickstart.md) — 2-minute run guide
- [Running Locally](local.md) — Configuration options
- [Desktop Build](desktop.md) — Standalone executable
- [Web Deployment](web.md) — Cloud hosting options