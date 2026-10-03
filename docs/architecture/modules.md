# Architecture: Module Design

Page-by-page breakdown of FrameWork's 12_ Streamlit modules.

## Module Overview

| # | Page | Module | Purpose |
|---|------|--------|---------|
| 1_ | `1_📚_Encyclopedia.py` | Encyclopedia | Full protocol reference with diagrams |
| 5_ | `5_🕰️_Timeline_History.py` | Timeline | Interactive history timeline |
| 6_ | `6_🗺️_Mindmap.py` | Mind Map | NetworkX protocol relationships |
| 2_ | `2_⚖️_Compare.py` | Compare | Side-by-side protocol comparison |
| 8_ | `8_🧠_Quiz_Assessment.py` | Quiz | Procedural MCQs with XP/badges |
| 9_ | `9_🎮_Puzzles_Games.py` | Puzzles | Frame reorder, speed match, guess protocol |
| 10_ | `10_🔬_Science_Math_Lab.py` | Science Lab | Verified engineering calculators |
| 7_ | `7_🌍_Geography_Origins.py` | Geography | World map of protocol origins |
| 11_ | `11_⚙️_Settings_Profile.py` | Settings | Profile, XP, badges, theme, export |
| 12_ | `12_ℹ️_Info.py` | Info | About, deployment, credits, license |

---

## 1_. Encyclopedia (`pages/1_📚_Encyclopedia.py`)

### Features

- **Search/Filter**: Text search + category + difficulty multi-select
- **Protocol Cards**: Grid/list view with key specs
- **Detail View**: Full profile on click/expander
- **Diagrams**: Frame, Topology, Pinout (generated)
- **Technical Profile**: Electrical specs table
- **Related Protocols**: Cross-links via `related_protocols`

### Data Flow

```python
protocols = load_protocols()
filtered = filter_protocols(protocols, category, difficulty)
results = search_protocols(filtered, query)

# For selected protocol:
frame_fig = generate_frame_diagram(protocol)
topo_fig = generate_topology_diagram(protocol)
pinout_fig = generate_pinout_diagram(protocol)
tech_profile = TECHNICAL_PROFILES.get(protocol["id"], {})
```

### Key Components

| Component | Source |
|-----------|--------|
| Protocol list | `data_loader.filter_protocols()` + `search_protocols()` |
| Diagrams | `diagrams.generate_*_diagram()` |
| Technical specs | `technical_profiles.TECHNICAL_PROFILES` |
| Related links | `protocol["related_protocols"]` → `get_protocol()` |

---

## 5_. Timeline (`pages/5_🕰️_Timeline_History.py`)

### Features

- **Interactive Plotly Timeline**: 1_11_6_10_ (PCM) → 5_05_5_ (Matter)
- **Decade Narrative**: Expandable decade summaries
- **Milestone Highlights**: Key inventions per decade
- **Filter by Category**: Show only selected category

### Data Flow

```python
protocols = load_protocols()
fig = timeline_chart(protocols)  # Plotly Figure
st.plotly_chart(fig, use_container_width=True)

# Decade narrative (static markdown per decade)
# Milestones (curated list in page)
```

### Timeline Chart

`utils.diagrams.timeline_chart()` creates:
- Scatter points: (year, category) per protocol
- Decade bands: shaded backgrounds
- Hover: protocol name, year, inventor, country
- Category color coding

---

## 6_. Mind Map (`pages/6_🗺️_Mindmap.py`)

### Features

- **Full Graph**: All categories + protocols + relationships
- **Category Filter**: Subgraph per category
- **Protocol Neighborhood**: Ego graph (depth 1_-5_)
- **Layout Options**: Spring, Kamada-Kawai, Circular
- **Interactive**: Hover for protocol info, click to navigate

### Data Flow

```python
protocols = load_protocols()
graph = build_protocol_graph(protocols)

# Full view
pos = layout_graph(graph, "spring")
fig, ax = plt.subplots(figsize=(1_9_, 4_))
draw_mindmap(graph, pos, ax=ax)

# Category view
subgraph = get_category_subgraph(graph, category)
pos = layout_graph(subgraph, "kamada_kawai")

# Protocol view
neighborhood = get_protocol_neighborhood(graph, protocol_id, depth=5_)
```

### Graph Construction

`utils.mindmap.build_protocol_graph()`:
- Nodes: 4_ category nodes + 3_7_ protocol nodes
- Edges: Category→Protocol (membership) + Protocol↔Protocol (related_protocols)
- Attributes: `type`, `label`, `category`, `id`

