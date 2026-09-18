# -*- coding: utf-8 -*-
"""
FrameWork
Home / Landing page.

Run with:  streamlit run app.py
"""
import datetime

import streamlit as st

from utils.data_loader import load_protocols, get_categories
from utils import state as state_utils
from utils import branding
from utils.branding import APP_ICON, APP_NAME, APP_TAGLINE
from utils.diagrams import category_bar_chart

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

branding.sidebar_identity()

protocols = load_protocols()
categories = get_categories(protocols)

if "user_state" not in st.session_state:
    st.session_state.user_state = state_utils.load_state()
us = st.session_state.user_state

# load_state() repairs or replaces a damaged progress file rather than crashing,
# but the user must be told — otherwise their progress just silently reads zero.
if us.pop("_recovered", False):
    st.warning(
        "Your saved progress file could not be read and has been reset. "
        "The original file was left untouched on disk, so nothing is lost "
        "permanently — see `data/user_state.json`.",
        icon="⚠️",
    )
if us.pop("_repaired", None):
    st.info(
        "Some values in your saved progress file were invalid and have been "
        "reset to their defaults. Everything else was kept.",
        icon="🛠️",
    )

# ---------------------------------------------------------------- HERO -----
st.markdown(
    f"""
    <div style="text-align:center; padding: 1.2rem 0 0.4rem 0;">
        <div style="font-size:0.82rem; letter-spacing:0.22em; text-transform:uppercase; color:#64748b;">
            Embedded Communication Protocols
        </div>
        <h1 style="font-size:2.9rem; margin:0.15rem 0 0.35rem 0;">
            {APP_ICON} {APP_NAME}
            <span style="font-size:0.95rem; vertical-align:middle; background:#1e293b;
                         color:#a5b4fc; border:1px solid #334155; border-radius:999px;
                         padding:0.15rem 0.65rem; margin-left:0.35rem; white-space:nowrap;">
                {branding.version_label()}
            </span>
        </h1>
        <p style="font-size:1.15rem; color:#94a3b8; margin-top:0.3rem;">{APP_TAGLINE}</p>
        <p style="font-size:0.8rem; color:#64748b; margin-top:0.35rem;">{branding.build_line()}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Protocols Covered", len(protocols))
c2.metric("Categories", len(categories))
c3.metric("Your Level", us["level"], f"{us['xp']} XP")
c4.metric("Protocols Explored", f"{len(us['protocols_viewed'])}/{len(protocols)}")
c5.metric("Badges Earned", len(us["badges"]))

st.divider()

# --------------------------------------------------------- QUICK SEARCH ----
st.subheader("🔎 Quick Jump")
q = st.text_input("Search any protocol by name, keyword, inventor, or year...", placeholder="e.g. CAN, Modbus, 1996, Bosch, Ethernet")
if q:
    from utils.data_loader import search_protocols
    results = search_protocols(protocols, q)[:8]
    if results:
        for p in results:
            with st.expander(f"**{p['name']}** — {p['category']} ({p['year']})"):
                st.write(p["description"])
                st.caption("Open the 📚 Encyclopedia page from the sidebar for the full interactive profile, diagrams, and examples.")
    else:
        st.info("No matches found. Try a broader term.")

st.divider()

# --------------------------------------------------------- NAV CARDS -------
st.subheader("🧭 Explore the Academy")

cards = [
    ("📚 Encyclopedia", "Browse, search & filter all protocols with full technical profiles — history, diagrams, pinouts, use-cases, limitations, examples.", "pages/1_📚_Encyclopedia.py"),
    ("🕰️ History & Timeline", "Travel through the decades — who invented what, where, and why, on an interactive timeline.", "pages/2_🕰️_Timeline_History.py"),
    ("🗺️ Mind Map", "Visualize how every protocol category and protocol relates to each other.", "pages/3_🗺️_Mindmap.py"),
    ("⚖️ Compare", "Put 2-4 protocols side-by-side: speed, pins, topology, use-cases and more.", "pages/4_⚖️_Compare.py"),
    ("🧠 Quiz & Assessment", "Auto-generated MCQs across every protocol, filterable by category & difficulty, with XP & badges.", "pages/5_🧠_Quiz_Assessment.py"),
    ("🎮 Puzzles & Games", "Frame-field reordering, protocol-speed matching, and 'guess the protocol' challenges.", "pages/6_🎮_Puzzles_Games.py"),
    ("🔬 Science & Math Lab", "Interactive calculators: baud rate & bit-timing, Nyquist/Shannon capacity, CRC, frequency↔wavelength.", "pages/7_🔬_Science_Math_Lab.py"),
    ("🌍 Geography & Origins", "See which countries and organizations invented the protocols that run the modern world.", "pages/8_🌍_Geography_Origins.py"),
    ("⚙️ Settings & Profile", "Your profile, XP, badges, theme accent, and progress reset.", "pages/9_⚙️_Settings_Profile.py"),
    ("ℹ️ About, Roadmap & Credits", "Deployment roadmap (web/EXE/APK), GitHub setup, license, and credits.", "pages/10_ℹ️_About_Roadmap_Credits.py"),
]

cols = st.columns(2)
for i, (title, desc, path) in enumerate(cards):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.write(desc)
            st.page_link(path, label=f"Open {title.split(' ',1)[1]}", icon="➡️")

st.divider()

# ------------------------------------------------------- PROTOCOL OF DAY ---
st.subheader("🌟 Protocol of the Day")
day_seed = int(datetime.date.today().strftime("%Y%m%d"))
potd = protocols[day_seed % len(protocols)]
with st.container(border=True):
    left, right = st.columns([2, 1])
    with left:
        st.markdown(f"## {potd['name']}")
        st.caption(f"Category: {potd['category']}  |  Invented: {potd['year']} by {potd['inventor']}")
        st.write(potd["description"])
        if potd.get("fun_fact"):
            st.info(f"💡 **Fun fact:** {potd['fun_fact']}")
    with right:
        st.metric("Typical Speed", potd.get("speed", "N/A"))
        st.metric("Topology", potd.get("topology", "N/A"))
        st.metric("Difficulty", potd.get("difficulty", "N/A"))

st.divider()
st.subheader("📊 Coverage Overview")
st.pyplot(category_bar_chart(protocols), width='stretch')

st.caption(
    "Built for students, hobbyists & professionals · No internet required · "
    "Runs 100% locally · See the sidebar for every module."
)

branding.page_footer()
