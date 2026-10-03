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

**These dictionaries are the design token source of truth.** They are mirrored by
the `[theme]` block in `.streamlit/config.toml`, which is what Streamlit actually
renders from - that file and these dicts must be changed together.
`build_scripts/visual_check.py` and `cross_browser.py` assert the rendered
colours match these values exactly, so the two cannot silently drift.

The module deliberately emits **no CSS**. An earlier version shipped
`tokens_css()` to inject a global stylesheet, but Streamlit 1.64's DOMPurify
strips both `<style>` and `<script>` on every `st.markdown`/`st.html` route, so
that stylesheet never reached the browser (verified: zero injected nodes, zero
custom properties). Do not reintroduce it - use native `[theme]` keys or
component-local inline styles instead.
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


