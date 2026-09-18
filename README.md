# 🛰️ FrameWork

### The interactive academy for every communication protocol an embedded engineer will meet in a career.

**v1.0.0** · stable · built 2026-09-18

[![CI](https://github.com/KSHNKMRJHA/Frame-work/actions/workflows/ci.yml/badge.svg)](https://github.com/KSHNKMRJHA/Frame-work/actions/workflows/ci.yml)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Last commit](https://img.shields.io/github/last-commit/KSHNKMRJHA/Frame-work)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b)
![Offline](https://img.shields.io/badge/offline-100%25-brightgreen)

FrameWork is a complete, **offline-first**, interactive learning platform covering
**118 communication protocols** — every bus, fieldbus, network, wireless standard,
audio/video link, USB class, high-speed serial link, sensor bus, security protocol,
and aerospace/defense bus an embedded or hardware engineer is likely to meet.

Everything runs **100% locally**. No internet connection, account, sign-up, or cloud
service is required — progress is stored in a plain JSON file on your own machine.

---

## 📑 Table of contents

- [✨ Feature tour](#-feature-tour)
- [📡 Protocol coverage](#-protocol-coverage)
- [🧰 Tech stack](#-tech-stack)
- [🚀 Quick start](#-quick-start)
- [📦 Project structure](#-project-structure)
- [🖥️ Deployment options](#️-deployment-options)
- [🔄 Updating the protocol database](#-updating-the-protocol-database)
- [🔖 Branding, versioning & releases](#-branding-versioning--releases)
- [✅ Quality gates](#-quality-gates)
- [🔗 Links](#-links)
- [🙏 Credits & license](#-credits--license)

---

## ✨ Feature tour

Ten modules, each driven live from a single master database — no hand-written pages,
so every protocol gets the same depth automatically.

### 📚 Encyclopedia
The core reference. Search by name, keyword, inventor, or year; filter by category and
difficulty; then open a full per-protocol profile:
- **Overview**, **How it works**, and an **Origin story** (inventor / standards body / country)
- **Typical speed**, **pins/wires**, and a **real-world example**
- **Use cases**, **advantages**, and **limitations**
- **Related protocols** with cross-links
- **Three auto-generated diagrams**: frame/packet structure, network topology, and pinout/wiring

### 🕰️ Timeline & History
An interactive Plotly timeline from **1937 (PCM)** to **2022 (Matter)**, plus a
decade-by-decade narrative and the milestones worth knowing.

### 🗺️ Mind Map
NetworkX-powered visual maps: a full graph of every category → protocol → relative, and a
per-category graph that also draws cross-links between related protocols (CAN ↔ CAN FD ↔
CANopen, and friends). Includes a plain list view.

### ⚖️ Compare
Put **2–4 protocols head-to-head** on speed, pins, topology, use cases, advantages, and
limitations — with a log-scale speed comparison chart.

### 🧠 Quiz & Assessment
A **procedurally generated** multiple-choice engine: questions are built from the live
database, so it never runs out of new combinations. Filter by category and difficulty,
choose the question count, and earn **XP, levels, and badges**. Tracks quizzes taken,
best score, and current level.

### 🎮 Puzzles & Games
- **Speed matching** — pair protocols with their throughput
- **Frame-field reordering** — rebuild a protocol frame in the right order
- **Guess the protocol** — identify a protocol from progressive clues (wrong guesses cost XP)

### 🔬 Science & Math Lab
Real, verified engineering calculators — not approximations:
- **UART baud rate & bit-timing** (with framing error analysis)
- **Shannon & Nyquist capacity** theorems
- **CRC-16 / CRC-32** calculator with standard catalogue check values
- **Frequency ↔ wavelength** conversion
- **CAN bit timing** with prescaler realizability checks
- Byte-string parsing helpers

### 🌍 Geography & Origins
Which countries and organizations invented what — with a world map, origin breakdowns,
and an explore-by-country view.

### ⚙️ Settings & Profile
Your username, accent colour, XP/level/badges, full activity history, **export progress as
JSON**, and a safe reset.

### ℹ️ About, Deployment & Credits
Five tabs covering what the project is, how to deploy it (local / .exe / web / APK),
repos and links, audience guidance, and full credits and licensing.

### 🔒 Offline-first persistence
Progress is saved to a local JSON file using **atomic writes** (temp file + `os.replace`),
so an interrupted write can never truncate your data. A damaged or hand-edited file is
**repaired or recovered with a visible warning** rather than silently resetting your XP.

---

## 📡 Protocol coverage

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

## 🧰 Tech stack

| Layer | Used |
|---|---|
| App framework | [Streamlit](https://streamlit.io) |
| Diagrams | [Matplotlib](https://matplotlib.org) (frame, topology, pinout, charts) |
| Mind maps | [NetworkX](https://networkx.org) |
| Timelines / maps / charts | [Plotly](https://plotly.com) |
| Data handling | [Pandas](https://pandas.pydata.org), [NumPy](https://numpy.org) |
| Mobile companion | [Kivy](https://kivy.org) (→ Android APK via Buildozer) |
| Packaging | [PyInstaller](https://pyinstaller.org) |
| CI | GitHub Actions (reproducibility, integrity, unit tests, lint) |

---

## 🚀 Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens automatically at `http://localhost:8501`.

**Requirements:** Python 3.10+ and the packages in `requirements.txt`. Nothing else —
no database, no API keys, no network access.

---

## 📦 Project structure

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
│   └── 10_ℹ️_About_Roadmap_Credits.py
├── utils/
│   ├── branding.py               # ⭐ Name, version, build metadata, links, credits
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
│   ├── main.py
│   ├── quiz_logic.py
│   ├── buildozer.spec
│   └── data/protocols.json
├── .github/workflows/ci.yml      # CI: reproducibility, integrity, tests, lint
├── requirements.txt
├── ruff.toml                     # Pinned lint policy
├── LICENSE (MIT)
└── .streamlit/config.toml        # Theme configuration
```

---

## 🖥️ Deployment options

FrameWork ships in **three forms** — the same code, three ways to use it.

| # | Form | Description |
|---|---|---|
| 1 | 🖥️ **Local** | Run from source. Fastest way to try it, fully offline. |
| 2 | 📦 **Desktop .exe** | Frozen with PyInstaller — double-click to launch, no Python needed on the target machine. |
| 3 | 🌐 **Web page** | Hosted online via Streamlit Community Cloud. *Web deployment in progress — live link to follow.* |

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

## 🔄 Updating the protocol database

All content lives in `build_data.py` as structured Python. Edit or extend the `add(...)`
calls, then regenerate:

```bash
python build_data.py                  # rewrite data/protocols.json
python build_scripts/sync_mobile.py   # keep the Kivy mobile copy in sync
```

One source of truth keeps the encyclopedia, quiz engine, mind map, diagrams, timeline,
geography module, and the mobile app all consistent. CI verifies that the committed JSON
still matches `build_data.py` output, so drift fails the build.

---

## 🔖 Branding, versioning & build number

Project name, version, build metadata, links, and credits live in exactly one place —
[`utils/branding.py`](utils/branding.py). Every page renders from it, so the name and
version can never drift apart.

**The build number is the short git commit tag** (e.g. `1999bc7`) and changes by itself
with every commit — it is never hand-maintained. It is resolved in this order:

| # | Source | When it applies |
|---|---|---|
| 1 | `FRAMEWORK_BUILD_COMMIT` env var | Always wins — CI release stamping |
| 2 | Live `.git` in the working tree | Running from source / Streamlit Cloud — always the commit you are actually on |
| 3 | `utils/_build_stamp.txt` | Packaged builds with no `.git`, written by `build_scripts/stamp_build.py` |

So running locally or on the web, the UI shows the exact commit you are on; a frozen
`.exe` shows the commit it was built from. If nothing can be resolved it falls back to
`dev`.

```
v1.0.0 · stable · built 2026-09-18 · commit 1999bc7
```

Other release values can be stamped the same way:

| Variable | Example | Purpose |
|---|---|---|
| `FRAMEWORK_BUILD_COMMIT` | `a1b2c3d` | Override the auto-detected build number |
| `FRAMEWORK_BUILD_DATE` | `2026-09-18` | Build date shown in the UI |
| `FRAMEWORK_BUILD_CHANNEL` | `stable` | Release channel |
| `FRAMEWORK_WEB_URL` | `https://…` | Public web app URL (empty until deployed) |

When packaging a desktop build, stamp the commit first so the frozen app knows it:

```bash
python build_scripts/stamp_build.py    # writes utils/_build_stamp.txt (gitignored)
```

---

## ✅ Quality gates

Run the same checks CI runs:

```bash
python build_scripts/check_data.py    # integrity: ids, categories, schema
python build_scripts/check_logic.py   # unit tests: CRC, formulas, boundaries
ruff check .                          # lint (policy in ruff.toml)
```

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on Python 3.10 and 3.11 and
covers:
1. **Reproducibility** — `data/protocols.json` must match `build_data.py` output
2. **No drift** — the mobile companion copies must match the desktop source
3. **Syntax** — every Python file compiles
4. **Data integrity** — referential, uniqueness, and schema checks
5. **Unit tests** — CRC vectors, engineering formulas, boundary guards, generators
6. **Lint** — `ruff check`

---

## 🔗 Links

- **Repository:** https://github.com/KSHNKMRJHA/Frame-work
- **LinkedIn:** https://www.linkedin.com/in/kshnkmrjha/
- **Web app:** *deployment in progress — link to follow*

---

## 🙏 Credits & license

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
