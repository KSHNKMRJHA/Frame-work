# -*- coding: utf-8 -*-
import streamlit as st
from utils.data_loader import load_protocols, get_categories
from utils.mindmap import full_mindmap, category_mindmap

from utils import branding

branding.page_config("Mind Map", "🗺️")
branding.sidebar_identity()

protocols = load_protocols()
categories = get_categories(protocols)

st.title("🗺️ Protocol Mind Map")
st.caption("A visual map of how every protocol connects — from the root concept down through categories to individual protocols and their close relatives.")

tab1, tab2 = st.tabs(["🌐 Full Universe Map", "🔬 Zoom Into a Category"])

with tab1:
    st.info("This map shows **all 116 protocols** grouped by category, radiating from the central concept. Larger nodes = categories; small nodes = individual protocols.")
    with st.spinner("Rendering mind map..."):
        fig = full_mindmap(protocols)
    st.pyplot(fig, width='stretch')

with tab2:
    cat = st.selectbox("Choose a category to explore its internal relationships:", categories)
    st.caption("Edges here also show cross-links between related protocols within the category (e.g., CAN ↔ CAN FD ↔ CANopen).")
    fig2 = category_mindmap(protocols, cat)
    st.pyplot(fig2, width='stretch')

    with st.expander("📋 List view of this category"):
        for p in [x for x in protocols if x["category"] == cat]:
            st.markdown(f"**{p['name']}** ({p['year']}) — {p['description']}")

branding.page_footer()
