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

from utils import ui_state

from utils import theme

import utils.components as components

from utils.branding import APP_ICON, APP_NAME, APP_TAGLINE

from utils.diagrams import category_bar_chart



st.set_page_config(

    page_title=APP_NAME,

    page_icon=APP_ICON,

    layout="wide",

    initial_sidebar_state="expanded",

)



branding.sidebar_identity()

branding.maybe_onboard()



protocols = load_protocols()

categories = get_categories(protocols)



# Quick search needs the data, so it is rendered after the load.

ui_state.global_search(protocols)



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



# --------------------------------------------------------------- home hero ----

_home_pal = theme.current_palette()

_version_chip = (

    f"<span style='display:inline-block; font-family:{theme.MONO_STACK}; "

    f"font-size:0.75rem; font-weight:700; color:{theme.contrast_text(_home_pal['accent'])}; "

    f"background:{_home_pal['accent']}; border-radius:999px; "

    f"padding:0.12rem 0.7rem; margin-left:0.4rem; white-space:nowrap;'>"

    f"{branding.version_label()}</span>"

)

st.markdown(
    f"""
<div style="padding:0.2rem 0 0.8rem 0; border-bottom:1px solid {_home_pal['border']};">
  <div style="display:flex; align-items:center; gap:0.9rem; align-items:baseline;">
    <div style="font-size:2.6rem;">{APP_ICON}</div>
    <div style="font-size:2.3rem; font-weight:700; color:{_home_pal['text']}; line-height:1.05;">
      {APP_NAME} {_version_chip}
    </div>
  </div>
  <div style="font-size:0.8rem; letter-spacing:0.18em; text-transform:uppercase; color:{_home_pal['accent']}; font-weight:600; margin-top:0.4rem;">
    Embedded Communication Protocols
  </div>
  <p style="font-size:1.02rem; color:{_home_pal['text_muted']}; margin-top:0.4rem; max-width:72ch; line-height:1.5;">
    {APP_TAGLINE}
  </p>
  <p style="font-size:0.78rem; color:{_home_pal['text_faint']}; margin-top:0.55rem;">
    {branding.build_line()}
  </p>
</div>
""",
    unsafe_allow_html=True,
)



# --------------------------------------------------------------- metric strip --

mrow1 = st.columns(3)
with mrow1[0]:
    components.engineering_metric("Protocols", len(protocols), tone="signal")
with mrow1[1]:
    components.engineering_metric("Categories", len(categories), tone="accent")
with mrow1[2]:
    components.engineering_metric("Level", us["level"], f"{us['xp']} XP", tone="ok")
mrow2 = st.columns(2)
with mrow2[0]:
    components.engineering_metric("Explored",
                                   f"{len(us['protocols_viewed'])}/{len(protocols)}",
                                   tone="warn")
with mrow2[1]:
    components.engineering_metric("Badges", len(us["badges"]), tone="neutral")


st.divider()



# --------------------------------------------------------- QUICK SEARCH ----

st.subheader("🔎 Quick Jump")

q = st.text_input(

    "Search any protocol by name, keyword, inventor, or year...", placeholder="e.g. CAN, Modbus, 1996, Bosch, Ethernet"

)

if q:

    from utils.data_loader import search_protocols



    results = search_protocols(protocols, q)[:8]

    if results:

        for p in results:

            with st.expander(f"**{p['name']}** — {p['category']} ({p['year']})"):

                st.write(p["description"])

                st.caption(

                    "Open the 📚 Encyclopedia page from the sidebar for the full interactive profile, diagrams, and examples."

                )

    else:

        st.info("No matches found. Try a broader term.")



st.divider()



