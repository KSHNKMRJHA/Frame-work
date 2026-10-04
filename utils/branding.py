# -*- coding: utf-8 -*-
"""
branding.py
Single source of truth for FrameWork's public identity: the project name,
version, build number, canonical links, and credits.

Every surface — the Streamlit pages, the README, the packaged executables, and
the mobile companion — reads from here, so nothing can drift out of sync.

**The build number is the short git commit tag** (e.g. ``015f212``) and changes
by itself with every commit. It is resolved in this order:

1. ``FRAMEWORK_BUILD_COMMIT`` — an explicit stamp. Wins always, and is the only
   mechanism available to a frozen/packaged build, which has no ``.git``.
2. The live repository — ``_detect_git_commit()`` reads ``.git`` directly, so
   running from source (or on Streamlit Cloud) always shows the commit you are
   actually on.
3. ``utils/_build_stamp.txt`` — a generated file the packaging scripts write so
   a frozen ``.exe``/binary still reports the commit it was built from.

``FRAMEWORK_BUILD_CHANNEL`` is read from the environment; everything else below
is a constant.
"""

import os

import streamlit as st

from utils import theme
from utils import ui_state


# ------------------------------------------------------------ build metadata
def _git_dir(root):
    """Locate the real git directory.

    In a normal checkout ``.git`` is a directory, but in a worktree or submodule
    it is a *file* containing ``gitdir: <path>`` — handle both, otherwise the
    commit silently resolves to nothing.
    """
    marker = os.path.join(root, ".git")
    if os.path.isdir(marker):
        return marker
    if os.path.isfile(marker):
        try:
            with open(marker, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("gitdir:"):
                        return os.path.normpath(os.path.join(root, line.split(":", 1)[1].strip()))
        except OSError:
            return None
    return None


def _detect_git_commit(short=7):
    """Return the short commit hash the running code came from, or ''.

    Reads ``.git`` directly rather than shelling out to ``git``: it stays cheap
    on every Streamlit rerun and still works on machines without git installed.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_dir = _git_dir(root)
    if not git_dir:
        return ""
    try:
        with open(os.path.join(git_dir, "HEAD"), "r", encoding="utf-8") as fh:
            head = fh.read().strip()
    except OSError:
        return ""
    if not head.startswith("ref:"):
        return head[:short]  # detached HEAD: HEAD holds the hash itself
    ref = head.split(" ", 1)[1].strip()
    try:
        with open(os.path.join(git_dir, *ref.split("/")), "r", encoding="utf-8") as fh:
            return fh.read().strip()[:short]
    except OSError:
        pass
    # After `git gc` the loose ref is gone and lives in packed-refs instead.
    try:
        with open(os.path.join(git_dir, "packed-refs"), "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith(("#", "^")):
                    continue
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[1].strip() == ref:
                    return parts[0][:short]
    except OSError:
        pass
    return ""


def _stamped_commit():
    """Read the packaging-time stamp file, if the build scripts generated one.

    A frozen build has no ``.git`` to inspect, so ``build_scripts/stamp_build.py``
    writes ``utils/_build_stamp.txt`` (bundled via ``--add-data "utils;utils"``)
    just before packaging. It is read as text — not imported — so there is no
    import machinery for PyInstaller to get wrong.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "utils", "_build_stamp.txt")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.lower().startswith("commit="):
                    return line.split("=", 1)[1].strip()
    except OSError:
        return ""
    return ""


# ------------------------------------------------------------------ identity
APP_NAME = "FrameWork"
APP_ICON = "🛰️"
APP_TAGLINE = "The interactive academy for every communication protocol an embedded engineer will meet in a career."

VERSION = "1.1.0"
BUILD_CHANNEL = os.environ.get("FRAMEWORK_BUILD_CHANNEL", "stable")
# Explicit stamp > live git working tree > packaging-time stamp > nothing.
BUILD_COMMIT = os.environ.get("FRAMEWORK_BUILD_COMMIT", "").strip() or _detect_git_commit() or _stamped_commit()

