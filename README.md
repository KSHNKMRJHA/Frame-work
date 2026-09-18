<div align="center">

# 🛰️ FrameWork

**Every embedded communication protocol an engineer will meet — in one offline, interactive academy.**

118 protocols · 12 categories · 10 learning modules · zero setup

[![CI](https://github.com/KSHNKMRJHA/Frame-work/actions/workflows/ci.yml/badge.svg)](https://github.com/KSHNKMRJHA/Frame-work/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/KSHNKMRJHA/Frame-work/releases)
[![Last commit](https://img.shields.io/github/last-commit/KSHNKMRJHA/Frame-work)](https://github.com/KSHNKMRJHA/Frame-work/commits/main)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Offline](https://img.shields.io/badge/offline-100%25-brightgreen)

**Run it locally · Package it as a desktop app · Use it on the web → [frame-work.streamlit.app](https://frame-work.streamlit.app/)**

</div>

---

## Why FrameWork

Protocol knowledge is scattered across datasheets, vendor PDFs, and terse wiki pages — each covering one bus, in one style, with no way to compare them or check what you actually retained.

FrameWork turns that fragmented landscape into a single, structured academy: a searchable reference where every protocol gets the same treatment, diagrams that are generated rather than hand-drawn, and practice tools that keep producing new questions instead of a fixed quiz bank.

**Designed around four principles:**

| Principle | What it means in practice |
|---|---|
| 🔌 **Offline-first** | No account, no network, no telemetry. Progress is a local JSON file you own. |
| ⚙️ **Generated, not hand-drawn** | Frame, topology, and pinout diagrams are produced from the database — every protocol gets consistent depth automatically. |
| 🧠 **Built for retention** | A procedural quiz engine and puzzle modes that never run out of new combinations. |
| 🧮 **Real engineering math** | Calculators verified against standard CRC check values and textbook formulas, not approximations. |

---

## At a glance

| | |
|---|---|
| **Protocols** | 118, across 12 categories |
| **Modules** | 10 (encyclopedia, timeline, mind map, compare, quiz, puzzles, science lab, geography, profile, info) |
| **Runtime** | Python 3.10+ · Streamlit |
| **Data** | One JSON database, regenerated from `build_data.py` |
| **Persistence** | Atomic local JSON — corruption-safe, no server |
| **Licence** | MIT |
| **Live app** | [frame-work.streamlit.app](https://frame-work.streamlit.app/) |

---

## Feature tour

### 📚 Encyclopedia
The core reference. Search by name, keyword, inventor, or year; filter by category and difficulty; then open a full profile with overview, how-it-works, origin story, typical speed, pins, real-world example, use cases, advantages, limitations, and related protocols — plus three generated diagrams (frame, topology, pinout).

### 🕰️ Timeline & History
An interactive Plotly timeline from **1937 (PCM)** to **2022 (Matter)**, a decade-by-decade narrative, and the milestones worth knowing.

### 🗺️ Mind Map
NetworkX-powered maps of how categories, protocols, and their relatives connect — including cross-links such as CAN ↔ CAN FD ↔ CANopen.

### ⚖️ Compare
Put 2–4 protocols head-to-head on speed, pins, topology, use cases, and trade-offs, with a log-scale speed chart.

### 🧠 Quiz & Assessment
Procedurally generated multiple-choice questions built live from the database. Filter by category and difficulty, track XP, levels, badges, best score, and full history.

### 🎮 Puzzles & Games
Speed matching, frame-field reordering, and "guess the protocol" from progressive clues.

### 🔬 Science & Math Lab
Verified calculators: UART baud rate and bit timing, Shannon and Nyquist capacity, CRC-16/CRC-32 with catalogue check values, frequency ↔ wavelength, and CAN bit timing with prescaler realizability checks.

### 🌍 Geography & Origins
Which countries and organisations invented what — with a world map and an explore-by-country view.

### ⚙️ Settings & Profile
Username, accent colour, XP and badges, JSON export, and a safe reset.

### ℹ️ Info
What the project is, the three ways to run it, canonical links, audience guidance, credits, and licence.

> **Robust by design:** progress is written with a temp-file + `os.replace` swap, so an interrupted write cannot truncate your data. A damaged file is repaired with a visible warning instead of silently resetting your XP.

---

## Protocol coverage

**118 protocols across 12 categories:**

| Category | Count | Examples |
|---|---:|---|
| Industrial | 18 | Modbus (RTU/TCP), PROFIBUS, PROFINET, EtherCAT, EtherNet/IP, DeviceNet, CANopen, HART, OPC UA, BACnet |
| Networking | 17 | Ethernet, TCP, UDP, IP, ARP, DHCP, DNS, ICMP, HTTP/HTTPS, MQTT, CoAP, WebSocket |
| On-Board | 15 | UART, RS-232, RS-485, SPI, QSPI, I²C, I3C, 1-Wire, Microwire, SMBus, PMBus, SDIO, eMMC |
| Automotive | 13 | CAN, CAN FD, LIN, FlexRay, MOST, Automotive Ethernet, SENT, PSI5, UDS, J1939, OBD-II |
| Wireless | 11 | Bluetooth Classic, BLE, Wi-Fi, Zigbee, Thread, Matter, Z-Wave, NFC, RFID, UWB, ANT+ |
| Audio/Video | 9 | I²S, TDM, PCM, S/PDIF, HDMI, MIPI DSI, MIPI CSI, DisplayPort, LVDS |
| Cellular | 8 | GSM/GPRS/EDGE, LTE/4G, LTE-M, NB-IoT, 5G, LoRa, LoRaWAN, Sigfox |
| USB | 8 | USB 1.1, USB 2.0, USB 3.x, USB-C/PD, USB CDC, HID, MSC, DFU |
| High-Speed/FPGA | 8 | PCIe, RapidIO, Aurora, JESD204B/C, SERDES, SGMII, RGMII, XAUI |
| Security | 5 | TLS, DTLS, IPSec, WPA2/WPA3, MACsec |
| Aerospace | 4 | ARINC 429, ARINC 664 (AFDX), MIL-STD-1553, SpaceWire |
| Sensor-Specific | 2 | IO-Link, DSI3 |

---

## Tech stack

| Layer | Used |
|---|---|
| App framework | [Streamlit](https://streamlit.io) |
| Diagrams | [Matplotlib](https://matplotlib.org) |
| Mind maps | [NetworkX](https://networkx.org) |
| Timelines, maps, charts | [Plotly](https://plotly.com) |
| Data | [Pandas](https://pandas.pydata.org), [NumPy](https://numpy.org) |
| Mobile companion | [Kivy](https://kivy.org) → Android APK via Buildozer |
| Packaging | [PyInstaller](https://pyinstaller.org) |
| CI | GitHub Actions — reproducibility, integrity, unit tests, lint |

---

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens at `http://localhost:8501`. Requirements are Python 3.10+ and the
packages in `requirements.txt` — no database, API keys, or network access.

---

## Project structure

```
FrameWork/
├── app.py                        # Home / landing page (entry point)
├── build_data.py                 # Single source of truth → regenerates data/protocols.json
├── data/
│   ├── protocols.json            # The master protocol database (118 entries)
│   └── user_state.json           # Local progress (XP, badges) — auto-created, gitignored
├── pages/                        # Streamlit multipage modules
│   ├── 1_📚_Encyclopedia.py
│   ├── 2_🕰️_Timeline_History.py
│   ├── 3_🗺️_Mindmap.py
│   ├── 4_⚖️_Compare.py
│   ├── 5_🧠_Quiz_Assessment.py
│   ├── 6_🎮_Puzzles_Games.py
│   ├── 7_🔬_Science_Math_Lab.py
│   ├── 8_🌍_Geography_Origins.py
│   ├── 9_⚙️_Settings_Profile.py
│   └── 10_ℹ️_Info.py
├── utils/
│   ├── branding.py               # ⭐ Name, version, build number, links, credits
│   ├── data_loader.py            # Cached JSON loading, search, category helpers
│   ├── diagrams.py               # Frame / topology / pinout / chart generators
│   ├── mindmap.py                # NetworkX mind-map builders
│   ├── quiz_engine.py            # Procedural quiz & puzzle generation
│   ├── science.py                # Verified engineering calculators
│   └── state.py                  # XP / badges / progress persistence (atomic writes)
├── build_scripts/
│   ├── desktop_launcher.py       # Frozen-app entry point (starts server + opens browser)
│   ├── stamp_build.py            # Writes the commit stamp for packaged builds
│   ├── build_exe.bat             # Windows .exe build
│   ├── build_exe.sh              # macOS / Linux binary build
│   ├── check_data.py             # Referential integrity, uniqueness, schema checks
│   ├── check_logic.py            # Unit tests: CRC vectors, formulas, boundary guards
│   └── sync_mobile.py            # Keeps the Kivy mobile copy in sync
├── kivy_mobile/                  # Cross-platform mobile companion (→ Android .apk)
├── .github/workflows/ci.yml      # CI: reproducibility, integrity, tests, lint
├── pyproject.toml                # Packaging metadata (version + deps single-sourced)
├── requirements.txt
├── ruff.toml                     # Pinned lint policy
├── .gitattributes                # Deterministic line endings across platforms
├── LICENSE (MIT)
└── .streamlit/config.toml        # Theme configuration
```

---

## Deployment

FrameWork ships in **three forms** — the same code, three ways to use it.

| # | Form | Description |
|---|---|---|
| 1 | 🖥️ **Local** | Run from source. Fastest way to try it, fully offline. |
| 2 | 📦 **Desktop .exe** | Frozen with PyInstaller — double-click to launch, no Python needed on the target machine. |
| 3 | 🌐 **Web page** | Live at **[frame-work.streamlit.app](https://frame-work.streamlit.app/)** — hosted on Streamlit Community Cloud. |

Plus a bonus 📱 **Android APK** via the Kivy companion.

### 1️⃣ Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 2️⃣ Desktop .exe / binary
```bash
pip install -r requirements.txt pyinstaller
build_scripts\build_exe.bat          # Windows  → dist\FrameWork.exe
bash build_scripts/build_exe.sh      # macOS/Linux
```
> When frozen, progress is written to a per-user OS data directory
> (`%LOCALAPPDATA%\FrameWork\` on Windows, `~/.local/share/FrameWork/` on Linux,
> `~/Library/Application Support/FrameWork/` on macOS) — never inside the temporary
> PyInstaller bundle, which is deleted on exit.

### 3️⃣ Web page
- **Streamlit Community Cloud** — point it at this repo on [share.streamlit.io](https://share.streamlit.io),
  pick `app.py` as the entry point, and it deploys automatically on every push. Free for public repos.
- **Render / Railway / Fly.io** — set the start command
  `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
- **Docker** — any container host works:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 4️⃣ Android APK (bonus)
```bash
cd kivy_mobile
pip install buildozer cython
buildozer -v android debug
```
See `kivy_mobile/README.md` for full steps, including release/Play Store signing.

---

## Updating the protocol database

All content lives in `build_data.py` as structured Python. Edit or extend the `add(...)`
calls, then regenerate:

```bash
python build_data.py                  # rewrite data/protocols.json
python build_scripts/sync_mobile.py   # keep the Kivy mobile copy in sync
```

One source of truth keeps the encyclopedia, quiz engine, mind map, diagrams, timeline,
geography module, and the mobile app consistent. CI verifies the committed JSON still
matches `build_data.py` output, so drift fails the build.

---

## Versioning & build number

Project identity lives in exactly one place — [`utils/branding.py`](utils/branding.py) —
and the package metadata in [`pyproject.toml`](pyproject.toml) reads its version straight
from there, so they cannot disagree.

**The build number is the short git commit tag** — seven hex characters such as
`a1b2c3d` — and it changes with every commit; it is never hand-maintained. It is
resolved in this order:

| # | Source | When it applies |
|---|---|---|
| 1 | `FRAMEWORK_BUILD_COMMIT` env var | Always wins — CI release stamping |
| 2 | Live `.git` in the working tree | Running from source and on Streamlit Cloud |
| 3 | `utils/_build_stamp.txt` | Packaged builds with no `.git`, written by `build_scripts/stamp_build.py` |

Running locally or on the web, the UI shows the exact commit you are on; a frozen `.exe`
shows the commit it was built from. Unresolvable builds report `dev`.

```
v1.0.0 · stable · commit a1b2c3d     # the commit the running app is on
```

| Variable | Purpose |
|---|---|
| `FRAMEWORK_BUILD_COMMIT` | Override the auto-detected build number |
| `FRAMEWORK_BUILD_CHANNEL` | Release channel (default `stable`) |
| `FRAMEWORK_WEB_URL` | Point the UI and footer at a different web deployment |

---

## Quality gates

Run the same checks CI runs:

```bash
python build_scripts/check_data.py    # integrity: ids, categories, schema
python build_scripts/check_logic.py   # unit tests: CRC, formulas, boundaries
ruff check .                          # lint (policy in ruff.toml)
```

CI runs on Python 3.10 and 3.11 and covers:

1. **Reproducibility** — `data/protocols.json` must match `build_data.py` output
2. **No drift** — the mobile companion copies must match the desktop source
3. **Syntax** — every Python file compiles
4. **Data integrity** — referential, uniqueness, and schema checks
5. **Unit tests** — CRC vectors, engineering formulas, boundary guards, generators
6. **Lint** — `ruff check`

---

## Links

- 🌐 **Live app:** https://frame-work.streamlit.app/
- 📦 **Repository:** https://github.com/KSHNKMRJHA/Frame-work
- 🏷️ **Releases:** https://github.com/KSHNKMRJHA/Frame-work/releases
- 💼 **LinkedIn:** https://www.linkedin.com/in/kshnkmrjha/

---

## Credits & licence

- **Created by** [Kishan J.](https://www.linkedin.com/in/kshnkmrjha/)
- **Design by** Piston
- **Made with love and AI**

Technical content is compiled from publicly documented protocol specifications and
standards-body publications (IEEE, IETF, ISO, SAE, JEDEC, MIPI Alliance, Bluetooth SIG,
LoRa Alliance, CAN in Automation, PI, ODVA, and others). Historical facts — invention
years, inventors, origin countries — are provided for educational context; always
cross-reference the original standards documents for contractual, compliance, or
certification purposes.

Released under the **MIT License** — free to use, modify, and redistribute, including
commercially. See [`LICENSE`](LICENSE).
