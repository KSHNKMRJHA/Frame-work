# -*- coding: utf-8 -*-
"""
mindmap.py
Builds interactive-feeling mind maps of the protocol universe using networkx
+ matplotlib (no external JS deps needed, works offline in Streamlit).
"""

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from utils import theme as theme_mod

CAT_COLORS = {
    "On-Board": "#2563eb",
    "Industrial": "#059669",
    "Automotive": "#dc2626",
    "Networking": "#7c3aed",
    "Wireless": "#d97706",
    "Cellular": "#0891b2",
    "Audio/Video": "#db2777",
    "USB": "#65a30d",
    "High-Speed/FPGA": "#4f46e5",
    "Sensor-Specific": "#0d9488",
    "Security": "#334155",
    "Aerospace": "#9333ea",
    "Debug & Trace": "#db2777",
}

ROOT_LABEL = "Embedded Communication Protocols"

# Radial geometry. The old layout used nx.spring_layout with a fixed seed and
# then labelled one node in three with a 3-letter abbreviation, so two thirds
# of the protocol set had no readable identity at all. A deterministic radial
# tree gives every protocol a stable slot that can carry its real name.
R_CAT = 1.0
R_PROTO = 1.42
R_PROTO_OUTER = 1.74


def _palette(palette=None):
    return palette or theme_mod.DARK


def _apply_axes_style(fig, ax, pal):
    """Never rely on Matplotlib defaults for figure/axes colour.

    The old code drew white label text on the default white figure, so the map
    was unreadable in light mode and washed out in dark mode. Everything below
    is explicit.
    """
    fig.patch.set_facecolor(pal["bg"])
    ax.set_facecolor(pal["bg"])


def _wrapped(text, width):
    import textwrap

    return "\n".join(textwrap.wrap(str(text), width=width)) or str(text)


def _radial_layout(protocols, root_label=ROOT_LABEL):
    """Deterministic root -> category -> protocol radial layout.

    Each category owns an angular sector sized in proportion to how many
    protocols it holds, and its protocols are spread evenly inside that sector.
    Categories with more than 12 protocols use a second outer ring so their
    labels do not crowd each other. No randomness, so the map is stable across
    reruns and screenshots are comparable.
    """
    cats = sorted({p["category"] for p in protocols})
    groups = {c: sorted((p for p in protocols if p["category"] == c), key=lambda p: p["name"])
              for c in cats}
    total = len(protocols) or 1

    pos = {"__root__": (0.0, 0.0)}
    angle = 0.0
    for cat in cats:
        plist = groups[cat]
        span = 2 * math.pi * len(plist) / total
        mid = angle + span / 2
        pos[("cat", cat)] = (R_CAT * math.cos(mid), R_CAT * math.sin(mid))

        n = len(plist)
        for i, p in enumerate(plist):
            a = angle + ((i + 0.5) / n) * span
            radius = R_PROTO if (n <= 12 or i % 2 == 0) else R_PROTO_OUTER
            pos[("proto", p["id"])] = (radius * math.cos(a), radius * math.sin(a))
        angle += span

    return pos, cats, groups


