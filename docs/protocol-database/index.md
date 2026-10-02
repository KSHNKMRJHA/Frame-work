# Protocol Database

Complete documentation for the FrameWork protocol database.

## Contents

- [Schema Reference](schema.md) — Complete field specification with JSON Schema
- [Adding Protocols](adding-protocols.md) — Step-by-step guide to extend the database
- [Validation](validation.md) — Running integrity checks

## Quick Overview

The protocol database is the single source of truth for all 140 protocols across 13 categories. It lives in `data/protocols.json` and is regenerated from `build_data.py`.

### Structure

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
      "description": "...",
      "speed": "Up to 5 Mbps",
      "topology": "Point-to-point",
      "difficulty": "Beginner",
      "pins": { "tx": "Transmit Data", "rx": "Receive Data", "gnd": "Ground" },
      "frame": { "fields": [...] },
      "electrical": { ... },
      "use_cases": [...],
      "advantages": [...],
      "limitations": [...],
      "related_protocols": ["rs-232", "spi", "i2c"],
      "fun_fact": "...",
      "standards": ["EIA-232"],
      "tags": ["serial", "async"]
    }
  ]
}
```

### Categories (12)

| Category | Count | Examples |
|----------|-------|----------|
| Industrial | 18 | Modbus, PROFIBUS, CANopen |
| Networking | 17 | Ethernet, TCP, MQTT |
| On-Board | 15 | UART, SPI, I²C, I3C |
| Automotive | 13 | CAN, LIN, FlexRay |
| Wireless | 11 | Bluetooth, Wi-Fi, Zigbee |
| Audio/Video | 9 | I²S, HDMI, DisplayPort |
| Cellular | 8 | LTE, 5G, LoRaWAN |
| USB | 8 | USB 2.0, USB 3.x, USB-C |
| High-Speed/FPGA | 8 | PCIe, JESD204B, SERDES |
| Security | 5 | TLS, IPSec, MACsec |
| Aerospace | 4 | ARINC 429, SpaceWire |
| Sensor-Specific | 2 | IO-Link, DSI3 |

---

## Regenerating the Database

```bash
# After editing build_data.py
python build_data.py

# Validate
python build_scripts/check_data.py
python build_scripts/check_logic.py

# Sync mobile
python build_scripts/sync_mobile.py
```

---

## See Also

- [Schema Reference](schema.md)
- [Adding Protocols](adding-protocols.md)
- [Validation](validation.md)
- [Architecture: Data Model](../architecture/data-model.md)