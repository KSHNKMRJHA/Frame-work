# Running Locally

Configuration options and tips for local development.

## Basic Usage

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` with default settings.

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--server.port` | Port to listen on | `--server.port 8502` |
| `--server.address` | Bind address | `--server.address 0.0.0.0` |
| `--server.headless` | Run without opening browser | `--server.headless true` |
| `--browser.gatherUsageStats` | Disable usage stats | `--browser.gatherUsageStats false` |
| `--theme.base` | Light/dark theme | `--theme.base dark` |

## Example Commands

```bash
# Custom port, no browser auto-open
streamlit run app.py --server.port 8502 --server.headless true

# Expose on network (LAN access)
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Force dark theme
streamlit run app.py --theme.base dark
```

## Configuration File

Create `.streamlit/config.toml` for persistent settings:

```toml
[server]
port = 8501
address = "localhost"
headless = false
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
base = "light"
primaryColor = "#4f46e5"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f1f5f9"
textColor = "#1e293b"
font = "sans serif"

[runner]
magicEnabled = true
installTracer = false
fixMatplotlib = true
```

The repo already includes a `.streamlit/config.toml` with the project's theme.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FRAMEWORK_BUILD_COMMIT` | Override auto-detected build commit | Auto from git |
| `FRAMEWORK_BUILD_CHANNEL` | Release channel | `stable` |
| `FRAMEWORK_WEB_URL` | Point UI footer to different web deployment | `https://frame-work.streamlit.app/` |

```bash
# Example: custom build info
FRAMEWORK_BUILD_COMMIT=abc1234 FRAMEWORK_BUILD_CHANNEL=dev streamlit run app.py
```

## Data Persistence

- **Source runs**: Progress saved to `data/user_state.json` (gitignored)
- **Frozen builds**: Progress saved to OS data directory:
  - Windows: `%LOCALAPPDATA%\FrameWork\`
  - Linux: `~/.local/share/FrameWork/`
  - macOS: `~/Library/Application Support/FrameWork/`

The atomic write strategy (temp file + `os.replace`) prevents corruption on crash.

## Hot Reloading

Streamlit auto-reloads on file changes. For faster iteration:

```bash
# Watch only specific directories
streamlit run app.py --server.runOnSave true
```

## Debugging

```bash
# Verbose logging
streamlit run app.py --logger.level debug

# Python debugger (add breakpoint in code)
import streamlit as st
st.breakpoint()  # Requires streamlit >= 1.32
```

## Performance Tips

- First load builds diagram cache — subsequent runs are faster
- Large protocol database (118 entries) loads once via `@st.cache_data`
- Diagrams are generated on-demand and cached per session

## Next Steps

- [Desktop Build](desktop.md) — Create standalone executable
- [Web Deployment](web.md) — Deploy to cloud
- [Architecture Overview](../architecture/overview.md) — Understand the codebase