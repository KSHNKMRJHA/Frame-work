# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from utils.data_loader import load_protocols
from utils.diagrams import speed_comparison_chart

from utils import branding

branding.page_config("Compare", "⚖️")
branding.sidebar_identity()

protocols = load_protocols()
names = [p["name"] for p in protocols]

st.title("⚖️ Compare Protocols")
st.caption(
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
st.dataframe(df.astype(str), width="stretch")

st.divider()
st.subheader("📈 Speed Comparison")
fig = speed_comparison_chart(protocols, ids=ids)
if fig:
    st.pyplot(fig, width="stretch")
else:
    st.info("Selected protocols don't have directly comparable numeric speed values.")

st.divider()
cols = st.columns(len(sel_protocols))
for col, p in zip(cols, sel_protocols):
    with col:
        st.markdown(f"### {p['name']}")
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
st.subheader("🏁 Which should you pick?")
st.write(
    "There's no single 'best' protocol — the right choice always depends on your constraints: "
    "required speed, distance, power budget, pin count, cost, and determinism needs. "
    "Use the detailed profiles above (and the full profile in 📚 Encyclopedia) to weigh these trade-offs "
    "for your specific embedded design."
)

branding.page_footer()
