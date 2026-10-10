# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import load_protocols, get_categories

from utils import branding, components, theme
from utils.diagrams import diagram_palette

branding.page_config("Timeline", "🕰️")
branding.sidebar_identity()

protocols = load_protocols()
categories = get_categories(protocols)

components.page_hero("Engineering context", "History & invention timeline",
                     "Explore invention years, standards organizations, and the protocols that followed.")

sel_cats = st.multiselect("Filter by category", categories, default=categories)
df = pd.DataFrame([p for p in protocols if p["category"] in sel_cats])
df = df.sort_values("year")

fig = px.scatter(
    df, x="year", y="category", color="category", hover_name="name",
    hover_data={"inventor": True, "place": True, "category": False, "year": True},
    size=[14] * len(df), size_max=14,
    color_discrete_sequence=diagram_palette()["series"],
    title="Protocol Invention Timeline (hover for details)",
)
fig.update_layout(height=650, showlegend=False, yaxis_title="", xaxis_title="Year")
pal = theme.current_palette()
fig.update_layout(paper_bgcolor=pal["bg"], plot_bgcolor=pal["surface"],
                  font_color=pal["text"], margin=dict(l=20, r=20, t=60, b=30))
fig.update_xaxes(gridcolor=pal["border"], zerolinecolor=pal["border"])
fig.update_yaxes(gridcolor=pal["border"])
st.plotly_chart(fig, width='stretch')

st.divider()
components.section_header("Decade-by-decade reference", index="01")

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
components.section_header("Early milestones", index="02")
milestones = sorted(protocols, key=lambda p: p["year"])[:6]
mcols = st.columns(3)
for i, p in enumerate(milestones):
    with mcols[i % 3]:
        with st.container(border=True):
            components.info_badge(str(p["year"]), tone="signal")
            components.section_header(p["name"])
            st.caption(f"{p['category']} · {p['inventor']}")
            st.write(p["description"][:140] + ("…" if len(p["description"]) > 140 else ""))

branding.page_footer()
