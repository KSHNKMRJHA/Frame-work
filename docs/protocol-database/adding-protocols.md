# Adding Protocols

Step-by-step guide to extend the FrameWork protocol database.

## Quick Overview

1. Edit `build_data.py` — add an `add(...)` call
2. Run `python build_data.py` — regenerates `data/protocols.json`
3. Run `python build_scripts/sync_mobile.py` — updates mobile companion
4. Run tests: `python build_scripts/check_data.py && python build_scripts/check_logic.py`
5. Commit and push

---

## Step 1: Understand the `add()` Function

Open `build_data.py` — the `add()` function signature:

```python
def add(
    *,
    id: str,
    name: str,
    category: str,
    year: int,
    inventor: str,
    country: str,
    organization: str,
    description: str,
    speed: str,
    topology: str,
    difficulty: str,
    pins: dict[str, str],
    frame: dict,
    electrical: dict,
    use_cases: list[str],
    advantages: list[str],
    limitations: list[str],
    related_protocols: list[str],
    fun_fact: str = "",
    standards: list[str] = None,
    tags: list[str] = None,
) -> None:
    ...
```

All fields are **keyword-only** — use `key=value` syntax.

---

## Step 2: Choose a Category

```python
CATEGORIES = [
    "Industrial",
    "Networking",
    "On-Board",
    "Automotive",
    "Wireless",
    "Audio/Video",
    "Cellular",
    "USB",
    "High-Speed/FPGA",
    "Security",
    "Aerospace",
    "Sensor-Specific",
    "Debug & Trace"
]
```

Pick the **single best fit**. If it spans categories, pick the primary domain.

> Numeric envelope (`data_rate_max_bps`, `distance_max_m`, `nodes_max`),
> `lifecycle`, `osi_layer` and `standard_doc` are attached automatically from
> `parametric.py` category defaults — add a per-protocol override there when
> you know the exact figures. Electrical text comes from
> `technical_profiles.py` the same way.

---

## Step 3: Write the Protocol Entry

### Template

Copy this template and fill in:

```python
add(
    id="your-protocol-id",           # lowercase, hyphens, unique
    name="Your Protocol Name",       # Display name
    category="Category",             # From CATEGORIES list
    year=2024,                       # Invention/standard year
    inventor="Name or Organization", # Person/team
    country="USA",                   # Country name
    organization="IEEE / Company",   # Standards body or company
    description=(
        "2-4 sentence technical overview. Cover: what it is, "
        "how it works at high level, key characteristics, "
        "primary domain. Minimum 50 characters."
    ),
    speed="Up to X Mbps/Gbps",       # Human-readable range
    topology="Point-to-point",       # Bus, Star, Mesh, Ring, Tree, Point-to-point
    difficulty="Intermediate",       # Beginner/Intermediate/Advanced/Expert
    pins={
        "pin_name": "Description",
        "gnd": "Ground reference"
    },
    frame={
        "fields": [
            {"name": "Field Name", "bits": 8, "description": "Purpose"},
            {"name": "Next Field", "bits": "16-32", "description": "Purpose"},
        ],
        "diagram_notes": "Optional notes for diagram generator"
    },
    electrical={
        "signaling": "Differential",  # Single-ended/Differential/Current Loop/Optical/RF
        "logic_high": "VCC + 0.2V",
        "logic_low": "VCC - 0.2V",
        "voltage_ref": "Common Mode",
        "clocking": "Source-Synchronous",
        "termination": "100Ω differential at each end",
        "biasing": "Weak pull-up/down for idle",
        "implementation_notes": "Practical tips: PCB layout, ESD, common pitfalls"
    },
    use_cases=[
        "Primary use case 1",
        "Primary use case 2",
        "Secondary use case"
    ],
    advantages=[
        "Key strength 1",
        "Key strength 2"
    ],
    limitations=[
        "Key limitation 1",
        "Key limitation 2"
    ],
    related_protocols=["protocol-id-1", "protocol-id-2"],
    fun_fact="Interesting historical or technical tidbit",
    standards=["IEEE 802.x", "ISO 12345"],
    tags=["keyword1", "keyword2", "domain"]
)
```

---

## Step 4: Field-by-Field Guidance

### `id`
- **Format**: lowercase, hyphens only (`can-fd`, `usb-3-1`, `i2c`)
- **Unique**: Check existing IDs in `build_data.py`
- **Used for**: URLs, cross-references, mind map edges

