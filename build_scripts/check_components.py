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
from unittest.mock import patch

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
    from utils.diagrams import diagram_palette

    fills = [fill for p in (theme_mod.DARK, theme_mod.LIGHT) for fill in diagram_palette(p)["series"]]
    for fill in fills + ["#ffffff", theme_mod.DARK["bg"]]:
        fg = theme_mod.contrast_text(fill)
        assert fg in ("#ffffff", "#0b1220"), f"{fill} -> {fg}"
        assert theme_mod.contrast_ratio(fg, fill) >= 4.5, f"low contrast: {fill} -> {fg}"


def test_rendered_component_values_are_escaped():
    """Exercise output, including icon/attribute values, rather than source only."""
    payload = '<img src=x onerror="alert(1)">\'&'
    calls = [
        (comp_mod.protocol_hero, (payload,), {"inventor": payload, "category": payload}),
        (comp_mod.engineering_metric, (payload, payload), {"unit": payload}),
        (comp_mod.spec_table, ([(payload, payload)],), {}),
        (comp_mod.callout, (payload,), {"label": payload, "icon": payload}),
        (comp_mod.info_badge, (payload,), {"icon": payload}),
        (comp_mod.status_led, (payload,), {"dot": payload}),
    ]
    for palette in (theme_mod.DARK, theme_mod.LIGHT):
        with patch.object(theme_mod, "current_palette", return_value=palette):
            for fn, args, kwargs in calls:
                with patch.object(comp_mod.st, "markdown") as output:
                    fn(*args, **kwargs)
                    markup = output.call_args.args[0]
                    assert payload not in markup, fn.__name__
                    assert "&lt;img" in markup, fn.__name__


def test_tinted_badges_meet_text_contrast():
    for palette in (theme_mod.DARK, theme_mod.LIGHT):
        with patch.object(theme_mod, "current_palette", return_value=palette):
            for tone in ("accent", "signal", "ok", "warn", "danger", "neutral"):
                color = comp_mod._tone_color(tone)
                for surface in (palette["bg"], palette["surface"]):
                    rgb = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
                    base = [int(surface[i:i + 2], 16) for i in (1, 3, 5)]
                    rendered = "#" + "".join(f"{round(v * 31 / 255 + b * 224 / 255):02x}" for v, b in zip(rgb, base))
                    assert theme_mod.contrast_ratio(color, rendered) >= 4.5, (tone, color, surface)


def test_every_diagram_canvas_follows_active_theme():
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_hex
    from utils import diagrams as diag

    protocols = [{"name": "CAN", "category": "Automotive", "speed": "1 Mbps", "id": "can"}]
    renderers = [
        lambda: diag.frame_diagram([{"name": "Start", "bits": 1}, {"name": "Data", "bits": 64}]),
        lambda: diag.topology_diagram("Bus", "CAN"),
        lambda: diag.pinout_diagram(["CAN_H", "CAN_L"], "CAN"),
        lambda: diag.category_bar_chart(protocols),
        lambda: diag.speed_comparison_chart(protocols),
        lambda: diag.waveform_diagram(diag.can_waveform()),
    ]
    for palette in (theme_mod.DARK, theme_mod.LIGHT):
        with patch.object(theme_mod, "current_palette", return_value=palette):
            for render in renderers:
                existing = plt.get_fignums()
                fig = render()
                assert plt.get_fignums() == existing, "renderer retains pyplot ownership"
                assert to_hex(fig.get_facecolor()) == palette["bg"]
                for ax in fig.axes:
                    assert to_hex(ax.get_facecolor()) == palette["bg"]
                    assert to_hex(ax.title.get_color()) == palette["text"]
                    for label in ax.get_xticklabels() + ax.get_yticklabels():
                        assert to_hex(label.get_color()) == palette["text_muted"]
                plt.close(fig)


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
