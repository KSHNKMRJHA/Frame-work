# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from utils.data_loader import load_protocols

from utils import branding

branding.page_config("Geography", "🌍")
branding.sidebar_identity()

protocols = load_protocols()

st.title("🌍 Geography & Origins")
st.caption("Where in the world did each protocol come from? A geographic tour of the organizations and countries that built the connected world.")


def primary_country(place):
    if not place:
        return "Unknown"
    # Take the first country-like token before a slash or comma
    p = place.split("/")[0].split(",")[0].strip()
    # Normalize a few common variants
    mapping = {
        "USA": "United States", "US": "United States",
        "International": "International", "Europe": "Europe (multi-country)",
    }
    return mapping.get(p, p)


countries = [primary_country(p.get("place", "")) for p in protocols]
counter = Counter(countries)
df = pd.DataFrame(sorted(counter.items(), key=lambda x: -x[1]), columns=["Country/Region", "Protocol Count"])

c1, c2 = st.columns([1.4, 1])
with c1:
    st.subheader("📊 Protocols Invented by Country/Region")
    st.dataframe(df, width='stretch', hide_index=True)
with c2:
    fig = px.pie(df.head(10), names="Country/Region", values="Protocol Count", title="Top 10 Contributing Countries/Regions")
    st.plotly_chart(fig, width='stretch')

st.divider()

# Attempt a choropleth using ISO country name matching (best-effort)
COUNTRY_ALIASES = {
    "United States": "United States", "Germany": "Germany", "Netherlands": "Netherlands",
    "Japan": "Japan", "Sweden": "Sweden", "Finland": "Finland", "Denmark": "Denmark",
    "France": "France", "Canada": "Canada", "Austria": "Austria", "Switzerland": "Switzerland",
    "United Kingdom": "United Kingdom", "UK": "United Kingdom",
}
map_rows = []
for country, count in counter.items():
    iso_name = COUNTRY_ALIASES.get(country)
    if iso_name:
        map_rows.append({"country": iso_name, "count": count})
if map_rows:
    map_df = pd.DataFrame(map_rows).groupby("country", as_index=False).sum()
    fig2 = px.choropleth(
        map_df, locations="country", locationmode="country names", color="count",
        color_continuous_scale="Blues", title="World Map: Protocol Origins",
    )
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, width='stretch')

st.divider()
st.subheader("🏢 Standards Organizations You Should Know")
orgs = {}
for p in protocols:
    org = p.get("organization") or "—"
    if org and org != "—":
        orgs.setdefault(org, []).append(p["name"])

org_cols = st.columns(2)
for i, (org, plist) in enumerate(sorted(orgs.items(), key=lambda x: -len(x[1]))[:16]):
    with org_cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"**{org}**")
            st.caption(", ".join(plist[:6]) + (f" +{len(plist)-6} more" if len(plist) > 6 else ""))

st.divider()
st.subheader("🔍 Explore by Country")
selected_country = st.selectbox("Pick a country/region:", sorted(counter.keys()))
matches = [p for p in protocols if primary_country(p.get("place", "")) == selected_country]
for p in matches:
    st.markdown(f"**{p['name']}** ({p['year']}) — {p.get('inventor','')}")
    st.caption(p["description"])

branding.page_footer()
