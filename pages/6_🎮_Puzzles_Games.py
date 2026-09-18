# -*- coding: utf-8 -*-
import random
import re
import unicodedata

import streamlit as st
from utils.data_loader import load_protocols, get_categories
from utils import state as state_utils
from utils.quiz_engine import generate_matching_puzzle, generate_frame_order_puzzle

from utils import branding

branding.page_config("Puzzles & Games", "🎮")
branding.sidebar_identity()

protocols = load_protocols()
categories = ["All"] + get_categories(protocols)

if "user_state" not in st.session_state:
    st.session_state.user_state = state_utils.load_state()
us = st.session_state.user_state

st.title("🎮 Puzzles & Games")
st.caption("Learn by playing — three game modes built directly from the protocol database.")

game = st.tabs(["🔗 Speed Matching Game", "🧩 Frame Field Reorder Puzzle", "🕵️ Guess the Protocol"])

CHOOSE = "-- choose --"


def _normalise(text):
    """Fold a guess for comparison: strip accents/punctuation, collapse spaces.

    'I²C', 'i2c' and 'I 2 C' all fold to 'i2c', so a learner who typed the
    right answer in a reasonable way is not marked wrong on formatting.
    """
    text = unicodedata.normalize("NFKD", text or "").casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", text)


def _accepted_answers(protocol):
    """Every spelling that counts as naming this protocol.

    The old check was `guess.strip().lower() in target["name"].lower()`, a
    substring test — so an EMPTY guess matched everything (the empty string is
    a substring of every string) and single letters matched most of the
    dataset. Matching is now against a set of whole names.
    """
    name = protocol["name"]
    answers = {_normalise(name)}

    # "I²C (Inter-Integrated Circuit)" -> also accept "I²C" and the expansion.
    short = re.sub(r"\s*\([^)]*\)\s*", "", name).strip()
    if short:
        answers.add(_normalise(short))
    for inner in re.findall(r"\(([^)]*)\)", name):
        if inner:
            answers.add(_normalise(inner))

    # "FTP / TFTP", "Telnet / SSH", "WPA2 / WPA3" -> accept either side.
    for part in re.split(r"\s*/\s*", short or name):
        part = part.strip()
        if len(part) >= 2:
            answers.add(_normalise(part))

    # The database id is a reasonable thing to type ("modbus_rtu", "can").
    answers.add(_normalise(protocol["id"]))
    return {a for a in answers if len(a) >= 2}


# ============================================================ GAME 1 =======
with game[0]:
    st.subheader("🔗 Match the Protocol to its Speed")
    cat = st.selectbox("Category (optional filter)", categories, key="match_cat")

    def _new_match_round(seed):
        st.session_state.match_puzzle = generate_matching_puzzle(
            protocols, n=6, seed=seed, category=cat
        )
        st.session_state.match_submitted = False
        # Clear the per-protocol selectboxes so a new round starts blank
        # instead of inheriting the previous round's answers.
        for key in [k for k in st.session_state if k.startswith("match_sel_")]:
            del st.session_state[key]

    if st.button("🎲 New Matching Round", key="new_match"):
        _new_match_round(random.randint(0, 99999))
        st.rerun()

    if "match_puzzle" not in st.session_state:
        _new_match_round(1)

    puzzle = st.session_state.match_puzzle
    st.write("For each protocol on the left, choose its correct typical speed from the dropdown.")

    user_matches = {}
    for name in puzzle["left"]:
        user_matches[name] = st.selectbox(
            name, [CHOOSE] + puzzle["right_shuffled"],
            key=f"match_sel_{name}",
            disabled=st.session_state.get("match_submitted", False),
        )

    unanswered = [n for n, v in user_matches.items() if v == CHOOSE]
    already_scored = st.session_state.get("match_submitted", False)

    if st.button("✅ Check Matches", disabled=already_scored):
        if unanswered:
            st.warning(f"Pick a speed for all {len(puzzle['left'])} protocols first "
                       f"({len(unanswered)} still unanswered).")
        else:
            correct_count = sum(1 for n in puzzle["left"] if user_matches[n] == puzzle["answer"][n])
            pct = 100 * correct_count / len(puzzle["left"])
            # Set before awarding so a double-submit cannot award twice.
            st.session_state.match_submitted = True
            if pct == 100:
                st.success(f"🎉 Perfect! {correct_count}/{len(puzzle['left'])} correct.")
                state_utils.add_xp(us, 15, "perfect matching game")
            else:
                st.warning(f"You got {correct_count}/{len(puzzle['left'])} correct.")
                state_utils.add_xp(us, 5, "matching game attempt")
            state_utils.save_state(us)
            with st.expander("See correct answers", expanded=True):
                for n in puzzle["left"]:
                    mark = "✅" if user_matches[n] == puzzle["answer"][n] else "❌"
                    st.markdown(f"{mark} **{n}** → {puzzle['answer'][n]}")

    if already_scored:
        st.info("Round scored. Click **🎲 New Matching Round** for another one.")

