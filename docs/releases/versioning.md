# Versioning

FrameWork uses a **dual versioning scheme**: Semantic Version for releases + Git Commit for builds.

## Semantic Version

Defined in **one place**: `utils/branding.py`

```python
VERSION = "1.0.0"  # MAJOR.MINOR.PATCH
```

### Version Bump Rules

| Change | Bump | Example |
|--------|------|---------|
| Breaking API/UX change | MAJOR | 1.0.0 → 2.0.0 |
| New feature/module | MINOR | 1.0.0 → 1.1.0 |
| Bug fix, minor improvement | PATCH | 1.0.0 → 1.0.1 |

### Version Consumers

| Consumer | Source |
|----------|--------|
| Running app (sidebar, footer) | `utils.branding.VERSION` |
| `pyproject.toml` (pip install) | Dynamic: `attr = "utils.branding.VERSION"` |
| PyInstaller build | Reads `VERSION` at build time |
| Streamlit Cloud | Reads `VERSION` at deploy |
| GitHub Release | Git tag `v{VERSION}` |

---

## Build Number (Git Commit)

**Never hand-maintained.** Always the short git commit hash (7 chars).

### Resolution Order

| Priority | Source | Context |
|----------|--------|---------|
| 1 | `FRAMEWORK_BUILD_COMMIT` env var | CI release builds |
| 2 | `git rev-parse --short=7 HEAD` | Source runs, Streamlit Cloud |
| 3 | `utils/_build_stamp.txt` | Frozen builds (no `.git`) |
| 4 | `"dev"` | Fallback |

### Implementation

`utils/branding.py`:

```python
import os
import subprocess
from pathlib import Path

def get_build_commit() -> str:
    # 1. CI override
    if commit := os.environ.get("FRAMEWORK_BUILD_COMMIT"):
        return commit[:7]
    
    # 2. Live git repo
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=7", "HEAD"],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    
    # 3. Build stamp (frozen)
    stamp_file = Path(__file__).parent / "_build_stamp.txt"
    if stamp_file.exists():
        return stamp_file.read_text().strip()[:7]
    
    # 4. Fallback
    return "dev"

def version_label() -> str:
    return f"v{VERSION} · {get_build_channel()} · commit {get_build_commit()}"

def build_line() -> str:
    commit = get_build_commit()
    channel = get_build_channel()
    return f"{channel} build {commit}" if commit != "dev" else "dev build"
```

### Build Stamp Generation

`build_scripts/stamp_build.py` runs during PyInstaller build:

```python
import subprocess
from pathlib import Path

result = subprocess.run(
    ["git", "rev-parse", "--short=7", "HEAD"],
    capture_output=True, text=True, cwd=Path(__file__).parent.parent
)
commit = result.stdout.strip() if result.returncode == 0 else "unknown"

stamp_file = Path(__file__).parent.parent / "utils" / "_build_stamp.txt"
stamp_file.write_text(commit)
```

Included in frozen app via `--add-data "utils/_build_stamp.txt;utils"`.

---

## Build Channel

From `FRAMEWORK_BUILD_CHANNEL` env var (default: `"stable"`).

| Channel | Use Case |
|---------|----------|
| `stable` | Main branch, tagged releases |
| `beta` | Pre-release testing |
| `dev` | Development builds |
| `nightly` | Automated nightly (future) |

---

## Display in UI

```python
# Home page hero
st.markdown(f"""
    <h1>{APP_ICON} {APP_NAME}
    <span class="version-badge">{version_label()}</span>
</h1>
""", unsafe_allow_html=True)

# Sidebar
st.caption(build_line())

# Footer
st.caption(f"{version_label()} | MIT License")
```

Output example:
```
v1.0.0 · stable · commit a1b2c3d
```

---

## Release Process

### 1. Prepare Release

```bash
# Update version
# Edit utils/branding.py: VERSION = "1.1.0"

# Update changelog
# Edit CHANGELOG.md (see releases/changelog.md)

# Commit
git add utils/branding.py CHANGELOG.md
git commit -m "chore: release v1.1.0"
```

### 2. Tag and Push

```bash
git tag v1.1.0
git push origin main --tags
```

### 3. GitHub Actions

- CI runs on tag push
- Release workflow builds desktop (Win/macOS/Linux) + mobile APK
- Creates GitHub Release with artifacts
- Streamlit Cloud auto-deploys from `main`

### 4. Verify

- Check GitHub Release artifacts
- Test `.exe` on Windows
- Verify Streamlit Cloud deployment
- Announce

---

## Changelog

Maintained in `CHANGELOG.md` (root). Format: [Keep a Changelog](https://keepachangelog.com/).

```markdown
# Changelog

## [1.1.0] - 2024-01-15

### Added
- MIPI D-PHY v2.0 protocol
- Timing diagram generator (Wavedrom)

### Fixed
- CAN bit timing sample point calculation
- UART 115200 baud error at 16 MHz

### Changed
- Quiz engine: new "guess protocol" puzzle type
```

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2024-01-15 | Initial release: 118 protocols, 10 modules |

---

## See Also

- [Architecture: Versioning](../architecture/adrs/0010-versioning-build-stamp.md)
- [Build Process](build-process.md)
- [Changelog](changelog.md)
- [Branding API](../api/branding.md)