# --------------------------------------------------------------------- links
REPO_URL = "https://github.com/KSHNKMRJHA/Frame-work"
LINKEDIN_URL = "https://www.linkedin.com/in/kshnkmrjha/"

# The live web app. Set FRAMEWORK_WEB_URL to deploy the same build elsewhere.
WEB_URL = os.environ.get("FRAMEWORK_WEB_URL", "").strip() or "https://frame-work.streamlit.app/"

# ------------------------------------------------------------------- credits
AUTHOR_NAME = "Kishan J."
DESIGNER_NAME = "Piston"
CREDIT_LINE = "Made with love and AI"


def version_label():
    """Short version string, e.g. 'v1.0.0'."""
    return f"v{VERSION}"


def build_number():
    """The build number: the short commit tag, or a placeholder for an unversioned tree."""
    return BUILD_COMMIT or "dev"


def build_line():
    """One-line, publishable build string, e.g. 'v1.0.0 · stable · commit 015f212'."""
    return " · ".join([version_label(), BUILD_CHANNEL, f"commit {build_number()}"])


def credit_line():
    """Attribution used in footers: author, designer, and the AI collaboration note."""
    return f"Created by {AUTHOR_NAME} · Design by {DESIGNER_NAME} · {CREDIT_LINE}"


# --------------------------------------------------------------- UI helpers


def page_config(page_label=None, page_icon=None, layout="wide"):
    """Configure the Streamlit page with consistent FrameWork branding.

    Theming is intentionally NOT handled here. The palette comes from
    `.streamlit/config.toml` (native Streamlit `[theme]` keys); the previous
    `inject_css()` call was removed after it was proven unreachable - DOMPurify
    strips both `<style>` and `<script>` on every st.markdown/st.html route, so
    it emitted nothing. A saved light/dark preference is applied by the Settings
    page writing the native `base` key instead.
    """
    import streamlit as st

    title = f"{page_label} | {APP_NAME}" if page_label else APP_NAME
    st.set_page_config(page_title=title, page_icon=page_icon or APP_ICON, layout=layout)


def sidebar_sections():
    """Render the Vectorform navigation groups in the sidebar.

    NOT CALLED by default. Streamlit already renders a complete multipage nav
    whose order follows the pages/ filename prefixes, so a second list here
    duplicates every destination - and the CSS rule that would hide the built-in
    list lives in an injected stylesheet, which Streamlit 1.64 strips. The
    built-in list is the single source of truth.

    Kept for reference and for the deferred st.navigation migration (task 1.1),
    where the built-in list disappears and these headings become useful.
    """
    import streamlit as st

    pal = theme.current_palette()
    with st.sidebar:
        st.markdown(
            f'<div style="font-size:.70rem;font-weight:700;letter-spacing:.14em;'
            f'text-transform:uppercase;color:{pal["text_faint"]};margin:.9rem 0 .25rem 0">'
            f'Navigate</div>', unsafe_allow_html=True
        )
        for heading, pages in ui_state.NAV_SECTIONS:
            st.markdown(
                f'<div style="font-size:.68rem;font-weight:700;letter-spacing:.10em;'
                f'text-transform:uppercase;color:{pal["accent"]};margin:.7rem 0 .15rem 0">'
                f'{heading}</div>', unsafe_allow_html=True
            )
            for label in pages:
                st.page_link(f"pages/{_page_file(label)}", label=label, icon=None)


