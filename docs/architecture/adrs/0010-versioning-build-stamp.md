# ADR 0010: Git Commit as Build Number

## Status

Accepted

## Context

FrameWork needs a version identifier for:
- Display in UI (sidebar, footer, about page)
- Bug reports (user says "I'm on v1.0.0 commit abc1234")
- Reproducibility (which exact code produced this build)
- Release automation (CI tags releases)

Traditional versioning (SemVer + manual bump) is error-prone and disconnected from git history.

## Decision

**The build number is the short git commit hash (7 hex chars). It is never hand-maintained.**

### Resolution Order

| Priority | Source | When It Applies |
|----------|--------|-----------------|
| 1 | `FRAMEWORK_BUILD_COMMIT` env var | CI release stamping (always wins) |
| 2 | Live `.git` in working tree | Running from source, Streamlit Cloud |
| 3 | `utils/_build_stamp.txt` | Packaged builds (no `.git`), written by `stamp_build.py` |
| 4 | — | Unresolvable → `"dev"` |

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
    
    # 3. Build stamp file (frozen builds)
    stamp_file = Path(__file__).parent / "_build_stamp.txt"
    if stamp_file.exists():
        return stamp_file.read_text().strip()[:7]
    
    # 4. Fallback
    return "dev"

def version_label() -> str:
    from utils.branding import VERSION
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

def main():
    # Get commit from git (available at build time)
    result = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent
    )
    commit = result.stdout.strip() if result.returncode == 0 else "unknown"
    
    # Write stamp file (bundled into .exe)
    stamp_file = Path(__file__).parent.parent / "utils" / "_build_stamp.txt"
    stamp_file.write_text(commit)
    print(f"Build stamp: {commit}")

if __name__ == "__main__":
    main()
```

PyInstaller `--add-data` includes `utils/_build_stamp.txt` in the frozen app.

### Version Display

UI shows:
```
v1.0.0 · stable · commit a1b2c3d
```

### CI Release Stamping

```yaml
# .github/workflows/release.yml
- name: Build with commit stamp
  env:
    FRAMEWORK_BUILD_COMMIT: ${{ github.sha }}
  run: |
    python build_scripts/stamp_build.py
    build_scripts/build_exe.bat
```

## Consequences

### Positive

- **Always accurate**: Build number = exact commit, never stale
- **Zero maintenance**: No version bump scripts, no changelog version sync
- **Traceable**: Bug report → commit → exact code
- **Reproducible**: Frozen build knows its origin
- **CI-friendly**: Env var override for release automation

### Negative

- **Not SemVer**: `v1.0.0 · commit abc1234` doesn't convey breaking changes
- **Requires git at build time** (for source/stamp) or env var (CI)
- **Short hash collision**: 7 hex chars = 268M possibilities (acceptable)

### Neutral

- Semantic version (`VERSION` in `branding.py`) still maintained for releases
- Build channel (`stable`, `beta`, `dev`) from `FRAMEWORK_BUILD_CHANNEL` env var

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| Manual SemVer bump | Clear release signals | Human error, drift from git, extra step |
| `setuptools_scm` | Auto from git tags | Extra dep, complex config, frozen builds tricky |
| Date-based (YYYY.MM.DD) | Chronological | No code correlation, same day = same version |
| Build counter (CI job number) | Monotonic | Not portable across CI systems, no local meaning |

## Related ADRs

- [ADR 0007: Three Deployment Forms](0007-three-deployment-forms.md) — Versioning across forms
- `utils/branding.py` — Single source for version + build info

## References

- `utils/branding.py` — Version, build commit, channel, labels
- `build_scripts/stamp_build.py` — Stamp generation
- `build_scripts/build_exe.bat` / `.sh` — Includes stamp
- `pyproject.toml` — Reads version from `utils.branding.VERSION`