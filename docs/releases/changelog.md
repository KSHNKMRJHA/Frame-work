# Changelog

All notable changes to FrameWork are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [Unreleased]

## [1.1.0] - 2026-10-03

### Added
- **140 protocols** across **13 categories** (new: Debug & Trace — JTAG, SWD; plus CAN XL, ISO-TP, SOME/IP, XCP, 10BASE-T1S, UFS, NVMe, SATA, MAVLink, Cyphal, TSN, DDS, DMX512, KNX, DALI, USB4, MIDI, FireWire, 6LoWPAN, NMEA 0183/2000)
- **Protocol Selector**: constraint-driven ranked shortlist (rate/reach/fan-out/lifecycle)
- **Glossary**: 60+ terms in 9 groups with protocol cross-links
- **Parametric envelope** (`parametric.py`): machine-readable rates, reach, fan-out, lifecycle, OSI scope, numbered standard docs
- **Deep bus parameters**: 8 new technical fields on every protocol (distance, nodes, duplex, addressing, error detection, line encoding, power, EMC)
- **Parametric deep-dives**: min/typ/max signal tables + bring-up checklists for 13 flagship protocols
- **Bring-up code snippets** and **troubleshooting bank** per flagship protocol, wired into search
- **Science Lab**: noise margin, UART/SPI efficiency, RS-485 stub, Ethernet efficiency calculators (13 tabs)
- **Quiz**: technical-parameter, highest-data-rate, and troubleshooting-cause generators
- MkDocs documentation with Material theme
- API reference (mkdocstrings)
- Architecture Decision Records (ADRs 0001-0010)
- Protocol database schema documentation
- Contributing guide and development docs
- Pre-commit hooks (Ruff, merge conflict, secrets)
- JSON Schema validation for protocols.json
- **Vectorform design system**: design tokens (`utils/theme.py`), ranked sidebar
  search, "continue where you left off" resume card, deep links (`?p=<id>`),
  protocol summary cards, conductor cards, voltage bars, PNG export, and an
  onboarding walkthrough
- **Browser verification tooling** (`build_scripts/`): `visual_check.py`
  (rendered theme + responsive in Chrome), `cross_browser.py`
  (Chromium/Firefox/WebKit), `page_sweep.py` (every page × every UI state,
  clipped-text and overflow checks), `smoke_pages.py`

### Changed
- Documentation restructured into docs/
- **Navigation reordered** into a learning-oriented sequence: Encyclopedia,
  Compare, Selector, Glossary, History, Mind Map, Geography, Quiz, Puzzles,
  Science Lab, Settings, Info. `pages/` filenames renumbered accordingly, so
  routes change (e.g. Compare is now `/Compare`, not `/Timeline`).
- **Global theming moved from injected CSS to native Streamlit theming.** The
  palette is now defined in `.streamlit/config.toml` (`[theme]`) and applied
  through Streamlit's own machinery; `utils/theme.py` mirrors those tokens and
  the browser tests assert the rendered colours match it exactly.
- **Light and dark themes** both supported. Streamlit follows the operating
  system preference; the Settings page can override it by writing the native
  `base` key (a restart is required).
- **Responsive layout** corrected. Metric grids on Encyclopedia and Science Lab
  were 4-up inside a narrow pane, which clipped values at tablet width
  (`-3.55%` rendered as `-3.…`); they are now 2-up. Long free-text fields
  (Topology, OSI layer, Standard) print as wrapping text because `st.metric`
  clips with an ellipsis.
- `frame_overhead()` surfaced across the protocol set.

### Removed
- The legacy global CSS/JS injection layer (`branding.inject_css()`,
  `component_css()`, `theme.tokens_css()`). Streamlit 1.64's DOMPurify strips
  both `<style>` and `<script>` on every `st.markdown`/`st.html` route, so it
  never reached the browser; it was dead weight replaced by native theming plus
  component-local inline styles.

### Fixed
- Badge documentation corrected: the previous API reference listed seven badges
  and a `check_badges(state, protocols)` signature that do not exist. Badges are
  defined by `BADGE_RULES` in `utils/state.py` and awarded by the one-argument
  `state.check_badges(state)`.
- Responsive clipping of metric values and of long protocol names in buttons.
- A verification script that logged a failing result without asserting on it,
  and a truncation detector that silently skipped every metric value.

---

## [1.0.0] - 2024-01-15

