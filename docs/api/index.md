# API Reference

Auto-generated API documentation for FrameWork modules.

## Module Index

| Module | Description |
|--------|-------------|
| [`data_loader`](data_loader.md) | Protocol database loading, search, filtering |
| [`diagrams`](diagrams.md) | Frame, topology, pinout, chart generators |
| [`mindmap`](mindmap.md) | NetworkX mind map construction |
| [`quiz_engine`](quiz_engine.md) | Procedural quiz and puzzle generation |
| [`science`](science.md) | Verified engineering calculators |
| [`state`](state.md) | XP, badges, progress persistence |
| [`branding`](branding.md) | App identity, versioning, build info |

---

## Quick Reference

### Data Loader (`utils.data_loader`)

```python
from utils.data_loader import load_protocols, search_protocols, get_categories

protocols = load_protocols()                    # List[dict] — all 118 protocols
results = search_protocols(protocols, "CAN")    # Filter by name/keyword/inventor/year
categories = get_categories(protocols)          # List[str] — 12 categories
protocol = get_by_id(protocols, "can")          # Single protocol by ID
```

### Diagrams (`utils.diagrams`)

```python
from utils.diagrams import (
    generate_frame_diagram,
    generate_topology_diagram,
    generate_pinout_diagram,
    category_bar_chart,
)

fig = generate_frame_diagram(protocol)          # matplotlib.Figure
fig = generate_topology_diagram(protocol)       # matplotlib.Figure
fig = generate_pinout_diagram(protocol)         # matplotlib.Figure
fig = category_bar_chart(protocols)             # matplotlib.Figure
```

### Quiz Engine (`utils.quiz_engine`)

```python
from utils.quiz_engine import generate_quiz, generate_frame_order_puzzle, generate_speed_matching_puzzle

quiz = generate_quiz(protocols, n=10, seed=42, category="Automotive", difficulty="Intermediate")
# Returns List[dict] with: question, options[4], answer, explain, category, difficulty

puzzle = generate_frame_order_puzzle(protocols, seed=123)
# Returns: protocol, scrambled[fields], correct_order[fields]

puzzle = generate_speed_matching_puzzle(protocols, seed=456)
# Returns: pairs to match
```

### Science (`utils.science`)

```python
from utils.science import (
    crc16_ccitt_false, crc16_modbus, crc32_ieee,
    uart_bit_timing, can_bit_timing,
    shannon_capacity, nyquist_max_rate,
    freq_to_wavelength, wavelength_to_freq,
    quarter_wave_antenna_length,
    parse_user_bytes,
)

# CRC (verified against reveng catalogue)
crc16_ccitt_false(b"123456789")  # 0x29B1
crc16_modbus(b"123456789")       # 0x4B37
crc32_ieee(b"123456789")         # 0xCBF43926

# UART
uart_bit_timing(f_clk=16_000_000, baud=9600, oversampling=16)
# Returns: divisor, actual_baud, error_pct, acceptable

# CAN
can_bit_timing(f_clk=16e6, bitrate=500_000, tq_prop=3, tq_ps1=3, tq_ps2=2)
# Returns: prescaler, total_tq, sample_point_pct, time_quantum_ns

# Information Theory
shannon_capacity(bandwidth_hz=20e6, snr_db=30)    # bits/sec
nyquist_max_rate(bandwidth_hz=3000, signal_levels=2)  # 6000 symbols/sec

# RF
freq_to_wavelength(2.4e9)          # 0.1249 m
wavelength_to_freq(0.1249)         # 2.4 GHz
quarter_wave_antenna_length(2.4e9) # 0.0312 m
```

### State (`utils.state`)

```python
from utils.state import load_state, save_state, get_state_path

state = load_state()          # Dict with xp, level, badges, protocols_viewed, ...
state["xp"] += 100
save_state(state)             # Atomic write
```

### Branding (`utils.branding`)

```python
from utils.branding import APP_NAME, APP_TAGLINE, APP_ICON, VERSION, version_label, build_line

APP_NAME          # "FrameWork"
APP_TAGLINE       # "Every embedded communication protocol..."
APP_ICON          # "🛰️"
VERSION           # "1.0.0"
version_label()   # "v1.0.0 · stable · commit a1b2c3d"
build_line()      # "stable build a1b2c3d"
```

---

## Navigation

- [Data Loader](data_loader.md)
- [Diagrams](diagrams.md)
- [Mind Map](mindmap.md)
- [Quiz Engine](quiz_engine.md)
- [Science](science.md)
- [State](state.md)
- [Branding](branding.md)