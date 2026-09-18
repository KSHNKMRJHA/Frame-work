# -*- coding: utf-8 -*-
"""
state.py
Lightweight local persistence for user profile, settings, and learning
progress — stored as JSON on disk so progress survives between runs
(no database/server required, works fully offline).

Two things here are deliberate and easy to break by accident:

1. When the app is frozen with PyInstaller, `__file__` lives under
   `sys._MEIPASS`, a temporary directory that is DELETED when the process
   exits. Writing progress there looks like it works and then silently loses
   everything on quit, so the frozen build writes to a per-user OS data
   directory instead.

2. `save_state` writes to a temp file and then `os.replace`s it, so an
   interrupted write cannot leave a truncated JSON file behind. `load_state`
   still has to cope with a damaged or hand-edited file, and reports that it
   did via the `_recovered` key rather than resetting progress silently.
"""
import json
import os
import sys
import tempfile
import datetime

APP_NAME = "FrameWork"
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FROZEN = getattr(sys, "frozen", False)


def _user_data_dir(app=APP_NAME):
    """Per-user, writable, persistent directory appropriate to the platform."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, app)


# Running from source: keep progress next to the project (as before, and
# .gitignore already excludes it). Frozen: the bundle directory is temporary,
# so progress must live in the user's own data directory.
STATE_DIR = _user_data_dir() if FROZEN else os.path.join(APP_ROOT, "data")
STATE_PATH = os.path.join(STATE_DIR, "user_state.json")

DEFAULT_STATE = {
    "username": "Learner",
    "accent_color": "#2563eb",
    "xp": 0,
    "level": 1,
    "quizzes_taken": 0,
    "best_score_pct": 0,
    "protocols_viewed": [],
    "badges": [],
    "history": [],  # list of {date, activity, detail}
    "created_at": None,
}

# Types each field must have for the mutators below to be safe. A file that is
# valid JSON but has the wrong types (hand-edited, or an old/foreign export)
# used to pass load_state() and then crash add_xp/check_badges/record_quiz.
_FIELD_TYPES = {
    "username": str,
    "accent_color": str,
    "xp": int,
    "level": int,
    "quizzes_taken": int,
    "best_score_pct": (int, float),
    "protocols_viewed": list,
    "badges": list,
    "history": list,
    "created_at": (str, type(None)),
}

BADGE_RULES = [
    ("First Steps", lambda s: s["quizzes_taken"] >= 1),
    ("Quiz Regular", lambda s: s["quizzes_taken"] >= 5),
    ("Quiz Master", lambda s: s["quizzes_taken"] >= 15),
    ("Perfectionist", lambda s: s["best_score_pct"] >= 100),
    ("Explorer (10 protocols)", lambda s: len(s["protocols_viewed"]) >= 10),
    ("Explorer (30 protocols)", lambda s: len(s["protocols_viewed"]) >= 30),
    ("Encyclopedia Master (60+)", lambda s: len(s["protocols_viewed"]) >= 60),
]


def _fresh_state():
    s = dict(DEFAULT_STATE)
    s["protocols_viewed"] = []
    s["badges"] = []
    s["history"] = []
    s["created_at"] = datetime.datetime.now().isoformat()
    return s


def load_state():
    """Load saved progress, repairing or replacing anything unusable.

    Returns a dict that always has every DEFAULT_STATE key with the right
    type. Two optional keys report what happened, so the UI can tell the user
    instead of silently showing zero progress:

        "_recovered": True  -- the file was unreadable and defaults were used
        "_repaired":  [..]  -- these fields had bad values and were reset
    """
    if not os.path.exists(STATE_PATH):
        s = _fresh_state()
        try:
            save_state(s)
        except OSError:
            pass  # read-only filesystem (e.g. Streamlit Cloud): session-only state
        return s

    raw = None
    unreadable = False
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError):
        unreadable = True

    s = _fresh_state()

    # Shape guard: valid JSON that is a list, string, number or null used to
    # raise AttributeError here and take the whole app down on startup.
    if not isinstance(raw, dict):
        if raw is not None:
            unreadable = True
        if unreadable:
            # Leave the bad file on disk untouched so the user can recover it.
            s["_recovered"] = True
        return s

    repaired = []
    for key, default in DEFAULT_STATE.items():
        if key not in raw:
            continue
        value = raw[key]
        expected = _FIELD_TYPES[key]
        # bool is a subclass of int; never accept it where a number is meant.
        if isinstance(value, bool) and expected is int:
            repaired.append(key)
            continue
        if not isinstance(value, expected):
            repaired.append(key)
            continue
        s[key] = value

    # `history` entries are rendered with entry["date"]/["activity"]/["detail"].
    s["history"] = [h for h in s["history"]
                    if isinstance(h, dict) and {"date", "activity", "detail"} <= set(h)]
    s["protocols_viewed"] = [p for p in s["protocols_viewed"] if isinstance(p, str)]
    s["badges"] = [b for b in s["badges"] if isinstance(b, str)]

    # Keep level consistent with xp rather than trusting a stored value.
    s["level"] = 1 + s["xp"] // 100
    if raw.get("created_at"):
        s["created_at"] = raw["created_at"] if isinstance(raw["created_at"], str) else s["created_at"]

    if repaired:
        s["_repaired"] = repaired
    return s


def save_state(state):
    """Write progress atomically.

    A plain open(..., "w") truncates first, so a crash or a second writer
    mid-dump leaves a half-written file that load_state can only discard.
    Writing to a temp file in the same directory and then os.replace()-ing it
    is atomic on both POSIX and Windows, so the file on disk is always either
    the old complete version or the new complete version.

    Note this makes each write all-or-nothing but does not make concurrent
    writers safe: with the app open in two tabs, the last writer still wins.
    """
    os.makedirs(STATE_DIR, exist_ok=True)
    # Never persist the transient diagnostic keys.
    payload = {k: v for k, v in state.items() if not k.startswith("_")}

    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, prefix=".user_state.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, STATE_PATH)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def add_xp(state, amount, reason=""):
    state["xp"] += amount
    state["level"] = 1 + state["xp"] // 100
    log_activity(state, "xp", f"+{amount} XP ({reason})")
    check_badges(state)
    return state


def log_activity(state, activity, detail=""):
    state["history"].append({
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "activity": activity,
        "detail": detail,
    })
    state["history"] = state["history"][-100:]  # keep last 100


def mark_protocol_viewed(state, pid):
    if pid not in state["protocols_viewed"]:
        state["protocols_viewed"].append(pid)
        add_xp(state, 2, "viewed a new protocol")
    check_badges(state)
    return state


def record_quiz_result(state, score_pct):
    state["quizzes_taken"] += 1
    state["best_score_pct"] = max(state["best_score_pct"], score_pct)
    log_activity(state, "quiz", f"Scored {score_pct:.0f}%")
    add_xp(state, int(10 + score_pct / 5), "completed a quiz")
    check_badges(state)
    return state


def check_badges(state):
    for name, rule in BADGE_RULES:
        if rule(state) and name not in state["badges"]:
            state["badges"].append(name)
            log_activity(state, "badge", f"Earned badge: {name}")
    return state


def reset_progress():
    s = _fresh_state()
    try:
        save_state(s)
    except OSError:
        pass
    return s
