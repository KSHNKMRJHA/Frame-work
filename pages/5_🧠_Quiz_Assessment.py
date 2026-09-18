# -*- coding: utf-8 -*-
import random
import streamlit as st
from utils.data_loader import load_protocols, get_categories
from utils import state as state_utils
from utils.quiz_engine import generate_quiz

from utils import branding

branding.page_config("Quiz", "🧠")
branding.sidebar_identity()

protocols = load_protocols()
categories = ["All"] + get_categories(protocols)
difficulties = ["All", "Beginner", "Intermediate", "Advanced"]

if "user_state" not in st.session_state:
    st.session_state.user_state = state_utils.load_state()
us = st.session_state.user_state

st.title("🧠 Quiz & Assessment")
st.caption("Every question is procedurally generated from the live protocol database — new combinations every time.")

if "quiz" not in st.session_state:
    st.session_state.quiz = None
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False

with st.form("quiz_setup"):
    c1, c2, c3 = st.columns(3)
    with c1:
        cat = st.selectbox("Category focus", categories)
    with c2:
        diff = st.selectbox("Difficulty", difficulties)
    with c3:
        n = st.slider("Number of questions", 5, 25, 10)
    start = st.form_submit_button("🎯 Start New Quiz", width='stretch')

if start:
    seed = random.randint(0, 1_000_000)
    st.session_state.quiz = generate_quiz(protocols, n=n, seed=seed, category=cat, difficulty=diff)
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False

quiz = st.session_state.quiz
if quiz:
    st.divider()
    st.subheader(f"📝 Your Quiz ({len(quiz)} questions)")
    for i, q in enumerate(quiz):
        st.markdown(f"**Q{i+1}.** {q['question']}")
        key = f"q_{i}"
        default_index = None
        choice = st.radio(
            "Select an answer:", q["options"], key=key, index=None,
            label_visibility="collapsed", disabled=st.session_state.quiz_submitted,
        )
        st.session_state.quiz_answers[i] = choice
        if st.session_state.quiz_submitted:
            if choice == q["answer"]:
                st.success(f"✅ Correct! {q['explain']}")
            else:
                st.error(f"❌ Correct answer: **{q['answer']}**. {q['explain']}")
        st.markdown("---")

    if not st.session_state.quiz_submitted:
        if st.button("✅ Submit Quiz", type="primary", width='stretch'):
            st.session_state.quiz_submitted = True
            correct = sum(1 for i, q in enumerate(quiz) if st.session_state.quiz_answers.get(i) == q["answer"])
            pct = 100 * correct / len(quiz)
            state_utils.record_quiz_result(us, pct)
            state_utils.save_state(us)
            st.session_state.last_score = (correct, len(quiz), pct)
            st.rerun()
    else:
        correct, total, pct = st.session_state.last_score
        st.divider()
        st.subheader("🏆 Results")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Score", f"{correct}/{total}")
        rc2.metric("Percentage", f"{pct:.0f}%")
        rc3.metric("XP Earned", f"+{int(10 + pct/5)}")
        if pct == 100:
            st.balloons()
            st.success("🎉 Perfect score! You've earned the 'Perfectionist' badge if this is your first 100%.")
        elif pct >= 70:
            st.success("Great job! Solid understanding of these protocols.")
        else:
            st.info("Keep practicing — revisit the 📚 Encyclopedia for the protocols you missed.")
        if st.button("🔁 Try Another Quiz"):
            st.session_state.quiz = None
            st.rerun()
else:
    st.info("Configure your quiz above and click **Start New Quiz** to begin.")

st.divider()
st.subheader("📊 Your Quiz Stats")
sc1, sc2, sc3 = st.columns(3)
sc1.metric("Quizzes Taken", us["quizzes_taken"])
sc2.metric("Best Score", f"{us['best_score_pct']:.0f}%")
sc3.metric("Current Level", us["level"])
if us["badges"]:
    st.write("**Badges:** " + ", ".join(f"🏅 {b}" for b in us["badges"]))

branding.page_footer()
