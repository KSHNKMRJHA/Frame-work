# Architecture: Data Model

Detailed data model for FrameWork's protocol database and runtime state.

## Protocol Record (`protocols.json`)

See [Protocol Database Schema](../protocol-database/schema.md) for complete field specification.

### Core Identity

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique slug (lowercase, hyphens) |
| `name` | string | Display name |
| `category` | string | One of 12 canonical categories |

### Historical

| Field | Type | Description |
|-------|------|-------------|
| `year` | integer | Invention/standardization year |
| `inventor` | string | Person or team |
| `country` | string | Origin country |
| `organization` | string | Company/standards body |

### Technical Specifications

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Technical overview (≥50 chars) |
| `speed` | string | Human-readable speed range |
| `topology` | string | Network topology |
| `difficulty` | string | Beginner/Intermediate/Advanced/Expert |

### Physical Layer

| Field | Type | Description |
|-------|------|-------------|
| `pins` | object | Pin name → description |
| `frame` | object | Frame structure with fields[] |
| `electrical` | object | Normalized electrical profile (8 fields) |

### Metadata

| Field | Type | Description |
|-------|------|-------------|
| `use_cases` | string[] | Typical applications |
| `advantages` | string[] | Strengths |
| `limitations` | string[] | Weaknesses |
| `related_protocols` | string[] | Related protocol IDs |
| `fun_fact` | string | Optional tidbit |
| `standards` | string[] | Standard numbers |
| `tags` | string[] | Searchable keywords |

---

## Frame Structure (`frame.fields[]`)

Each field:

```json
{
  "name": "Start Bit",
  "bits": 1,
  "description": "Logic low, synchronizes receiver"
}
```

- `bits`: integer or string range ("5-9")
- Ordered by transmission sequence

---

## Electrical Profile (`electrical`)

8 required fields:

| Field | Example |
|-------|---------|
| `signaling` | "Differential" |
| `logic_high` | "+2.5V differential" |
| `logic_low` | "-2.5V differential" |
| `voltage_ref` | "Common Mode" |
| `clocking` | "Synchronous" |
| `termination` | "120Ω at each end" |
| `biasing` | "Weak pull-up/down" |
| `implementation_notes` | "PCB: matched impedance..." |

---

## User State (`user_state.json`)

```json
{
  "username": "Engineer",
  "xp": 1250,
  "level": 4,
  "badges": ["first_steps", "explorer", "quiz_master"],
  "protocols_viewed": ["uart", "spi", "i2c", "can"],
  "quiz_history": [
    {"timestamp": "2024-01-15T10:30:00Z", "score": 8, "total": 10, "category": "On-Board", "difficulty": "Beginner", "seed": 42, "xp_earned": 80}
  ],
  "puzzle_history": [
    {"timestamp": "2024-01-15T10:35:00Z", "type": "frame_order", "protocol_id": "uart", "solved": true, "attempts": 1, "time_seconds": 30.5, "xp_earned": 25}
  ],
  "accent_color": "#4f46e5",
  "theme": "dark"
}
```

---

## Technical Profiles (`technical_profiles.py`)

Supplementary implementation data keyed by protocol ID:

```python
TECHNICAL_PROFILES = {
    "uart": {
        "baud_rates": [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600],
        "data_bits_options": [5, 6, 7, 8, 9],
        "parity_options": ["none", "even", "odd", "mark", "space"],
        "stop_bits_options": [1, 1.5, 2],
        "oversampling": 16,
        "max_cable_length_m": 15,
        "esd_protection_kv": 15,
        "common_ics": ["16550", "16C550", "FT232RL", "CP2102", "CH340"]
    },
    "can": {
        "bitrates": [10000, 20000, 50000, 100000, 125000, 250000, 500000, 1000000],
        "max_nodes": 127,
        "max_cable_length_m": 40,  # at 1 Mbps
        "common_controllers": ["MCP2515", "SJA1000", "STM32 bxCAN", "NXP FlexCAN"],
        "common_transceivers": ["TJA1050", "MCP2551", "SN65HVD230"]
    }
    # ... 116 more
}
```

Used by Science Lab calculators for realistic defaults.

---

## Relationships

```
protocols.json (source of truth)
    │
    ├──► data_loader.load_protocols() → List[dict]
    │       │
    │       ├──► Encyclopedia: full display
    │       ├──► Quiz Engine: question generation
    │       ├──► Mind Map: graph nodes/edges
    │       ├──► Diagrams: frame/topology/pinout
    │       ├──► Compare: side-by-side fields
    │       ├──► Timeline: year/inventor/country
    │       ├──► Geography: country/organization
    │       └──► Science Lab: electrical params
    │
    ├──► build_scripts/sync_mobile.py → kivy_mobile/data/protocols.json
    │
    └──► technical_profiles.py (supplementary, keyed by id)
```

---

## Validation Rules

Enforced by `build_scripts/check_data.py`:

1. All `id` unique
2. All `category` ∈ canonical 12
3. All `difficulty` ∈ {Beginner, Intermediate, Advanced, Expert}
4. All `related_protocols` IDs exist
5. `frame.fields` ≥ 1, unique names, ordered
6. `electrical` has all 8 sub-fields
7. `use_cases`, `advantages`, `limitations`, `related_protocols` ≥ 1 item
8. `year` ∈ [1900, 2030]
9. `description` length ≥ 50
10. JSON Schema compliance

---

## Extending the Model

To add fields:

1. Update `build_data.py` `add()` signature and calls
2. Update JSON Schema in `docs/protocol-database/schema.md`
3. Update `check_data.py` validation
4. Update consumers (pages, diagrams, quiz, mobile sync)
5. Run `python build_data.py` and all tests

---

## See Also

- [Protocol Database Schema](../protocol-database/schema.md)
- [Adding Protocols](../protocol-database/adding-protocols.md)
- [Validation](../protocol-database/validation.md)
- [API: Data Loader](../api/data_loader.md)