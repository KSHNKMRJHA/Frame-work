# -*- coding: utf-8 -*-
"""
branding.py
Single source of truth for FrameWork's public identity: the project name,
version, build metadata, canonical links, and credits.

Every surface — the Streamlit pages, the README, the packaged executables,
and the mobile companion — reads from here, so the name, version, and links
can never drift out of sync with one another. Change them in exactly one
place.

Build metadata can be stamped at publish time by the CI/release pipeline via
the FRAMEWORK_BUILD_DATE and FRAMEWORK_BUILD_CHANNEL environment variables;
the constants below are the sensible defaults for a local build.
"""

import os

# ------------------------------------------------------------------ identity
APP_NAME = "FrameWork"
APP_ICON = "🛰️"
APP_TAGLINE = "The interactive academy for every communication protocol an embedded engineer will meet in a career."

VERSION = "1.0.0"
BUILD_CHANNEL = os.environ.get("FRAMEWORK_BUILD_CHANNEL", "stable")
BUILD_DATE = os.environ.get("FRAMEWORK_BUILD_DATE", "2026-09-18")
BUILD_COMMIT = os.environ.get("FRAMEWORK_BUILD_COMMIT", "")

# --------------------------------------------------------------------- links
REPO_URL = "https://github.com/KSHNKMRJHA/Frame-work"
LINKEDIN_URL = "https://www.linkedin.com/in/kshnkmrjha/"

# Public web app URL. Left empty until the Streamlit Community Cloud / hosted
# deployment is live — when it is, set FRAMEWORK_WEB_URL (or paste it here) and
# every surface that mentions the web build starts linking to it.
WEB_URL = os.environ.get("FRAMEWORK_WEB_URL", "")

# ------------------------------------------------------------------- credits
AUTHOR_NAME = "Kishan J."
DESIGNER_NAME = "Piston"
CREDIT_LINE = "Made with love and AI"

# The three places this project ships to, in the order most users meet them.
DEPLOY_TARGETS = ("local", "desktop .exe", "web page")


def version_label():
    """Short version string, e.g. 'v1.0.0'."""
    return f"v{VERSION}"


def build_line():
    """One-line, publishable build string, e.g.
    'v1.0.0 · stable · built 2026-09-18 · commit qwedr344'."""
    parts = [version_label(), BUILD_CHANNEL, f"built {BUILD_DATE}"]
    if BUILD_COMMIT:
        parts.append(f"commit {BUILD_COMMIT}")
    return " · ".join(parts)


def web_status():
    """Human-readable state of the web deployment (a URL once it is live)."""
    return WEB_URL or "web deployment in progress — link to follow"


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
    """Render the FrameWork name, version, build info, and links in the sidebar."""
    import streamlit as st

    commit_html = f'<div style="font-size:0.70rem; color:#64748b;">commit {BUILD_COMMIT}</div>' if BUILD_COMMIT else ""
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding:0.15rem 0 0.6rem 0; line-height:1.35;">
                <div style="font-size:1.12rem; font-weight:700;">{APP_ICON} {APP_NAME}</div>
                <div style="font-size:0.78rem; color:#94a3b8;">{version_label()} · {BUILD_CHANNEL}</div>
                <div style="font-size:0.70rem; color:#64748b;">built {BUILD_DATE}</div>
                {commit_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size:0.78rem;'>"
            f"<a href='{REPO_URL}' target='_blank'>GitHub</a> · "
            f"<a href='{LINKEDIN_URL}' target='_blank'>LinkedIn</a>"
            f"</div>",
            unsafe_allow_html=True,
        )


def page_footer():
    """Render the standard publication footer (version, build, links, credits)."""
    import streamlit as st

    web = f" · [Web app]({WEB_URL})" if WEB_URL else ""
    st.divider()
    st.caption(
        f"**{APP_NAME}** {build_line()}  \n"
        f"[GitHub repository]({REPO_URL}) · [LinkedIn]({LINKEDIN_URL}){web}  \n"
        f"{credit_line()}"
    )
