# API: Branding

`utils.branding` — Application identity, versioning, build information, and UI chrome.

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `APP_NAME` | `"FrameWork"` | Application name |
| `APP_TAGLINE` | `"Every embedded communication protocol..."` | Tagline |
| `APP_ICON` | `"🛰️"` | Emoji icon |
| `VERSION` | `"1.0.0"` | Semantic version |

## Functions

### `version_label()`

**Short version string, e.g. 'v1.0.0'.**

Returns formatted version with channel and commit.

```python
def version_label() -> str:
    return f"v{VERSION} · {get_build_channel()} · commit {get_build_commit()}"
```

**Returns:** `str` — Formatted version string like `"v1.0.0 · stable · commit a1b2c3d"`

---

### `build_line()`

**One-line, publishable build string, e.g. 'v1.0.0 · stable · commit 015f212'.**

```python
def build_line() -> str:
    commit = get_build_commit()
    channel = get_build_channel()
    return f"{channel} build {commit}" if commit != "dev" else "dev build"
```

**Returns:** `str` — Build line for footer

---

### `build_number()`

**The build number: the short commit tag, or a placeholder for an unversioned tree.**

Resolved from (in priority order):
1. `FRAMEWORK_BUILD_COMMIT` env var (CI override)
2. `git rev-parse --short=7 HEAD` (live repo)
3. `utils/_build_stamp.txt` (frozen builds)
4. `"dev"` (fallback)

```python
def build_number() -> str:
    ...
```

**Returns:** `str` — 7-char commit hash or `"dev"`

---

### `get_build_channel()`

**Get release channel from environment.**

```python
def get_build_channel() -> str:
    return os.environ.get("FRAMEWORK_BUILD_CHANNEL", "stable")
```

**Returns:** `str` — Channel name (default: `"stable"`)

---

### `get_build_commit()`

**Resolve build commit hash (7 chars) from multiple sources.**

```python
def get_build_commit() -> str:
    # Priority: env var > git > build stamp > "dev"
    ...
```

**Returns:** `str` — 7-character commit hash or `"dev"`

---

### `page_config()`

**Configure the Streamlit page with consistent FrameWork branding.**

```python
def page_config() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
```

Call once at top of each page script.

---

### `sidebar_identity()`

**Render the FrameWork name, version, build number, and links in the sidebar.**

```python
def sidebar_identity() -> None:
    ...
```

Renders:
- App icon + name
- Version label
- Links: GitHub, Live App, LinkedIn
- Build info

Call once per session in `app.py`.

---

### `page_footer()`

**Render the standard publication footer (version, build, links, credits).**

```python
def page_footer() -> None:
    ...
```

Renders:
- Version + build line
- GitHub / Live App / LinkedIn links
- MIT License notice

Call at bottom of each page.

---

### `credit_line()`

**Attribution used in footers: author, designer, and the AI collaboration note.**

```python
CREDIT_LINE = (
    "Created by [Kishan J.](https://www.linkedin.com/in/kshnkmrjha/) · "
    "Design by Piston · Made with love and AI"
)
```

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FRAMEWORK_BUILD_COMMIT` | Override build commit (CI) | Auto-detected |
| `FRAMEWORK_BUILD_CHANNEL` | Release channel | `"stable"` |
| `FRAMEWORK_WEB_URL` | Canonical web URL for footer | `"https://frame-work.streamlit.app/"` |

---

## Usage

```python
from utils.branding import APP_NAME, APP_ICON, APP_TAGLINE, version_label, build_line
from utils import branding

# Page config
st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")

# Sidebar (once per session)
branding.sidebar_identity()

# Footer (each page)
branding.page_footer()

# Version in hero
st.markdown(f"## {APP_ICON} {APP_NAME} <span>{version_label()}</span>")
st.caption(build_line())
```