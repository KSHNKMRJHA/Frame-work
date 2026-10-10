# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from utils.data_loader import load_protocols
from utils.diagrams import speed_comparison_chart

from utils import branding, components, theme

branding.page_config("Compare", "⚖️")
branding.sidebar_identity()

protocols = load_protocols()
names = [p["name"] for p in protocols]

components.page_hero("Decision workspace", "Compare protocols",
    "Select 2 to 4 protocols to compare side-by-side across every dimension — speed, topology, pins, use-cases, advantages, and limitations."
)

default_sel = names[:2]
chosen = st.multiselect("Choose protocols to compare (2-4):", names, default=default_sel, max_selections=4)

if len(chosen) < 2:
    st.warning("Pick at least 2 protocols to compare.")
    st.stop()

sel_protocols = [p for p in protocols if p["name"] in chosen]
ids = [p["id"] for p in sel_protocols]

# ---- Comparison table ----
components.section_header("Parameters & differences", index="01",
                          description="Compare the same engineering dimensions across the selected protocols.")
rows = {
    "Category": [p["category"] for p in sel_protocols],
    "Year Invented": [p["year"] for p in sel_protocols],
    "Inventor": [p["inventor"] for p in sel_protocols],
    "Topology": [p.get("topology", "—") for p in sel_protocols],
    "Speed": [p.get("speed", "—") for p in sel_protocols],
    "Pins": [", ".join(p.get("pins", [])) or "—" for p in sel_protocols],
    "Logic high / 1": [p.get("technical", {}).get("logic_high", "—") for p in sel_protocols],
    "Logic low / 0": [p.get("technical", {}).get("logic_low", "—") for p in sel_protocols],
    "Voltage / reference": [p.get("technical", {}).get("voltage_reference", "—") for p in sel_protocols],
    "Clocking / timing": [p.get("technical", {}).get("clocking", "—") for p in sel_protocols],
    "Max distance": [p.get("technical", {}).get("max_distance", "—") for p in sel_protocols],
    "Max nodes": [p.get("technical", {}).get("max_nodes", "—") for p in sel_protocols],
    "Duplex": [p.get("technical", {}).get("duplex_mode", "—") for p in sel_protocols],
    "Addressing": [p.get("technical", {}).get("addressing", "—") for p in sel_protocols],
    "Error detection": [p.get("technical", {}).get("error_detection", "—") for p in sel_protocols],
    "Line encoding": [p.get("technical", {}).get("line_encoding", "—") for p in sel_protocols],
    "Power profile": [p.get("technical", {}).get("power_profile", "—") for p in sel_protocols],
    "EMC / isolation": [p.get("technical", {}).get("emc_isolation", "—") for p in sel_protocols],
    "Interface silicon": ["; ".join(p.get("technical", {}).get("transceivers", [])) or "—" for p in sel_protocols],
    "Difficulty": [p.get("difficulty", "—") for p in sel_protocols],
}
df = pd.DataFrame(rows, index=[p["name"] for p in sel_protocols]).T
# Mixed int/str cells (e.g. Year Invented vs prose) break Arrow
# serialization on modern pyarrow — the table is for reading, so strings.
readable = df.astype(str)
different = readable.nunique(axis=1) > 1
st.caption(f"{different.sum()} of {len(readable)} parameters differ. Highlighted rows contain different values.")
pal = theme.current_palette()
styled = readable.style.apply(
    lambda row: [f"background-color: {pal['surface_alt']}" if different[row.name] else "" for _ in row],
    axis=1,
)
st.dataframe(styled, width="stretch")

st.divider()
components.section_header("Speed comparison", index="02")
fig = speed_comparison_chart(protocols, ids=ids)
if fig:
    st.pyplot(fig, width="stretch")
else:
    st.info("Selected protocols don't have directly comparable numeric speed values.")

st.divider()
components.section_header("Design trade-offs", index="03")
cols = st.columns(2)
for i, p in enumerate(sel_protocols):
    col = cols[i % 2]
    with col:
        components.section_header(p["name"])
        components.info_badge(p["category"], tone="signal")
        st.markdown("**✅ Advantages**")
        for a in p.get("advantages", []):
            st.markdown(f"- {a}")
        st.markdown("**⚠️ Limitations**")
        for limitation in p.get("limitations", []):
            st.markdown(f"- {limitation}")
        st.markdown("**Use Cases**")
        for u in p.get("use_cases", []):
            st.markdown(f"- {u}")

st.divider()
components.section_header("Choose against your constraints", index="04")
st.write(
    "There's no single 'best' protocol — the right choice always depends on your constraints: "
    "required speed, distance, power budget, pin count, cost, and determinism needs. "
    "Use the detailed profiles above (and the full profile in 📚 Encyclopedia) to weigh these trade-offs "
    "for your specific embedded design."
)

branding.page_footer()
