# -*- coding: utf-8 -*-
"""Regression tests for theme handling (Bug #6).

The Appearance tab used to rewrite `.streamlit/config.toml` from inside a
visitor's session. On a multi-user deployment one visitor's click changed the
theme for everybody, and the control could not do what it claimed anyway.

Run: python build_scripts/check_theme.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils import theme as theme_mod  # noqa: E402

CONFIG = os.path.join(ROOT, ".streamlit", "config.toml")
SETTINGS = os.path.join(ROOT, "pages", "11_⚙️_Settings_Profile.py")


def _config_text():
    with open(CONFIG, encoding="utf-8") as fh:
        return fh.read()


def test_settings_page_never_writes_project_config():
    """The core Bug #6 regression: no runtime mutation of tracked config."""
    with open(SETTINGS, encoding="utf-8") as fh:
        src = fh.read()
    assert "config.toml" not in re.sub(r"#.*", "", src).replace(
        "`.streamlit/config.toml`", ""
    ), "the Appearance tab still writes .streamlit/config.toml at runtime"
    assert 'open(".streamlit/config.toml", "w")' not in src
    assert "primaryColor" not in re.sub(r"#.*", "", src)


def test_config_defines_both_palettes_and_pins_nothing():
    text = _config_text()
    assert "[theme.light]" in text, "no light palette"
    assert "[theme.dark]" in text, "no dark palette"
    # `base` would override the user's own Light/Dark/System choice.
    assert not re.search(r"^base\s*=", text, flags=re.M), (
        "`base` is pinned, which defeats Streamlit's own theme selection"
    )


def test_helper_returns_python_values_only():
    """No CSS, no JS, no private API - just a dict of colours."""
    import inspect

    for name in ("active_theme_type", "current_palette", "is_dark", "contrast_text"):
        assert callable(getattr(theme_mod, name)), name
    pal = theme_mod.current_palette()
    assert isinstance(pal, dict)
    assert all(isinstance(v, str) and v.startswith("#") for v in pal.values()), pal

    # Scan only the helper functions, not the module docstring - the docstring
    # mentions st.markdown precisely to explain why that approach is banned.
    body = "\n".join(
        inspect.getsource(getattr(theme_mod, name))
        for name in ("active_theme_type", "current_palette", "is_dark", "contrast_text")
    )
    code = re.sub(r'""".*?"""', "", body, flags=re.S)
    for banned in ("st.markdown", "unsafe_allow_html", "<style", "<script",
                   "components.html", "st.context._", "st._"):
        assert banned not in code, f"theme helper must not emit markup: found {banned}"
    assert "st.context.theme" in code, "helper must read the documented theme API"


def inspect_source(mod):
    import inspect

    return inspect.getsource(mod)


def test_no_hardcoded_dark_palette_in_visible_components():
    """Custom components must follow the active theme, not assume dark."""
    from utils import branding

    src = inspect_source(branding)
    assert "theme.DARK" not in src, "branding.py still hardcodes the dark palette"
    assert "theme.current_palette()" in src, "branding.py does not follow the active theme"


def test_contrast_helper_returns_readable_text():
    for fill in ("#ffffff", "#0b1220", "#3b82f6", "#db2777"):
        fg = theme_mod.contrast_text(fill)
        assert fg in ("#ffffff", "#0b1220"), fg


def test_both_palettes_are_fully_populated():
    for name in ("DARK", "LIGHT"):
        pal = getattr(theme_mod, name)
        for key in ("bg", "bg_alt", "surface", "surface_alt", "border",
                    "text", "text_muted", "accent", "signal"):
            assert key in pal, f"{name} is missing {key}"
            assert pal[key].startswith("#"), f"{name}.{key} = {pal[key]}"


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
        print(f"Theme tests FAILED: {failed} of {len(tests)}")
        sys.exit(1)
    print(f"Theme tests passed ({len(tests)} checks)")