### `name`
- Display name with proper capitalization
- Examples: "CAN FD", "USB 3.1 Gen 2", "I3C", "1000BASE-T"

### `year`
- Invention year OR standardization year (whichever is more meaningful)
- Examples: 1986 (CAN), 1996 (USB 1.0), 2022 (Matter 1.0)

### `inventor`
- Person: "Robert Bosch GmbH", "Gordon Bell (DEC)"
- Organization: "Bluetooth SIG", "USB-IF", "CAN in Automation"
- Team: "Intel & Microsoft", "MIPI Alliance"

### `country`
- Full country name: "Germany", "USA", "Japan", "Sweden"
- For standards bodies: use headquarters country

### `organization`
- Standards body: "IEEE", "ISO", "SAE", "MIPI Alliance"
- Company: "Bosch", "Intel", "NXP"
- Consortium: "Bluetooth SIG", "USB-IF", "LoRa Alliance"

### `description`
- **Minimum 50 characters**
- Cover: purpose, mechanism, speed class, typical use
- Avoid marketing fluff — be technical

### `speed`
- Human-readable: "Up to 1 Mbps", "10/100/1000 Mbps", "480 Mbps (HS), 5 Gbps (SS)"
- Include units (bps, Mbps, Gbps, kbaud)

### `topology`
- Choose one: `Point-to-point`, `Bus`, `Star`, `Mesh`, `Ring`, `Tree`
- For switched fabrics: `Star` (e.g., Ethernet, PCIe, USB)

### `difficulty`
| Level | Typical Protocol |
|-------|------------------|
| Beginner | UART, I²C, SPI, GPIO |
| Intermediate | CAN, RS-485, Modbus, USB 2.0 |
| Advanced | Ethernet, PCIe, USB 3.x, MIPI |
| Expert | 100G Ethernet, JESD204C, CXL, NVLink |

### `pins`
- Map pin/signal name → description
- Include: data, clock, power, ground, control
- Example for SPI: `{"sclk": "Serial Clock", "mosi": "Master Out Slave In", "miso": "Master In Slave Out", "cs": "Chip Select", "gnd": "Ground"}`

### `frame.fields[]`
- **Ordered** from first bit transmitted to last
- `bits`: integer or string range ("5-9")
- `description`: what the field carries
- Used by: diagram generator, frame puzzle, quiz

### `electrical`
All 8 fields **required**. Be specific:

| Field | Example Values |
|-------|----------------|
| `signaling` | "Differential", "Single-ended", "Current Loop", "RF" |
| `logic_high` | "3.3V", "VCC", "+2.5V differential", "Optical high" |
| `logic_low` | "0V", "GND", "-2.5V differential", "Optical low" |
| `voltage_ref` | "GND", "Common Mode", "VCC", "Signal Ground" |
| `clocking` | "Asynchronous", "Synchronous", "Source-Synchronous", "Embedded" |
| `termination` | "120Ω at each end", "None (short runs)", "AC coupling + 50Ω to VTT" |
| `biasing` | "Weak pull-up to 5V", "N/A", "Failsafe biasing resistors" |
| `implementation_notes` | Practical PCB/layout/ESD/firmware tips |

### `related_protocols`
- List of **existing protocol IDs** (from `build_data.py`)
- Used for mind map edges and "See also" in Encyclopedia
- Include: predecessors, successors, variants, related standards

### `standards` (optional)
- Standard numbers: `["IEEE 802.3", "ISO 11898-2", "SAE J1939"]`
- Links to authoritative specs

### `tags` (optional)
- Searchable keywords: `["serial", "differential", "automotive", "safety-critical"]`
- Used by search and filtering

---

## Step 5: Regenerate and Validate

```bash
# Regenerate protocols.json
python build_data.py

# Validate integrity
python build_scripts/check_data.py

# Run logic tests (CRC, formulas, generators)
python build_scripts/check_logic.py

# Sync mobile companion
python build_scripts/sync_mobile.py
```

All must pass before committing.

---

## Step 6: Verify in App

```bash
streamlit run app.py
```