_PAGE_FILES = {
    "📚 Encyclopedia": "1_📚_Encyclopedia.py",
    "⚖️ Compare": "2_⚖️_Compare.py",
    "🧭 Selector": "3_🧭_Selector.py",
    "📖 Glossary": "4_📖_Glossary.py",
    "🕰️ History & Timeline": "5_🕰️_Timeline_History.py",
    "🗺️ Mind Map": "6_🗺️_Mindmap.py",
    "🌍 Geography & Origins": "7_🌍_Geography_Origins.py",
    "🧠 Quiz & Assessment": "8_🧠_Quiz_Assessment.py",
    "🎮 Puzzles & Games": "9_🎮_Puzzles_Games.py",
    "🔬 Science & Math Lab": "10_🔬_Science_Math_Lab.py",
    "⚙️ Settings & Profile": "11_⚙️_Settings_Profile.py",
    "ℹ️ Info": "12_ℹ️_Info.py",
}


def _page_file(label):
    return _PAGE_FILES[label]


_ONBOARD_KEY = "_fw_onboarded"

_ONBOARD_STEPS = [
    ("🔌 Wiring, not just specs",
     "Every protocol now shows its real conductors, the differential pair, and "
     "the volts on the wire — USB's D+/D− sitting at 3.0 V, not 0 and 1."),
    ("⚡ Derived waveforms",
     "Waveforms are generated from the line coding rather than drawn by hand, "
     "so the trace always matches the numbers. Change the cable length and "
     "watch the RX traces shift."),
    ("🔗 Share any protocol",
     "The address bar carries `?p=usb20`, so a specific entry is bookmarkable "
     "and citable instead of something you have to go and find again."),
]

_ONBOARD_STEPS_KEY = "_fw_onboard_step"


