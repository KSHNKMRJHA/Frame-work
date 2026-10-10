# -*- coding: utf-8 -*-
import datetime

import streamlit as st
from utils.data_loader import load_protocols
from utils import branding, components
from utils.branding import (
    APP_ICON,
    APP_NAME,
    APP_TAGLINE,
    AUTHOR_NAME,
    CREDIT_LINE,
    DESIGNER_NAME,
    LINKEDIN_URL,
    REPO_URL,
    VERSION,
    WEB_URL,
)

branding.page_config("Info", "ℹ️")
branding.sidebar_identity()

protocols = load_protocols()

components.page_hero("Product reference", "Info", APP_TAGLINE, meta=branding.version_label())

tabs = st.tabs(["📖 About", "🚀 Deployment", "🔗 Links & Web", "👥 Audience", "🙏 Credits & License"])

# ================================================================ ABOUT ====
with tabs[0]:
    components.section_header(f"{APP_ICON} {APP_NAME}")
    st.markdown(
        f"**Build number:** `{branding.build_number()}` · {branding.version_label()} · {branding.BUILD_CHANNEL}"
    )
    components.spec_table([("Version", branding.version_label()), ("Build", branding.build_number()), ("Channel", branding.BUILD_CHANNEL), ("Protocols", len(protocols))])
    b1, b2, b3 = st.columns(3)
    b1.link_button("🐙 GitHub", REPO_URL, width="stretch")
    b2.link_button("🌐 Web app", WEB_URL, width="stretch")
    b3.link_button("💼 LinkedIn", LINKEDIN_URL, width="stretch")

    st.write(
        f"""
{APP_NAME} is a complete, offline-first interactive learning platform covering
**{len(protocols)} communication protocols** an embedded/hardware engineer may encounter
across a career — on-board buses, industrial fieldbuses, automotive networks, general
networking/internet protocols, wireless & cellular standards, audio/video interfaces, USB,
high-speed FPGA links, sensor-specific buses, security protocols, and aerospace/defense buses.

It combines:
- A **searchable encyclopedia** with auto-generated frame, topology, and pinout diagrams
- A **protocol selector** that ranks all protocols against your rate/reach/fan-out constraints
- A **glossary** of 60+ terms, code examples and troubleshooting per flagship protocol
- An **interactive history timeline** (1937 PCM → 2022 Matter)
- A **mind map** of how every protocol category and protocol relates to the others
- A **comparison tool** for head-to-head protocol trade-off analysis
- A **procedurally-generated quiz engine** (never runs out of new question combinations)
- **Puzzle games**: speed matching, frame-field reordering, and "guess the protocol"
- A **Science & Math Lab** with 14 real, verified engineering calculators (UART/SPI
  timing & efficiency, Shannon/Nyquist capacity, CRC-16/32, frequency↔wavelength,
  CAN bit timing & bus load, I²C pull-ups, RS-485 biasing & stubs, Ethernet efficiency,
  RF link budget, logic noise margin)
- A **geography module** mapping protocols to their countries/organizations of origin
- A **profile system** with XP, levels, badges, and persistent local progress tracking
        """
    )
    st.info(
        "Everything runs 100% locally and offline once installed — no internet connection, account, or cloud service is required."
    )

