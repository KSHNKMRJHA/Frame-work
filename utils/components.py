# -*- coding: utf-8 -*-
"""SignalBench shared UI primitives.

A small, focused component layer that gives FrameWork its "engineering
instrument meets documentation" character. Each function renders native
Streamlit output plus a *scoped, inline-styled* HTML block built from the
active theme tokens.

Design rules (SignalBench):

* Colour always comes from ``theme.current_palette()`` so every component is
  correct in Dark and Light. Never hardcode a palette hex here - the theme
  regression test (``check_theme.py``) forbids it, and a dark-only badge would
  disappear on the light background.
* Measured values use the monospace stack; prose uses the sans stack.
* Any coloured fill picks its own label colour through ``theme.contrast_text()``
  so text is never white-on-white.
* Nothing here injects a global ``<style>`` or ``<script>`` (DOMPurify strips
  both). Styling is carried on the element itself, which is the supported,
  maintainable route on Streamlit 1.64.
* Borders and elevation - not big shadows - carry the hierarchy (radius ~6-8px,
  hairline 1px borders).

This is deliberately NOT a frontend framework. It is a handful of focused
helpers.
"""
from html import escape

import streamlit as st

from utils import theme


def _esc(value):
    """HTML-escape any value headed for inline markup.

    Protocol names, inventors and standards bodies are data; a stray '<' must
    not become markup.
    """
    return escape(str(value if value is not None else ""))


def _pal():
    """The active palette, resolved once per call."""
    return theme.current_palette()


def _tone_color(tone):
    """Map a semantic tone name (or a raw hex) to a colour string."""
    if str(tone).startswith("#"):
        return tone
    p = _pal()
    return {
        "ok": p["ok"], "warn": p["warn"], "danger": p["danger"],
        "signal": p["signal"], "accent": p["accent"],
        "neutral": p["text_muted"],
    }.get(str(tone).lower(), p["text_muted"])


def _tint(color, _p=None):
    """A very low-alpha version of `color` for chip/callout backgrounds.

    Uses an 8-digit hex (colour + alpha) so it composites correctly over either
    the dark or light surface without a per-theme hardcoded value.
    """
    c = str(color).lstrip("#")
    if len(c) == 6:
        c += "1f"  # ~12% alpha
    return f"#{c}"