# Ordered to match the sidebar: reference first, then context, then
# practice, then tools. Grouped into compact rows below; cards are NOT hidden
# or reordered.
#
# `cards` is the flat ordered nav (source of truth for the nav gate, which
# parses this list and requires it to match pages/ sidebar order exactly).
cards = [
    "pages/1_📚_Encyclopedia.py",
    "pages/2_⚖️_Compare.py",
    "pages/3_🧭_Selector.py",
    "pages/4_📖_Glossary.py",
    "pages/5_🕰️_Timeline_History.py",
    "pages/6_🗺️_Mindmap.py",
    "pages/7_🌍_Geography_Origins.py",
    "pages/8_🧠_Quiz_Assessment.py",
    "pages/9_🎮_Puzzles_Games.py",
    "pages/10_🔬_Science_Math_Lab.py",
    "pages/11_⚙️_Settings_Profile.py",
    "pages/12_ℹ️_Info.py",
]

# Grouped display derived from the flat list above.
_NAV_DESCRIPTIONS = {
    "Encyclopedia": "Browse, search and filter every protocol with full technical profiles.",
    "Compare": "Put protocols side-by-side: speed, pins, wiring, voltages and more.",
    "Selector": "Answer 4 questions and get a ranked shortlist with standard documents.",
    "Glossary": "Every term in one place, each with the protocols where it matters.",
    "Timeline": "Travel the decades: who invented what, where, and why.",
    "Mindmap": "See how every category and protocol relates.",
    "Geography": "Which countries and organizations invented the protocols.",
    "Quiz": "Auto-generated MCQs across every protocol, with XP and badges.",
    "Puzzles": "Frame-field reordering, speed matching, guess-the-protocol.",
    "Lab": "Baud rate, Nyquist/Shannon, CRC, CAN, I2C, RS-485, RF link budget.",
    "Settings": "Profile, XP, badges, theme accent, progress reset.",
    "Info": "About, deployment, links, audience guide, credits and license.",
}

def _nav_title(path):
    stem = path.split("pages/", 1)[-1]
    stem = stem.split("_", 1)[-1]
    return stem.rsplit(".py", 1)[0].replace("_", " ")

NAV_GROUPS = [
    ("Reference", cards[0:4]),
    ("Context", cards[4:7]),
    ("Practice", cards[7:10]),
    ("Tools", cards[10:12]),
]

_pal = theme.current_palette()

for group_title, paths in NAV_GROUPS:
    items = [(_nav_title(p), _NAV_DESCRIPTIONS.get(_nav_title(p), ""), p) for p in paths]
    st.markdown(
        f"<div style='font-size:0.72rem; letter-spacing:0.14em; text-transform:uppercase; "
        f"font-weight:700; color:{_pal['accent']}; margin:0.15rem 0 0.3rem 0;'>{group_title}</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(min(len(items), 2))
    for col, (card_title, card_desc, page_file) in zip(cols, items):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div style='font-weight:700; font-size:1.02rem; color:{_pal['text']};'>"
                    f"{card_title}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='font-size:0.78rem; color:{_pal['text_muted']}; margin-top:0.2rem;'>"
                    f"{card_desc}</div>",
                    unsafe_allow_html=True,
                )
                st.page_link(page_file, label="Open")


st.divider()


# ------------------------------------------------- CONTINUE WHERE YOU LEFT OFF

resume_id = ui_state.last_protocol()

if resume_id:

    resume = next((p for p in protocols if p["id"] == resume_id), None)

    if resume:

        with st.container(border=True):

            rc = st.columns([4, 1])

            with rc[0]:

                st.markdown("**↩️ Continue where you left off**")

                st.caption(f"{resume['name']} · {resume['category']} · "

                           f"{resume.get('topology', '—')}")

            with rc[1]:

                st.page_link(f"pages/1_📚_Encyclopedia.py?p={resume_id}",

                             label="Resume", icon="➡️")



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

st.pyplot(category_bar_chart(protocols), width="stretch")



st.caption(

    "Built for students, hobbyists & professionals · No internet required · "

    "Runs 100% locally · See the sidebar for every module."

)



branding.page_footer()

