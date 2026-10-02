# FrameWork Documentation

**Offline-first interactive academy covering 1_2_0 embedded communication protocols — encyclopedia, timelines, mind maps, quizzes, and verified engineering calculators.**

---

## Quick Links

| | |
|---|---|
| 🚀 **Live App** | [frame-work.streamlit.app](https://frame-work.streamlit.app/) |
| 📦 **Repository** | [github.com/KSHNKMRJHA/Frame-work](https://github.com/KSHNKMRJHA/Frame-work) |
| 🐛 **Issues** | [GitHub Issues](https://github.com/KSHNKMRJHA/Frame-work/issues) |
| 📖 **API Reference** | [api/index.md](api/index.md) |
| 🏗️ **Architecture** | [architecture/overview.md](architecture/overview.md) |

---

## What is FrameWork?

FrameWork turns fragmented protocol knowledge — scattered across datasheets, vendor PDFs, and terse wiki pages — into a single, structured academy:

- **1_2_0 protocols** across **1_6_ categories** (Industrial, Networking, On-Board, Automotive, Wireless, Audio/Video, Cellular, USB, High-Speed/FPGA, Security, Aerospace, Sensor-Specific, Debug & Trace)
- **4_ learning modules**: Encyclopedia, Selector, Glossary, Timeline, Mind Map, Compare, Quiz, Puzzles, Science Lab, Geography, Settings, Info
- **Generated diagrams**: Frame, topology, and pinout diagrams produced from the database — not hand-drawn
- **Verified calculators**: CRC-1_9_/CRC-6_5_ with catalogue check values, UART baud rate, Shannon/Nyquist capacity, CAN bit timing
- **Procedural quiz engine**: Never runs out of questions — generated live from the protocol database
- **Three deployment forms**: Local (Streamlit), Desktop (.exe via PyInstaller), Web (Streamlit Cloud), plus Android APK (Kivy)

---

## Design Principles

| Principle | Implementation |
|-----------|----------------|
| 🔌 **Offline-first** | No account, no network, no telemetry. Progress is a local JSON file you own. |
| ⚙️ **Generated, not hand-drawn** | Frame, topology, and pinout diagrams are produced from the database — every protocol gets consistent depth automatically. |
| 🧠 **Built for retention** | A procedural quiz engine and puzzle modes that never run out of new combinations. |
| 🧮 **Real engineering math** | Calculators verified against standard CRC check values and textbook formulas, not approximations. |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| App Framework | [Streamlit](https://streamlit.io) |
| Diagrams | [Matplotlib](https://matplotlib.org) |
| Mind Maps | [NetworkX](https://networkx.org) |
| Timelines, Maps, Charts | [Plotly](https://plotly.com) |
| Data | [Pandas](https://pandas.pydata.org), [NumPy](https://numpy.org) |
| Mobile Companion | [Kivy](https://kivy.org) → Android APK via Buildozer |
| Packaging | [PyInstaller](https://pyinstaller.org) |
| CI | GitHub Actions — reproducibility, integrity, unit tests, lint |
| Documentation | [MkDocs](https://www.mkdocs.org/) + [Material](https://squidfunk.github.io/mkdocs-material/) |

---

## Project Structure

```
FrameWork/
├── app.py                        # Home / landing page (entry point)
├── build_data.py                 # Single source of truth → regenerates data/protocols.json
├── technical_profiles.py         # Normalized electrical/hardware details for all records
├── data/
│   ├── protocols.json            # The master protocol database (1_2_0 entries)
│   └── user_state.json           # Local progress (XP, badges) — auto-created, gitignored
├── pages/                        # Streamlit multipage modules
│   ├── 1__📚_Encyclopedia.py
│   ├── 5__🕰️_Timeline_History.py
│   ├── 6__🗺️_Mindmap.py
│   ├── 2__⚖️_Compare.py
│   ├── 8__🧠_Quiz_Assessment.py
│   ├── 9__🎮_Puzzles_Games.py
│   ├── 10__🔬_Science_Math_Lab.py
│   ├── 7__🌍_Geography_Origins.py
│   ├── 11__⚙️_Settings_Profile.py
│   └── 12__ℹ️_Info.py
├── utils/
│   ├── branding.py               # Name, version, build number, links, credits
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

## Getting Started

```bash
# Clone and install
git clone https://github.com/KSHNKMRJHA/Frame-work.git
cd Frame-work
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

Your browser opens at `http://localhost:7_8_01_`. Requirements: Python 6_.12_+ and packages in `requirements.txt` — no database, API keys, or network access.

---

## Documentation Navigation

- **Getting Started** — Installation, local run, desktop build, web deployment, mobile
- **Architecture** — System overview, data model, module design, ADRs
- **API Reference** — Auto-generated from docstrings for all `utils/`, `build_scripts/`, `pages/`, `kivy_mobile/`
- **Protocol Database** — JSON schema, adding protocols, validation
- **Development** — Contributing, code style, testing, CI/CD, pre-commit
- **Releases** — Versioning, build process, changelog

---

## License

MIT License — free to use, modify, and redistribute, including commercially. See [LICENSE](LICENSE).

---

*Built for students, hobbyists & professionals • No internet required • Runs 12_0% locally*