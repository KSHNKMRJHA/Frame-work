# -*- coding: utf-8 -*-
import json
import streamlit as st
from utils import state as state_utils
from utils.data_loader import load_protocols

from utils import branding
from utils import theme as theme_mod

branding.page_config("Settings", "⚙️")
branding.sidebar_identity()

protocols = load_protocols()

if "user_state" not in st.session_state:
    st.session_state.user_state = state_utils.load_state()
us = st.session_state.user_state

st.title("⚙️ Settings & Profile")
st.caption("Your learning profile, progress, and app configuration — stored locally in `data/user_state.json`.")

tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🎨 Appearance", "📈 Progress & History", "🗑️ Reset / Export"])

with tab1:
    st.subheader("Your Profile")
    new_name = st.text_input("Display name", value=us["username"])
    if new_name != us["username"]:
        us["username"] = new_name
        state_utils.save_state(us)
        st.success("Name updated.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Level", us["level"])
    c2.metric("Total XP", us["xp"])
    c3.metric("Next Level At", (us["level"]) * 100)
    st.progress(min(1.0, (us["xp"] % 100) / 100))

    st.markdown("#### 🏅 Badges")
    if us["badges"]:
        # Size the row to the badge count. A fixed st.columns(4) left three
        # empty quarters whenever fewer than four badges were earned, and at
        # tablet widths that squeezed the used column to ~98px.
        ncols = min(4, len(us["badges"]))
        bcols = st.columns(ncols)
        for i, b in enumerate(us["badges"]):
            with bcols[i % ncols]:
                st.markdown(f"🏅 **{b}**")
    else:
        st.info("No badges yet — take a quiz or explore the encyclopedia to start earning them!")

with tab2:
    st.subheader("Appearance")

    # Streamlit 1.64 exposes the browser's resolved theme READ-ONLY through
    # st.context.theme. There is no public Python API to set it per session, so
    # the honest thing is to report the active theme and point at the control
    # Streamlit actually ships - rather than offering a toggle that cannot work.
    active = theme_mod.active_theme_type()
    shown = {"light": "Light", "dark": "Dark"}.get(active, "System / default")

    st.markdown(f"**Current active theme:** {shown}")

    with st.container(border=True):
        st.markdown("**Change the theme**")
        st.markdown(
            "Use Streamlit's own menu:\n\n"
            "**⋮ → Settings → Theme**, then choose:\n\n"
            "- **Light**\n"
            "- **Dark**\n"
            "- **Use system setting** — follows your OS\n\n"
            "This is applied by Streamlit itself and remembered by your browser, "
            "per user and per device."
        )

    st.caption(
        "FrameWork defines both palettes under native `[theme.light]` and "
        "`[theme.dark]` keys, so both are fully styled. There is deliberately no "
        "in-app theme switcher: writing `.streamlit/config.toml` from a visitor's "
        "session would change the app for everyone, which is why that approach "
        "was removed."
    )

    st.divider()
    st.markdown('<div class="fw-fieldlabel">Accent color</div>', unsafe_allow_html=True)
    color = st.color_picker(
        "Accent color", value=us.get("accent_color", "#3b82f6"), label_visibility="collapsed"
    )
    if color != us.get("accent_color"):
        # Saved for the learner's own profile. It cannot restyle the running app
        # for everyone, so it is stored rather than pushed into project config.
        us["accent_color"] = color
        state_utils.save_state(us)
        st.info(
            f"Saved {color} to your profile. Streamlit's accent colour is fixed "
            "for all users by `.streamlit/config.toml`; this preference is kept "
            "with your progress."
        )

with tab3:
    st.subheader("Learning Progress")
    c1, c2, c3 = st.columns(3)
    c1.metric("Protocols Explored", f"{len(us['protocols_viewed'])}/{len(protocols)}")
    c2.metric("Quizzes Taken", us["quizzes_taken"])
    c3.metric("Best Quiz Score", f"{us['best_score_pct']:.0f}%")

    st.markdown("#### 🕘 Recent Activity")
    if us["history"]:
        for entry in reversed(us["history"][-20:]):
            st.markdown(f"`{entry['date']}` — **{entry['activity']}**: {entry['detail']}")
    else:
        st.info("No activity yet.")

with tab4:
    st.subheader("Reset or Export Your Data")
    st.download_button(
        "⬇️ Export progress as JSON",
        data=json.dumps(us, indent=2),
        file_name="embedded_academy_progress.json",
        mime="application/json",
    )
    st.warning("Resetting will permanently erase your XP, badges, and history.")
    if st.button("🗑️ Reset All Progress", type="secondary"):
        st.session_state.user_state = state_utils.reset_progress()
        st.success("Progress reset. Reloading...")
        st.rerun()

branding.page_footer()
