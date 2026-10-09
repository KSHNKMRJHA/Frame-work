# -*- coding: utf-8 -*-
"""Regression tests for SignalBench component primitives (utils/components.py).

The primitives are the highest-leverage theming surface: one hardcoded hex
here ships to every page that uses them. These tests pin the three rules:

1. Palette-following - every primitive resolves colours through
   theme.current_palette(), never a hardcoded dark hex.
2. Contrast - any coloured fill picks its label through
   theme.contrast_text() so text is never white-on-white.
3. No injection surface - no <style>/<script> (Streamlit 1.64 DOMPurify
   strips both) and every data value is HTML-escaped.

Run: python build_scripts/check_components.py
"""

import inspect
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils import components as comp_mod  # noqa: E402
from utils import theme as theme_mod  # noqa: E402

PRIMITIVES = (
    "page_hero",
    "protocol_hero",
    "section_header",
    "info_badge",
    "engineering_metric",
    "callout",
    "spec_table",
    "status_led",
)

DARK_ONLY_HEX = ("#0b1220", "#141c2e", "#1e293b", "#e2e8f0", "#22d3ee")


def _source(name):
    return inspect.getsource(getattr(comp_mod, name))


def test_all_primitives_exist_and_are_callable():
    for name in PRIMITIVES:
        assert callable(getattr(comp_mod, name, None)), f"missing primitive: {name}"


def test_primitives_follow_active_palette():
    """Every primitive must resolve colours from the active theme."""
    src = inspect.getsource(comp_mod)
    assert "theme.current_palette()" in src, "components.py does not follow the active theme"
    assert "theme.DARK" not in src, "components.py hardcodes the dark palette"
    for name in PRIMITIVES:
        body = _source(name)
        # Direct palette read, or via _tone_color() which itself reads _pal().
        assert "_pal()" in body or "current_palette()" in body or "_tone_color(" in body, (
            f"{name}() does not resolve the active palette"
        )


def test_no_hardcoded_dark_hex_in_components():
    for name in PRIMITIVES:
        body = _source(name)
        for hx in DARK_ONLY_HEX:
            assert hx.lower() not in body.lower(), (
                f"{name}() hardcodes dark-only {hx}"
            )


def test_contrast_text_used_for_colored_fills():
    """Solid fills must pick labels via contrast_text().

    Component chips/callouts use translucent _tint() backgrounds with
    tone-coloured text (readable on both themes by construction). Solid
    fills - frame fields in diagrams.py - must use contrast_text(); this
    test pins that the helper is wired and sane on the frame palette.
    """
    src = inspect.getsource(comp_mod)
    assert "_tint(" in src, "tinted-background helper missing"
    import utils.diagrams as diag_mod

    dsrc = inspect.getsource(diag_mod)
    assert "contrast_text(" in dsrc, "diagrams.py draws solid fills without contrast_text()"


def test_no_style_or_script_injection():
    src = inspect.getsource(comp_mod)
    code = re.sub(r'""".*?"""', "", src, flags=re.S)
    assert "<style" not in code and "<script" not in code, (
        "components.py injects <style>/<script> (stripped by DOMPurify)"
    )


def test_data_values_are_escaped():
    """Protocol names/inventors are data; a stray '<' must not become markup."""
    src = inspect.getsource(comp_mod)
    assert "_esc(" in src, "no HTML-escaping helper in use"
    for name in ("page_hero", "protocol_hero", "info_badge", "spec_table"):
        assert "_esc(" in _source(name), f"{name}() renders data without escaping"


def test_contrast_helper_sane_on_frame_palette():
    from utils.diagrams import FRAME_PALETTE

    for fill in list(FRAME_PALETTE) + ["#ffffff", theme_mod.DARK["bg"]]:
        fg = theme_mod.contrast_text(fill)
        assert fg in ("#ffffff", "#0b1220"), f"{fill} -> {fg}"


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ok  {name}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {name}: {type(exc).__name__}: {exc}")

    print()
    if failed:
        print(f"Component tests FAILED: {failed} of {len(tests)}")
        sys.exit(1)
    print(f"Component tests passed ({len(tests)} checks)")
