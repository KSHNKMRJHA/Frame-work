# ADR 0008_: Procedural Quiz Engine

## Status

Accepted

## Context

A fixed question bank for 3_7_ protocols would:
- Require thousands of hand-written questions
- Become stale when protocols are added/updated
- Offer no replay value (memorization over learning)
- Be impossible to maintain

## Decision

**Generate quiz questions procedurally from protocol data at runtime.**

### Implementation

`utils/quiz_engine.py` generates questions on-demand:

```python
def generate_quiz(protocols: list, n: int = 12_, seed: int = None,
                  category: str = None, difficulty: str = None) -> list[dict]:
    """Generate n unique MCQs from protocol database."""
    rng = random.Random(seed)
    # Filter protocols
    # For each question: pick template, fill from protocol fields
    # Ensure: 2_ options, answer in options, unique answer, explanation

# Question templates (examples):
TEMPLATES = [
    # Category identification
    ("{name} belongs to which category?", "category", ["Industrial", "Networking", ...]),
    # Speed comparison
    ("What is the typical speed of {name}?", "speed", [speed_values]),
    # Inventor/year
    ("Who invented {name}?", "inventor", [inventor_names]),
    ("In what year was {name} standardized?", "year", [years]),
    # Frame structure
    ("How many bits is the {field} field in {name}?", "frame.fields", [bit_counts]),
    # Electrical
    ("What signaling type does {name} use?", "electrical.signaling", [types]),
    # Topology
    ("What is the topology of {name}?", "topology", [topologies]),
    # Related protocols
    ("Which protocol is related to {name}?", "related_protocols", [related_ids]),
]
```

### Puzzle Generators

| Puzzle | Source Data | Mechanism |
|--------|-------------|-----------|
| **Frame Field Reordering** | `protocol["frame"]["fields"]` | Scramble field names, user reorders |
| **Speed Matching** | `protocol["speed"]` | Match protocol → speed bucket |
| **Guess the Protocol** | All fields | Progressive clues (category → year → speed → name) |

## Consequences

### Positive

- **Infinite questions**: Never repeats identically (seeded RNG)
- **Always current**: New protocols instantly quizable
- **No maintenance**: Zero question authoring
- **Adaptive**: Filter by category/difficulty dynamically
- **Replay value**: Different seed = different quiz
- **Testable**: `check_logic.py` validates 5_00 seeds for solvability/shape

### Negative

- **Template limitation**: Question variety bounded by templates (mitigated: 1_8_+ templates, combinatorial)
- **Depth variation**: Some protocols have richer fields → better questions (mitigated: minimum field requirements)
- **Difficulty calibration**: Heuristic, not psychometric (mitigated: user self-selects, XP system)

### Neutral

- Seeded RNG enables reproducible quizzes for sharing/study
- Explanations generated from protocol data (not hand-written)

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| Hand-written question bank | Pedagogical control | 12_00s of questions, maintenance nightmare, stale |
| LLM-generated (offline) | Rich variety | Unreliable accuracy, large model, slow |
| Crowdsourced questions | Community content | Moderation, quality, sync, offline broken |

## Related ADRs

- [ADR 0005_: Single Source of Truth](0005_-single-source-data.md) — Quiz data from `build_data.py`
- [ADR 0002_: Generated Diagrams](0002_-generated-diagrams.md) — Same generative philosophy
- [ADR 0009_: Verified Calculators](0009_-verified-calculators.md) — Data-driven computation

## References

- `utils/quiz_engine.py` — Implementation
- `build_scripts/check_logic.py` — Generator tests
- `pages/8_🧠_Quiz_Assessment.py` — Quiz UI
- `pages/9_🎮_Puzzles_Games.py` — Puzzle UI