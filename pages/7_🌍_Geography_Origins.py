
import streamlit as st
import pandas as pd
import plotly.express as px

from utils import origins
from utils.data_loader import load_protocols

from utils import branding, components, theme

branding.page_config("Geography", "🌍")
branding.sidebar_identity()

protocols = load_protocols()

components.page_hero("Origin reference", "Geography & origins",
    "Where in the world did each protocol come from? A geographic tour of the organizations and countries that built the connected world."
)

# One normalisation source for the map, the counts and the explorer below. The
# old page parsed `place` twice with two different, naive splitters, which is how
# "Cambridge, Massachusetts, USA" turned into a country called "Cambridge" that
# has no map polygon - and that protocol simply disappeared from the map.
summary = origins.summarize(protocols)

# Two rows of two. A single row of four left each metric ~98px wide at 900px,
# and st.metric clips its label with an ellipsis rather than wrapping it.
m1, m2 = st.columns(2)
with m1:
    components.engineering_metric("Protocols", summary["total"])
with m2:
    components.engineering_metric("Single-country origins", summary["mapped_count"])
m3, m4 = st.columns(2)
with m3:
    components.engineering_metric("International / multi-country", summary["international_count"])
with m4:
    components.engineering_metric("Unresolved", summary["unknown_count"])

concrete_country_ids = {p["id"] for group in summary["per_country"].values() for p in group}
st.caption(
    f"Coverage: **{len(concrete_country_ids)}**"
    f" of {summary['total']} protocols resolve to at least one concrete country. "
    "Counts always add up to the total - unresolved origins are reported, never dropped."
)

# Countries that have a polygon we can actually shade.
map_rows = []
for country, plist in summary["per_country"].items():
    iso = origins.iso_name(country)
    if not iso:
        continue
    names = sorted(p["name"] for p in plist)
    shown = ", ".join(names[:6]) + (f" +{len(names) - 6} more" if len(names) > 6 else "")
    map_rows.append({
        "country": iso,
        "count": len(plist),
        "protocols": shown,
        "hover": f"<b>{country}</b><br>{len(plist)} protocol(s)<br>{shown}",
    })

if map_rows:
    map_df = pd.DataFrame(map_rows).sort_values("count", ascending=False)
    fig2 = px.choropleth(
        map_df,
        locations="country",
        locationmode="country names",
        color="count",
        hover_name="country",
        hover_data={"protocols": False, "count": True, "hover": True},
        color_continuous_scale="Blues",
        title="World Map: Protocol Origins (hover a country for its protocols)",
    )
    fig2.update_layout(height=520)
    pal = theme.current_palette()
    fig2.update_layout(paper_bgcolor=pal["bg"], font_color=pal["text"],
                       margin=dict(l=10, r=10, t=70, b=10))
    fig2.update_geos(bgcolor=pal["bg"], landcolor=pal["surface_alt"],
                     showland=True, coastlinecolor=pal["border_strong"])
    st.plotly_chart(fig2, width="stretch")

components.section_header("Country accounting", index="01")
st.dataframe(
    pd.DataFrame([
        {
            "Country": c,
            "Protocols": len(plist),
            "Names": ", ".join(sorted(p["name"] for p in plist)[:8])
            + (f" +{len(plist) - 8} more" if len(plist) > 8 else ""),
        }
        for c, plist in sorted(summary["per_country"].items(), key=lambda kv: -len(kv[1]))
    ]),
    width="stretch",
    hide_index=True,
)

st.divider()
components.section_header("Standards organizations", index="02")
orgs = {}
for p in protocols:
    org = p.get("organization") or "—"
    if org and org != "—":
        orgs.setdefault(org, []).append(p["name"])

org_cols = st.columns(2)
for i, (org, plist) in enumerate(sorted(orgs.items(), key=lambda x: -len(x[1]))[:16]):
    with org_cols[i % 2]:
        with st.container(border=True):
            components.section_header(org)
            st.caption(", ".join(plist[:6]) + (f" +{len(plist) - 6} more" if len(plist) > 6 else ""))

st.divider()
components.section_header("Explore by country", index="03")
# Same normalisation source as the map above - one parser, one answer.
selected_country = st.selectbox(
    "Pick a country:", sorted(summary["per_country"].keys(), key=lambda c: (-len(summary["per_country"][c]), c))
)
for p in summary["per_country"][selected_country]:
    st.markdown(f"**{p['name']}** ({p['year']}) — {p.get('inventor', '')}")
    st.caption(p["description"])

if summary["international_count"] or summary["unknown_count"]:
    with st.expander(
        f"🌍 International / multi-country and unresolved origins "
        f"({summary['international_count']} + {summary['unknown_count']})"
    ):
        st.caption(
            "These are deliberately not forced onto a single country. The map shades "
            "every concrete country they name; the remaining entries have no single "
            "origin to shade."
        )
        for info in summary["international"]:
            p = info["protocol"]
            note = f" — {info['note']}" if info["note"] else ""
            st.markdown(f"**{p['name']}** — {info['label']}{note}")
            st.caption(f"Source string: `{p.get('place', '')}`")
        for info in summary["unknown"]:
            p = info["protocol"]
            st.markdown(f"**{p['name']}** — unresolved")
            st.caption(f"Source string: `{p.get('place', '')}`")

branding.page_footer()
