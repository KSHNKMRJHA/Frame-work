# -*- coding: utf-8 -*-
"""Protocol Selector — answer 4 questions, get a ranked shortlist.

Ranks the database against the numeric envelope in parametric.py
(data_rate_max_bps, distance_max_m, nodes_max). A None envelope means the
dimension is defined by the carrier, not the protocol — those entries pass
the filter but are flagged "carrier-defined" so nobody mistakes Modbus TCP
for a 1 Gbps guarantee on a congested plant LAN.
"""

import streamlit as st
import pandas as pd

from parametric import format_bps, format_m
from utils.data_loader import load_protocols, get_categories

from utils import branding, components
from utils import ui_state

branding.page_config("Selector", "🧭")
branding.sidebar_identity()

protocols = load_protocols()

components.page_hero("Decision assistant", "Protocol selector",
    "Tell the wizard your constraints — it ranks all 140 protocols by how many "
    "it provably meets. Numbers are representative maxima (never simultaneous), "
    "so treat the shortlist as a starting point, then read the full profile."
)

RATE_STEPS = [
    ("Any", 0),
    ("≥ 9.6 kbps (telemetry)", 9_600),
    ("≥ 115.2 kbps (serial console)", 115_200),
    ("≥ 1 Mbps (CAN-class)", 1_000_000),
    ("≥ 12 Mbps (USB full-speed)", 12_000_000),
    ("≥ 100 Mbps (fast control/video)", 100_000_000),
    ("≥ 1 Gbps (backbone)", 1_000_000_000),
    ("≥ 10 Gbps (datacenter)", 10_000_000_000),
]
DIST_STEPS = [
    ("Any", 0),
    ("≥ 1 m (on-board)", 1),
    ("≥ 10 m (room/vehicle)", 10),
    ("≥ 100 m (building/plant)", 100),
    ("≥ 1 km (campus/field)", 1000),
    ("≥ 10 km (long-range RF)", 10_000),
]

components.section_header("Environment & rate", index="01")
c1, c2 = st.columns(2)
with c1:
    cat = st.selectbox("Environment", ["Any"] + get_categories(protocols))
with c2:
    rate_label = st.selectbox("Data rate needed", [label for label, _ in RATE_STEPS], index=0)
components.section_header("Reach & devices", index="02")
c3, c4 = st.columns(2)
with c3:
    dist_label = st.selectbox("Distance needed", [label for label, _ in DIST_STEPS], index=0)
with c4:
    nodes_need = st.number_input("Devices on one segment", min_value=1, max_value=100000, value=2, step=1)
with st.container():
    include_legacy = st.checkbox(
        "Include legacy / retiring protocols",
        value=False,
        help="Off hides lifecycle=legacy entries (MicroWire, GSM, MOST, FireWire…).",
    )

rate_need = dict(RATE_STEPS)[rate_label]
dist_need = dict(DIST_STEPS)[dist_label]

pool = protocols
if cat != "Any":
    pool = [p for p in pool if p["category"] == cat]
if not include_legacy:
    pool = [p for p in pool if p.get("lifecycle") != "legacy"]


def _check(have, need):
    """(passed, carrier_defined, headroom_ratio). None always passes flagged."""
    if need <= 0:
        return True, False, None
    if have is None:
        return True, True, None
    return have >= need, False, (have / need if need else None)


ranked = []
for p in pool:
    r_ok, r_car, r_head = _check(p.get("data_rate_max_bps"), rate_need)
    d_ok, d_car, d_head = _check(p.get("distance_max_m"), dist_need)
    n_ok, n_car, n_head = _check(p.get("nodes_max"), nodes_need)
    if not (r_ok and d_ok and n_ok):
        continue
    defined_passes = sum(
        [
            rate_need > 0 and not r_car,
            dist_need > 0 and not d_car,
            nodes_need > 1 and not n_car,
        ]
    )
    notes = []
    notes.append(
        "rate carrier-defined"
        if r_car and rate_need > 0
        else (f"rate {format_bps(p.get('data_rate_max_bps'))}" if rate_need > 0 else "")
    )
    notes.append(
        "distance carrier-defined"
        if d_car and dist_need > 0
        else (f"reach {format_m(p.get('distance_max_m'))}" if dist_need > 0 else "")
    )
    notes.append(
        "fan-out carrier-defined"
        if n_car and nodes_need > 1
        else (f"{p.get('nodes_max')} nodes" if nodes_need > 1 and p.get("nodes_max") else "")
    )
    ranked.append(
        {
            "Protocol": p["name"],
            "Category": p["category"],
            "Max rate": format_bps(p.get("data_rate_max_bps")),
            "Max reach": format_m(p.get("distance_max_m")),
            "Max nodes": str(p.get("nodes_max")) if p.get("nodes_max") is not None else "carrier-defined",
            "Lifecycle": p.get("lifecycle", "—"),
            "OSI": p.get("osi_layer", "—"),
            "Standard": p.get("standard_doc", "—"),
            "Why it matches": "; ".join(n for n in notes if n) or "fits scope",
            "_score": (defined_passes, p.get("data_rate_max_bps") or 0),
            "_id": p["id"],
        }
    )

ranked.sort(key=lambda r: r["_score"], reverse=True)

st.divider()
if not ranked:
    st.warning(
        "No protocol meets all constraints. Relax them — try a lower rate, shorter "
        "reach, fewer nodes, or include legacy protocols."
    )
    st.stop()

components.section_header(f"{len(ranked)} matching protocols", index="03",
                          description="Ranked by confirmed constraints met, then maximum rate. Carrier-defined limits stay flagged.")
for position, result in enumerate(ranked[:3], start=1):
    with st.container(border=True):
        components.section_header(result["Protocol"], index=f"{position:02}")
        components.info_badge(result["Category"], tone="signal")
        components.spec_table([("Max rate", result["Max rate"]),
                               ("Max reach", result["Max reach"]),
                               ("Max nodes", result["Max nodes"])])
        st.caption(result["Why it matches"])
st.dataframe(
    pd.DataFrame(
        [
            {
                k: r[k]
                for k in (
                    "Protocol",
                    "Category",
                    "Max rate",
                    "Max reach",
                    "Max nodes",
                    "Lifecycle",
                    "OSI",
                    "Standard",
                    "Why it matches",
                )
            }
            for r in ranked
        ]
    ),
    width="stretch",
    hide_index=True,
)

st.divider()
components.section_header("Inspect a full profile", index="04")
# Identity, not the display name: two protocols can share a label, and the
# Encyclopedia needs the stable id to open the right profile. The name is only
# ever shown to the user.
ids = [r["_id"] for r in ranked]
row_label = {r["_id"]: r["Protocol"] for r in ranked}
pick_id = st.selectbox(
    "Open in the Encyclopedia:",
    ids,
    format_func=lambda pid: row_label.get(pid, pid),
    key="fw_selector_pick",
)
# Keep the action concise while the selectbox identifies the exact destination.
if st.button("Open in Encyclopedia", type="primary", width="stretch"):
    # Carry the protocol id across the page switch. `open_protocol` is the
    # session-state handoff and query_params makes the destination shareable -
    # either alone would work, both together survive a hard reload.
    ui_state.open_protocol(pick_id)
    st.switch_page("pages/1_📚_Encyclopedia.py", query_params={"p": pick_id})
st.caption(
    "Reminder: maxima are never simultaneous (RS-485 does 10 Mbps XOR 1200 m). "
    "Confirm the rate×distance corner you need in the standard and the transceiver datasheet."
)

branding.page_footer()
