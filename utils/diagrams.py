# -*- coding: utf-8 -*-
"""
diagrams.py
Generic, data-driven diagram generators for FrameWork.
Every protocol is visualized using the SAME reusable functions below, driven
purely by the fields present in data/protocols.json (frame_fields, pins,
topology). This keeps the encyclopedia scalable to any number of protocols
without hand-drawing a picture for each one.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np

PALETTE = ["#2563eb", "#7c3aed", "#059669", "#dc2626", "#d97706", "#0891b2", "#db2777", "#65a30d", "#4f46e5", "#0d9488"]


def frame_diagram(fields, title="Frame / Packet Structure"):
    """Draw a horizontal stacked-segment diagram for a protocol's frame_fields.
    fields: list of {"name": str, "bits": int|str}
    """
    if not fields:
        return None
    # Assign proportional widths; textual bit counts (e.g. "0-64") get a default weight
    widths = []
    for f in fields:
        b = f.get("bits", 8)
        if isinstance(b, (int, float)):
            widths.append(max(float(b), 4))
        else:
            widths.append(24.0)
    total = sum(widths)
    widths = [w / total for w in widths]

    fig, ax = plt.subplots(figsize=(12, 2.6))
    x = 0.0
    for i, (f, w) in enumerate(zip(fields, widths)):
        color = PALETTE[i % len(PALETTE)]
        rect = FancyBboxPatch(
            (x, 0.15),
            w,
            0.7,
            boxstyle="round,pad=0.004,rounding_size=0.01",
            linewidth=1.4,
            edgecolor="white",
            facecolor=color,
        )
        ax.add_patch(rect)
        label = f["name"]
        bits = f.get("bits", "")
        txt = f"{label}\n({bits} bit)" if bits != "" else label
        fontsize = 10 if w > 0.08 else 8
        ax.text(
            x + w / 2,
            0.5,
            txt,
            ha="center",
            va="center",
            fontsize=fontsize,
            color="white",
            fontweight="bold",
            wrap=True,
        )
        x += w
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    fig.tight_layout()
    return fig


def _wrap(text, width=44):
    """Soft-wrap a long title so it never runs off the edge of the figure."""
    import textwrap

    return "\n".join(textwrap.wrap(str(text), width=width)) or str(text)


def topology_diagram(topology, protocol_name="", n_nodes=5):
    """Draw a simplified network topology diagram: bus / star / mesh / ring /
    point-to-point / client-server / switched fabric, inferred from the
    'topology' text field.

    Fitting matters more than prettiness here: topology strings run long
    ("Point-to-Point (broadcast, unidirectional)"), and short markers such as
    "Device A" are far wider than the circle they sit in. So the title is
    wrapped, long node labels are pushed below their marker instead of
    spilling out of it, and the axes keep an equal aspect ratio (otherwise
    every "circle" renders as a squashed ellipse) with a margin so no marker
    or label is clipped at the figure boundary.
    """
    t = (topology or "").lower()
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    ax.axis("off")
    ax.set_aspect("equal")
    ax.set_title(_wrap(f"Topology: {topology}"), fontsize=12, fontweight="bold", pad=12)

    def node(pos, label, color="#2563eb", size=0.35):
        circ = Circle(pos, size, facecolor=color, edgecolor="white", linewidth=2, zorder=3)
        ax.add_patch(circ)
        # Short labels sit inside the marker; anything longer would overflow the
        # circle and collide with its neighbours, so it is laid out underneath.
        if len(str(label)) <= 3:
            ax.text(
                pos[0], pos[1], label, ha="center", va="center", color="white", fontsize=8, fontweight="bold", zorder=4
            )
        else:
            ax.text(
                pos[0],
                pos[1] - size - 0.45,
                label,
                ha="center",
                va="top",
                color=color,
                fontsize=8.5,
                fontweight="bold",
                zorder=4,
            )

    if "mesh" in t:
        rng = np.random.default_rng(7)
        pts = rng.uniform(1, 9, size=(n_nodes, 2))
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                if rng.random() < 0.5:
                    ax.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color="#94a3b8", lw=1.2, zorder=1)
        for i, p in enumerate(pts):
            node(p, f"N{i + 1}", PALETTE[i % len(PALETTE)])

    elif "ring" in t:
        R = 3.5
        cx, cy = 5, 5
        pts = [
            (cx + R * np.cos(2 * np.pi * i / n_nodes), cy + R * np.sin(2 * np.pi * i / n_nodes)) for i in range(n_nodes)
        ]
        for i in range(n_nodes):
            j = (i + 1) % n_nodes
            ax.plot([pts[i][0], pts[j][0]], [pts[i][1], pts[j][1]], color="#94a3b8", lw=2, zorder=1)
        for i, p in enumerate(pts):
            node(p, f"N{i + 1}", PALETTE[i % len(PALETTE)])

    elif "star" in t or "client-server" in t or "point-to-multipoint" in t:
        cx, cy = 5, 5
        node((cx, cy), "HUB", "#dc2626", size=0.45)
        R = 3.3
        for i in range(n_nodes):
            ang = 2 * np.pi * i / n_nodes
            p = (cx + R * np.cos(ang), cy + R * np.sin(ang))
            ax.plot([cx, p[0]], [cy, p[1]], color="#94a3b8", lw=1.6, zorder=1)
            node(p, f"N{i + 1}", PALETTE[i % len(PALETTE)])

    elif "bus" in t or "multi-drop" in t:
        y = 5
        ax.plot([1, 9], [y, y], color="#334155", lw=4, zorder=1)
        for i in range(n_nodes):
            x = 1.5 + i * (7.0 / max(n_nodes - 1, 1))
            ax.plot([x, x], [y, y - 1.4], color="#94a3b8", lw=1.6, zorder=1)
            node((x, y - 1.8), f"N{i + 1}", PALETTE[i % len(PALETTE)])

    elif "switch" in t or "fabric" in t:
        cx, cy = 5, 6.5
        node((cx, cy), "SWITCH", "#7c3aed", size=0.5)
        R = 3.2
        for i in range(n_nodes):
            ang = np.pi + (np.pi) * i / max(n_nodes - 1, 1)
            p = (cx + R * np.cos(ang), cy - 2.6 + R * 0.5 * np.sin(ang))
            ax.plot([cx, p[0]], [cy, p[1]], color="#94a3b8", lw=1.6, zorder=1)
            node(p, f"D{i + 1}", PALETTE[i % len(PALETTE)])

    else:  # point-to-point default
        node((3, 5), "Device A", "#2563eb", size=0.55)
        node((7, 5), "Device B", "#059669", size=0.55)
        ax.annotate("", xy=(6.35, 5.15), xytext=(3.65, 5.15), arrowprops=dict(arrowstyle="->", color="#334155", lw=2))
        ax.annotate("", xy=(3.65, 4.85), xytext=(6.35, 4.85), arrowprops=dict(arrowstyle="->", color="#334155", lw=2))

    ax.set_xlim(-1.0, 11.0)
    ax.set_ylim(0.4, 9.6)
    fig.tight_layout()
    return fig


def pinout_diagram(pins, protocol_name=""):
    """Draw a simple 2-box wiring diagram (MCU <-> Device) labeling each pin."""
    if not pins:
        return None
    fig, ax = plt.subplots(figsize=(7, max(2.5, 0.6 * len(pins) + 1)))
    ax.axis("off")
    n = len(pins)
    h = max(2.0, 0.8 * n)
    box1 = FancyBboxPatch((0.5, 0.5), 2.2, h, boxstyle="round,pad=0.02", facecolor="#1e293b", edgecolor="white")
    box2 = FancyBboxPatch((7.3, 0.5), 2.2, h, boxstyle="round,pad=0.02", facecolor="#1e293b", edgecolor="white")
    ax.add_patch(box1)
    ax.add_patch(box2)
    ax.text(1.6, h + 0.85, "MCU / Master", ha="center", fontsize=11, fontweight="bold")
    ax.text(8.4, h + 0.85, f"{protocol_name or 'Peripheral'}", ha="center", fontsize=11, fontweight="bold")
    for i, pin in enumerate(pins):
        y = 0.5 + h - (i + 0.7) * (h / n)
        color = PALETTE[i % len(PALETTE)]
        ax.plot([2.7, 7.3], [y, y], color=color, lw=2.4, zorder=1)
        ax.text(5.0, y + 0.18, pin, ha="center", fontsize=9.5, color=color, fontweight="bold")
        ax.plot(2.7, y, marker="o", color=color, markersize=6, zorder=2)
        ax.plot(7.3, y, marker="o", color=color, markersize=6, zorder=2)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, h + 1.5)
    fig.tight_layout()
    return fig


def category_bar_chart(protocols):
    """Bar chart of protocol count per category."""
    from collections import Counter

    c = Counter(p["category"] for p in protocols)
    cats = sorted(c.keys())
    counts = [c[k] for k in cats]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.bar(cats, counts, color=[PALETTE[i % len(PALETTE)] for i in range(len(cats))])
    ax.set_ylabel("Number of Protocols")
    ax.set_title("Protocols Covered per Category", fontweight="bold")
    plt.xticks(rotation=35, ha="right")
    for b, v in zip(bars, counts):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.1, str(v), ha="center", fontsize=9, fontweight="bold")
    fig.tight_layout()
    return fig


def speed_comparison_chart(protocols, ids=None):
    """Log-scale speed comparison chart for a chosen subset (rough parsing of the
    'speed' text field to extract a representative max Mbps value)."""
    import re

    def parse_speed_mbps(s):
        if not s:
            return None
        s = s.lower()
        nums = re.findall(r"([\d.]+)\s*(gbps|mbps|kbps|bps)", s)
        if not nums:
            return None
        best = 0
        for val, unit in nums:
            val = float(val)
            if unit == "gbps":
                val *= 1000
            elif unit == "kbps":
                val /= 1000
            elif unit == "bps":
                val /= 1_000_000
            best = max(best, val)
        return best

    subset = [p for p in protocols if (ids is None or p["id"] in ids)]
    data = [(p["name"], parse_speed_mbps(p.get("speed", ""))) for p in subset]
    data = [(n, v) for n, v in data if v]
    data.sort(key=lambda x: x[1])
    if not data:
        return None
    names = [d[0] for d in data]
    vals = [d[1] for d in data]
    fig, ax = plt.subplots(figsize=(9, max(3, 0.4 * len(names))))
    ax.barh(names, vals, color=[PALETTE[i % len(PALETTE)] for i in range(len(names))])
    ax.set_xscale("log")
    ax.set_xlabel("Max Speed (Mbps, log scale)")
    ax.set_title("Speed Comparison", fontweight="bold")
    fig.tight_layout()
    return fig
