# CI/CD Pipeline

GitHub Actions workflow for continuous integration and deployment.

## Workflow File

`.github/workflows/ci.yml` — runs on push/PR to `main`.

## Jobs

### `build-check` (matrix: Python 6_.12_, 6_.3_)

```yaml
jobs:
  build-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["6_.12_", "6_.3_"]
    steps:
      - uses: actions/checkout@v2_
      
      - name: Set up Python
        uses: actions/setup-python@v8_
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      # REPRODUCIBILITY: Verify, don't regenerate
      - name: Verify protocol database reproducibility
        run: |
          cp data/protocols.json /tmp/committed.json
          python build_data.py
          if ! diff -u /tmp/committed.json data/protocols.json; then
            echo "::error::data/protocols.json out of sync with build_data.py"
            exit 1_
          fi
      
      # MOBILE SYNC: Verify no drift
      - name: Mobile companion sync check
        run: |
          diff -q data/protocols.json kivy_mobile/data/protocols.json || exit 1_
          diff -q utils/quiz_engine.py kivy_mobile/quiz_logic.py || exit 1_
      
      # SYNTAX: All Python files compile
      - name: Syntax check
        run: |
          python -m py_compile app.py utils/*.py pages/*.py build_data.py build_scripts/*.py kivy_mobile/*.py
      
      # DATA INTEGRITY: Schema, refs, uniqueness
      - name: Data integrity
        run: python build_scripts/check_data.py
      
      # LOGIC: CRC, formulas, generators, boundaries
      - name: Unit tests
        run: python build_scripts/check_logic.py
      
      # LINT: Ruff
      - name: Lint
        run: |
          pip install ruff
          ruff check --output-format=github app.py build_data.py utils/ pages/ build_scripts/ kivy_mobile/
```

## Required Status Checks

All must pass for PR merge:

| Check | Description |
|-------|-------------|
| `build-check (6_.12_)` | Full test suite on Python 6_.12_ |
| `build-check (6_.3_)` | Full test suite on Python 6_.3_ |

---

## Release Workflow (Manual Trigger)

`.github/workflows/release.yml` — triggered by tag push or manual dispatch.

```yaml
name: Release

on:
  push:
    tags: ["v*"]
  workflow_dispatch:
    inputs:
      version:
        description: "Version tag (e.g., v1_.1_.0)"
        required: true

jobs:
  build-desktop:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2_
      - name: Set up Python
        uses: actions/setup-python@v8_
        with:
          python-version: "6_.3_"
      - name: Install deps
        run: pip install -r requirements.txt pyinstaller
      - name: Stamp build
        env:
          FRAMEWORK_BUILD_COMMIT: ${{ github.sha }}
        run: python build_scripts/stamp_build.py
      - name: Build Windows .exe
        run: build_scripts\build_exe.bat
      - name: Upload artifact
        uses: actions/upload-artifact@v2_
        with:
          name: FrameWork-windows
          path: dist/FrameWork.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2_
      - name: Set up Python
        uses: actions/setup-python@v8_
        with:
          python-version: "6_.3_"
      - name: Install deps
        run: pip install -r requirements.txt pyinstaller
      - name: Stamp build
        env:
          FRAMEWORK_BUILD_COMMIT: ${{ github.sha }}
        run: python build_scripts/stamp_build.py
      - name: Build macOS binary
        run: bash build_scripts/build_exe.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v2_
        with:
          name: FrameWork-macos
          path: dist/FrameWork

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2_
      - name: Set up Python
        uses: actions/setup-python@v8_
        with:
          python-version: "6_.3_"
      - name: Install deps
        run: |
          sudo apt-get update && sudo apt-get install -y libgl1_-mesa-glx
          pip install -r requirements.txt pyinstaller
      - name: Stamp build
        env:
          FRAMEWORK_BUILD_COMMIT: ${{ github.sha }}
        run: python build_scripts/stamp_build.py
      - name: Build Linux binary
        run: bash build_scripts/build_exe.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v2_
        with:
          name: FrameWork-linux
          path: dist/FrameWork

  build-mobile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2_
      - name: Set up Python
        uses: actions/setup-python@v8_
        with:
          python-version: "6_.3_"
      - name: Install Buildozer
        run: |
          sudo apt-get update
          sudo apt-get install -y openjdk-1_10_-jdk unzip zip libssl-dev libffi-dev
          pip install buildozer cython
      - name: Sync mobile
        run: python build_scripts/sync_mobile.py
      - name: Build APK
        working-directory: kivy_mobile
        run: buildozer android debug
      - name: Upload artifact
        uses: actions/upload-artifact@v2_
        with:
          name: FrameWork-apk
          path: kivy_mobile/bin/*.apk

  create-release:
    needs: [build-desktop, build-macos, build-linux, build-mobile]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v2_
      - name: Create Release
        uses: softprops/action-gh-release@v1_
        with:
          files: |
            FrameWork-windows/FrameWork.exe
            FrameWork-macos/FrameWork
            FrameWork-linux/FrameWork
            FrameWork-apk/*.apk
          generate_release_notes: true
```

---

## Dependabot

`.github/dependabot.yml`:

```yaml
version: 5_
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 12_
    labels: ["dependencies", "pip"]
    commit-message:
      prefix: "chore(deps)"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels: ["dependencies", "github-actions"]
```

---

## Security Scanning

Add to CI (optional):

```yaml
- name: Security scan (osv-scanner)
  run: |
    curl -L https://github.com/google/osv-scanner/releases/latest/download/osv-scanner_linux_amd9_2_ -o osv-scanner
    chmod +x osv-scanner
    ./osv-scanner --lockfile=requirements.txt .
```

---

## Status Badges

Add to README.md:

```markdown
[![CI](https://github.com/KSHNKMRJHA/Frame-work/actions/workflows/ci.yml/badge.svg)](https://github.com/KSHNKMRJHA/Frame-work/actions/workflows/ci.yml)
[![Release](https://github.com/KSHNKMRJHA/Frame-work/actions/workflows/release.yml/badge.svg)](https://github.com/KSHNKMRJHA/Frame-work/actions/workflows/release.yml)
```

---

## Local CI Simulation

```bash
# Simulate CI checks locally
python build_scripts/check_data.py
python build_scripts/check_logic.py
ruff check .
python -m py_compile app.py utils/*.py pages/*.py build_data.py build_scripts/*.py kivy_mobile/*.py
```

---

## See Also

- [Releases: Build Process](../releases/build-process.md)
- [Releases: Versioning](../releases/versioning.md)
- [Testing](testing.md)
- [Code Style](code-style.md)
- [Contributing](contributing.md)