# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import load_protocols, get_categories

from utils import branding

branding.page_config("Timeline", "🕰️")
branding.sidebar_identity()

protocols = load_protocols()
categories = get_categories(protocols)

st.title("🕰️ History & Invention Timeline")
st.caption("Every protocol placed on a timeline by the year it was invented or first standardized — a 65-year journey from 1937's PCM to 5G and Matter.")

sel_cats = st.multiselect("Filter by category", categories, default=categories)
df = pd.DataFrame([p for p in protocols if p["category"] in sel_cats])
df = df.sort_values("year")

fig = px.scatter(
    df, x="year", y="category", color="category", hover_name="name",
    hover_data={"inventor": True, "place": True, "category": False, "year": True},
    size=[14] * len(df), size_max=14,
    title="Protocol Invention Timeline (hover for details)",
)
fig.update_layout(height=650, showlegend=False, yaxis_title="", xaxis_title="Year")
st.plotly_chart(fig, width='stretch')

st.divider()
st.subheader("📜 Decade-by-Decade Story")

decades = sorted(set((p["year"] // 10) * 10 for p in protocols))
for decade in decades:
    items = sorted([p for p in protocols if (p["year"] // 10) * 10 == decade], key=lambda p: p["year"])
    with st.expander(f"**{decade}s** — {len(items)} protocol(s) introduced", expanded=(decade >= 2010)):
        for p in items:
            st.markdown(f"**{p['year']} — {p['name']}** ({p['category']}) — {p['inventor']}"
                        + (f", {p['place']}" if p.get("place") else ""))
            st.caption(p["description"])
            st.markdown("---")

st.divider()
st.subheader("🏆 Milestones Worth Knowing")
milestones = sorted(protocols, key=lambda p: p["year"])[:6]
mcols = st.columns(3)
for i, p in enumerate(milestones):
    with mcols[i % 3]:
        with st.container(border=True):
            st.markdown(f"**{p['year']}**")
            st.markdown(f"### {p['name']}")
            st.caption(p["category"])
            st.write(p["description"][:140] + ("…" if len(p["description"]) > 140 else ""))

branding.page_footer()