# --------------------------------------------------------------- page_hero --
def page_hero(eyebrow, title, description="", meta=None, accent=None):
    """Compact page identity block: eyebrow, title, one-line description.

    Not a billboard - a tight, left-aligned header that establishes where you
    are and what the page is for, then gets out of the way.

    eyebrow:     small uppercase category line (e.g. "Reference")
    title:       page title (rendered as H2-equivalent, not a giant H1)
    description: one sentence of context
    meta:        optional small right-aligned meta text (e.g. a count)
    """
    p = _pal()
    accent = accent or p["accent"]
    meta_html = (
        f"<div style='font-size:0.8rem; color:{p['text_faint']}; "
        f"font-family:{theme.MONO_STACK}; white-space:nowrap;'>{_esc(meta)}</div>"
        if meta
        else ""
    )
    desc = (
        f"<div style='font-size:1rem; color:{p['text_muted']}; "
        f"margin-top:0.15rem; max-width:70ch; line-height:1.5;'>{_esc(description)}</div>"
        if description
        else ""
    )
    st.markdown(
        f"""
        <div style="padding:0.15rem 0 0.75rem 0; border-bottom:1px solid {p['border']};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem;">
                <div>
                    <div style="font-size:0.72rem; letter-spacing:0.18em; text-transform:uppercase;
                                color:{accent}; font-weight:600;">{_esc(eyebrow)}</div>
                    <div style="font-size:1.9rem; font-weight:700; color:{p['text']};
                                margin:0.1rem 0 0 0; line-height:1.15;">{_esc(title)}</div>
                    {desc}
                </div>
                {meta_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------- protocol_hero --
def protocol_hero(name, category="", year="", inventor="", difficulty="",
                  lifecycle="", accent=None):
    """The Encyclopedia signature header: a compact identity band for a protocol.

    Name on the left, structured metadata as chips below. This is meant to read
    like the title block of a datasheet, not a marketing hero.

    All values are optional; empty fields simply omit their chip so the band
    never shows an empty pill.
    """
    p = _pal()
    accent = accent or p["accent"]

    chips = []

    def _chip(label, tone="neutral"):
        if not label:
            return
        color = _tone_color(tone)
        chips.append(
            f"<span style=\"display:inline-block; font-family:{theme.MONO_STACK}; "
            f"font-size:0.74rem; font-weight:600; color:{color}; "
            f"background:{_tint(color)}; border:1px solid {color}; "
            f"border-radius:999px; padding:0.12rem 0.6rem; white-space:nowrap;\">"
            f"{_esc(label)}</span>"
        )

    _chip(category, "signal")
    if year:
        _chip(str(year), "neutral")
    if inventor:
        _chip(inventor, "neutral")
    if difficulty:
        _chip(difficulty, "accent")
    if lifecycle:
        _chip(str(lifecycle).capitalize(), "neutral")

    chips_html = (
        f"<div style=\"display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.45rem;\">"
        f"{''.join(chips)}</div>"
        if chips
        else ""
    )

    st.markdown(
        f"""
        <div style="padding:0.2rem 0 0.85rem 0; border-bottom:1px solid {p['border']};
                    border-left:3px solid {accent}; padding-left:0.7rem;">
            <div style="font-size:2.0rem; font-weight:700; color:{p['text']};
                        line-height:1.1; letter-spacing:-0.01em;">{_esc(name)}</div>
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------- section_header --
def section_header(title, index=None, description="", accent=None):
    """A compact technical section heading with an optional index and blurb.

    index:       small leading number/marker (e.g. "02") rendered in mono
    description: one line of context under the heading
    """
    p = _pal()
    accent = accent or p["accent"]
    idx_html = (
        f"<span style=\"font-family:{theme.MONO_STACK}; font-size:0.78rem; "
        f"color:{accent}; font-weight:700; margin-right:0.55rem;\">{_esc(index)}</span>"
        if index
        else ""
    )
    desc = (
        f"<div style=\"font-size:0.85rem; color:{p['text_muted']}; "
        f"margin-top:0.15rem; line-height:1.4;\">{_esc(description)}</div>"
        if description
        else ""
    )
    st.markdown(
        f"""
        <div style="margin:1.1rem 0 0.5rem 0; padding-bottom:0.3rem;
                    border-bottom:1px solid {p['border']};">
            <div style="font-size:1.25rem; font-weight:700; color:{p['text']}; line-height:1.2;">
                {idx_html}{_esc(title)}
            </div>
            {desc}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------- info_badge --
def info_badge(text, tone="neutral", icon=""):
    """A small semantic pill for category / difficulty / status / standard.

    Semantic tones render as a tinted outline chip (soft, never low-contrast).
    Always carries its own text, never colour alone.
    """
    text_html = _esc(text)
    prefix = f"{icon} " if icon else ""
    color = _tone_color(tone)
    st.markdown(
        f"<span style=\"display:inline-block; font-family:{theme.MONO_STACK}; "
        f"font-size:0.72rem; font-weight:600; color:{color}; "
        f"background:{_tint(color)}; border:1px solid {color}; "
        f"border-radius:999px; padding:0.12rem 0.6rem; white-space:nowrap;\">"
        f"{prefix}{text_html}</span>",
        unsafe_allow_html=True,
    )


# ----------------------------------------------------- engineering_metric --
def engineering_metric(label, value, unit="", tone="accent"):
    """A compact labelled value for a single engineering quantity.

    Intentionally NOT a big dashboard tile. Label is a small uppercase mono
    micro-label; value is mono and tabular so a column of them aligns.
    """
    p = _pal()
    color = _tone_color(tone)
    unit_html = (
        f"<span style=\"font-size:0.72rem; color:{p['text_muted']}; "
        f"margin-left:0.2rem; font-family:{theme.MONO_STACK};\">{_esc(unit)}</span>"
        if unit
        else ""
    )
    st.markdown(
        f"""
        <div style="padding:0.35rem 0; min-width:0;">
            <div style="font-size:0.68rem; letter-spacing:0.08em; text-transform:uppercase;
                        color:{p['text_faint']}; font-weight:600;">{_esc(label)}</div>
            <div style="font-family:{theme.MONO_STACK}; font-variant-numeric:tabular-nums;
                        font-size:1.12rem; font-weight:700; color:{color};
                        margin-top:0.1rem; line-height:1.2;">{_esc(value)}{unit_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# ---------------------------------------------------------------- callout --
_CALLOUT_TONES = {
    "info": ("accent", "ℹ", "Note"),
    "success": ("ok", "✓", "Success"),
    "warning": ("warn", "⚠", "Caution"),
    "danger": ("danger", "✕", "Warning"),
}


def callout(text, kind="info", label="", icon=""):
    """A focused note with a semantic accent border and tinted background.

    kind:  info | success | warning | danger
    text:  the message body
    label: optional short heading (defaults to the kind's label word)
    icon:  optional leading glyph (defaults to the kind's icon)

    The colour is never the only signal: the icon and the label word carry the
    meaning too, so it survives greyscale printing and colour-blind viewing.
    """
    p = _pal()
    tone_key, default_icon, default_label = _CALLOUT_TONES.get(
        str(kind).lower(), _CALLOUT_TONES["info"]
    )
    color = _tone_color(tone_key)
    icon = icon or default_icon
    label = label or default_label
    label_html = f"<span style='font-weight:700;'>{_esc(label)}</span>"
    st.markdown(
        f"""<div style="border-left:3px solid {color}; background:{_tint(color)};
                    border-radius:0 6px 6px 0; padding:0.6rem 0.85rem; margin:0.5rem 0;">
            <div style="font-size:0.95rem; color:{p['text']}; line-height:1.55;">
                <span style="margin-right:0.45rem;">{_esc(icon)}</span>{label_html}
                — {_esc(text)}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------- spec_table --
def spec_table(rows, min_width="230px", unit_color=None):
    """Compact engineering parameter/value grid (label left, mono value right).

    rows:      iterable of (parameter, value) pairs, e.g.
               [("VOH", "3.3 V"), ("VOL", "0.3 V"), ("Z0", "120 Ω"),
                ("Bit period", "1 µs")]
    min_width: minimum column width before the grid wraps. The grid uses
               auto-fit so it collapses to a single clean column on mobile
               without a media query.

    Values use the monospace stack with tabular numerals so a column of them
    aligns and scans like a datasheet. This is deliberately NOT a Streamlit
    dataframe - it is a tight typographic spec strip that belongs on the page,
    with hairline separators instead of a detached table chrome.
    """
    p = _pal()
    unit_color = unit_color or p["text_muted"]
    items = "".join(
        f"""<div style="display:flex; justify-content:space-between; gap:0.8rem;
                        padding:0.32rem 0; border-bottom:1px solid {p['border']};">
                <span style="color:{unit_color}; font-size:0.88rem;">{_esc(k)}</span>
                <span style="font-family:{theme.MONO_STACK}; font-variant-numeric:tabular-nums;
                             color:{p['text']}; font-weight:600; font-size:0.88rem;
                             white-space:nowrap; text-align:right;">{_esc(v)}</span>
            </div>"""
        for k, v in rows
    )
    st.markdown(
        f"<div style='display:grid; grid-template-columns:"
        f"repeat(auto-fit, minmax(min({min_width}, 100%), 1fr)); "
        f"column-gap:1.5rem; margin:0.35rem 0;'>{items}</div>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------- status_led --
def status_led(text, tone="ok", dot="●"):
    """A tiny semantic status marker: a small coloured dot plus its label.

    tone: semantic colour for the dot - ok / warn / danger / signal / accent /
          neutral (or a raw hex).
    text: the accompanying status word (never the dot alone).
    dot:  the glyph used as the LED (defaults to a filled circle).

    Intentionally subtle: a small dot, not a glowing cyberpunk LED.
    """
    p = _pal()
    color = _tone_color(tone)
    st.markdown(
        f"<span style='display:inline-flex; align-items:center; gap:0.4rem; "
        f"font-family:{theme.MONO_STACK}; font-size:0.8rem; color:{p['text_muted']};'>"
        f"<span style='color:{color}; font-size:0.7rem; line-height:1;'>{_esc(dot)}</span>"
        f"{_esc(text)}</span>",
        unsafe_allow_html=True,
    )