def full_mindmap(protocols, root_label=ROOT_LABEL, palette=None, return_meta=False):
    """Root -> category -> protocol radial map covering every protocol.

    Every protocol gets a node AND a readable label. The previous version drew
    all 140 nodes but labelled only every third one with a 3-letter
    abbreviation, which is exactly the reported "map does not show protocol
    names" bug.
    """
    pal = _palette(palette)
    pos, cats, groups = _radial_layout(protocols, root_label)

    fig, ax = plt.subplots(figsize=(19, 19), dpi=110)
    _apply_axes_style(fig, ax, pal)

    # Edges: root -> category, category -> protocol.
    for cat in cats:
        cx, cy = pos[("cat", cat)]
        ax.plot([0, cx], [0, cy], color=pal["border_strong"], lw=1.1, zorder=1)
        for p in groups[cat]:
            px, py = pos[("proto", p["id"])]
            ax.plot([cx, px], [cy, py], color=pal["border"], lw=0.6, alpha=0.75, zorder=1)

    # Category nodes, with label colour derived from the node fill so white text
    # never lands on a pale fill (the old hard-coded font_color="white").
    for cat in cats:
        cx, cy = pos[("cat", cat)]
        color = CAT_COLORS.get(cat, pal["text_faint"])
        ax.scatter([cx], [cy], s=1500, c=color, edgecolors="white", linewidths=1.4, zorder=2)
        ax.text(cx, cy, cat, ha="center", va="center", fontsize=7.4, fontweight="bold",
                color=theme_mod.contrast_text(color), zorder=3)

    # Root node: drawn last-ish with a bbox so the label is readable over both
    # the figure background and any edge that passes underneath.
    ax.scatter([0], [0], s=5200, c=pal["accent"], edgecolors="white", linewidths=2, zorder=3)
    ax.text(0, 0, _wrapped(root_label, 18), ha="center", va="center", fontsize=11,
            fontweight="bold", color=theme_mod.contrast_text(pal["accent"]), zorder=4)

    labelled = []
    for p in protocols:
        px, py = pos[("proto", p["id"])]
        ax.scatter([px], [py], s=70, c=pal["surface_alt"], edgecolors=pal["border_strong"],
                   linewidths=0.8, zorder=2)

    # Protocol names, placed outside their node along the radius and kept upright
    # (text on the left half is rotated 180 degrees so it never reads upside
    # down). Long names wrap onto two lines rather than colliding.
    for p in protocols:
        px, py = pos[("proto", p["id"])]
        angle = math.atan2(py, px)
        deg = math.degrees(angle)
        right = px >= 0
        rot = deg if right else deg + 180
        offset = 0.085
        if right:
            tx, ty, ha = px + offset, py, "left"
        else:
            tx, ty, ha = px - offset, py, "right"
        name = _wrapped(p["name"], 20)
        ax.text(tx, ty, name, rotation=rot, rotation_mode="anchor",
                ha=ha, va="center", fontsize=6.6, color=pal["text"], zorder=4)
        labelled.append((p["id"], name))

    ax.set_xlim(-1.95, 1.95)
    ax.set_ylim(-1.95, 1.95)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"{root_label.replace(chr(10), ' ')} — {len(protocols)} protocols across {len(cats)} categories",
        fontsize=14, fontweight="bold", color=pal["text"], pad=16,
    )
    fig.tight_layout()

    meta = {
        "labels": labelled,
        "named": len(labelled),
        "total": len(protocols),
        "categories": cats,
    }
    if return_meta:
        return fig, meta
    return fig


def category_mindmap(protocols, category, palette=None):
    """Zoomed map for one category, with every protocol fully named."""
    pal = _palette(palette)
    subset = sorted((p for p in protocols if p["category"] == category), key=lambda p: p["name"])
    n = len(subset)

    fig, ax = plt.subplots(figsize=(13, 10), dpi=110)
    _apply_axes_style(fig, ax, pal)

    cx, cy = 0.0, 0.0
    color = CAT_COLORS.get(category, pal["text_faint"])
    for i, p in enumerate(subset):
        a = 2 * math.pi * i / max(n, 1) - math.pi / 2
        radius = 1.0 + 0.30 * (i % 2)
        px, py = radius * math.cos(a), radius * math.sin(a)
        ax.plot([cx, px], [cy, py], color=pal["border"], lw=0.9, alpha=0.8, zorder=1)
        ax.scatter([px], [py], s=180, c=pal["surface_alt"], edgecolors=pal["border_strong"],
                   linewidths=0.9, zorder=2)

        deg = math.degrees(a)
        right = px >= 0
        rot = deg if right else deg + 180
        off = 0.10
        tx, ty, ha = (px + off, py, "left") if right else (px - off, py, "right")
        ax.text(tx, ty, _wrapped(p["name"], 20), rotation=rot, rotation_mode="anchor",
                ha=ha, va="center", fontsize=8.0, color=pal["text"], zorder=4)

    ax.scatter([0], [0], s=4200, c=color, edgecolors="white", linewidths=2, zorder=3)
    ax.text(0, 0, _wrapped(category, 14), ha="center", va="center", fontsize=11,
            fontweight="bold", color=theme_mod.contrast_text(color), zorder=4)

    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{category} — {n} protocols", fontsize=14, fontweight="bold",
                 color=pal["text"], pad=14)
    fig.tight_layout()
    return fig
