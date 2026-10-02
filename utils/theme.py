# -*- coding: utf-8 -*-
"""Vectorform design tokens — the single source of truth for FrameWork's look.

Dark-first, because the app is an engineering instrument: an oscilloscope or
EDA tool is dark, and bright wireframes on a white page glare. A full light
theme is also provided for daylight and accessibility.

Three rules give the interface its "instrument" character:

1. **Tabular numerals everywhere.** Engineer's digits must not shift width as
   a value updates, or the eye cannot compare readings down a column.
2. **Monospace for every measured value.** Hex, binary, decimal, pin names and
   voltages are data, not prose, so they get a monospace face.
3. **Three weights only** (400/600/700). A fourth weight reads as noise.

`--fw-*` custom properties are emitted into the page once by
`branding.inject_css()`; every later phase styles against these names rather
than hardcoding hex values, so a theme change stays a one-file edit.
"""

# --------------------------------------------------------------- palettes ---
DARK = {
    "bg": "#0b1220",
    "bg_alt": "#0f172a",
    "surface": "#141c2e",
    "surface_alt": "#1e293b",
    "border": "#243044",
    "border_strong": "#334155",
    "text": "#e2e8f0",
    "text_muted": "#94a3b8",
    "text_faint": "#64748b",
    "accent": "#3b82f6",
    "accent_text": "#ffffff",
    "signal": "#22d3ee",
    "warn": "#f59e0b",
    "danger": "#ef4444",
    "ok": "#22c55e",
}

LIGHT = {
    "bg": "#f8fafc",
    "bg_alt": "#f1f5f9",
    "surface": "#ffffff",
    "surface_alt": "#f1f5f9",
    "border": "#e2e8f0",
    "border_strong": "#cbd5e1",
    "text": "#0f172a",
    "text_muted": "#475569",
    "text_faint": "#64748b",
    "accent": "#1965d8",
    "accent_text": "#ffffff",
    "signal": "#0891b2",
    "warn": "#b45309",
    "danger": "#dc2626",
    "ok": "#15803d",
}

FONT_STACK = (
    "'Inter var', Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', "
    "Roboto, 'Helvetica Neue', Arial, sans-serif"
)
MONO_STACK = (
    "'JetBrains Mono', 'SF Mono', 'Cascadia Code', Consolas, "
    "'Liberation Mono', Menlo, monospace"
)


def _vars(palette, prefix="fw"):
    return "\n".join(f"  --{prefix}-{name.replace('_', '-')}: {value};"
                     for name, value in palette.items())


def tokens_css():
    """Both palettes as CSS custom properties.

    Streamlit exposes the active theme on the <body> element, so light mode is
    selected by matching its background rather than by a class we would have to
    inject onto every widget.
    """
    return f""":root {{
{_vars(DARK)}
  --fw-font: {FONT_STACK};
  --fw-mono: {MONO_STACK};
  --fw-radius: 10px;
  --fw-radius-sm: 6px;
  --fw-gap: 0.75rem;
  --fw-measure: 78ch;
}}

/* Streamlit sets this attribute/background per theme; match on it. */
[data-testid="stAppViewContainer"] > .main,
.stApp {{
  font-family: var(--fw-font);
}}

html body,
body {{
  background-color: var(--fw-bg);
  color: var(--fw-text);
}}

/* Light theme: Streamlit gives the page a near-white background. */
body:has([data-testid="stAppViewContainer"] .stApp:not([data-testid="stAppViewContainer"])),
.stApp[data-theme="light"] {{
  --fw-bg: {LIGHT['bg']};
  --fw-surface: {LIGHT['surface']};
  --fw-border: {LIGHT['border']};
  --fw-text: {LIGHT['text']};
  --fw-text-muted: {LIGHT['text_muted']};
  --fw-accent: {LIGHT['accent']};
  --fw-signal: {LIGHT['signal']};
}}

@media (prefers-color-scheme: light) {{
  [data-testid="stAppViewContainer"] {{
    --fw-bg: {LIGHT['bg']};
    --fw-surface: {LIGHT['surface']};
    --fw-border: {LIGHT['border']};
    --fw-text: {LIGHT['text']};
    --fw-text-muted: {LIGHT['text_muted']};
    --fw-accent: {LIGHT['accent']};
    --fw-signal: {LIGHT['signal']};
  }}
}}"""


def current_palette(prefers_light=False):
    """Token dict for one theme, so non-CSS surfaces can match it."""
    return LIGHT if prefers_light else DARK


def hex_of(name, prefers_light=False):
    """Look up a token by name; used to colour matplotlib/Plotly output."""
    return current_palette(prefers_light)[name]
