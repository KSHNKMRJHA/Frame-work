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

VERSION = "1.0.0"
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
    """Configure the Streamlit page with consistent FrameWork branding."""
    import streamlit as st

    title = f"{page_label} | {APP_NAME}" if page_label else APP_NAME
    st.set_page_config(page_title=title, page_icon=page_icon or APP_ICON, layout=layout)


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
