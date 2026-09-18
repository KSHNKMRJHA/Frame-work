# FrameWork — Mobile Companion

A lightweight Kivy app (quiz + encyclopedia browser) that runs on **desktop
(Windows/macOS/Linux) and Android**, built from the same protocol database as
the full Streamlit edition.

## Run on desktop (fastest way to try it)

```bash
pip install kivy
cd kivy_mobile
python main.py
```

## Build a real Android APK

You need a Linux machine (or WSL2 on Windows) for Buildozer — it downloads
and configures the Android SDK/NDK automatically on first run.

```bash
pip install buildozer cython
cd kivy_mobile
buildozer -v android debug
```

The first build takes 15–40 minutes (downloading SDK/NDK/toolchains). The
resulting APK will appear in `kivy_mobile/bin/framework-1.0.0-debug.apk`.

Install it on a connected device/emulator with:

```bash
buildozer android deploy run
```

### Notes & tips
- Add a `1024x1024` `icon.png` in this folder before building for a custom app icon (referenced in `buildozer.spec`).
- To publish to the Google Play Store, build a **release** APK/AAB instead
  (`buildozer android release`) and follow Google's signing requirements.
- If you update `data/protocols.json` in the main project, copy the updated
  file into `kivy_mobile/data/protocols.json` before rebuilding so the mobile
  app stays in sync:
  ```bash
  cp ../data/protocols.json ./data/protocols.json
  ```
- `quiz_logic.py` is a self-contained copy of the main app's quiz engine
  (pure Python, no Streamlit dependency) so this folder can be built
  completely independently of the rest of the repository.