@st.dialog("Welcome to FrameWork", width="medium")
def _onboarding_dialog():
    """Three-step first-run tour.

    Explains the three things that are genuinely new about this build, because
    an unlabelled D+/D− diagram reads as a bug until you know it is deliberate.
    """
    idx = st.session_state.get(_ONBOARD_STEPS_KEY, 0)
    title, body = _ONBOARD_STEPS[idx]
    dots = "".join(
        f'<span class="{"on" if i == idx else ""}"></span>'
        for i in range(len(_ONBOARD_STEPS))
    )
    st.markdown(
        f'<div class="fw-modal-hero"><div style="font-size:1.5rem">{title}</div>'
        f'<div class="fw-step-dots">{dots}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(body)

    # NB: do not bind a local named `dialog` or `open` here - Streamlit
    # rewrites attribute access on those names, and `dialog.open()` raises
    # "`open()` is not a valid Streamlit command".
    nav = st.columns([1, 1, 1])
    if nav[0].button("← Back", disabled=idx == 0, width="stretch"):
        st.session_state[_ONBOARD_STEPS_KEY] = idx - 1
        st.rerun()
    if nav[2].button("Get started →", type="primary", width="stretch"):
        st.session_state[_ONBOARD_KEY] = True
        st.rerun()
    if nav[1].button("Skip", width="stretch"):
        st.session_state[_ONBOARD_KEY] = True
        st.rerun()
    if idx < len(_ONBOARD_STEPS) - 1:
        st.caption("Step " + str(idx + 1) + " of " + str(len(_ONBOARD_STEPS)))


def maybe_onboard():
    """Show the tour once, on the home page only.

    st.dialog needs a live Streamlit runtime to open. The bare-mode smoke test
    has none, and Streamlit's own decorator raises there, so the call is guarded
    rather than letting the whole page fail.
    """
    if st.session_state.get(_ONBOARD_KEY):
        return
    st.session_state.setdefault(_ONBOARD_STEPS_KEY, 0)
    if not _runtime_available():
        st.session_state[_ONBOARD_KEY] = True    # do not nag in bare mode
        return
    _onboarding_dialog()


def _runtime_available():
    """True when a real Streamlit runtime is driving this script."""
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    return get_script_run_ctx() is not None


def mark_onboarded():
    st.session_state[_ONBOARD_KEY] = True


def protocol_summary_card(selected):
    """Render a one-page PNG summary of a protocol for offline study notes.

    Matplotlib is already a dependency, so this produces a clean, printable
    figure with the identity block, the conductor list and the signal levels -
    the three things a student copies into a notebook.
    """
    import io

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    spec = selected.get("electrical") or {}
    pal = theme.current_palette()
    fig = plt.figure(figsize=(10, 13), facecolor=pal["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(0.06, 0.955, selected["name"], color=pal["text"], fontsize=26,
            fontweight="bold", va="top")
    ax.text(0.06, 0.915, f"{selected['category']}  ·  {selected['year']}  ·  "
            f"{selected.get('topology','—')}", color=pal["text_muted"], fontsize=12, va="top")
    ax.plot([0.06, 0.94], [0.895, 0.895], color=pal["border"], lw=1)

    y = 0.855
    ax.text(0.06, y, "CONDUCTORS", color=pal["accent"], fontsize=11,
            fontweight="bold", va="top")
    y -= 0.030
    spec_pairs = {p["a"]: (p["b"], p["role"]) for p in (spec.get("pairs") or [])}
    for sig in (selected.get("signals") or [])[:10]:
        mate = spec_pairs.get(sig["name"])
        ax.text(0.075, y, f"{sig['name']:<12}", color=pal["text"], fontsize=11,
                family="monospace", va="top")
        ax.text(0.30, y, sig["description"][:52], color=pal["text_muted"],
                fontsize=10, va="top")
        if mate:
            ax.text(0.94, y, f"⇄ {mate[0]} ({mate[1]})", color=pal["signal"],
                    fontsize=9, family="monospace", va="top", ha="right")
        y -= 0.030

    y -= 0.015
    ax.text(0.06, y, "SIGNAL LEVELS", color=pal["accent"], fontsize=11,
            fontweight="bold", va="top")
    y -= 0.030
    for line in electrical_levels_text(spec):
        ax.text(0.075, y, line, color=pal["text"], fontsize=11, family="monospace", va="top")
        y -= 0.028

    y -= 0.015
    ax.text(0.06, y, "KEY PARAMETERS", color=pal["accent"], fontsize=11,
            fontweight="bold", va="top")
    y -= 0.030
    for label, value in [
        ("Max rate", str(selected.get("speed", "—"))[:60]),
        ("Max reach", str(selected.get("distance_max_m", "—"))),
        ("Max nodes", str(selected.get("nodes_max", "—"))),
        ("OSI layer", str(selected.get("osi_layer", "—"))),
        ("Standard", str(selected.get("standard_doc", "—"))[:60]),
    ]:
        ax.text(0.075, y, f"{label:<14}", color=pal["text_muted"], fontsize=10, va="top")
        ax.text(0.30, y, value, color=pal["text"], fontsize=10, va="top")
        y -= 0.026

    ax.text(0.06, 0.035, f"FrameWork  ·  {selected['id']}", color=pal["text_faint"],
            fontsize=9, va="bottom")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=pal["bg"])
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def electrical_levels_text(spec):
    """Human-readable level lines, shared by the PNG export."""
    import electrical_specs

    if not spec:
        return ["no electrical data"]
    lines = [electrical_specs.format_levels(spec) or "—"]
    z = spec.get("impedance_ohm")
    rise = spec.get("rise_time_ns")
    bit = spec.get("bit_period_ns")
    if z:
        lines.append(f"Z0            {z:g} ohm")
    if rise:
        lines.append(f"Rise time     {rise:g} ns")
    if bit:
        lines.append(f"Bit period    {bit:g} ns  ({1000.0 / bit:,.1f} Mbit/s)")
    return lines


# ------------------------------------------------- Vectorform components ---
_ARROW = {
    "O": "→", "I": "←", "B": "↔", "I/O": "↔",
    "P": "⚡", "G": "⏚", "-": "·",
}
_ROLE = {
    "transmit": "TX", "receive": "RX", "bidirectional": "½ duplex",
}


def conductor_cards(selected):
    """Render conductors as bordered cards with direction and pair badges.

    Styles are INLINE rather than from the injected stylesheet. Verified with
    Playwright against Streamlit 1.64: DOMPurify strips <style> blocks on every
    injection route, so a stylesheet silently disappears, whereas inline style
    attributes survive reliably. Inline is the only dependable option here.
    """
    spec = selected.get("electrical") or {}
    pal = theme.current_palette()
    mate, role_of = {}, {}
    for pr in spec.get("pairs") or []:
        mate[pr["a"]] = pr["b"]
        mate[pr["b"]] = pr["a"]
        role_of[pr["a"]] = role_of[pr["b"]] = _ROLE.get(pr["role"], pr["role"])

    cards = []
    for sig in selected.get("signals") or []:
        arrow = _ARROW.get(sig["dir"], "·")
        badge = ""
        if sig["name"] in mate:
            badge = (
                f'<div style="margin-top:.22rem;font-size:.68rem;font-weight:700;'
                f'color:{pal["signal"]};background:{pal["surface_alt"]};'
                f'border:1px solid {pal["border"]};border-radius:999px;'
                f'padding:.05rem .45rem;display:inline-block;'
                f'font-family:{theme.MONO_STACK}">'
                f'⇄ {mate[sig["name"]]} · {role_of.get(sig["name"], "")}</div>'
            )
        cards.append(
            f'<div style="background:{pal["surface"]};border:1px solid {pal["border"]};'
            f'border-radius:6px;padding:.55rem .7rem">'
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:baseline;gap:.5rem">'
            f'<span style="font-family:{theme.MONO_STACK};font-weight:700;'
            f'font-size:.92rem;color:{pal["text"]}">{sig["name"]}</span>'
            f'<span style="color:{pal["accent"]};font-size:1.05rem;'
            f'font-weight:700">{arrow}</span></div>'
            f'{badge}'
            f'<div style="margin-top:.3rem;font-size:.78rem;line-height:1.4;'
            f'color:{pal["text_muted"]}">{sig["description"]}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div style="display:grid;gap:.55rem;margin:.35rem 0 .75rem 0;'
        f'grid-template-columns:repeat(auto-fill,minmax(190px,1fr))">'
        f'{"".join(cards)}</div>',
        unsafe_allow_html=True)


def level_bars(spec):
    """Draw the signal's two levels as proportional bars.

    Numbers alone hide the *shape* of a signal: an RS-485 swing of 4 V on a
    zero common mode looks nothing like USB's 0.4 V on 3.0 V, and the bars make
    that difference immediate.
    """
    signaling = spec.get("signaling")
    if signaling in ("differential", "bipolar", "passive"):
        hi, lo = spec.get("vdiff_high_volts"), spec.get("vdiff_low_volts")
        if hi is None or lo is None:
            return
        vcm = spec.get("vcm_volts") or 0.0
        hi, lo = float(hi), float(lo)
        top = vcm + max(abs(hi), abs(lo)) / 2.0
        bottom = vcm - max(abs(hi), abs(lo)) / 2.0
        bars = [
            _bar(f"V+ max  {vcm + hi / 2:+.2f} V", vcm + hi / 2, bottom, top, "hi"),
            _bar(f"V+ min  {vcm + lo / 2:+.2f} V", vcm + lo / 2, bottom, top, "lo"),
            _bar(f"V− max  {vcm - hi / 2:+.2f} V", vcm - hi / 2, bottom, top, "hi"),
            _bar(f"V− min  {vcm - lo / 2:+.2f} V", vcm - lo / 2, bottom, top, "lo"),
        ]
        note = f"VDiff swing {abs(hi - lo):.2f} V about a {vcm:.2f} V common mode"
    elif signaling == "rf":
        dbm = spec.get("vdiff_high_volts") or 0
        st.markdown(
            f'<div class="fw-card"><div class="fw-card-top">'
            f'<span class="fw-sig">Transmit power</span></div>'
            f'<div class="fw-bigval">{dbm:g} <span>dBm</span></div>'
            f'<div class="fw-card-desc">into a {spec.get("impedance_ohm") or 50:g} Ω '
            f'matched load</div></div>',
            unsafe_allow_html=True)
        return
    else:
        voh, vol = spec.get("voh_volts"), spec.get("vol_volts")
        if voh is None or vol is None:
            return
        hi, lo = float(max(voh, vol)), float(min(voh, vol))
        bars = [
            _bar(f"VOH  {hi:+.2f} V", hi, lo, hi, "hi"),
            _bar(f"VOL  {lo:+.2f} V", lo, lo, hi, "lo"),
        ]
        note = f"Swing {abs(hi - lo):.2f} V"
    st.markdown(
        f'<div style="margin:.4rem 0 .2rem 0;display:grid;gap:.28rem">'
        f'{"".join(bars)}</div>'
        f'<div style="font-size:.75rem;margin-top:.25rem;'
        f'color:{theme.current_palette()["text_faint"]};font-variant-numeric:tabular-nums">'
        f'{note}</div>', unsafe_allow_html=True)


def _bar(label, value, floor, ceiling, kind):
    """One level bar. Inline styles for the same DOMPurify reason as the cards."""
    pal = theme.current_palette()
    span = (ceiling - floor) or 1.0
    pct = max(0.0, min(100.0, (value - floor) / span * 100.0))
    colour = pal["signal"] if kind == "hi" else pal["accent"]
    return (
        f'<div style="display:grid;grid-template-columns:9.5rem 1fr;'
        f'align-items:center;gap:.6rem">'
        f'<span style="font-family:{theme.MONO_STACK};font-size:.76rem;'
        f'color:{pal["text_muted"]};font-variant-numeric:tabular-nums">{label}</span>'
        f'<span style="display:block;height:.55rem;background:{pal["surface_alt"]};'
        f'border:1px solid {pal["border"]};border-radius:999px;overflow:hidden">'
        f'<span style="display:block;height:100%;width:{pct:.1f}%;'
        f'background:{colour};border-radius:999px"></span></span></div>'
    )


@st.dialog("Command / opcode vocabulary", width="large")
def commands_dialog(selected):
    """Show a protocol's command table in a modal.

    Command tables are reference material: most users never open them, and in
    the page flow they added a lot of scrolling to every single protocol.
    """
    commands = selected.get("commands") or []
    if not commands:
        st.info("This protocol defines no command set of its own.")
        return
    st.dataframe(
        [{"Code": c["code"], "Name": c["name"], "Purpose": c.get("note", "")}
         for c in commands],
        width="stretch", hide_index=True,
    )


def sidebar_identity():
    """Render the FrameWork name, version, build number, and links in the sidebar."""
    import streamlit as st

    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding:0.15rem 0 0.6rem 0; line-height:1.35;">
                <div style="font-size:1.12rem; font-weight:700;">{APP_ICON} {APP_NAME}</div>
                <div style="font-size:0.78rem; color:#94a3b8;">{version_label()} · {BUILD_CHANNEL}</div>
                <div style="font-size:0.70rem; color:#64748b;">build {build_number()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size:0.78rem;'>"
            f"<a href='{REPO_URL}' target='_blank'>GitHub</a> · "
            f"<a href='{WEB_URL}' target='_blank'>Web</a> · "
            f"<a href='{LINKEDIN_URL}' target='_blank'>LinkedIn</a>"
            f"</div>",
            unsafe_allow_html=True,
        )


def page_footer():
    """Render the standard publication footer (version, build, links, credits)."""
    import streamlit as st

    st.divider()
    st.caption(
        f"**{APP_NAME}** {build_line()}  \n"
        f"[GitHub repository]({REPO_URL}) · [Web app]({WEB_URL}) · [LinkedIn]({LINKEDIN_URL})  \n"
        f"{credit_line()}"
    )
