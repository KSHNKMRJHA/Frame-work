# -*- coding: utf-8 -*-
"""Regression tests for protocol-selection state ownership (Bug #1).

These drive the REAL utils/ui_state.py against a real Streamlit script run via
AppTest, so they exercise the decision logic the app actually uses rather than a
copy of it. The original defect was invisible to plain unit tests: the state
looked right in Python, but the widget was never rendered at all.

Run: python build_scripts/check_navigation.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from streamlit.testing.v1 import AppTest  # noqa: E402

PROTOCOLS = [
    {"id": "uart", "name": "UART", "category": "On-Board", "year": 1960},
    {"id": "can", "name": "CAN", "category": "Automotive", "year": 1985},
    {"id": "i2c", "name": "I2C", "category": "On-Board", "year": 1982},
    {"id": "usb20", "name": "USB 2.0", "category": "USB", "year": 2000},
]

# A miniature Encyclopedia using the same helpers in the same order as the real
# page. Kept deliberately in sync: if the page's contract changes, this breaks,
# which is the point.
HARNESS = '''
import sys
sys.path.insert(0, {root!r})

import streamlit as st
from utils import ui_state

PROTOCOLS = {protocols!r}
by_id = {{p["id"]: p for p in PROTOCOLS}}

ACTIVE_CAT = st.session_state.get("fw_cat", "All")
filtered = [p for p in PROTOCOLS if ACTIVE_CAT == "All" or p["category"] == ACTIVE_CAT]

option_ids = [p["id"] for p in filtered]
labels = {{p["id"]: p["name"] for p in filtered}}

seeded_id = ui_state.ensure_active_protocol(PROTOCOLS)
start = option_ids.index(seeded_id) if seeded_id in option_ids else 0

picked = st.selectbox(
    "Select a protocol to open its full profile:",
    option_ids,
    index=start,
    format_func=lambda pid: labels.get(pid, pid),
    key="fw_proto_pick",
)

active_id = ui_state.active_protocol_id(PROTOCOLS, widget_value=picked)
selected = by_id.get(active_id) if active_id in set(option_ids) else None
if selected is None:
    selected = by_id[picked]

ui_state.sync_active_protocol(selected["id"])

st.write("ACTIVE=" + selected["id"])
'''

BUGGY = '''
import sys
sys.path.insert(0, {root!r})
import streamlit as st

PROTOCOLS = {protocols!r}

def protocol_from_url(protocols):
    pid = st.query_params.get("p")
    if not pid:
        return None
    for p in protocols:
        if p["id"] == pid:
            return p
    return None

def set_protocol_url(protocol_id):
    if st.query_params.get("p") != protocol_id:
        st.query_params["p"] = protocol_id

filtered = PROTOCOLS
names = [p["name"] for p in filtered]
deep = protocol_from_url(filtered)
selected = deep if deep else filtered[names.index(st.selectbox("pick", names, key="pick"))]
set_protocol_url(selected["id"])
st.write("ACTIVE=" + selected["id"])
'''


def _app():
    return AppTest.from_string(
        HARNESS.format(root=ROOT, protocols=PROTOCOLS), default_timeout=30
    )


def _active(at):
    for md in at.markdown:
        if md.value.startswith("ACTIVE="):
            return md.value.split("=", 1)[1]
    return None


def _url_p(at):
    """Read ?p= from the test harness.

    AppTest's query_params proxy normalises multi-value params to a list
    ({"p": ["can"]}) even though the script itself sees a bare string, so unwrap
    it rather than comparing a list to a str.
    """
    raw = at.query_params.get("p")
    if isinstance(raw, (list, tuple)):
        return raw[0] if raw else None
    return raw


def test_direct_deep_link():
    """?p=uart must open UART."""
    at = _app()
    at.query_params["p"] = "uart"
    at = at.run()
    assert not at.exception, at.exception
    assert _active(at) == "uart", f"expected uart, got {_active(at)}"


def test_selector_rendered_on_deep_link():
    """The dropdown must EXIST on a deep-linked visit.

    Core regression: the old code built the selectbox inside the false branch of
    the conditional, so a deep link meant no widget at all and the user could
    never leave that protocol.
    """
    at = _app()
    at.query_params["p"] = "uart"
    at = at.run()
    assert len(at.selectbox) == 1, "selectbox was not rendered on a deep-linked visit"


def test_selectbox_available_without_param():
    at = _app().run()
    assert len(at.selectbox) == 1
    assert _active(at) in {p["id"] for p in PROTOCOLS}


def test_user_can_change_protocol_and_url_follows():
    """The headline bug: ?p=uart, user picks CAN -> CAN must become active."""
    at = _app()
    at.query_params["p"] = "uart"
    at = at.run()
    assert _active(at) == "uart"

    at.selectbox[0].set_value("can").run()
    assert _active(at) == "can", (
        f"deep link trapped the user: expected can, got {_active(at)}"
    )
    assert _url_p(at) == "can", "URL did not follow the selection"


def test_second_and_third_selection():
    at = _app()
    at.query_params["p"] = "uart"
    at = at.run()
    at.selectbox[0].set_value("can").run()
    at.selectbox[0].set_value("i2c").run()
    assert _active(at) == "i2c", f"expected i2c, got {_active(at)}"
    assert _url_p(at) == "i2c"


def test_refresh_keeps_selection():
    """A fresh load of the URL the page itself wrote must keep that protocol."""
    at = _app()
    at.query_params["p"] = "uart"
    at = at.run()
    at.selectbox[0].set_value("can").run()
    assert _url_p(at) == "can"

    fresh = _app()
    fresh.query_params["p"] = "can"
    fresh = fresh.run()
    assert _active(fresh) == "can"


def test_invalid_deep_link_falls_back_safely():
    at = _app()
    at.query_params["p"] = "not-a-real-protocol"
    at = at.run()
    assert not at.exception, at.exception
    assert _active(at) in {p["id"] for p in PROTOCOLS}
    assert len(at.selectbox) == 1


def test_handoff_id_opens_exact_protocol():
    """A Selector handoff must open THAT protocol, not the first/default one."""
    at = _app()
    at.session_state["_fw_protocol_handoff"] = "usb20"
    at = at.run()
    assert _active(at) == "usb20", f"handoff ignored: got {_active(at)}"


def test_filtered_out_target_does_not_crash_or_substitute_invisibly():
    """A filter excluding the recalled protocol must not raise or lie."""
    at = _app()
    at.session_state["_fw_protocol_handoff"] = "usb20"   # USB
    at.session_state["fw_cat"] = "On-Board"             # excludes USB
    at = at.run()
    assert not at.exception, at.exception
    active = _active(at)
    assert active in {"uart", "i2c"}, f"expected a visible On-Board protocol, got {active}"


def test_detector_catches_stale_url_ownership():
    """NEGATIVE TEST: prove the detector fails under the original buggy logic.

    Reimplements the old expression verbatim - the URL wins on every rerun and the
    selectbox is not rendered while a deep link is active. The check below is the
    same one test_user_can_change_protocol_and_url_follows makes; it MUST fail
    here, or the detector cannot be trusted to catch the regression.
    """
    at = AppTest.from_string(
        BUGGY.format(root=ROOT, protocols=PROTOCOLS), default_timeout=30
    )
    at.query_params["p"] = "uart"
    at = at.run()

    reached_can = False
    if len(at.selectbox) == 1:
        at.selectbox[0].set_value("CAN").run()
        reached_can = _active(at) == "can"

    assert not reached_can, (
        "NEGATIVE TEST FAILED: the buggy implementation appeared to work, so this "
        "regression detector cannot be trusted."
    )


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ok  {name}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {name}: {type(exc).__name__}: {exc}")

    print()
    if failed:
        print(f"Navigation tests FAILED: {failed} of {len(tests)}")
        sys.exit(1)
    print(f"Navigation tests passed ({len(tests)} checks)")