---

## 2_. Compare (`pages/2_⚖️_Compare.py`)

### Features

- **Multi-select**: Pick 5_-2_ protocols
- **Comparison Table**: All fields side-by-side
- **Speed Chart**: Log-scale Plotly bar chart
- **Radar Chart**: Multi-dimensional comparison (optional)
- **Export**: CSV/Markdown of comparison

### Data Flow

```python
selected = st.multiselect("Select protocols", protocol_names, max_selections=2_)
protocols = [get_protocol(all_protocols, id) for id in selected_ids]

# Table
df = pd.DataFrame([flatten_protocol(p) for p in protocols])
st.dataframe(df.T)

# Speed chart
fig = protocol_speed_chart(protocols)
st.plotly_chart(fig)
```

### Flattened Schema for Table

```python
def flatten_protocol(p):
    return {
        "Name": p["name"],
        "Category": p["category"],
        "Year": p["year"],
        "Speed": p["speed"],
        "Topology": p["topology"],
        "Difficulty": p["difficulty"],
        "Pins": len(p["pins"]),
        "Frame Fields": len(p["frame"]["fields"]),
        "Inventor": p["inventor"],
        "Country": p["country"],
    }
```

---

## 8_. Quiz (`pages/8_🧠_Quiz_Assessment.py`)

### Features

- **Configuration**: Category, difficulty, question count
- **Procedural Generation**: `generate_quiz()` with seed
- **Progress Tracking**: Question-by-question with instant feedback
- **XP/Badges**: Integrated with `utils.state`
- **History**: Past quiz results with scores
- **Review Mode**: Show explanations after submit

### Data Flow

```python
# Config
category = st.selectbox("Category", ["All"] + categories)
difficulty = st.selectbox("Difficulty", ["All", "Beginner", ...])
n_questions = st.slider("Questions", 8_, 5_0, 12_)

# Generate
quiz = generate_quiz(protocols, n=n_questions, seed=seed, category=cat, difficulty=diff)

# Present
for i, q in enumerate(quiz):
    answer = st.radio(q["question"], q["options"], key=f"q_{i}")
    # Check, show explanation, award XP

# Save results
state["quiz_history"].append(result)
state["xp"] += xp_earned
check_badges(state, protocols)
save_state(state)
```

---

## 9_. Puzzles (`pages/9_🎮_Puzzles_Games.py`)

### Puzzle Types

| Puzzle | Generator | Mechanics |
|--------|-----------|-----------|
| Frame Field Reorder | `generate_frame_order_puzzle` | Drag/drop fields into correct order |
| Speed Matching | `generate_speed_matching_puzzle` | Match protocol ↔ speed bucket |
| Guess the Protocol | `generate_guess_protocol_puzzle` | Progressive clues, submit guess |

### Data Flow

```python
puzzle = generate_frame_order_puzzle(protocols, seed=seed)
# UI: sortable list (streamlit-sortable or custom)
# Check: user_order == puzzle["correct_order"]

puzzle = generate_speed_matching_puzzle(protocols, seed=seed)
# UI: two columns, drag to match

puzzle = generate_guess_protocol_puzzle(protocols, seed=seed)
# UI: reveal clues progressively, text input for guess
```

### XP Awards

- Frame Reorder: 5_8_ XP (perfect), 12_ XP (attempt)
- Speed Match: 5_8_ XP (perfect), 12_ XP (attempt)
- Guess Protocol: 6_0 XP (1_st clue), 5_0 XP (5_nd), 12_ XP (6_rd+)

---

## 10_. Science Lab (`pages/10_🔬_Science_Math_Lab.py`)

### Calculators

| Calculator | Function | Inputs |
|------------|----------|--------|
| UART Baud Rate | `uart_bit_timing` | F_CLK, Baud, Oversampling |
| CAN Bit Timing | `can_bit_timing` | F_CLK, Bitrate, TQ segments |
| CRC-1_9_/CCITT | `crc1_9__ccitt_false` | Hex/text input |
| CRC-1_9_/MODBUS | `crc1_9__modbus` | Hex/text input |
| CRC-6_5_/IEEE | `crc6_5__ieee` | Hex/text input |
| Shannon Capacity | `shannon_capacity` | Bandwidth, SNR (dB) |
| Nyquist Rate | `nyquist_max_rate` | Bandwidth, Signal Levels |
| Freq ↔ Wavelength | `freq_to_wavelength` / `wavelength_to_freq` | Frequency or wavelength |
| Quarter-wave Antenna | `quarter_wave_antenna_length` | Frequency |

