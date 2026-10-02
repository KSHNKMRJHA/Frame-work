# Enhancement Roadmap

Every item below is written so it can be picked up and implemented without
re-deriving the analysis. Priority: **P1** ships next, **P2** after that,
**P3** are larger research items.

Legend: *effort* is rough (S ≈ half a day, M ≈ 1-2 days, L ≈ a week).

---

## Where the project stands

| Metric | Value |
|--------|-------|
| Protocols | 140 across 13 categories |
| Frame layouts | 116 documented + 24 explicitly carrier-defined |
| Electrical/technical profiles | 140 (100%) |
| Interface silicon references | 19 protocols |
| Waveform renderers | 9 builders, 64 protocols mapped |
| Verified calculators | 28 in `utils/science.py` |
| Automated checks | `check_data.py`, `check_logic.py` (11 groups), `ruff` |

---

## P1 — Ship next (high value, contained risk)

### 1. Waveform builders for the remaining physical protocols
`ethernet_waveform`, `i2s_waveform`, `arinc429_waveform` exist. Still missing
waveforms for protocols that genuinely have a drawable signal:
- `flexray`, `most`, `sent`, `psi5`, `t1s` (automotive single/dual-wire)
- `mipi_dsi`, `mipi_csi`, `hdmi` (already have TMDS/DSI packet builders — extend)
- `spacewire`, `mil1553` (command/response word diagrams)
- `lin` (single-wire with break/sync)
- `jtag`, `swd` (4-wire debug signal sets)

*Effort:* M · *Where:* `utils/diagrams.py`, then extend `_WAVE_MAP`.

### 2. Transceiver coverage from 19 → 60+ protocols
`_TRANSCEIVERS` in `technical_profiles.py` only covers core interfaces.
Highest-value additions: every Industrial protocol (Modbus/Profibus/CANopen
already partially), USB classes, Automotive, Wireless modules (ESP32-C6,
nRF52840, SX1262), and Audio (PCM1794, ES8388).
*Effort:* S per batch · *Rule:* only list parts you can verify in a datasheet.

### 3. Frame-overhead comparison across protocols
The new `frame_overhead()` already computes per-protocol efficiency. Surface it
as a sortable table and bar chart on the Compare page so users can see "CAN is
efficient at 8 bytes, terrible at 1 byte".
*Effort:* S · *Where:* `pages/4_⚖️_Compare.py`.

### 4. Bring-up checklist generator
Turn each protocol's `design_notes` + `technical` into a per-protocol bring-up
checklist (decoupling, termination, pull-ups, first scope measurement).
*Effort:* M · *Where:* new `utils/bringup.py` + Encyclopedia section.

---

## P2 — Depth and pedagogy

### 5. Bit-level decoder playground
Let users paste a hex frame and get a field-by-field breakdown for any of the
116 protocols with known layouts. This is the single most engaging feature:
it turns static diagrams into a real tool.
*Effort:* L · *Depends on:* per-protocol field offsets (a bigger `frame_specs`
schema: each field needs `offset`, `length`, `endian`, and a decode description).

### 6. Layer-stack explorer
Visualise where each protocol sits (PHY / link / network / transport / app) and
which other protocols stack on it. Data already exists in `parametric.py`
(`osi_scope`); needs a diagram + filters.
*Effort:* M · *Where:* new `utils/layer_diagram.py`.

### 7. Performance comparison at equal payload size
Extend Compare so speed is always paired with a payload size — "1 Mbps" means
something very different at 1 B vs 1500 B.
*Effort:* S.

### 8. Per-protocol worked example traces
Show a real capture (hex + annotated) for 15-20 landmark protocols: CAN, Modbus,
MQTT, TLS 1.3 handshake, I²C, SPI, HTTP/2 headers.
*Effort:* L · *Source:* craft accurate synthetic captures from the specs.

---

## P3 — Larger builds

### 9. Glossary ↔ protocol cross-linking
`utils/glossary.py` and `pages/12_📖_Glossary.py` exist; make every term link to
the protocols that use it, and vice versa.
*Effort:* M.

### 10. RF spectrum / modulation explorer
Visualise ASK/FSK/PSK/QAM, spreading factors, and sensitivity vs. range using the
existing `fspl_db` / `link_budget_db`.
*Effort:* L.

### 11. Timing-budget visualiser
Given a bitrate, frame size, and jitter budget, show whether a deadline is met —
the real question behind the CAN bit-timing calculator.
*Effort:* M.

### 12. Problem-based learning paths
Guided projects ("build a Modbus RTU sensor node", "bring up an I²C bus with a
scope") that chain several protocols.
*Effort:* L.

---

## Data-quality rules to keep

These are enforced by `build_scripts/check_data.py` and should never be relaxed:

1. `frame_fields` names must be unique within a protocol (frame puzzles grade on
   names).
2. A protocol must either declare `frame_fields` **or** appear in
   `frame_specs.NO_FIXED_FRAME` — no silent gaps.
3. Every protocol needs a non-empty `frame_note`.
4. Every record must expose the same core key set (catches partial writes).
5. `fun_fact` requires `fun_fact_source`.
6. `technical.*` fields must be non-empty strings; `design_notes` a non-empty
   list of strings; `transceivers` a list of strings.

**Never invent a frame layout.** If a standard has no fixed frame (LoRa, Wi-Fi,
LVDS), say so explicitly rather than drawing a plausible-looking diagram.

---

## Known gaps / honest limitations

- The 24 protocols in `NO_FIXED_FRAME` intentionally have no bit-level diagram.
- `technical_profiles.py` values are representative, not authoritative; always
  defer to the device datasheet for VOH/VIL, rise times and drive strength.
- Waveforms are generated from framing rules, not captured from real hardware.
- `site/` is generated output and should be gitignored, not committed.