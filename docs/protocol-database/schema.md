# Data Model

Complete specification of the FrameWork protocol database schema.

## `protocols.json` Structure

```json
{
  "protocols": [
    {
      "id": "uart",
      "name": "UART",
      "category": "On-Board",
      "year": 1960,
      "inventor": "Gordon Bell (DEC)",
      "country": "USA",
      "organization": "DEC",
      "description": "Universal Asynchronous Receiver-Transmitter...",
      "speed": "Up to 5 Mbps (standard), 10+ Mbps (high-speed)",
      "topology": "Point-to-point",
      "difficulty": "Beginner",
      "pins": {
        "tx": "Transmit Data",
        "rx": "Receive Data",
        "gnd": "Ground"
      },
      "frame": {
        "fields": [
          {"name": "Start Bit", "bits": 1, "description": "Logic low"},
          {"name": "Data Bits", "bits": "5-9", "description": "LSB first"},
          {"name": "Parity Bit", "bits": "0-1", "description": "Optional"},
          {"name": "Stop Bits", "bits": "1-2", "description": "Logic high"}
        ],
        "diagram_notes": "Start=0, Stop=1, parity optional"
      },
      "electrical": {
        "signaling": "Single-ended",
        "logic_high": "VCC (3.3V/5V)",
        "logic_low": "GND (0V)",
        "voltage_ref": "GND",
        "clocking": "Asynchronous (oversampling)",
        "termination": "None required for short runs",
        "biasing": "N/A",
        "implementation_notes": "Oversample at 16x baud rate..."
      },
      "use_cases": [
        "Microcontroller-to-PC serial",
        "GPS modules",
        "Bluetooth modules",
        "Debug consoles"
      ],
      "advantages": [
        "Simple, universal",
        "No clock line needed",
        "Low pin count (2-3)"
      ],
      "limitations": [
        "No multi-drop",
        "Speed limited by async timing",
        "No built-in addressing"
      ],
      "related_protocols": ["RS-232", "RS-485", "SPI", "I²C"],
      "fun_fact": "Original DECwriter LA36 used 110 baud current loop",
      "standards": ["EIA-232", "EIA-422", "EIA-485"],
      "tags": ["serial", "async", "microcontroller", "debug"]
    }
  ]
}
```

---

## Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique slug (lowercase, hyphens). Used for URLs, cross-refs. |
| `name` | string | ✅ | Display name (e.g., "UART", "CAN FD", "USB 3.0") |
| `category` | string | ✅ | One of 12 canonical categories |
| `year` | integer | ✅ | Invention/standardization year |
| `inventor` | string | ✅ | Person or team credited |
| `country` | string | ✅ | ISO 3166-1 alpha-2 or full name |
| `organization` | string | ✅ | Company, standards body, or consortium |
| `description` | string | ✅ | 2-4 sentence technical overview |
| `speed` | string | ✅ | Human-readable speed range |
| `topology` | string | ✅ | Network topology (Point-to-point, Bus, Star, Mesh, Ring, Tree) |
| `difficulty` | string | ✅ | Beginner / Intermediate / Advanced / Expert |
| `pins` | object | ✅ | Pin name → description mapping |
| `frame` | object | ✅ | Frame structure with fields array |
| `frame.fields[]` | array | ✅ | Ordered frame fields |
| `frame.fields[].name` | string | ✅ | Field name |
| `frame.fields[].bits` | string/int | ✅ | Bit width (can be range like "5-9") |
| `frame.fields[].description` | string | ✅ | Field purpose |
| `frame.diagram_notes` | string | ❌ | Notes for diagram generator |
| `electrical` | object | ✅ | Normalized electrical profile |
| `electrical.signaling` | string | ✅ | Single-ended / Differential / Current Loop / Optical / RF |
| `electrical.logic_high` | string | ✅ | Voltage/level for logic 1 |
| `electrical.logic_low` | string | ✅ | Voltage/level for logic 0 |
| `electrical.voltage_ref` | string | ✅ | Reference (GND, VCC, Common Mode, etc.) |
| `electrical.clocking` | string | ✅ | Synchronous / Asynchronous / Source-Synchronous / Embedded |
| `electrical.termination` | string | ✅ | Termination requirements |
| `electrical.biasing` | string | ✅ | Biasing requirements (idle line state) |
| `electrical.implementation_notes` | string | ✅ | Practical implementation guidance |
| `use_cases` | string[] | ✅ | Typical applications |
| `advantages` | string[] | ✅ | Strengths |
| `limitations` | string[] | ✅ | Weaknesses |
| `related_protocols` | string[] | ✅ | Related protocol IDs (for mind map links) |
| `fun_fact` | string | ❌ | Interesting historical/technical tidbit |
| `standards` | string[] | ❌ | Standard numbers (IEEE 802.3, ISO 11898, etc.) |
| `tags` | string[] | ❌ | Searchable keywords |

