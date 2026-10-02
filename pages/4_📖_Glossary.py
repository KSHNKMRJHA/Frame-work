# -*- coding: utf-8 -*-
import streamlit as st

from utils.data_loader import load_protocols, get_by_id
from utils.glossary import GLOSSARY, GROUPS, search_glossary

from utils import branding

branding.page_config("Glossary", "📖")
branding.sidebar_identity()

protocols = load_protocols()

st.title("📖 Glossary")
st.caption(
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

st.caption(f"Showing **{len(terms)}** of {len(GLOSSARY)} terms.")

for t in terms:
    with st.container(border=True):
        st.markdown(f"### {t['term']}")
        st.caption(t["group"])
        st.write(t["definition"])
        if t.get("see"):
            names = []
            for pid in t["see"]:
                p = get_by_id(protocols, pid)
                names.append(p["name"] if p else pid)
            st.caption("📎 See: " + " · ".join(names))

branding.page_footer()
