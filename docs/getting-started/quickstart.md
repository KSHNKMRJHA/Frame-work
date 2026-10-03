# Quick Start

Get FrameWork running in under 2 minutes.

## Prerequisites

- **Python 3.10+** (3.11 recommended)
- **Git** (for cloning)
- **pip** (comes with Python)

## 1. Clone the Repository

```bash
git clone https://github.com/KSHNKMRJHA/Frame-work.git
cd Frame-work
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies include: `streamlit`, `pandas`, `numpy`, `plotly`, `networkx`, `matplotlib`, `kivy` (mobile), `pyinstaller` (desktop).

## 3. Run Locally

```bash
streamlit run app.py
```

Your browser opens automatically at `http://localhost:8501`.

## 4. Explore

- **📚 Encyclopedia** — Browse all 140 protocols with full technical profiles
- **🕰️ Timeline** — Interactive history from 1937 (PCM) to 2022 (Matter)
- **🗺️ Mind Map** — NetworkX-powered protocol relationship graphs
- **⚖️ Compare** — Side-by-side protocol comparison with log-scale speed chart
- **🧠 Quiz** — Procedurally generated MCQs with XP, levels, badges
- **🎮 Puzzles** — Frame-field reordering, speed matching, guess-the-protocol
- **🔬 Science Lab** — Verified calculators: baud rate, CRC, Shannon/Nyquist, wavelength
- **🌍 Geography** — World map of protocol origins by country/organization
- **⚙️ Settings** — Profile, theme, progress export/reset
- **ℹ️ Info** — About, deployment, links, credits

---

## Alternative: Run with uv (faster)

```bash
pip install uv
uv pip install -r requirements.txt
uv run streamlit run app.py
```

---

## Next Steps

- [Installation Details](installation.md) — Virtual environments, optional dependencies
- [Running Locally](local.md) — Configuration, ports, themes
- [Desktop Build](desktop.md) — Create standalone .exe / binary
- [Web Deployment](web.md) — Streamlit Cloud, Render, Docker
- [Mobile (Android)](mobile.md) — Build APK with Buildozer