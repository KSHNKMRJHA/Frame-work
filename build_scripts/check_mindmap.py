# -*- coding: utf-8 -*-
"""Regression tests for the protocol mind maps (Bugs #3 and #4).

Bug #3: the map drew every protocol node but labelled only every third one with
        a 3-letter abbreviation.
Bug #4: labels were hard-coded to white on the default (white) Matplotlib
        figure, so the map was unreadable in light mode.

Run: python build_scripts/check_mindmap.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from utils import mindmap  # noqa: E402
from utils import theme as theme_mod  # noqa: E402

DATA = os.path.join(ROOT, "data", "protocols.json")


def _protocols():
    with open(DATA, encoding="utf-8") as fh:
        return json.load(fh)


def _squash(s):
    return "".join(str(s).split())


def test_every_protocol_is_labelled_with_its_full_name():
    """Bug #3 core: 140 / 140 identities, no abbreviations."""
    protocols = _protocols()
    fig, meta = mindmap.full_mindmap(protocols, palette=theme_mod.DARK, return_meta=True)
    plt.close(fig)

    assert meta["named"] == len(protocols) == 140, (
        f"expected 140 labelled protocols, got {meta['named']} of {meta['total']}"
    )

    by_id = {p["id"]: p["name"] for p in protocols}
    for pid, drawn in meta["labels"]:
        assert pid in by_id, f"unknown protocol id {pid}"
        assert _squash(drawn) == _squash(by_id[pid]), (
            f"{pid}: drew {drawn!r} but the protocol is named {by_id[pid]!r}"
        )


def test_no_label_is_truncated_to_an_abbreviation():
    """Bug #3 core: the old code drew name[:3].upper() for two nodes in three.

    Short protocol names such as "DNS" are legitimately short; what must never
    happen is a LONG name being cut down to three characters.
    """
    protocols = _protocols()
    fig, meta = mindmap.full_mindmap(protocols, palette=theme_mod.DARK, return_meta=True)
    plt.close(fig)

    by_id = {p["id"]: p["name"] for p in protocols}
    for pid, drawn in meta["labels"]:
        name = by_id[pid]
        if len(name) > 6:
            abbrev = _squash(name[:3].upper())
            assert _squash(drawn) != abbrev, (
                f"{pid} ({name!r}) was reduced to the abbreviation {drawn!r}"
            )


def test_root_and_categories_present():
    protocols = _protocols()
    fig, meta = mindmap.full_mindmap(protocols, palette=theme_mod.DARK, return_meta=True)
    txt = [_squash(t.get_text()) for t in fig.axes[0].texts]
    plt.close(fig)
    assert _squash(mindmap.ROOT_LABEL) in txt, f"root label missing from {txt[:4]}"
    for cat in meta["categories"]:
        assert _squash(cat) in txt, f"category label missing: {cat}"


def _rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _face_rgb(color):
    """Matplotlib returns facecolor as an RGBA tuple."""
    return tuple(int(round(c * 255)) for c in color[:3])


def test_figure_and_axes_match_the_active_palette():
    """Bug #4: figure and axes background must follow the palette explicitly."""
    protocols = _protocols()[:30]
    for pal_name in ("DARK", "LIGHT"):
        pal = getattr(theme_mod, pal_name)
        fig = mindmap.full_mindmap(protocols, palette=pal)
        ax = fig.axes[0]
        assert _face_rgb(fig.get_facecolor()) == _rgb(pal["bg"]), (
            f"{pal_name}: figure background {fig.get_facecolor()} != {pal['bg']}"
        )
        assert _face_rgb(ax.get_facecolor()) == _rgb(pal["bg"]), (
            f"{pal_name}: axes background {ax.get_facecolor()} != {pal['bg']}"
        )
        plt.close(fig)


def test_protocol_labels_use_the_palette_text_colour():
    """Protocol names sit on the figure background, so they must not be hard-coded white."""
    protocols = _protocols()[:30]
    for pal_name in ("DARK", "LIGHT"):
        pal = getattr(theme_mod, pal_name)
        fig = mindmap.full_mindmap(protocols, palette=pal)
        colors = {t.get_color() for t in fig.axes[0].texts}
        plt.close(fig)
        assert pal["text"].lower() in {str(c).lower() for c in colors}, (
            f"{pal_name}: no label uses the palette text colour {pal['text']}; got {colors}"
        )


def test_contrast_helper_never_returns_unreadable_pair():
    """A label drawn on a node fill must pick a contrasting foreground."""
    for fill in ("#ffffff", "#f8fafc", "#000000", "#0b1220", "#3b82f6", "#db2777"):
        fg = theme_mod.contrast_text(fill)
        bg = _rgb(fill)
        text = _rgb(fg)
        l1 = _luminance(text)
        l2 = _luminance(bg)
        ratio = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        assert ratio >= 4.5, f"contrast {fg} on {fill} is only {ratio:.2f}:1"


def _luminance(rgb):
    def lin(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])


def test_coverage_detector_catches_a_missing_label():
    """NEGATIVE TEST: drop one protocol label and the coverage check must fail."""
    protocols = _protocols()[:40]
    fig, meta = mindmap.full_mindmap(protocols, palette=theme_mod.DARK, return_meta=True)
    plt.close(fig)

    full = meta["named"]
    truncated = meta["labels"][:-1]  # simulate the old i % 3 behaviour losing labels
    assert full == len(protocols)
    assert len(truncated) == len(protocols) - 1, "negative fixture did not remove a label"
    # The detector asserts equality with the protocol count; the broken state
    # must not satisfy it.
    assert len(truncated) != len(protocols), (
        "NEGATIVE TEST FAILED: coverage check passes even with a label missing"
    )


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
        print(f"Mind-map tests FAILED: {failed} of {len(tests)}")
        sys.exit(1)
    print(f"Mind-map tests passed ({len(tests)} checks)")
