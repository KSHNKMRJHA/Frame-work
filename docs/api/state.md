# API: State

`utils.state` — User progress persistence (XP, badges, viewed protocols, settings).

## Data Model

```python
DEFAULT_STATE = {
    "username": "Engineer",
    "xp": 0,
    "level": 1,
    "badges": [],              # List of badge IDs
    "protocols_viewed": [],    # List of protocol IDs
    "quiz_history": [],        # List of quiz result dicts
    "puzzle_history": [],      # List of puzzle result dicts
    "accent_color": "#4f46e5",
    "theme": "light",          # "light" or "dark"
}
```

## Functions

### `get_state_path() -> Path`

```python
def get_state_path() -> Path:
    """Get platform-appropriate state file path.
    
    Source runs: data/user_state.json
    Frozen Windows: %LOCALAPPDATA%/FrameWork/user_state.json
    Frozen Linux: ~/.local/share/FrameWork/user_state.json
    Frozen macOS: ~/Library/Application Support/FrameWork/user_state.json
    
    Returns:
        Path to state file.
    """
```

---

### `load_state() -> dict`

```python
def load_state() -> dict:
    """Load user state with corruption recovery.
    
    Returns:
        State dict with DEFAULT_STATE as base.
        May include special keys:
        - _recovered: bool (file was unreadable, reset to defaults)
        - _repaired: list[str] (field names that were invalid and reset)
    """
```

**Recovery Behavior:**
- Missing file → returns `DEFAULT_STATE.copy()`
- Invalid JSON → `_recovered=True`, returns defaults, original file preserved
- Invalid fields → `_repaired=[field_names]`, valid fields kept, invalid reset to defaults

---

### `save_state(state: dict) -> None`

```python
def save_state(state: dict) -> None:
    """Atomically save state to disk.
    
    Uses temp file + os.replace for atomicity.
    Strips internal keys (_recovered, _repaired) before writing.
    
    Args:
        state: State dict from load_state() (modified).
    """
```

**Atomic Write Guarantee:**
- POSIX: `os.replace` is atomic
- Windows: `os.replace` replaces atomically (since Python 3.3)
- Crash during write → original file intact
- Power loss → either old or new complete file

---

### `reset_state() -> dict`

```python
def reset_state() -> dict:
    """Reset to defaults and save.
    
    Returns:
        Fresh DEFAULT_STATE copy.
    """
```

---

## Usage in Streamlit

```python
# In app.py (initialization)
from utils import state as state_utils

if "user_state" not in st.session_state:
    st.session_state.user_state = state_utils.load_state()

us = st.session_state.user_state

# Handle recovery notifications
if us.pop("_recovered", False):
    st.warning("Progress file corrupted, reset to defaults. Original preserved.")
if us.pop("_repaired", None):
    st.info("Some progress fields were invalid and reset.")

# Update progress
us["xp"] += 100
us["level"] = quiz_engine.xp_to_level(us["xp"])
us["protocols_viewed"].append("can")

# Persist
state_utils.save_state(us)
```

---

## Quiz/Puzzle History Schema

```python
# quiz_history entries
{
    "timestamp": "2024-01-15T10:30:00.000Z",
    "score": 8,
    "total": 10,
    "category": "Automotive",
    "difficulty": "Intermediate",
    "seed": 42,
    "xp_earned": 80
}

# puzzle_history entries
{
    "timestamp": "2024-01-15T10:35:00.000Z",
    "type": "frame_order",  # or "speed_matching", "guess_protocol"
    "protocol_id": "can",
    "solved": True,
    "attempts": 1,
    "time_seconds": 45.2,
    "xp_earned": 25
}
```

---

## Badge Definitions

| Badge | Condition (`BADGE_RULES` in `utils/state.py`) |
|-------|----------------------------------------------|
| First Steps | `quizzes_taken >= 1` |
| Quiz Regular | `quizzes_taken >= 5` |
| Quiz Master | `quizzes_taken >= 15` |
| Perfectionist | `best_score_pct >= 100` |
| Explorer (10 protocols) | `len(protocols_viewed) >= 10` |
| Explorer (30 protocols) | `len(protocols_viewed) >= 30` |
| Encyclopedia Master (60+) | `len(protocols_viewed) >= 60` |

Badge names are stored verbatim in `state["badges"]`, so there is no separate
badge-ID table. Awarded by `state.check_badges(state)`, which takes only the
state dict, appends any newly-earned name, and logs the award to history.

> Note: earlier revisions of this page described badges ("Scholar", "Master",
> "Puzzle Solver", "Category Master", "Speed Demon", "Frame Architect",
> "Detective") and a two-argument `check_badges(state, protocols)` that do not
> exist in the implementation. The table above mirrors `BADGE_RULES` exactly.

---

## Settings Persistence

| Setting | Key | Type | Default |
|---------|-----|------|---------|
| Username | `username` | str | "Engineer" |
| Accent Color | `accent_color` | str (hex) | "#4f46e5" |
| Theme | `theme` | "light"\|"dark" | "light" |

Applied via `utils/branding.py` and `.streamlit/config.toml`.

---

## Export/Import

```python
# Export (Settings page)
import json
json_str = json.dumps(state, indent=2)
st.download_button("Export Progress", json_str, "framework_progress.json")

# Import (Settings page)
uploaded = st.file_uploader("Import Progress", type="json")
if uploaded:
    imported = json.load(uploaded)
    # Merge with current state (preserve XP, badges)
    state_utils.save_state(imported)
```

---

## Testing

```python
# In build_scripts/check_logic.py (indirectly via quiz_engine tests)
# State persistence tested by:
# 1. load_state() on missing file → defaults
# 2. save_state() + load_state() round-trip
# 3. Corrupted JSON → _recovered=True
# 4. Invalid fields → _repaired=[...]
```

---

## See Also

- [Architecture: Atomic Persistence](../architecture/adrs/0008-atomic-persistence.md)
- [Quiz Engine](quiz_engine.md) — XP/badges logic
- [Branding](branding.md) — Theme/color application
- [Settings Page](../getting-started/quickstart.md) — UI for state management