# ============================================================= ROADMAP =====
with tabs[1]:
    components.section_header("🚀 Where & how you can run this")

    st.markdown("FrameWork ships in **three forms** — the same code, three ways to use it:")
    t1, t2, t3 = st.columns(3)
    with t1:
        components.section_header("🖥️ 1. Local")
        st.caption("Run from source on your own machine. The fastest way to try it — and fully offline.")
    with t2:
        components.section_header("📦 2. Desktop .exe")
        st.caption("Frozen with PyInstaller into a double-click Windows/macOS/Linux app.")
    with t3:
        components.section_header("🌐 3. Web page")
        st.caption(f"Live on Streamlit Community Cloud — [open the web app]({WEB_URL}).")

    if branding.WEB_URL:
        st.link_button("🌐 Open the live web app", branding.WEB_URL, width="stretch")
    else:
        st.info(
            "The public web deployment is being set up — the live link will be added here "
            "and to the README as soon as it is live.",
            icon="🌐",
        )

    components.section_header("🔗 Project links")
    lc1, lc2 = st.columns(2)
    lc1.link_button("🐙 FrameWork on GitHub", REPO_URL, width="stretch")
    lc2.link_button("💼 Connect on LinkedIn", LINKEDIN_URL, width="stretch")
    st.code(f"git clone {REPO_URL}.git\ncd Frame-work", language="bash")
    st.caption("Clone, fork, report issues, or open a pull request — all on GitHub.")

    components.section_header("🖥️ 1️⃣ Run locally right now (fastest)")
    st.code("pip install -r requirements.txt\nstreamlit run app.py", language="bash")
    st.caption("Opens automatically in your browser at http://localhost:8501")

    components.section_header("🌐 2️⃣ Deploy to the web (free options)")
    st.caption(f"Live at [{WEB_URL}]({WEB_URL}) — hosted on Streamlit Community Cloud.")
    st.markdown(
        f"""
- **Streamlit Community Cloud** — point it at [this repo]({REPO_URL}) on [share.streamlit.io](https://share.streamlit.io), pick `app.py` as the entry point, and it deploys automatically on every push. Free for public repos.
- **Render / Railway / Fly.io** — add a simple start command (`streamlit run app.py --server.port $PORT --server.address 0.0.0.0`) and deploy as a web service.
- **Docker** — a minimal Dockerfile works well for any container host:
        """
    )
    st.code(
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        "COPY . .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "EXPOSE 8501\n"
        'CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]',
        language="dockerfile",
    )

    components.section_header("📦 3️⃣ Package as a standalone .exe / desktop app")
    st.write(
        "The `build_scripts/` folder contains everything needed: `desktop_launcher.py` "
        "starts the Streamlit server programmatically and opens your browser automatically, "
        "and `build_exe.bat` (Windows) / `build_exe.sh` (macOS/Linux) freeze it with PyInstaller."
    )
    st.code("pip install pyinstaller\nbuild_scripts\\build_exe.bat", language="bash")
    st.caption("Produces dist/FrameWork.exe — double-click to launch, no Python install needed on the target machine.")

    components.section_header("📱 4️⃣ Package as an Android APK (bonus)")
    st.write(
        "Streamlit itself cannot run natively on Android. Instead, this project ships a "
        "**genuine cross-platform mobile companion app** in `kivy_mobile/` (built with Kivy), "
        "covering the Quiz and Encyclopedia modules, which **does** build to a real installable "
        "`.apk` via Buildozer."
    )
    st.code("cd kivy_mobile\npip install buildozer cython\nbuildozer -v android debug", language="bash")
    st.caption(
        "See kivy_mobile/README.md for full step-by-step instructions, including release/Play Store signing notes."
    )

    components.section_header("5️⃣ Future roadmap ideas")
    st.markdown(
        """
- Add packet-capture (.pcap) import so users can visualize *real* captured frames against the reference frame diagrams
- Add a spaced-repetition mode to the quiz engine for long-term retention
- Add multiplayer quiz mode (local network) for classroom/team use
- Expand the mobile app to include the mind map and comparison tool
- Add audio narration for accessibility
        """
    )

