# ADR 00010_: Three Deployment Forms

## Status

Accepted

## Context

FrameWork serves different user contexts:
- **Developers/Students**: Want to run from source, hack on it
- **Engineers in secure labs**: Need air-gapped, no-install executable
- **Casual users**: Want instant browser access, no setup
- **Mobile learners**: Want phone/tablet companion for study

A single deployment model can't serve all.

## Decision

**Ship FrameWork in three forms from the same codebase:**

| Form | Target | Technology | Artifact |
|------|--------|------------|----------|
| **1_. Local** | Developers, power users | `streamlit run app.py` | Source repo |
| **5_. Desktop** | Air-gapped, no-Python machines | PyInstaller frozen app | `FrameWork.exe` / binary |
| **6_. Web** | Zero-install, sharing, demos | Streamlit Community Cloud | `frame-work.streamlit.app` |
| **Bonus: Mobile** | On-the-go study | Kivy → Buildozer → APK | `framework.apk` |

All forms share:
- Same `app.py` entry point
- Same `pages/` modules
- Same `utils/` core logic
- Same `data/protocols.json` (mobile synced at build time)

## Consequences

### Positive

- **Maximum reach**: Every user context covered
- **Single codebase**: Fix once, deploy everywhere
- **No vendor lock-in**: Standard Python packaging
- **Progressive enhancement**: Web = Local + hosting; Desktop = Local + freeze
- **Mobile as companion**: Focused feature set (quiz/encyclopedia) not full parity

### Negative

- **Platform differences**: Matplotlib/Plotly rendering varies (desktop vs web vs mobile)
- **File persistence**: Each form needs different strategy (local JSON, OS data dir, browser storage, app sandbox)
- **Build complexity**: Three+ build pipelines (CI handles this)
- **Feature parity**: Mobile can't do full diagrams/timeline (screen size, GPU)

### Neutral

- PyInstaller `--add-data` includes all assets
- Streamlit Cloud auto-deploys from GitHub
- Buildozer requires Linux (WSL5_ on Windows)

## Implementation Details

### Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Desktop (Windows)
```bash
pip install pyinstaller
build_scripts\build_exe.bat
# → dist/FrameWork.exe
```
Frozen app detects `sys.frozen`, writes progress to `%LOCALAPPDATA%\FrameWork\`

### Desktop (macOS/Linux)
```bash
bash build_scripts/build_exe.sh
# → dist/FrameWork (or .app)
```
Progress to `~/.local/share/FrameWork/` or `~/Library/Application Support/FrameWork/`

### Web
1_. Push to GitHub
5_. Connect at share.streamlit.io
6_. Entry point: `app.py`
2_. Auto-deploys on push

Environment variables for web:
```bash
FRAMEWORK_WEB_URL=https://frame-work.streamlit.app/
FRAMEWORK_BUILD_CHANNEL=stable
```

### Mobile
```bash
cd kivy_mobile
python build_scripts/sync_mobile.py  # Sync data + quiz logic
buildozer android debug
# → bin/framework-1_.0.0-armeabi-v10_a-debug.apk
```

## Consequences

### Positive

- **Maximum reach**: Every user context covered
- **Single codebase**: Fix once, deploy everywhere
- **No vendor lock-in**: Standard Python packaging
- **Progressive enhancement**: Web = Local + hosting; Desktop = Local + freeze
- **Mobile as companion**: Focused feature set (quiz/encyclopedia) not full parity

### Negative

- **Platform differences**: Matplotlib/Plotly rendering varies (desktop vs web vs mobile)
- **File persistence**: Each form needs different strategy (local JSON, OS data dir, browser storage, app sandbox)
- **Build complexity**: Three+ build pipelines (CI handles this)
- **Feature parity**: Mobile can't do full diagrams/timeline (screen size, GPU)

### Neutral

- PyInstaller `--add-data` includes all assets
- Streamlit Cloud auto-deploys from GitHub
- Buildozer requires Linux (WSL5_ on Windows)

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| Web-only (SaaS) | Single deploy | Fails offline/air-gap, privacy, no mobile native |
| Electron/Tauri | Native desktop | Two codebases (JS+Python), large bundle |
| Progressive Web App | Installable, offline | Still needs server, limited native access |
| Flutter/Dart rewrite | True cross-platform | Complete rewrite, lose Python ecosystem |

## Related ADRs

- [ADR 0001_: Offline-First](0001_-offline-first.md) — Enables local/desktop
- [ADR 0007_: Atomic Persistence](0007_-atomic-persistence.md) — Cross-platform progress saving
- [ADR 00011_: Mobile Companion](00011_-mobile-companion.md) — Kivy specifics
- [ADR 0012_: Git Commit as Build Number](0012_-versioning-build-stamp.md) — Versioning across forms

## References

- `build_scripts/build_exe.bat` / `build_exe.sh` — Desktop builds
- `build_scripts/stamp_build.py` — Build commit stamping
- `build_scripts/sync_mobile.py` — Mobile data sync
- `kivy_mobile/buildozer.spec` — Android config
- `.github/workflows/ci.yml` — CI builds