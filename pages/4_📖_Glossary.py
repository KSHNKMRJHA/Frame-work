# -*- coding: utf-8 -*-
import streamlit as st

from utils.data_loader import load_protocols, get_by_id
from utils.glossary import GLOSSARY, GROUPS, search_glossary

from utils import branding, components

branding.page_config("Glossary", "📖")
branding.sidebar_identity()

protocols = load_protocols()

components.page_hero("Engineering reference", "Glossary",
    f"{len(GLOSSARY)} terms, each linked to the protocols where it matters — "
    "the jargon decoder ring for the whole Academy."
)

c1, c2 = st.columns([2, 1])
with c1:
    q = st.text_input("Search terms", placeholder="e.g. arbitration, jitter, PLCA…")
with c2:
    grp = st.selectbox("Group", ["All"] + GROUPS)

terms = search_glossary(q)
if grp != "All":
    terms = [t for t in terms if t["group"] == grp]

letters = sorted({t["term"][0].upper() for t in terms})
letter = st.pills("Browse alphabetically", ["All"] + letters, default="All")
if letter and letter != "All":
    terms = [t for t in terms if t["term"][0].upper() == letter]

st.caption(f"Showing **{len(terms)}** of {len(GLOSSARY)} terms.")

for t in terms:
    components.section_header(t["term"])
    components.info_badge(t["group"], tone="signal")
    st.write(t["definition"])
    if t.get("see"):
        names = []
        for pid in t["see"]:
            p = get_by_id(protocols, pid)
            names.append(p["name"] if p else pid)
        st.caption("Related protocols: " + " · ".join(names))

branding.page_footer()