# ======================================================== GITHUB/LINKS =====
with tabs[2]:
    components.section_header("🐙 GitHub & Links")
    components.spec_table([
        ("Repository", REPO_URL), ("Web app", WEB_URL), ("LinkedIn", LINKEDIN_URL),
        ("Version", f"{branding.version_label()} ({branding.BUILD_CHANNEL})"),
        ("Build number", branding.build_number()),
    ])
    st.link_button("GitHub repository", REPO_URL, width="stretch")
    st.link_button("Open web app", WEB_URL, width="stretch")
    st.link_button("LinkedIn", LINKEDIN_URL, width="stretch")

    components.section_header("Clone & contribute")
    st.code(
        f"git clone {REPO_URL}.git\ncd Frame-work\npip install -r requirements.txt\nstreamlit run app.py",
        language="bash",
    )
    st.write(
        "The repo already includes a `.gitignore` (excludes build artifacts and local progress "
        "data), an MIT `LICENSE`, and a GitHub Actions CI workflow "
        "(`.github/workflows/ci.yml`) that verifies the protocol database is reproducible, "
        "checks the mobile companion has not drifted, runs data-integrity checks, unit tests, "
        "and linting on every push/PR."
    )
    st.markdown(
        f"""
**README badges**
- ![CI]({REPO_URL}/actions/workflows/ci.yml/badge.svg) — GitHub Actions workflow
- ![License](https://img.shields.io/badge/license-MIT-blue)
- ![Python](https://img.shields.io/badge/python-3.10%2B-blue)
- ![Version](https://img.shields.io/badge/version-{VERSION}-blue)
        """
    )

# ============================================================ AUDIENCE =====
with tabs[3]:
    components.section_header("👥 Who this is for")
    c1, c2, c3 = st.columns(3)
    with c1:
        components.section_header("🎓 Students")
        st.write(
            "Use the **Timeline**, **Encyclopedia**, and **Science & Math Lab** to build "
            "foundational understanding, then self-test with the **Quiz** and **Puzzle** modes "
            "before exams or interviews."
        )
    with c2:
        components.section_header("🛠️ Hobbyists")
        st.write(
            "Jump straight to the **Encyclopedia** for pinouts and wiring diagrams when wiring "
            "up a new sensor or module, and use **Compare** to pick between two candidate "
            "protocols for a weekend project."
        )
    with c3:
        components.section_header("💼 Professionals")
        st.write(
            "Use **Compare** and the **Science Lab** calculators (CRC, bit-timing) during real "
            "design/VAVE decisions, and the **Geography** module for quick standards-body "
            "reference during compliance or documentation work."
        )

# ============================================================ CREDITS ======
with tabs[4]:
    components.section_header("🙏 Credits")
    st.markdown(
        f"""
- **{APP_NAME}** — concept, engineering & content by **[{AUTHOR_NAME}]({LINKEDIN_URL})**.
- **Design** by **{DESIGNER_NAME}**.
- **{CREDIT_LINE}** — the code, content, and design in this project were built in
  collaboration with AI tooling, reviewed and curated by the humans above.
        """
    )
    st.write(
        """
- **Technical content**: Compiled from publicly documented protocol specifications, standards
  body publications (IEEE, IETF, ISO, SAE, JEDEC, MIPI Alliance, Bluetooth SIG, LoRa Alliance,
  CAN in Automation, PI, ODVA, and others), and widely published engineering references.
- **Built with**: [Streamlit](https://streamlit.io), [Matplotlib](https://matplotlib.org),
  [NetworkX](https://networkx.org), [Plotly](https://plotly.com), [Pandas](https://pandas.pydata.org),
  and [Kivy](https://kivy.org) (mobile companion).
- **Historical facts** (invention years, inventors, origin countries) are provided for
  educational context; always cross-reference original standards documents for
  contractual/compliance/certification purposes.
        """
    )
    components.section_header("📄 License")
    st.write(
        f"Released under the **MIT License** — free to use, modify, and redistribute, including "
        f"commercially. See `LICENSE` in the project root. © {datetime.date.today().year} {AUTHOR_NAME}."
    )
    st.caption(
        f"{APP_NAME} {branding.version_label()} — made for engineers who want to actually understand the wires and waveforms behind every buzzword."
    )

branding.page_footer()
