# -*- coding: utf-8 -*-
import json
import streamlit as st
from utils import state as state_utils
from utils.data_loader import load_protocols

from utils import branding

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
        bcols = st.columns(4)
        for i, b in enumerate(us["badges"]):
            with bcols[i % 4]:
                st.markdown(f"🏅 **{b}**")
    else:
        st.info("No badges yet — take a quiz or explore the encyclopedia to start earning them!")

with tab2:
    st.subheader("Appearance")
    st.write("The app theme is controlled by `.streamlit/config.toml`. Choose your preferred accent color to update it (restart the app for the new theme to fully apply).")
    color = st.color_picker("Accent color", value=us.get("accent_color", "#2563eb"))
    if color != us.get("accent_color"):
        us["accent_color"] = color
        state_utils.save_state(us)
        try:
            with open(".streamlit/config.toml", "r") as f:
                content = f.read()
            import re
            content = re.sub(r'primaryColor = ".*"', f'primaryColor = "{color}"', content)
            with open(".streamlit/config.toml", "w") as f:
                f.write(content)
            st.success(f"Accent color updated to {color}. Restart the app (`streamlit run app.py`) to see the full theme change.")
        except OSError:
            st.warning("Could not write to config.toml in this environment, but your preference was saved.")

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