Check:
- [ ] Encyclopedia shows new protocol
- [ ] Search finds it
- [ ] Category filter works
- [ ] Diagrams render (frame, topology, pinout)
- [ ] Quiz generates questions for it
- [ ] Mind map shows connections
- [ ] Compare includes it
- [ ] Timeline places it correctly
- [ ] Geography shows country/org
- [ ] Science Lab calculators work (if applicable)

---

## Example: Adding "I3C" (Improved Inter-Integrated Circuit)

```python
add(
    id="i3c",
    name="I3C",
    category="On-Board",
    year=2017,
    inventor="MIPI Alliance",
    country="USA",
    organization="MIPI Alliance",
    description=(
        "I3C (Improved Inter-Integrated Circuit) is a backward-compatible "
        "evolution of I²C that adds higher speeds (up to 12.5 MHz), "
        "in-band interrupts, dynamic address assignment, and hot-join "
        "capability while retaining the 2-wire SDA/SCL physical layer."
    ),
    speed="Up to 12.5 MHz (SD), 25-50 MHz (HDR)",
    topology="Bus (multi-drop, multi-master)",
    difficulty="Advanced",
    pins={
        "sda": "Serial Data (bidirectional)",
        "scl": "Serial Clock",
        "vdd": "Power (1.2V-3.3V)",
        "gnd": "Ground"
    },
    frame={
        "fields": [
            {"name": "START", "bits": 1, "description": "SDA high→low while SCL high"},
            {"name": "Address + R/W", "bits": 8, "description": "7-bit dynamic address + direction"},
            {"name": "ACK/NACK", "bits": 1, "description": "Target acknowledgment"},
            {"name": "Data", "bits": 8, "description": "Payload byte"},
            {"name": "ACK/NACK", "bits": 1, "description": "Controller/target acknowledgment"},
            {"name": "STOP", "bits": 1, "description": "SDA low→high while SCL high"},
        ],
        "diagram_notes": "HDR modes use different encoding (ternary, DDR)"
    },
    electrical={
        "signaling": "Single-ended (open-drain SDA, push-pull SCL in HDR)",
        "logic_high": "VCC (1.2V-3.3V)",
        "logic_low": "GND (0V)",
        "voltage_ref": "GND",
        "clocking": "Synchronous (controller-driven SCL)",
        "termination": "Pull-up resistors on SDA/SCL (typically 1-10kΩ)",
        "biasing": "Pull-ups provide idle-high state",
        "implementation_notes": "Supports mixed I²C/I3C buses. Dynamic address assignment eliminates address collision. Hot-join allows devices to appear after bus start. HDR-DDR and HDR-TSP modes for higher throughput."
    },
    use_cases=[
        "Sensor interfaces (IMU, ToF, temperature)",
        "Power management ICs",
        "Mobile/wearable peripherals",
        "Automotive zone controllers"
    ],
    advantages=[
        "Backward compatible with I²C targets",
        "Higher speed than I²C (12.5 vs 3.4 MHz)",
        "In-band interrupts (no extra GPIO)",
        "Dynamic addressing (no address conflicts)",
        "Hot-join support"
    ],
    limitations=[
        "More complex controller firmware",
        "HDR modes require push-pull SCL (not pure open-drain)",
        "Less mature ecosystem than I²C",
        "Mixed I²C/I3C bus limited to I²C fast-mode speeds"
    ],
    related_protocols=["i2c", "spi", "smbus", "pmbus"],
    fun_fact="I3C v1.0 was ratified in 2017; v1.1 added HDR-Burst mode for display/touch",
    standards=["MIPI I3C v1.0", "MIPI I3C v1.1"],
    tags=["i2c", "sensor", "mipi", "mobile", "wearable", "backward-compatible"]
)
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Duplicate `id` | Search `build_data.py` for existing IDs |
| Invalid `category` | Use exact canonical category name |
| Missing `electrical` sub-fields | All 8 required |
| `related_protocols` with non-existent IDs | Check IDs in `build_data.py` |
| `description` < 50 chars | Expand technical overview |
| `frame.fields` empty | At least one field required |
| `bits` as float | Use int or string range |

---

## Updating Existing Protocols

1. Find the `add(...)` call in `build_data.py`
2. Modify fields
3. Run `python build_data.py`
4. Run validation tests
5. Commit

---

## Next Steps

- [Schema Reference](schema.md) — Complete field specification
- [Validation](validation.md) — Running checks
- [Architecture Overview](../architecture/overview.md) — System design