### Added
- **118 protocols** across 12 categories
- **10 learning modules**: Encyclopedia, Timeline, Mind Map, Compare, Quiz, Puzzles, Science Lab, Geography, Settings, Info
- **Generated diagrams**: Frame, topology, pinout (Matplotlib)
- **Procedural quiz engine**: Infinite MCQs from protocol data
- **Puzzle modes**: Frame reorder, speed matching, guess protocol
- **Verified calculators**: CRC-16/CCITT, CRC-16/MODBUS, CRC-32/IEEE, UART, CAN, Shannon, Nyquist, RF
- **Offline-first architecture**: No network, no accounts, local JSON progress
- **Three deployment forms**: Local (Streamlit), Desktop (PyInstaller), Web (Streamlit Cloud)
- **Mobile companion**: Kivy Android APK (quiz/encyclopedia focused)
- **Atomic JSON persistence**: Temp file + os.replace, corruption recovery
- **Git commit as build number**: Auto-resolved, never hand-maintained
- **CI pipeline**: Reproducibility, mobile sync, data integrity, logic tests, lint
- **Single source of truth**: `build_data.py` → `protocols.json` for all modules

### Technical Details

**Protocol Categories (12):**
- Industrial (18): Modbus, PROFIBUS, PROFINET, EtherCAT, EtherNet/IP, DeviceNet, CANopen, HART, OPC UA, BACnet
- Networking (17): Ethernet, TCP, UDP, IP, ARP, DHCP, DNS, ICMP, HTTP/HTTPS, MQTT, CoAP, WebSocket
- On-Board (15): UART, RS-232, RS-485, SPI, QSPI, I²C, I3C, 1-Wire, Microwire, SMBus, PMBus, SDIO, eMMC
- Automotive (13): CAN, CAN FD, LIN, FlexRay, MOST, Automotive Ethernet, SENT, PSI5, UDS, J1939, OBD-II
- Wireless (11): Bluetooth Classic, BLE, Wi-Fi, Zigbee, Thread, Matter, Z-Wave, NFC, RFID, UWB, ANT+
- Audio/Video (9): I²S, TDM, PCM, S/PDIF, HDMI, MIPI DSI, MIPI CSI, DisplayPort, LVDS
- Cellular (8): GSM/GPRS/EDGE, LTE/4G, LTE-M, NB-IoT, 5G, LoRa, LoRaWAN, Sigfox
- USB (8): USB 1.1, USB 2.0, USB 3.x, USB-C/PD, USB CDC, HID, MSC, DFU
- High-Speed/FPGA (8): PCIe, RapidIO, Aurora, JESD204B/C, SERDES, SGMII, RGMII, XAUI
- Security (5): TLS, DTLS, IPSec, WPA2/WPA3, MACsec
- Aerospace (4): ARINC 429, ARINC 664 (AFDX), MIL-STD-1553, SpaceWire
- Sensor-Specific (2): IO-Link, DSI3

**Tech Stack:**
- Streamlit, Matplotlib, NetworkX, Plotly, Pandas, NumPy
- Kivy (mobile), PyInstaller (desktop)
- GitHub Actions CI (Python 3.10, 3.11)
- Ruff lint/format

**Quality Gates:**
- Reproducibility: `protocols.json` must match `build_data.py` output
- Mobile sync: `kivy_mobile/data/protocols.json` must match desktop
- Data integrity: 10 validation rules
- Logic tests: CRC catalogue vectors, formula verification, boundary guards, generator solvability
- Lint: Ruff with strict config

---

## Version History Summary

| Version | Date | Protocols | Modules | Key Milestone |
|---------|------|-----------|---------|---------------|
| 1.1.0 | 2026-10-03 | 140 | 12 | Vectorform redesign, native theming, browser verification gates |
| 1.0.0 | 2024-01-15 | 118 | 10 | Initial public release |

---

## Upgrade Notes

### From Source (Any Version)

```bash
git pull origin main
pip install -r requirements.txt
streamlit run app.py
```

Progress (`data/user_state.json`) is forward-compatible.

### Desktop (.exe)

Download new `.exe` from GitHub Releases. Run — progress auto-migrates from `%LOCALAPPDATA%\FrameWork\`.

### Mobile (APK)

Uninstall old APK, install new. Progress is separate from desktop (by design).

---

## Contributors

- **Kishan J.** — Creator, lead developer
- **Piston** — Design
- **AI Assistance** — Code generation, documentation, testing

---

## See Also

- [Releases: Versioning](versioning.md)
- [Releases: Build Process](build-process.md)
- [Architecture: Versioning](../architecture/adrs/0010-versioning-build-stamp.md)
- [GitHub Releases](https://github.com/KSHNKMRJHA/Frame-work/releases)