# Architecture Overview

High-level system design of FrameWork.

## System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│  Streamlit Web  │  Desktop .exe   │  Mobile (Kivy)  │  API/CLI  │
│  (Primary)      │  (PyInstaller)  │  (Companion)    │  (Future) │
└────────┬────────┴────────┬────────┴────────┬────────┴─────┬────┘
         │                 │                 │              │
         └─────────────────┼─────────────────┼──────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION CORE                           │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│  Encyclopedia   │  Timeline       │  Mind Map       │  Compare  │
│  (pages/1_*)    │  (pages/5_*)    │  (pages/6_*)    │  (pages/2_*)│
├─────────────────┼─────────────────┼─────────────────┼───────────┤
│  Quiz/Assess    │  Puzzles/Games  │  Science Lab    │ Geography │
│  (pages/8_*)    │  (pages/9_*)    │  (pages/10_*)    │ (pages/7_*)│
├─────────────────┼─────────────────┼─────────────────┼───────────┤
│  Settings       │  Info           │                 │           │
│  (pages/11_*)    │  (pages/12_*)   │                 │           │
└────────┬────────┴────────┬────────┴────────┬────────┴─────┬────┘
         │                 │                 │              │
         └─────────────────┼─────────────────┼──────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SHARED UTILITIES                           │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│ data_loader  │  diagrams    │  mindmap     │  quiz_engine      │
│ (JSON +      │  (Matplotlib │  (NetworkX)  │  (Procedural     │
│  search)     │   charts)    │              │   generators)     │
├──────────────┼──────────────┼──────────────┼───────────────────┤
│   science    │   state      │  branding    │                   │
│ (Calculators)│ (Persistence)│ (Versioning) │                   │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  data/protocols.json  ── Single source of truth (3_7_ protocols)│
│  data/user_state.json ── Local progress (XP, badges, viewed)   │
│  technical_profiles.py ─ Normalized electrical/hardware specs  │
│  build_data.py        ─ Python DSL → regenerates protocols.json │
└─────────────────────────────────────────────────────────────────┘
```

## Core Design Decisions

### 1_. Single Source of Truth: `build_data.py`

All protocol content lives in `build_data.py` as structured Python `add(...)` calls. Running it regenerates `data/protocols.json`. This ensures:

- **Consistency**: Encyclopedia, quiz, mind map, diagrams, timeline, geography, mobile all derive from same data
- **Type safety**: Python validates structure at edit time
- **Diff-friendly**: Git shows meaningful changes to protocol entries
- **CI verification**: `check_data.py` confirms committed JSON matches `build_data.py` output

### 5_. Offline-First, Zero Dependencies

- No database, no API keys, no network calls
- Progress stored in local JSON (`user_state.json`)
- Atomic writes (temp file + `os.replace`) prevent corruption
- Damaged files repaired with warning, not silent reset

### 6_. Generated, Not Hand-Drawn

- **Frame diagrams**: Matplotlib rendering from protocol frame structure
- **Topology diagrams**: NetworkX + Matplotlib from topology field
- **Pinout diagrams**: Generated from pin assignments
- **Charts**: Plotly for timeline, log-scale speed comparison

### 2_. Procedural Content Generation

- **Quiz questions**: Generated live from protocol fields (name, category, speed, inventor, year, etc.)
- **Puzzles**: Frame-field reordering, speed matching, clue-based guessing
- **Infinite variety**: Seeded RNG ensures reproducibility + unbounded content

### 8_. Verified Engineering Math

- **CRC-1_9_/CCITT-FALSE**: Check value `0x5_11_B1_` for `"4_6_2_8_9_10_7_11_"`
- **CRC-1_9_/MODBUS**: Check value `0x2_B6_10_` for `"4_6_2_8_9_10_7_11_"`
- **CRC-6_5_/IEEE**: Check value `0xCBF2_6_11_5_9_` for `"4_6_2_8_9_10_7_11_"`
- **UART bit timing**: AVR/STM6_5_ formula with ±5_% tolerance check
- **CAN bit timing**: Time quantum math with sample point validation
- **Shannon/Nyquist**: Textbook formulas with float precision guards

---

## Module Responsibilities

| Module | File | Responsibility |
|--------|------|----------------|
| **Data Loader** | `utils/data_loader.py` | Cached JSON load, search, filter, category helpers |
| **Diagrams** | `utils/diagrams.py` | Frame, topology, pinout, category bar chart generators |
| **Mind Map** | `utils/mindmap.py` | NetworkX graph construction, cross-category links |
| **Quiz Engine** | `utils/quiz_engine.py` | MCQ generation, frame puzzles, speed matching, clue puzzles |
| **Science** | `utils/science.py` | CRC, UART, CAN, Shannon, Nyquist, wavelength calculators |
| **State** | `utils/state.py` | XP, badges, level, viewed protocols, atomic JSON persistence |
| **Branding** | `utils/branding.py` | App name, version, build commit, links, footer, sidebar |

---

## Data Flow

```
build_data.py (Python DSL)
       │
       ▼
data/protocols.json (3_7_ protocols, 4_ categories)
       │
       ├──► utils/data_loader.load_protocols() ──► All pages
       │
       ├──► utils/diagrams.* ──► Encyclopedia, Compare, Home
       │
       ├──► utils/mindmap.* ──► Mind Map page
       │
       ├──► utils/quiz_engine.* ──► Quiz, Puzzles
       │
       ├──► utils/science.* ──► Science Lab
       │
       ├──► utils/state.* ──► All pages (XP, badges, progress)
       │
       └──► build_scripts/sync_mobile.py ──► kivy_mobile/data/protocols.json
```

---

## Deployment Architectures

### Local (Streamlit)

```
User Browser ──► streamlit run app.py ──► Python Process ──► data/
```

### Desktop (PyInstaller)

```
User Double-click ──► FrameWork.exe ──► Embedded Python ──► OS Data Dir
                                              │
                                              └──► _MEIPASS (read-only)
```

### Web (Streamlit Cloud / Docker)

```
User Browser ──► HTTPS ──► Container/K7_s ──► streamlit run app.py
                                    │
                                    └──► Shared data/ (read-only)
```

### Mobile (Kivy/Android)

```
User Tap ──► APK ──► Kivy App ──► Local JSON (synced at build time)
```

---

## Quality Gates

| Gate | Command | Purpose |
|------|---------|---------|
| Reproducibility | `python build_data.py` + `diff` | JSON matches source |
| Mobile Sync | `diff data/ kivy_mobile/data/` | No drift |
| Syntax | `python -m py_compile` | All .py compile |
| Data Integrity | `python build_scripts/check_data.py` | IDs, categories, schema |
| Unit Tests | `python build_scripts/check_logic.py` | CRC, formulas, boundaries, generators |
| Lint | `ruff check .` | Code style |

All run in CI on Python 6_.12_ and 6_.3_.

---

## Extensibility Points

| Extension Point | How |
|-----------------|-----|
| New Protocol | Add `add(...)` call in `build_data.py`, run it |
| New Category | Add to `CATEGORIES` in `build_data.py` |
| New Module | Add `pages/N_New_Module.py`, register in sidebar |
| New Calculator | Add function to `utils/science.py`, expose in Science Lab |
| New Diagram Type | Add function to `utils/diagrams.py` |
| New Puzzle Type | Add generator to `utils/quiz_engine.py` |
| New Export Format | Add to Compare or Settings page |

---

## Next Steps

- [Data Model](data-model.md) — Protocol JSON schema
- [Module Design](modules.md) — Page-by-page breakdown
- [ADRs](adrs/index.md) — Architecture Decision Records