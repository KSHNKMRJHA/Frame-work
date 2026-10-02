# Desktop Build

Create a standalone executable (.exe on Windows, binary on macOS/Linux) that runs without Python installed.

## Prerequisites

```bash
# Install desktop dependencies
pip install -e .[desktop]
# or
pip install pyinstaller>=6.0
```

## Windows (.exe)

```bash
# Build
build_scripts\build_exe.bat

# Output: dist\FrameWork.exe
```

### build_exe.bat contents

```bat
@echo off
pyinstaller --clean --noconfirm ^
  --name FrameWork ^
  --icon=assets/icon.ico ^
  --add-data "data;data" ^
  --add-data "pages;pages" ^
  --add-data "utils;utils" ^
  --add-data ".streamlit;.streamlit" ^
  --add-data "technical_profiles.py;." ^
  --add-data "build_data.py;." ^
  --add-data "README.md;." ^
  --add-data "LICENSE;." ^
  --hidden-import=streamlit ^
  --hidden-import=plotly ^
  --hidden-import=networkx ^
  --hidden-import=matplotlib ^
  --hidden-import=pandas ^
  --hidden-import=numpy ^
  --hidden-import=utils.branding ^
  --hidden-import=utils.data_loader ^
  --hidden-import=utils.diagrams ^
  --hidden-import=utils.mindmap ^
  --hidden-import=utils.quiz_engine ^
  --hidden-import=utils.science ^
  --hidden-import=utils.state ^
  --hidden-import=pages.1_📚_Encyclopedia ^
  --hidden-import=pages.2_🕰️_Timeline_History ^
  --hidden-import=pages.3_🗺️_Mindmap ^
  --hidden-import=pages.4_⚖️_Compare ^
  --hidden-import=pages.5_🧠_Quiz_Assessment ^
  --hidden-import=pages.6_🎮_Puzzles_Games ^
  --hidden-import=pages.7_🔬_Science_Math_Lab ^
  --hidden-import=pages.8_🌍_Geography_Origins ^
  --hidden-import=pages.9_⚙️_Settings_Profile ^
  --hidden-import=pages.10_ℹ️_Info ^
  app.py
```

## macOS / Linux (Binary)

```bash
# Make executable
chmod +x build_scripts/build_exe.sh

# Build
bash build_scripts/build_exe.sh

# Output: dist/FrameWork (or dist/FrameWork.app on macOS)
```

### build_exe.sh contents

```bash
#!/usr/bin/env bash
set -euo pipefail

pyinstaller --clean --noconfirm \
  --name FrameWork \
  --icon=assets/icon.icns \
  --add-data "data:data" \
  --add-data "pages:pages" \
  --add-data "utils:utils" \
  --add-data ".streamlit:.streamlit" \
  --add-data "technical_profiles.py:." \
  --add-data "build_data.py:." \
  --add-data "README.md:." \
  --add-data "LICENSE:." \
  --hidden-import=streamlit \
  --hidden-import=plotly \
  --hidden-import=networkx \
  --hidden-import=matplotlib \
  --hidden-import=pandas \
  --hidden-import=numpy \
  --hidden-import=utils.branding \
  --hidden-import=utils.data_loader \
  --hidden-import=utils.diagrams \
  --hidden-import=utils.mindmap \
  --hidden-import=utils.quiz_engine \
  --hidden-import=utils.science \
  --hidden-import=utils.state \
  --hidden-import=pages.1_📚_Encyclopedia \
  --hidden-import=pages.2_🕰️_Timeline_History \
  --hidden-import=pages.3_🗺️_Mindmap \
  --hidden-import=pages.4_⚖️_Compare \
  --hidden-import=pages.5_🧠_Quiz_Assessment \
  --hidden-import=pages.6_🎮_Puzzles_Games \
  --hidden-import=pages.7_🔬_Science_Math_Lab \
  --hidden-import=pages.8_🌍_Geography_Origins \
  --hidden-import=pages.9_⚙️_Settings_Profile \
  --hidden-import=pages.10_ℹ️_Info \
  app.py
```

## Build Stamp

The build number (git commit hash) is embedded via `build_scripts/stamp_build.py`:

```bash
# Runs automatically during PyInstaller build
python build_scripts/stamp_build.py
```

This writes `utils/_build_stamp.txt` which the frozen app reads when no `.git` is present.

## Distribution

| Platform | Artifact | Notes |
|----------|----------|-------|
| Windows | `dist/FrameWork.exe` | ~150-200 MB, includes Python runtime |
| macOS | `dist/FrameWork.app` | App bundle, codesign for distribution |
| Linux | `dist/FrameWork` | ELF binary, may need `patchelf` for portability |

## Data Directory in Frozen Builds

When frozen, the app detects `sys.frozen` and writes progress to:

```python
# utils/state.py logic
if getattr(sys, 'frozen', False):
    # PyInstaller bundle
    base = Path(sys.executable).parent
else:
    # Source run
    base = Path(__file__).parent.parent / "data"
```

**Never** write inside the PyInstaller temp bundle (`sys._MEIPASS`) — it's deleted on exit.

## Testing the Build

```bash
# Windows
dist\FrameWork.exe

# macOS
open dist/FrameWork.app

# Linux
./dist/FrameWork
```

Verify:
1. App launches without Python installed
2. All 10 modules accessible
3. Progress persists across restarts
4. Diagrams render correctly

## CI Integration

The GitHub Actions workflow can build and upload artifacts:

```yaml
# .github/workflows/release.yml (add to your workflows)
- name: Build Windows executable
  run: build_scripts\build_exe.bat
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: FrameWork-windows
    path: dist/FrameWork.exe
```

## Troubleshooting

### `ModuleNotFoundError` in frozen app

Add missing modules to `--hidden-import` in build script.

### Large executable size

- Use `--exclude-module` for unused stdlib modules
- Consider `--onefile` for single-file (slower startup)
- UPX compression: `pyinstaller --upx-dir=... --onefile ...`

### macOS Gatekeeper / "unidentified developer"

```bash
# Ad-hoc sign for local testing
codesign --force --deep --sign - dist/FrameWork.app

# For distribution: use Apple Developer ID certificate
codesign --force --deep --sign "Developer ID Application: Your Name" dist/FrameWork.app
```

### Linux: `libGL.so.1` missing

```bash
sudo apt install libgl1-mesa-glx  # Ubuntu/Debian
sudo dnf install mesa-libGL       # Fedora
```

## Next Steps

- [Web Deployment](web.md) — Cloud hosting
- [Mobile (Android)](mobile.md) — APK build
- [Release Process](../releases/build-process.md) — Versioning and packaging