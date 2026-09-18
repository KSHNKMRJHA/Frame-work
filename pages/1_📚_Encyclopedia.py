# -*- coding: utf-8 -*-
import streamlit as st
from utils.data_loader import load_protocols, get_categories, get_by_id
from utils import state as state_utils
from utils.diagrams import frame_diagram, topology_diagram, pinout_diagram

from utils import branding

branding.page_config("Encyclopedia", "📚")
branding.sidebar_identity()

protocols = load_protocols()
categories = ["All"] + get_categories(protocols)

if "user_state" not in st.session_state:
    st.session_state.user_state = state_utils.load_state()
us = st.session_state.user_state

st.title("📚 Protocol Encyclopedia")
st.caption(
    "Every field below — history, diagrams, pinouts, use-cases, limitations, and real-world examples — is generated live from the master protocol database."
)

# ------------------------------------------------------------- FILTERS -----
fc1, fc2, fc3 = st.columns([2, 1, 1])
with fc1:
    query = st.text_input("Search", placeholder="Search by name, keyword, inventor...")
with fc2:
    cat = st.selectbox("Category", categories)
with fc3:
    diffs = ["All"] + sorted(set(p.get("difficulty", "Beginner") for p in protocols))
    diff = st.selectbox("Difficulty", diffs)

filtered = protocols
if cat != "All":
    filtered = [p for p in filtered if p["category"] == cat]
if diff != "All":
    filtered = [p for p in filtered if p.get("difficulty") == diff]
if query:
    ql = query.lower()
    filtered = [p for p in filtered if ql in (p["name"] + p["description"] + p["inventor"] + str(p["year"])).lower()]

st.caption(f"Showing **{len(filtered)}** of {len(protocols)} protocols.")

names = [f"{p['name']}  ·  {p['category']} ({p['year']})" for p in filtered]
if not names:
    st.warning("No protocols match your filters. Try clearing search or category.")
    st.stop()

selected_label = st.selectbox("Select a protocol to open its full profile:", names)
selected = filtered[names.index(selected_label)]

state_utils.mark_protocol_viewed(us, selected["id"])
state_utils.save_state(us)

st.divider()

# --------------------------------------------------------------- PROFILE ---
left, right = st.columns([2.2, 1])
with left:
    st.header(selected["name"])
    badge_cols = st.columns(4)
    badge_cols[0].metric("Category", selected["category"])
    badge_cols[1].metric("Invented", selected["year"])
    badge_cols[2].metric("Difficulty", selected.get("difficulty", "—"))
    badge_cols[3].metric("Topology", selected.get("topology", "—"))

    st.markdown("#### 📖 Overview")
    st.write(selected["description"])

    st.markdown("#### ⚙️ How It Works")
    st.write(selected.get("how_it_works", "—"))

    st.markdown("#### 🕰️ Origin Story")
    origin_bits = []
    if selected.get("inventor"):
        origin_bits.append(f"**Inventor / Organization:** {selected['inventor']}")
    if selected.get("organization"):
        origin_bits.append(f"**Standards Body:** {selected['organization']}")
    if selected.get("place"):
        origin_bits.append(f"**Origin:** {selected['place']}")
    st.markdown("  \n".join(origin_bits))
    if selected.get("fun_fact"):
        st.info(f"💡 **Fun fact:** {selected['fun_fact']}")

with right:
    st.markdown("#### 🚀 Speed")
    st.success(selected.get("speed", "Not specified"))
    if selected.get("pins"):
        st.markdown("#### 🔌 Pins / Wires")
        st.code(", ".join(selected["pins"]))
    st.markdown("#### 🌍 Real-World Example")
    st.write(selected.get("real_world_example", "—"))

st.divider()

uc1, uc2 = st.columns(2)
with uc1:
    st.markdown("#### ✅ Use Cases")
    for u in selected.get("use_cases", []):
        st.markdown(f"- {u}")
    st.markdown("#### 👍 Advantages")
    for a in selected.get("advantages", []):
        st.markdown(f"- {a}")
with uc2:
    st.markdown("#### ⚠️ Limitations")
    for limitation in selected.get("limitations", []):
        st.markdown(f"- {limitation}")
    if selected.get("related"):
        st.markdown("#### 🔗 Related Protocols")
        rel_names = []
        for rid in selected["related"]:
            rp = get_by_id(protocols, rid)
            if rp:
                rel_names.append(rp["name"])
        st.markdown(", ".join(rel_names) if rel_names else "—")

st.divider()
st.markdown("### 🖼️ Interactive Diagrams")
d1, d2, d3 = st.tabs(["📦 Frame / Packet Structure", "🕸️ Network Topology", "🔌 Pinout / Wiring"])

with d1:
    fig = frame_diagram(selected.get("frame_fields", []), title=f"{selected['name']} — Frame Structure")
    if fig:
        st.pyplot(fig, width="stretch")
        # Caveats a bit-level bar chart cannot show: variable-length fields
        # that only move in 8-bit steps, conditions that occupy no clock
        # cycle, interframe gaps that are not fields, and so on.
        if selected.get("frame_note"):
            st.caption(f"ℹ️ {selected['frame_note']}")
        st.caption(
            "Segment widths are proportional to bit count. Fields with a range "
            "(e.g. `0-64`) are drawn at a fixed nominal width because their real "
            "size varies per frame."
        )
    else:
        st.info(
            "This protocol doesn't define a fixed bit-level frame structure (e.g., it's a networking/application-layer or wireless protocol without a simple fixed frame)."
        )

with d2:
    fig = topology_diagram(selected.get("topology", "Point-to-Point"), selected["name"])
    # The topology canvas stays square-circled, so it is centred in a narrower
    # column rather than stretched across the full page width — otherwise the
    # diagram overflows the content area on a wide screen.
    _tc = st.columns([1, 2.4, 1])
    with _tc[1]:
        st.pyplot(fig, width="stretch")
    st.caption(
        "Illustrative layout — the node count and wiring shown are representative "
        "of this topology class, not the exact device list of the protocol."
    )

with d3:
    fig = pinout_diagram(selected.get("pins", []), selected["name"])
    if fig:
        _pc = st.columns([1, 2.4, 1])
        with _pc[1]:
            st.pyplot(fig, width="stretch")
    else:
        st.info(
            "No fixed physical pinout applies (e.g., this is a software/network-layer protocol running over Ethernet/Wi-Fi/etc.)."
        )

st.divider()
st.caption("Tip: use the ⚖️ Compare page to put this protocol head-to-head against alternatives.")

branding.page_footer()
