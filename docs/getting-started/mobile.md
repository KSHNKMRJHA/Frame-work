# Mobile (Android)

Build and install the Kivy-based Android companion app.

## Prerequisites

### Linux (Recommended)

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
  git zip unzip openjdk-17-jdk python3-pip \
  build-essential libssl-dev libffi-dev python3-dev \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
  zlib1g-dev

# Install Buildozer
pip install buildozer cython
```

### macOS

```bash
brew install git openjdk@17 python3
pip install buildozer cython
# May need: brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi
```

### Windows: Use WSL2 (Required)

Buildozer does **not** run natively on Windows. Use WSL2 with Ubuntu:

```powershell
# In PowerShell as Admin
wsl --install -d Ubuntu

# Then in Ubuntu terminal, follow Linux instructions above
```

---

## Project Structure

```
kivy_mobile/
├── main.py                 # Kivy app entry point
├── quiz_logic.py           # Synced from utils/quiz_engine.py
├── data/
│   └── protocols.json      # Synced from data/protocols.json
├── buildozer.spec          # Buildozer configuration
└── README.md               # Mobile-specific docs
```

---

## Sync Mobile Sources

Before building, sync from desktop source:

```bash
python build_scripts/sync_mobile.py
```

This copies:
- `data/protocols.json` → `kivy_mobile/data/protocols.json`
- `utils/quiz_engine.py` → `kivy_mobile/quiz_logic.py`

---

## Build Debug APK

```bash
cd kivy_mobile

# First build (downloads SDK/NDK, takes 10-30 min)
buildozer -v android debug

# Subsequent builds (faster)
buildozer android debug
```

Output: `bin/framework-1.0.0-armeabi-v7a-debug.apk`

---

## Build Release APK (for Play Store)

```bash
# Generate keystore (one time)
keytool -genkey -v -keystore framework-release.keystore \
  -alias framework -keyalg RSA -keysize 2048 -validity 10000

# Configure buildozer.spec with keystore details
# Then build release
buildozer android release
```

Output: `bin/framework-1.0.0-armeabi-v7a-release.apk` (signed)

---

## Buildozer Configuration

Key settings in `kivy_mobile/buildozer.spec`:

```ini
[app]
title = FrameWork
package.name = framework
package.domain = org.frameworks
source.dir = .
source.include_exts = py,png,json,kv,atlas
version = 1.0.0
requirements = python3,kivy,pandas,numpy,plotly,networkx,matplotlib
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 31
minapi = 21
ndk_api = 21
archs = arm64-v8a, armeabi-v7a
permisions = INTERNET,ACCESS_NETWORK_STATE
```

---

## Install on Device

### USB Debugging

```bash
# Enable USB debugging on device, then:
adb install -r bin/framework-1.0.0-armeabi-v7a-debug.apk
```

### Wireless (Android 11+)

```bash
adb pair <ip>:<port>  # From Settings > Developer > Wireless debugging
adb connect <ip>:<port>
adb install -r bin/framework-1.0.0-armeabi-v7a-debug.apk
```

---

## Testing Checklist

- [ ] App launches without crash
- [ ] All 10 modules accessible via navigation
- [ ] Encyclopedia loads protocols with diagrams
- [ ] Quiz generates questions correctly
- [ ] Science Lab calculators work
- [ ] Progress persists across restarts
- [ ] Orientation changes handled
- [ ] Back button works correctly

---

## Common Issues

### `buildozer: command not found`

```bash
export PATH=$PATH:~/.local/bin
# Add to ~/.bashrc for persistence
```

### SDK/NDK license not accepted

```bash
# Run once to accept licenses
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses
```

### `ModuleNotFoundError` in APK

Add missing modules to `requirements` in `buildozer.spec`:

```ini
requirements = python3,kivy,pandas,numpy,plotly,networkx,matplotlib,your_missing_module
```

### Build fails with "out of memory"

```bash
# Increase Gradle memory
export GRADLE_OPTS="-Xmx4g"
buildozer android debug
```

### App crashes on launch

Check logs:

```bash
adb logcat -s python:V
# Or filter for your package
adb logcat | grep org.frameworks
```

---

## Architecture Notes

| Aspect | Desktop (Streamlit) | Mobile (Kivy) |
|--------|---------------------|---------------|
| UI Framework | Streamlit (web-based) | Kivy (native OpenGL) |
| Quiz Logic | `utils/quiz_engine.py` | `kivy_mobile/quiz_logic.py` (synced) |
| Data | `data/protocols.json` | `kivy_mobile/data/protocols.json` (synced) |
| Diagrams | Matplotlib (server-rendered) | Simplified / text-based |
| Persistence | `data/user_state.json` | `kivy_mobile/user_state.json` |
| Sync Script | `build_scripts/sync_mobile.py` | — |

The mobile app is a **companion** — focused on quiz/puzzle/encyclopedia. Full diagram rendering and timeline visualizations are desktop/web only.

---

## CI for Mobile

Add to `.github/workflows/android.yml`:

```yaml
name: Android Build

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install buildozer
        run: pip install buildozer cython
      - name: Install system deps
        run: |
          sudo apt update
          sudo apt install -y openjdk-17-jdk unzip zip libssl-dev libffi-dev
      - name: Sync mobile
        run: python build_scripts/sync_mobile.py
      - name: Build APK
        working-directory: kivy_mobile
        run: buildozer android debug
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: framework-apk
          path: kivy_mobile/bin/*.apk
```

---

## Next Steps

- [Desktop Build](desktop.md) — Standalone executable
- [Web Deployment](web.md) — Cloud hosting
- [Architecture: Module Design](../architecture/modules.md) — Mobile vs desktop differences