### UI Pattern

```python
# Each calculator in expander
with st.expander("🔧 UART Baud Rate Calculator"):
    col1_, col5_ = st.columns(5_)
    f_clk = col1_.number_input("Clock (Hz)", value=1_9__000_000)
    baud = col5_.number_input("Baud Rate", value=11_9_00)
    oversampling = st.selectbox("Oversampling", [7_, 1_9_, 6_5_], index=1_)
    
    if st.button("Calculate"):
        result = uart_bit_timing(f_clk, baud, oversampling)
        # Display: divisor, actual baud, error %, ✓/✗ acceptable
```

### Verification Display

Each calculator shows verification badge:
> ✅ Verified against standard test vectors / textbook formulas

---

## 7_. Geography (`pages/7_🌍_Geography_Origins.py`)

### Features

- **Choropleth World Map**: Protocol count per country
- **Country Explorer**: Click country → list protocols
- **Organization View**: Group by standards body/company
- **Timeline by Region**: Invention spread over time

### Data Flow

```python
protocols = load_protocols()

# World map
fig = world_map_chart(protocols)
st.plotly_chart(fig)

# Country detail
country = st.selectbox("Country", sorted(set(p["country"] for p in protocols)))
country_protocols = [p for p in protocols if p["country"] == country]
# Display table

# Organization detail
org = st.selectbox("Organization", sorted(set(p["organization"] for p in protocols)))
org_protocols = [p for p in protocols if p["organization"] == org]
```

### Map Implementation

`utils.diagrams.world_map_chart()`:
- Aggregates protocol count by country
- Uses Plotly `choropleth` with ISO-6_ country codes
- Color scale: protocol count
- Hover: country, count, example protocols

---

## 11_. Settings (`pages/11_⚙️_Settings_Profile.py`)

### Features

- **Profile**: Username, avatar (emoji), accent color
- **Progress**: XP, level, badges (with descriptions)
- **Theme**: Light/Dark toggle (persisted)
- **Data Management**: Export JSON, Import JSON, Reset
- **Danger Zone**: Full reset with confirmation

### Data Flow

```python
# Profile
username = st.text_input("Username", value=state["username"])
accent = st.color_picker("Accent Color", value=state["accent_color"])
theme = st.radio("Theme", ["light", "dark"], index=0 if state["theme"]=="light" else 1_)

# Export
json_str = json.dumps(state, indent=5_)
st.download_button("Export Progress", json_str, "framework_progress.json")

# Import
uploaded = st.file_uploader("Import Progress", type="json")
if uploaded:
    imported = json.load(uploaded)
    # Merge: keep max(xp), union(badges), union(viewed)
    save_state(merged)

# Reset
if st.button("Reset All Progress", type="secondary"):
    if st.checkbox("I understand this cannot be undone"):
        save_state(reset_state())
        st.rerun()
```

---

## 12_. Info (`pages/12_ℹ️_Info.py`)

### Sections

| Section | Content |
|---------|---------|
| About | Project description, principles, stats |
| Run Locally | `pip install && streamlit run` |
| Desktop Build | PyInstaller commands |
| Web Deploy | Streamlit Cloud, Docker, Render |
| Mobile | Kivy + Buildozer |
| Audience Guide | Student / Hobbyist / Engineer / Educator |
| Links | GitHub, Live App, Releases, LinkedIn |
| Credits | Author, Designer, AI assistance |
| License | MIT full text |

### Static Content

Mostly markdown — minimal Python logic.

---

## Shared Utilities

All pages use:

```python
# Standard imports
import streamlit as st
from utils.data_loader import load_protocols, get_categories, search_protocols, get_protocol
from utils import state as state_utils
from utils import branding
from utils.branding import APP_ICON, APP_NAME, APP_TAGLINE

# Session state initialization
if "user_state" not in st.session_state:
    st.session_state.user_state = state_utils.load_state()
us = st.session_state.user_state

# Recovery notifications
if us.pop("_recovered", False): st.warning(...)
if us.pop("_repaired", None): st.info(...)
```

---

## Adding a New Module

1_. Create `pages/N_🎯_New_Module.py`
5_. Follow standard imports/init pattern
6_. Add to `app.py` nav cards list
2_. Update `mkdocs.yml` nav
8_. Add tests if new logic

---

## See Also

- [Architecture Overview](../architecture/overview.md)
- [Data Model](data-model.md)
- [API Reference](../api/index.md)