---

## Canonical Categories

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
    "Sensor-Specific"
]
```

---

## Difficulty Levels

| Level | Criteria |
|-------|----------|
| **Beginner** | Ubiquitous, simple frame, 2-4 pins, async or basic sync |
| **Intermediate** | Multi-drop, addressing, moderate frame complexity |
| **Advanced** | High-speed, complex state machine, multiple PHY options |
| **Expert** | Multi-lane, protocol stacks, advanced error recovery |

---

## Topology Values

| Value | Examples |
|-------|----------|
| Point-to-point | UART, RS-232, SPI, I²C, USB |
| Bus | CAN, RS-485, Modbus, PROFIBUS, I²C (multi-master) |
| Star | Ethernet (switched), USB (hub), PCIe |
| Mesh | Zigbee, Thread, Matter, Bluetooth Mesh |
| Ring | Token Ring, FDDI, RapidIO |
| Tree | CANopen, DeviceNet, PROFIBUS DP |

---

## Signaling Types

| Type | Protocols |
|------|-----------|
| Single-ended | UART, SPI, GPIO, SDIO |
| Differential | RS-485, CAN, Ethernet, USB, PCIe, LVDS |
| Current Loop | 4-20mA, HART, MIDI |
| Optical | S/PDIF (TOSLINK), POF |
| RF | Bluetooth, Wi-Fi, Zigbee, LoRa, NFC |

---

## Clocking Types

| Type | Protocols |
|------|-----------|
| Asynchronous | UART, RS-232, RS-485 |
| Synchronous | SPI, I²C, I3C, SMBus, PCIe |
| Source-Synchronous | DDR, MIPI DSI/CSI, JESD204B |
| Embedded Clock | USB, SATA, Ethernet (1000BASE-T), PCIe |

---

## JSON Schema (for validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FrameWork Protocol Database",
  "type": "object",
  "required": ["protocols"],
  "properties": {
    "protocols": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": [
          "id", "name", "category", "year", "inventor", "country",
          "organization", "description", "speed", "topology", "difficulty",
          "pins", "frame", "electrical", "use_cases", "advantages",
          "limitations", "related_protocols"
        ],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z0-9-]+$"},
          "name": {"type": "string", "minLength": 1},
          "category": {"type": "string", "enum": ["Industrial", "Networking", "On-Board", "Automotive", "Wireless", "Audio/Video", "Cellular", "USB", "High-Speed/FPGA", "Security", "Aerospace", "Sensor-Specific"]},
          "year": {"type": "integer", "minimum": 1900, "maximum": 2030},
          "inventor": {"type": "string"},
          "country": {"type": "string"},
          "organization": {"type": "string"},
          "description": {"type": "string", "minLength": 50},
          "speed": {"type": "string"},
          "topology": {"type": "string"},
          "difficulty": {"type": "string", "enum": ["Beginner", "Intermediate", "Advanced", "Expert"]},
          "pins": {"type": "object", "additionalProperties": {"type": "string"}},
          "frame": {
            "type": "object",
            "required": ["fields"],
            "properties": {
              "fields": {
                "type": "array",
                "minItems": 1,
                "items": {
                  "type": "object",
                  "required": ["name", "bits", "description"],
                  "properties": {
                    "name": {"type": "string"},
                    "bits": {"type": ["string", "integer"]},
                    "description": {"type": "string"}
                  }
                }
              },
              "diagram_notes": {"type": "string"}
            }
          },
          "electrical": {
            "type": "object",
            "required": ["signaling", "logic_high", "logic_low", "voltage_ref", "clocking", "termination", "biasing", "implementation_notes"],
            "properties": {
              "signaling": {"type": "string"},
              "logic_high": {"type": "string"},
              "logic_low": {"type": "string"},
              "voltage_ref": {"type": "string"},
              "clocking": {"type": "string"},
              "termination": {"type": "string"},
              "biasing": {"type": "string"},
              "implementation_notes": {"type": "string"}
            }
          },
          "use_cases": {"type": "array", "items": {"type": "string"}},
          "advantages": {"type": "array", "items": {"type": "string"}},
          "limitations": {"type": "array", "items": {"type": "string"}},
          "related_protocols": {"type": "array", "items": {"type": "string"}},
          "fun_fact": {"type": "string"},
          "standards": {"type": "array", "items": {"type": "string"}},
          "tags": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

---

## Validation Rules (enforced by `check_data.py`)

1. **Unique IDs**: All `id` values must be unique
2. **Valid Categories**: `category` must be in canonical list
3. **Valid Difficulty**: Must be one of 4 levels
4. **Referential Integrity**: All `related_protocols` IDs must exist
5. **Frame Fields**: At least one field, ordered, no duplicate names
6. **Electrical Profile**: All 8 sub-fields present
7. **Non-empty Arrays**: `use_cases`, `advantages`, `limitations`, `related_protocols` ≥ 1 item
8. **Year Range**: 1900-2030
9. **Description Length**: ≥ 50 characters

---

## Adding a New Protocol

See [Adding Protocols](adding-protocols.md) for step-by-step guide.

---

## Technical Profiles (`technical_profiles.py`)

Normalized electrical/hardware details for advanced use:

```python
# Example structure
TECHNICAL_PROFILES = {
    "uart": {
        "baud_rates": [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600],
        "data_bits_options": [5, 6, 7, 8, 9],
        "parity_options": ["none", "even", "odd", "mark", "space"],
        "stop_bits_options": [1, 1.5, 2],
        "oversampling": 16,
        "max_cable_length_m": 15,  # at 9600 baud
        "esd_protection_kv": 15,
        "common_ics": ["16550", "16C550", "FT232RL", "CP2102", "CH340"]
    }
    # ... 117 more
}
```

This supplements `protocols.json` with implementation-specific data for calculators and reference.

---

## Parametric envelope (`parametric.py`)

Machine-readable numbers powering the Selector page and sortable comparisons.
`None` means "defined by the carrier, not here" (e.g. TCP has no data rate
of its own). Numbers are representative maxima, never simultaneous
(RS-485: 10 Mbps XOR 1200 m).

| Field | Type | Example (CAN) |
|---|---|---|
| `data_rate_max_bps` | number \| null | `1000000` |
| `data_rate_min_bps` | null (reserved) | `null` |
| `distance_max_m` | number \| null | `1000` |
| `nodes_max` | number \| null | `30` |
| `lifecycle` | `emerging` \| `active` \| `mature` \| `legacy` | `mature` |
| `osi_layer` | string | `L1+L2 (vehicle network)` |
| `standard_doc` | string (numbered!) | `ISO 11898-1:2015` |

Category defaults cover every protocol; per-protocol overrides pin the
flagships. `check_data.py` enforces positivity, `min ≤ max`, and the
lifecycle vocabulary.

---

## Practical content banks (`utils/`)

| Module | Content | UI |
|---|---|---|
| `code_snippets.py` | Copy-paste bring-up snippets (Arduino, STM32 HAL, MicroPython, Linux, SocketCAN) | Encyclopedia "Bring-up code" |
| `troubleshooting.py` | Symptom → cause → fix, wiring-first order | Encyclopedia "Troubleshooting"; Quiz generator |
| `glossary.py` | 60+ terms in 9 groups with protocol cross-links | Glossary page |
| `technical_deep.py` | Min/typ/max signal tables, timing, bus rules, standards, checklists | Encyclopedia "Parametric deep-dive" |

---

## Next Steps

- [Adding Protocols](adding-protocols.md) — How to extend the database
- [Validation](validation.md) — Running integrity checks
- [API: Data Loader](../api/data_loader.md) — Programmatic access