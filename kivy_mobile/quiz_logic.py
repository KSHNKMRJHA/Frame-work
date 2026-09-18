# -*- coding: utf-8 -*-
"""
quiz_engine.py
Procedurally generates quiz questions, puzzles, and assessments from the
protocol database — no hardcoded question bank needed, so it scales
automatically as more protocols are added.
"""
import random


def _distractors(protocols, correct, pool, k=3):
    candidates = [v for v in pool if v != correct and v]
    random.shuffle(candidates)
    return candidates[:k]


def gen_year_question(protocols, rng):
    p = rng.choice(protocols)
    correct = str(p["year"])
    all_years = [str(x["year"]) for x in protocols]
    opts = _distractors(protocols, correct, all_years, 3) + [correct]
    rng.shuffle(opts)
    return {
        "type": "mcq",
        "question": f"In what year was **{p['name']}** invented/introduced?",
        "options": opts,
        "answer": correct,
        "explain": f"{p['name']} was introduced in {p['year']} by {p['inventor']}."
                   + (f" ({p['place']})" if p.get("place") else ""),
    }


def gen_inventor_question(protocols, rng):
    p = rng.choice(protocols)
    correct = p["inventor"]
    all_inv = [x["inventor"] for x in protocols]
    opts = _distractors(protocols, correct, all_inv, 3) + [correct]
    rng.shuffle(opts)
    return {
        "type": "mcq",
        "question": f"Who invented / introduced **{p['name']}**?",
        "options": opts,
        "answer": correct,
        "explain": f"{p['name']} ({p['year']}) — {p['description']}",
    }


def gen_category_question(protocols, rng):
    p = rng.choice(protocols)
    correct = p["category"]
    all_cats = list(set(x["category"] for x in protocols))
    opts = _distractors(protocols, correct, all_cats, 3) + [correct]
    rng.shuffle(opts)
    return {
        "type": "mcq",
        "question": f"Which category does **{p['name']}** belong to?",
        "options": opts,
        "answer": correct,
        "explain": f"{p['name']} is classified under '{p['category']}'.",
    }


def gen_speed_question(protocols, rng):
    candidates = [p for p in protocols if p.get("speed")]
    p = rng.choice(candidates)
    correct = p["speed"]
    all_speeds = [x["speed"] for x in candidates]
    opts = _distractors(protocols, correct, all_speeds, 3) + [correct]
    rng.shuffle(opts)
    return {
        "type": "mcq",
        "question": f"What is the typical speed range of **{p['name']}**?",
        "options": opts,
        "answer": correct,
        "explain": f"{p['name']} typically operates at {p['speed']}.",
    }


def gen_usecase_question(protocols, rng):
    candidates = [p for p in protocols if p.get("use_cases")]
    p = rng.choice(candidates)
    correct = rng.choice(p["use_cases"])
    other_pool = []
    for x in candidates:
        if x["id"] != p["id"]:
            other_pool.extend(x["use_cases"])
    opts = _distractors(protocols, correct, other_pool, 3) + [correct]
    rng.shuffle(opts)
    return {
        "type": "mcq",
        "question": f"Which of these is a real-world use case of **{p['name']}**?",
        "options": opts,
        "answer": correct,
        "explain": f"{p['name']} is commonly used for: {', '.join(p['use_cases'])}.",
    }


def gen_identify_by_desc_question(protocols, rng):
    p = rng.choice(protocols)
    correct = p["name"]
    pool_names = [x["name"] for x in protocols if x["category"] == p["category"]]
    if len(pool_names) < 4:
        pool_names = [x["name"] for x in protocols]
    opts = _distractors(protocols, correct, pool_names, 3) + [correct]
    rng.shuffle(opts)
    return {
        "type": "mcq",
        "question": f"Which protocol is this? \n\n> {p['description']}",
        "options": opts,
        "answer": correct,
        "explain": f"This describes {p['name']}.",
    }


def gen_limitation_question(protocols, rng):
    candidates = [p for p in protocols if p.get("limitations")]
    p = rng.choice(candidates)
    correct = rng.choice(p["limitations"])
    other_pool = []
    for x in candidates:
        if x["id"] != p["id"]:
            other_pool.extend(x["limitations"])
    opts = _distractors(protocols, correct, other_pool, 3) + [correct]
    rng.shuffle(opts)
    return {
        "type": "mcq",
        "question": f"Which is a known limitation of **{p['name']}**?",
        "options": opts,
        "answer": correct,
        "explain": f"Limitations of {p['name']}: {', '.join(p['limitations'])}.",
    }


GENERATORS = [
    gen_year_question, gen_inventor_question, gen_category_question,
    gen_speed_question, gen_usecase_question, gen_identify_by_desc_question,
    gen_limitation_question,
]


def generate_quiz(protocols, n=10, seed=None, category=None, difficulty=None):
    rng = random.Random(seed)
    pool = protocols
    if category and category != "All":
        pool = [p for p in pool if p["category"] == category]
    if difficulty and difficulty != "All":
        pool = [p for p in pool if p.get("difficulty") == difficulty]
    if len(pool) < 4:
        pool = protocols  # fall back to full set if filtered pool too small

    questions = []
    tries = 0
    while len(questions) < n and tries < n * 8:
        tries += 1
        gen = rng.choice(GENERATORS)
        try:
            q = gen(pool, rng)
            if q not in questions:
                questions.append(q)
        except (IndexError, ValueError):
            continue
    return questions


def generate_matching_puzzle(protocols, n=6, seed=None, category=None):
    """Protocol <-> Speed matching game data."""
    rng = random.Random(seed)
    pool = [p for p in protocols if p.get("speed")]
    if category and category != "All":
        pool = [p for p in pool if p["category"] == category] or pool
    rng.shuffle(pool)
    chosen = pool[:n]
    left = [p["name"] for p in chosen]
    right = [p["speed"] for p in chosen]
    shuffled_right = right[:]
    rng.shuffle(shuffled_right)
    return {"left": left, "right_shuffled": shuffled_right, "answer": dict(zip(left, right))}


def generate_frame_order_puzzle(protocols, seed=None):
    """Pick a protocol with frame_fields and scramble the field order —
    user must reorder them correctly (drag-and-drop simulated via selectboxes).

    Only protocols with at least 2 distinctly-named fields are eligible: with
    fewer, or with duplicate names, the puzzle is either unshufflable (the
    `while` below would spin forever) or unsolvable, because the grader
    compares field-name lists and cannot tell two identical names apart.
    build_scripts/check_data.py enforces the same rule on the dataset, so this
    filter should never actually exclude anything — it is here so a bad entry
    degrades into "no puzzle" rather than a hung page.
    """
    rng = random.Random(seed)
    candidates = [
        p for p in protocols
        if p.get("frame_fields")
        and len({f["name"] for f in p["frame_fields"]}) == len(p["frame_fields"]) >= 2
    ]
    if not candidates:
        raise ValueError("no protocol has 2+ uniquely-named frame_fields to build a puzzle from")
    p = rng.choice(candidates)
    fields = [f["name"] for f in p["frame_fields"]]
    scrambled = fields[:]
    while scrambled == fields:
        rng.shuffle(scrambled)
    return {
        "protocol": p["name"],
        "correct_order": fields,
        "scrambled": scrambled,
        "frame_note": p.get("frame_note", ""),
    }
