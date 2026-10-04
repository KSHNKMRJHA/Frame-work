# -*- coding: utf-8 -*-
"""Cross-page UI state: deep links, remembered context, and global search.

Streamlit discards everything between page navigations, so without this a user
who was reading USB on the Encyclopedia arrives at Compare with no idea what
they were looking at. This module is the app's memory.

Deep links (`?p=usb20`) matter most for a learning tool: a student should be
able to cite a specific protocol entry rather than "go and find it".
"""
import streamlit as st

# Section grouping for the sidebar. Keys are the app's page labels, values are
# the heading shown above that group. Order here defines the reading path.
NAV_SECTIONS = [
    ("Reference", ["📚 Encyclopedia", "⚖️ Compare", "🧭 Selector", "📖 Glossary"]),
    ("Context", ["🕰️ History & Timeline", "🗺️ Mind Map", "🌍 Geography & Origins"]),
    ("Practice", ["🧠 Quiz & Assessment", "🎮 Puzzles & Games", "🔬 Science & Math Lab"]),
    ("Meta", ["⚙️ Settings & Profile", "ℹ️ Info"]),
]

_MEM = "_fw_memory"
# A cross-page "open this protocol" request. Lives outside _mem because it is a
# one-shot instruction to the next page, not a remembered preference.
_MEM_HANDOFF = "_fw_protocol_handoff"


def _mem():
    if _MEM not in st.session_state:
        st.session_state[_MEM] = {"last_protocol": None, "filters": {}}
    return st.session_state[_MEM]


def remember_protocol(protocol_id):
    """Record the protocol the user is currently reading."""
    if protocol_id:
        _mem()["last_protocol"] = protocol_id


def last_protocol():
    return _mem().get("last_protocol")


def remember_filter(key, value):
    """Persist a filter/search term so it survives navigation."""
    _mem()["filters"][key] = value


def recall_filter(key, default=""):
    return _mem()["filters"].get(key, default)


# ---------------------------------------------------------------- deep links
def protocol_from_url(protocols):
    """Resolve ?p=<id> to a protocol record, or None.

    An unknown id is ignored rather than raising: a stale bookmark should land
    on the default protocol, not an error page.
    """
    pid = st.query_params.get("p")
    if not pid:
        return None
    for p in protocols:
        if p["id"] == pid:
            return p
    return None


def set_protocol_url(protocol_id):
    """Write the current protocol into the URL so the view is shareable."""
    if st.query_params.get("p") != protocol_id:
        st.query_params["p"] = protocol_id


# --------------------------------------------------------- active protocol
# One clear owner for "which protocol am I reading". The rules, in order:
#
#   1. An explicit ?p=<id> (deep link, bookmark, or a cross-page handoff) seeds
#      the selection ONCE. It is not consulted again on later reruns, otherwise
#      the URL would permanently outrank the dropdown: the page writes ?p=<id>
#      itself, so on the next rerun protocol_from_url() would keep returning the
#      previous protocol and the user could never change it.
#   2. After that, the selectbox is the source of truth.
#   3. The URL and the remembered context follow the selection.
#
# The active value is a protocol ID, never a rendered "name · category (year)"
# string: those labels are not unique, get reformatted, and made identity
# depend on parsing.
_ACTIVE = "_fw_active_protocol_id"
_SEEDED = "_fw_protocol_seeded"


def requested_protocol_id():
    """The id explicitly asked for by the URL/handoff, or None."""
    pid = st.query_params.get("p")
    return pid or None


def open_protocol(protocol_id):
    """Intentional cross-page handoff: remember the target for the next page.

    Used by buttons whose entire meaning is "open this protocol". The Encyclopedia
    consumes it once during initialization, so it seeds the selection rather than
    fighting the user on every rerun.
    """
    if protocol_id:
        st.session_state[_MEM_HANDOFF] = protocol_id


def _mem_handoff_take():
    """Read and clear the pending handoff, if any."""
    return st.session_state.pop(_MEM_HANDOFF, None)


