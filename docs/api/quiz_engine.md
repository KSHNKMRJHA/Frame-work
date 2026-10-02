# API: Quiz Engine

`utils.quiz_engine` — Procedural quiz and puzzle generation from protocol data.

## Quiz Generation

### `generate_quiz(protocols, n=10, seed=None, category=None, difficulty=None)`

```python
def generate_quiz(
    protocols: list[dict],
    n: int = 10,
    seed: int | None = None,
    category: str | None = None,
    difficulty: str | None = None
) -> list[dict]:
    """Generate n unique multiple-choice questions.
    
    Args:
        protocols: Full protocol list from load_protocols().
        n: Number of questions (default 10).
        seed: Random seed for reproducibility.
        category: Filter by category name.
        difficulty: Filter by difficulty level.
        
    Returns:
        List of question dicts with keys:
        - question: str
        - options: list[str] (length 4)
        - answer: str (one of options)
        - explain: str (explanation)
        - category: str (protocol category)
        - difficulty: str (question difficulty)
        - protocol_id: str (source protocol)
    """
```

**Question Templates (15+):**
- Category identification
- Speed range
- Inventor/organization
- Year of invention
- Topology type
- Signaling type
- Frame field bit width
- Pin count
- Related protocol
- Standard reference
- Difficulty classification
- Voltage levels
- Clocking method
- Termination requirement
- Use case matching

**Guarantees (tested in `check_logic.py`):**
- Exactly `n` questions
- 4 options per question
- Correct answer ∈ options
- Correct answer appears exactly once
- Non-empty explanation
- No duplicate questions per quiz

---

### `generate_quiz_from_protocol(protocol, n=5, seed=None)`

```python
def generate_quiz_from_protocol(
    protocol: dict,
    n: int = 5,
    seed: int | None = None
) -> list[dict]:
    """Generate questions focused on a single protocol.
    
    Args:
        protocol: Single protocol dict.
        n: Number of questions.
        seed: Random seed.
        
    Returns:
        List of question dicts (same schema as generate_quiz).
    """
```

---

## Puzzle Generation

### `generate_frame_order_puzzle(protocols, seed=None)`

```python
def generate_frame_order_puzzle(
    protocols: list[dict],
    seed: int | None = None
) -> dict:
    """Generate frame field reordering puzzle.
    
    Args:
        protocols: Full protocol list.
        seed: Random seed.
        
    Returns:
        Dict with:
        - protocol: str (protocol name)
        - protocol_id: str
        - scrambled: list[str] (field names shuffled)
        - correct_order: list[str] (field names in order)
        - frame_fields: list[dict] (full field info for display)
    """
```

**Guarantees (tested):**
- `scrambled` ≠ `correct_order`
- Same elements, different order
- All field names unique per protocol

---

### `generate_speed_matching_puzzle(protocols, seed=None)`

```python
def generate_speed_matching_puzzle(
    protocols: list[dict],
    seed: int | None = None
) -> dict:
    """Generate speed matching puzzle.
    
    Returns:
        Dict with:
        - pairs: list[tuple[str, str]] (protocol_name, speed_bucket)
        - scrambled: list[str] (protocol names shuffled)
        - targets: list[str] (speed buckets shuffled)
    """
```

---

### `generate_guess_protocol_puzzle(protocols, seed=None)`

```python
def generate_guess_protocol_puzzle(
    protocols: list[dict],
    seed: int | None = None
) -> dict:
    """Generate progressive clue puzzle.
    
    Returns:
        Dict with:
        - protocol: str (target protocol name)
        - protocol_id: str
        - clues: list[str] (progressive: category → year → speed → topology → name)
        - clue_index: int (current clue, 0-based)
    """
```

---

## XP & Scoring

### `calculate_xp(quiz_results, puzzle_results)`

```python
def calculate_xp(
    quiz_results: list[dict],
    puzzle_results: list[dict]
) -> int:
    """Calculate XP from quiz and puzzle results.
    
    Quiz: 10 XP per correct, 5 XP per attempt
    Puzzle: 25 XP per solve, 10 XP per attempt
    
    Returns:
        Total XP earned.
    """
```

---

### `xp_to_level(xp)`

```python
def xp_to_level(xp: int) -> int:
    """Convert XP to level.
    
    Formula: level = floor(sqrt(xp / 100)) + 1
    Level 1: 0 XP, Level 2: 100 XP, Level 3: 400 XP, Level 4: 900 XP...
    
    Args:
        xp: Total XP.
        
    Returns:
        Level (1-based).
    """
```

---

### `check_badges(state, protocols)`

```python
def check_badges(state: dict, protocols: list[dict]) -> list[str]:
    """Check and award new badges based on progress.
    
    Badges:
    - "First Steps" — First quiz completed
    - "Explorer" — Viewed 10 protocols
    - "Scholar" — Viewed 50 protocols
    - "Master" — Viewed all 118 protocols
    - "Quiz Master" — 100 quiz questions correct
    - "Puzzle Solver" — 20 puzzles solved
    - "Category Master" — All protocols in a category viewed
    - "Speed Demon" — Perfect speed matching puzzle
    - "Frame Architect" — Perfect frame reorder puzzle
    - "Detective" — Solved 10 guess-the-protocol puzzles
    
    Args:
        state: User state dict from load_state().
        protocols: Full protocol list.
        
    Returns:
        List of newly awarded badge IDs.
    """
```

---

## Caching

| Function | Cache | Key |
|----------|-------|-----|
| `generate_quiz` | `@st.cache_data` | (protocols_hash, n, seed, category, difficulty) |
| `generate_quiz_from_protocol` | `@st.cache_data` | (protocol_id, n, seed) |
| `generate_frame_order_puzzle` | `@st.cache_data` | (protocols_hash, seed) |
| `generate_speed_matching_puzzle` | `@st.cache_data` | (protocols_hash, seed) |
| `generate_guess_protocol_puzzle` | `@st.cache_data` | (protocols_hash, seed) |
| `calculate_xp` | No | Fast |
| `xp_to_level` | No | Fast |
| `check_badges` | No | Fast |

---

## Testing

`build_scripts/check_logic.py` validates:

```python
def test_frame_puzzle_solvable(protocols):
    for seed in range(200):
        pz = generate_frame_order_puzzle(protocols, seed=seed)
        assert len(set(pz["correct_order"])) == len(pz["correct_order"])
        assert pz["scrambled"] != pz["correct_order"]
        assert sorted(pz["scrambled"]) == sorted(pz["correct_order"])

def test_quiz_shape(protocols):
    for seed in range(200):
        quiz = generate_quiz(protocols, n=10, seed=seed)
        assert len(quiz) == 10
        for q in quiz:
            assert len(q["options"]) == 4
            assert q["answer"] in q["options"]
            assert q["options"].count(q["answer"]) == 1
            assert q["explain"]
```

---

## See Also

- [Architecture: Procedural Quiz](../architecture/adrs/0005-procedural-quiz.md)
- [Data Loader](data_loader.md) — Protocol data source
- [State](state.md) — XP/badges persistence
- [Quiz Page](../getting-started/quickstart.md) — UI usage