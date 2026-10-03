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


def clear_protocol_url():
    if "p" in st.query_params:
        del st.query_params["p"]


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