def ensure_active_protocol(protocols):
    """Seed the active protocol ONCE for this page visit. Returns the current id.

    Called before the dropdown is built so the widget can render with the right
    current value. After seeding, the stored id is authoritative.
    """
    ids = {p["id"] for p in protocols}

    if not st.session_state.get(_SEEDED):
        # Precedence: explicit ?p=<id> > cross-page handoff > last read.
        seed = requested_protocol_id() or _mem_handoff_take() or last_protocol()
        st.session_state[_ACTIVE] = seed if seed in ids else None
        st.session_state[_SEEDED] = True
    elif _MEM_HANDOFF in st.session_state:
        # A handoff that lands after initialization (Selector -> Encyclopedia)
        # replaces the selection exactly once.
        handoff = _mem_handoff_take()
        if handoff in ids:
            st.session_state[_ACTIVE] = handoff

    active = st.session_state.get(_ACTIVE)
    return active if active in ids else None


def active_protocol_id(protocols, widget_value=None):
    """Reconcile the widget with the stored selection and return the active id.

    Called AFTER the dropdown renders. Because the widget is built with
    ``index`` pointing at the current active protocol, its value matches the
    stored id unless the user moved it - so a difference means a real user
    action, and the user wins from then on.
    """
    ids = {p["id"] for p in protocols}
    if widget_value in ids and widget_value != st.session_state.get(_ACTIVE):
        st.session_state[_ACTIVE] = widget_value

    active = st.session_state.get(_ACTIVE)
    return active if active in ids else None


def sync_active_protocol(protocol_id):
    """Push the selection out to the URL and the app memory."""
    if not protocol_id:
        return
    set_protocol_url(protocol_id)
    remember_protocol(protocol_id)


def reset_active_protocol():
    """Forget the seeded state so the next visit re-seeds (fresh navigation)."""
    st.session_state.pop(_ACTIVE, None)
    st.session_state.pop(_SEEDED, None)


# ------------------------------------------------------------- global search
def global_search(protocols, key="fw_search", placeholder="Search 140 protocols…"):
    """Render a persistent search box in the sidebar with a Ctrl/Cmd+K hint.

    Results are ranked so an exact id or name prefix beats a body-text hit —
    searching "can" should surface CAN, not every protocol that mentions it.
    """
    with st.sidebar:
        query = st.text_input("🔎 Quick search", key=key,
                              placeholder=placeholder, label_visibility="collapsed")
        if query and query.strip():
            hits = rank(protocols, query.strip())
            for p in hits[:8]:
                st.page_link(f"pages/{_page_file(p['id'])}", label=f"{_emoji(p['id'])} {p['name']}",
                             icon=None)
            if not hits:
                st.caption("No protocol matches that.")
            elif len(hits) > 8:
                st.caption(f"+{len(hits) - 8} more — refine your search")


def rank(protocols, query, limit=25):
    """Rank protocols for a query: id > name prefix > name > tags > body."""
    q = query.lower()
    scored = []
    for p in protocols:
        pid = p.get("id", "").lower()
        name = p.get("name", "").lower()
        score = 0
        if pid == q:
            score = 100
        elif name.startswith(q):
            score = 90
        elif q in pid:
            score = 70
        elif q in name:
            score = 60
        elif q in " ".join(p.get("use_cases", [])).lower():
            score = 30
        elif q in (p.get("description", "") + p.get("how_it_works", "")).lower():
            score = 15
        if score:
            scored.append((score, p))
    scored.sort(key=lambda t: (-t[0], t[1]["name"]))
    return [p for _, p in scored[:limit]]


# The page file for a protocol id. Only the Encyclopedia has per-protocol deep
# links; other pages take a query string instead.
def _page_file(_pid):
    return "1_📚_Encyclopedia.py"


_EMOJI = {
    "usb20": "🔌", "usb3x": "⚡", "usb4": "⚡", "i2c": "🔗", "spi": "🔗",
    "uart": "🔗", "rs485": "🔗", "rs232": "🔗", "can": "🚗", "ethernet": "🌐",
    "lin": "🚗", "flexray": "🚗", "lvds": "⚡", "pcie": "⚡", "wifi": "📡",
    "ble": "📡", "zigbee": "📡", "modbus_rtu": "🏭", "modbus_tcp": "🏭",
}


def _emoji(pid):
    return _EMOJI.get(pid, "📘")
