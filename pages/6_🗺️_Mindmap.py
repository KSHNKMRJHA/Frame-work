# -*- coding: utf-8 -*-
import streamlit as st
from utils.data_loader import load_protocols, get_categories
from utils.mindmap import full_mindmap, category_mindmap
from utils import theme as theme_mod

from utils import branding, components

branding.page_config("Mind Map", "🗺️")
branding.sidebar_identity()

protocols = load_protocols()
categories = get_categories(protocols)

components.page_hero("Relationship explorer", "Protocol mind map",
                     "Trace categories, individual protocols, and their close relatives.",
                     meta=f"{len(protocols)} protocol identities")

tab1, tab2 = st.tabs(["🌐 Full Universe Map", "🔬 Zoom Into a Category"])

# Diagrams are drawn with Matplotlib, which knows nothing about the browser's
# theme, so the active palette is detected here and passed in. This returns
# Python colour tokens only - no CSS, no JS.
pal = theme_mod.current_palette()

with tab1:
    components.callout(
        f"This map shows all {len(protocols)} protocols grouped by category, "
        "radiating from the central concept. Larger nodes = categories; "
        "small nodes = individual protocols, each labelled with its full name."
    )
    with st.spinner("Rendering mind map..."):
        fig = full_mindmap(protocols, palette=pal)
    st.pyplot(fig, width='stretch')
    st.caption("Full protocol names are preserved. Use category exploration or list view for a closer inspection on small screens.")

with tab2:
    cat = st.selectbox("Choose a category to explore its internal relationships:", categories)
    st.caption("Each protocol in this category is shown with its full name.")
    fig2 = category_mindmap(protocols, cat, palette=pal)
    st.pyplot(fig2, width='stretch')

    with st.expander("📋 List view of this category"):
        for p in [x for x in protocols if x["category"] == cat]:
            st.markdown(f"**{p['name']}** ({p['year']}) — {p['description']}")

branding.page_footer()
