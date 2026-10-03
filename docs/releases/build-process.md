# Build Process

How FrameWork artifacts are built for each deployment target.

## Overview

| Target | Script | Output | Platform |
|--------|--------|--------|----------|
| Local dev | `streamlit run app.py` | Running server | Any |
| Windows .exe | `build_scripts/build_exe.bat` | `dist/FrameWork.exe` | Windows |
| macOS binary | `build_scripts/build_exe.sh` | `dist/FrameWork` | macOS |
| Linux binary | `build_scripts/build_exe.sh` | `dist/FrameWork` | Linux |
| Android APK | `kivy_mobile/buildozer` | `bin/*.apk` | Android |
| Web | Streamlit Cloud | Live URL | Browser |
| Docker | `Dockerfile` | Image | Any container host |

---

## Prerequisites

```bash
# Desktop builds
pip install pyinstaller>=6.0

# Mobile builds (Linux/WSL2 only)
pip install buildozer cython
# System deps: openjdk-17-jdk, zip, unzip, libssl-dev, libffi-dev, etc.

# Docker
docker build -t framework .
```

---

## Desktop Build (PyInstaller)

### Windows (`build_exe.bat`)

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

### macOS/Linux (`build_exe.sh`)

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

### Key PyInstaller Options

| Option | Purpose |
|--------|---------|
| `--clean` | Clean cache before build |
| `--noconfirm` | Overwrite output without prompt |
| `--name` | Executable name |
| `--icon` | Application icon |
| `--add-data` | Include data files (src:dest) |
| `--hidden-import` | Force include modules not auto-detected |

### Build Stamp Integration

Both scripts should run stamp first:

```bash
# Windows
python build_scripts/stamp_build.py
build_scripts\build_exe.bat

# Unix
python build_scripts/stamp_build.py
bash build_scripts/build_exe.sh
```

`stamp_build.py` writes `utils/_build_stamp.txt` which frozen app reads when no `.git`.

---

## Output Structure

```
dist/
└── FrameWork.exe          # Windows
    # or
└── FrameWork              # Linux/macOS binary
    # or
└── FrameWork.app/         # macOS app bundle
```

### Size Estimates

| Platform | Size | Notes |
|----------|------|-------|
| Windows | ~180 MB | Includes Python 3.11 + all deps |
| macOS | ~200 MB | Universal2 (arm64 + x86_64) |
| Linux | ~150 MB | glibc-dependent |

---

## Mobile Build (Android)

### Prerequisites (Linux/WSL2)

```bash
sudo apt update && sudo apt install -y \
  git zip unzip openjdk-17-jdk python3-pip \
  build-essential libssl-dev libffi-dev python3-dev \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
  zlib1g-dev

pip install buildozer cython
```

### Build Steps

```bash
cd kivy_mobile

# Sync from desktop source (critical!)
python ../build_scripts/sync_mobile.py

# First build (downloads SDK/NDK, 10-30 min)
buildozer -v android debug

# Subsequent builds
buildozer android debug
```

### Output

```
kivy_mobile/bin/framework-1.0.0-armeabi-v7a-debug.apk
```

### Release Build

```bash
# Generate keystore (once)
keytool -genkey -v -keystore framework-release.keystore \
  -alias framework -keyalg RSA -keysize 2048 -validity 10000

# Edit buildozer.spec with keystore info
# Then:
buildozer android release
```

Output: `bin/framework-1.0.0-armeabi-v7a-release.apk` (signed)

---

## Web Deployment (Streamlit Cloud)

### Automatic (Recommended)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. New app → Select repo → Branch `main` → Entry point `app.py`
4. Deploy

### Environment Variables (Streamlit Cloud Secrets)

```toml
# .streamlit/secrets.toml (in Streamlit Cloud dashboard)
FRAMEWORK_WEB_URL = "https://frame-work.streamlit.app/"
FRAMEWORK_BUILD_CHANNEL = "stable"
```

### Custom Domain

1. Add CNAME: `framework.yourdomain.com` → `frame-work.streamlit.app`
2. Set `FRAMEWORK_WEB_URL` in secrets
3. Streamlit provisions TLS automatically

---

## Docker Build

### Dockerfile

```dockerfile
# Multi-stage for smaller image
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Runtime deps for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

### Build & Run

```bash
docker build -t framework .
docker run -p 8501:8501 framework
```

### Docker Compose

```yaml
version: '3.8'
services:
  framework:
    build: .
    ports:
      - "8501:8501"
    environment:
      - FRAMEWORK_WEB_URL=https://your-domain.com
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Verification Checklist

After any build:

- [ ] App launches without error
- [ ] All 10 modules accessible
- [ ] Encyclopedia: protocols load, diagrams render
- [ ] Quiz: generates questions, XP awards
- [ ] Puzzles: all 3 types work
- [ ] Science Lab: calculators compute correctly
- [ ] Timeline: interactive Plotly chart
- [ ] Mind Map: NetworkX graph renders
- [ ] Compare: table + speed chart
- [ ] Geography: world map + country view
- [ ] Settings: export/import/reset work
- [ ] Progress persists across restarts
- [ ] Version/build info displayed correctly

---

## Troubleshooting

### PyInstaller: ModuleNotFoundError

Add missing module to `--hidden-import` in build script.

### PyInstaller: Large executable

```bash
# Exclude unused stdlib modules
--exclude-module=tkinter --exclude-module=test --exclude-module=unittest

# Single file (slower startup)
--onefile

# UPX compression (if installed)
--upx-dir=/path/to/upx
```

### Buildozer: SDK license not accepted

```bash
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses
```

### Buildozer: Out of memory

```bash
export GRADLE_OPTS="-Xmx4g"
buildozer android debug
```

### Streamlit Cloud: Deploy fails

- Check `requirements.txt` for incompatible versions
- Verify `app.py` is entry point
- Check logs in Streamlit Cloud dashboard

---

## See Also

- [Versioning](versioning.md)
- [Changelog](changelog.md)
- [Architecture: Three Deployment Forms](../architecture/adrs/0007-three-deployment-forms.md)
- [Architecture: Versioning](../architecture/adrs/0010-versioning-build-stamp.md)