# ============================================================ GAME 2 =======
with game[1]:
    st.subheader("🧩 Reorder the Frame Fields")
    st.write("Some protocols have a strict, standardized bit-level frame layout. "
             "Can you put the fields back in the correct order?")

    def _new_frame_round(seed):
        st.session_state.frame_puzzle = generate_frame_order_puzzle(protocols, seed=seed)
        st.session_state.frame_submitted = False
        for key in [k for k in st.session_state if k.startswith("frame_pos_")]:
            del st.session_state[key]

    if st.button("🎲 New Frame Puzzle", key="new_frame"):
        _new_frame_round(random.randint(0, 99999))
        st.rerun()

    if "frame_puzzle" not in st.session_state:
        _new_frame_round(2)

    fp = st.session_state.frame_puzzle
    st.info(f"Protocol: **{fp['protocol']}** — arrange these {len(fp['correct_order'])} "
            f"fields in the correct transmission order (first to last).")

    frame_scored = st.session_state.get("frame_submitted", False)

    # Each position offers only the fields not already used above it, so the
    # same field cannot be placed twice (previously every dropdown offered the
    # full list, making an all-identical answer possible).
    user_order = []
    remaining = list(fp["scrambled"])
    for i in range(len(fp["correct_order"])):
        options = [CHOOSE] + remaining
        key = f"frame_pos_{i}"
        # If an earlier pick changed, a stored value may no longer be offered.
        if st.session_state.get(key) not in options:
            st.session_state.pop(key, None)
        choice = st.selectbox(f"Position {i + 1}", options, key=key, disabled=frame_scored)
        user_order.append(choice)
        if choice != CHOOSE and choice in remaining:
            remaining.remove(choice)

    if st.button("✅ Check Order", disabled=frame_scored):
        if CHOOSE in user_order:
            st.warning("Fill in every position before checking.")
        else:
            st.session_state.frame_submitted = True
            if user_order == fp["correct_order"]:
                st.success(f"🎉 Correct order! {' → '.join(user_order)}")
                state_utils.add_xp(us, 15, "correct frame order")
            else:
                st.error(f"Not quite. Correct order is: {' → '.join(fp['correct_order'])}")
                state_utils.add_xp(us, 3, "frame puzzle attempt")
            state_utils.save_state(us)
            if fp.get("frame_note"):
                st.caption(f"ℹ️ {fp['frame_note']}")

    if frame_scored:
        st.info("Puzzle scored. Click **🎲 New Frame Puzzle** for another one.")

# ============================================================ GAME 3 =======
with game[2]:
    st.subheader("🕵️ Guess the Protocol")
    st.write("Read the clues one at a time. Fewer clues used = more points!")

    def _new_mystery():
        st.session_state.guess_target = random.choice(protocols)
        st.session_state.guess_revealed = 1
        st.session_state.guess_attempts = 0
        st.session_state.guess_done = False
        st.session_state.pop("guess_input", None)

    if "guess_target" not in st.session_state:
        _new_mystery()

    # Rendered unconditionally: this button used to sit on the right of an
    # `or`, so Python's short-circuit meant it was never drawn on first visit.
    if st.button("🎲 New Mystery Protocol"):
        _new_mystery()
        st.rerun()

    target = st.session_state.guess_target
    done = st.session_state.get("guess_done", False)
    attempts = st.session_state.get("guess_attempts", 0)

    clues = [
        f"Category: **{target['category']}**",
        f"Invented in **{target['year']}**",
        f"Typical speed: **{target.get('speed', '—')}**",
        f"Topology: **{target.get('topology', '—')}**",
        f"Description: {target['description']}",
    ]

    for i in range(st.session_state.guess_revealed):
        st.markdown(f"🔎 Clue {i + 1}: {clues[i]}")

    if st.session_state.guess_revealed < len(clues) and not done:
        if st.button("➕ Reveal next clue"):
            st.session_state.guess_revealed += 1
            st.rerun()

    guess = st.text_input("Your guess (protocol name):", key="guess_input", disabled=done)

    if st.button("✅ Submit Guess", disabled=done):
        normalised = _normalise(guess)
        if not normalised:
            # An empty guess used to score as CORRECT, because "" is a
            # substring of every name.
            st.warning("Type a protocol name before submitting.")
        elif normalised in _accepted_answers(target):
            # Every wrong attempt costs as much as revealing a clue, so
            # brute-forcing is no cheaper than reading the clues.
            points = max(1, 25 - 5 * (st.session_state.guess_revealed - 1) - 5 * attempts)
            st.success(
                f"🎉 Correct! It was **{target['name']}**. You earned {points} XP "
                f"for using {st.session_state.guess_revealed} clue(s)"
                + (f" and {attempts + 1} guesses." if attempts else ".")
            )
            state_utils.add_xp(us, points, "guess the protocol")
            state_utils.save_state(us)
            st.session_state.guess_done = True
        else:
            st.session_state.guess_attempts = attempts + 1
            st.error(f"Not quite — that's guess {attempts + 1}. "
                     "Each wrong guess costs 5 XP off the reward, same as revealing a clue.")

    if done:
        st.info("Solved. Click **🎲 New Mystery Protocol** to play again.")

st.divider()
st.caption(f"Current XP: **{us['xp']}** | Level **{us['level']}**")

branding.page_footer()
