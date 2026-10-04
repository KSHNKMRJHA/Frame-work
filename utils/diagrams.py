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


# Visual geometry constants.
#
# This diagram is explanatory, not an oscilloscope time scale. A literal
# proportional layout is actively harmful: DMX512 has a 4096-bit slot field, so
# a proportional bar leaves "Break" and "Start Code" about 1% of the width each
# and their labels collide. The bit counts are still printed exactly, so the
# engineering data is never lost - only the geometry is bounded.
FIG_WIDTH = 12.0
# Room for a single legend digit inside a box (about 0.14 inch of canvas).
MIN_BOX_FRAC = 0.012
# No single field may take more than this share of a row.
MAX_BOX_FRAC = 0.55
# Width per character used to decide whether a full name fits in a box.
CHAR_INCH = 0.085


def _bit_weight(bits):
    """Visual weight for a field.

    sqrt() compresses the dynamic range: 1 : 8 : 4096 would be 1% : 0.2% :
    98.6% proportionally, but 1 : 2.8 : 64 here - the big field still dominates
    (as it should) while its neighbours stay legible. Textual widths like
    "0-1500" describe a variable-length payload, which is given a typical
    64-bit weight; the exact text is preserved in the legend.
    """
    import math

    if isinstance(bits, (int, float)):
        return math.sqrt(max(float(bits), 1.0))
    return math.sqrt(64.0)


def _balanced_fracs(weights, min_frac=MIN_BOX_FRAC, max_frac=MAX_BOX_FRAC):
    """Normalise weights into fractions that respect a readable width band.

    Water-filling: values below the floor are raised to it and values above the
    cap are lowered to it, and the difference is redistributed across the
    fields that still have headroom. The result always sums to 1, so a row can
    never overflow the axes - the failure mode of a naive max(width, minimum).
    """
    n = len(weights)
    if n == 0:
        return []
    if n == 1:
        return [1.0]

    total = sum(weights) or 1.0
    fr = [w / total for w in weights]

    for _ in range(64):
        low = [i for i in range(n) if fr[i] < min_frac - 1e-12]
        high = [i for i in range(n) if fr[i] > max_frac + 1e-12]
        if not low and not high:
            break
        moved = False
        if low:
            deficit = sum(min_frac - fr[i] for i in low)
            donors = [i for i in range(n) if fr[i] > min_frac]
            pool = sum(fr[i] - min_frac for i in donors)
            if pool > 1e-12:
                for i in low:
                    fr[i] = min_frac
                for i in donors:
                    fr[i] -= deficit * ((fr[i] - min_frac) / pool)
                moved = True
        if high:
            excess = sum(fr[i] - max_frac for i in high)
            takers = [i for i in range(n) if fr[i] < max_frac]
            pool = sum(max_frac - fr[i] for i in takers)
            if pool > 1e-12:
                for i in high:
                    fr[i] = max_frac
                for i in takers:
                    fr[i] += excess * ((max_frac - fr[i]) / pool)
                moved = True
        if not moved:
            break

    s = sum(fr) or 1.0
    return [f / s for f in fr]


def _fmt_bits(bits):
    if bits in ("", None):
        return ""
    return f"{bits} bit" if isinstance(bits, (int, float)) else f"{bits} bit"


def _wrap_name(text, width):
    """Wrap a field name to the characters that actually fit inside its box."""
    import textwrap

    return "\n".join(textwrap.wrap(text, width)) or text


def _layout_rows(fields, wrap_over=6):
    """Split fields into balanced rows so a complex frame is not one thin strip.

    Long frames (CAN XL, USB, Ethernet) previously squeezed every field into a
    single 12-inch strip, which is what made labels collide. Frames with more
    than ``wrap_over`` fields are split into two balanced rows, keeping each box
    wide enough for a readable label. Fewer fields stay on one row, where a
    narrow box simply falls back to a legend index - splitting those would add
    visual noise for nothing. Field order is never changed.
    """
    import math

    n = len(fields)
    if n <= wrap_over:
        return [list(range(n))]
    per_row = math.ceil(n / 2)
    return [list(range(i, min(i + per_row, n))) for i in range(0, n, per_row)]


def _draw_row(ax, indices, fields, row_total, y, legend_ids):
    """Draw one horizontal strip of fields. Returns the text artists created.

    Geometry comes from ``_balanced_fracs`` rather than raw bit counts, so a
    4096-bit payload cannot crush its neighbours into unreadable slivers.
    """
    weights = [_bit_weight(fields[i].get("bits", 8)) for i in indices]
    fracs = _balanced_fracs(weights)

    artists = []
    x = 0.0
    for pos, idx in enumerate(indices):
        f = fields[idx]
        w = fracs[pos]
        color = PALETTE[idx % len(PALETTE)]
        rect = FancyBboxPatch(
            (x, y),
            w,
            0.62,
            boxstyle="round,pad=0.003,rounding_size=0.008",
            linewidth=1.2,
            edgecolor="white",
            facecolor=color,
        )
        ax.add_patch(rect)

        name = f["name"]
        # Characters that genuinely fit inside this box.
        fits = int((w * (FIG_WIDTH - 0.6)) / CHAR_INCH)
        numbered = fits < 9

        if numbered:
            label = str(legend_ids[idx])
            fontsize = 8.5
        else:
            label = _wrap_name(name, max(9, min(fits, 22)))
            fontsize = 9.5 if w > 0.12 else 8.5

        artists.append(
            ax.text(
                x + w / 2,
                y + 0.31,
                label,
                ha="center",
                va="center",
                fontsize=fontsize,
                color="white",
                fontweight="bold",
            )
        )
        x += w
    return artists


def frame_diagram(fields, title="Frame / Packet Structure", return_meta=False):
    """Draw an adaptive stacked-segment diagram for a protocol's frame_fields.

    fields: list of {"name": str, "bits": int|str}

    The old version put every field on one 12x2.6 inch strip. Frames with many
    fields, very narrow fields (1-bit SOF/ACK), or long names overlapped badly.
    This scales the canvas and the number of rows to the frame:

      * few wide fields      -> one row, names inside, as before
      * many fields          -> wrapped across rows, order preserved
      * fields too narrow    -> numbered inside, full text in a legend below

    ``return_meta`` additionally returns {"rows": n, "legend": [...]} for tests.
    """
    if not fields:
        return None

    weights = [_bit_weight(f.get("bits", 8)) for f in fields]
    rows = _layout_rows(fields)

    # Number shown inside a box when the name does not fit; the legend below
    # carries the full text and the exact bit count either way.
    legend_ids = {i: i + 1 for i in range(len(fields))}

    legend = [
        (i, f["name"], _fmt_bits(f.get("bits", "")))
        for i, f in enumerate(fields, start=1)
    ]

    height = 1.35 * len(rows) + 0.75
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, height))

    artists = []
    for r, indices in enumerate(rows):
        y = 0.5 + 0.95 * (len(rows) - 1 - r)
        row_total = sum(weights[i] for i in indices) or 1.0
        artists.extend(_draw_row(ax, indices, fields, row_total, y, legend_ids))
        if r < len(rows) - 1:
            ax.annotate(
                "",
                xy=(1.0, y - 0.16),
                xytext=(0.93, y - 0.16),
                arrowprops={"arrowstyle": "->", "color": "#94a3b8", "lw": 1.2},
            )

    # A field whose name did not fit inside its box is listed here in full, so
    # no information is lost by showing a number in the diagram.
    legend_lines = [
        f"{n} — {name} — {bits}" if bits else f"{n} — {name}"
        for n, name, bits in legend
    ]
    if len(legend_lines) > 8:
        col = (len(legend_lines) + 1) // 2
        left = legend_lines[:col]
        right = legend_lines[col:]
        left_txt = "\n".join(left)
        right_txt = "\n".join(right)
        ax.text(0.0, -0.30, left_txt, ha="left", va="top", fontsize=7.5, color="#334155",
                transform=ax.transAxes)
        ax.text(0.5, -0.30, right_txt, ha="left", va="top", fontsize=7.5, color="#334155",
                transform=ax.transAxes)
    else:
        ax.text(0.0, -0.30, "\n".join(legend_lines), ha="left", va="top", fontsize=8,
                color="#334155", transform=ax.transAxes)

    ax.set_xlim(-0.005, 1.005)
    ax.set_ylim(0, 0.5 + 0.95 * len(rows) + 0.08)
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()

    if return_meta:
        return fig, {"rows": len(rows), "legend": legend, "artists": artists}
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


# ------------------------------------------------------------- WAVEFORMS ---
def waveform_diagram(model, figsize=None):
    """Draw a multi-trace digital waveform (logic-analyzer style).

    model = {
      "title": str,
      "traces": [{"name": str, "segments": [(level, width), ...],
                  "markers": [x, ...] (optional sample points)}],
      "fields": [(x0, x1, label), ...]   # shaded bands above the traces
      "xticks": [(pos, label), ...]      # optional tick labels
      "time_label": str                  # x axis description
    }
    Levels are plain numbers: 0/1 for logic traces, volts for differential
    pairs (each trace auto-scales its own range, so 2.5 V and 3.5 V both work).
    """
    traces = model.get("traces", [])
    if not traces:
        return None
    n = len(traces)
    fig, ax = plt.subplots(figsize=figsize or (12, 1.15 * n + 1.6))

    total = 0.0
    for i, tr in enumerate(traces):
        segs = tr.get("segments", [])
        if not segs:
            continue
        widths = [w for _, w in segs]
        levels = [lv for lv, _ in segs]
        xs = [0.0]
        for w in widths:
            xs.append(xs[-1] + w)
        total = max(total, xs[-1])
        vmin, vmax = min(levels), max(levels)
        span = (vmax - vmin) or 1.0
        base = n - 1 - i
        # Map the trace's own level range into a fixed drawing band.
        y = [base + 0.18 + 0.72 * (lv - vmin) / span for lv in levels] + [
            base + 0.18 + 0.72 * (levels[-1] - vmin) / span
        ]
        color = PALETTE[i % len(PALETTE)]
        ax.step(xs, y, where="post", color=color, linewidth=2.0, zorder=3)
        ax.text(
            -0.01,
            base + 0.5,
            tr["name"],
            ha="right",
            va="center",
            fontsize=9.5,
            fontweight="bold",
            color=color,
            transform=ax.get_yaxis_transform(),
        )
        # Annotate the actual level values at the top/bottom of the band.
        if tr.get("show_levels", True):
            ax.text(xs[-1] + 0.1, base + 0.9, f"{vmax:g}", ha="left", va="center", fontsize=7.5, color="#64748b")
            ax.text(xs[-1] + 0.1, base + 0.12, f"{vmin:g}", ha="left", va="center", fontsize=7.5, color="#64748b")
        for m in tr.get("markers", []):
            idx = next((k for k in range(len(xs) - 1) if xs[k] <= m <= xs[k + 1]), 0)
            lv = levels[min(idx, len(levels) - 1)]
            my = base + 0.18 + 0.72 * (lv - vmin) / span
            ax.plot([m], [my], marker="o", color="#0f172a", markersize=5, zorder=5)

    # Shaded field bands (START, ADDR, ACK, ...) labelled above the top trace.
    for x0, x1, label in model.get("fields", []):
        ax.axvspan(x0, x1, ymin=0.0, ymax=1.0, color="#94a3b8", alpha=0.07, zorder=0)
        ax.text(
            (x0 + x1) / 2, n + 0.12, label, ha="center", va="bottom", fontsize=8, color="#475569", fontweight="bold"
        )

    ticks = model.get("xticks")
    if ticks:
        ax.set_xticks([p for p, _ in ticks])
        ax.set_xticklabels([lb for _, lb in ticks], fontsize=8)
    ax.set_xlim(-0.6, total + 1.1)
    ax.set_ylim(-0.25, n + 0.7)
    ax.set_yticks([])
    ax.set_xlabel(model.get("time_label", "time (bit periods)"), fontsize=9)
    ax.set_title(model.get("title", "Signal Waveform"), fontsize=12, fontweight="bold", pad=26)
    ax.grid(axis="x", linestyle=":", alpha=0.35)
    fig.tight_layout()
    return fig


def uart_waveform(byte_value=0x55, data_bits=8, parity="none", stop_bits=1, baud=115200):
    """UART TX frame: idle high, start low, data LSB-first, optional parity, stop high.

    Markers are placed at the receiver's mid-bit sample points — where the UART
    actually latches each data bit.
    """
    byte_value &= (1 << data_bits) - 1
    bits = [(byte_value >> i) & 1 for i in range(data_bits)]
    segs = [(1, 0.5), (0, 1.0)] + [(b, 1.0) for b in bits]
    fields = [(0.0, 0.5, "idle"), (0.5, 1.5, "START")]
    x = 1.5
    markers = []
    for i, b in enumerate(bits):
        fields.append((x, x + 1, f"D{i}={b}"))
        markers.append(x + 0.5)
        x += 1
    if parity != "none":
        p = sum(bits) % 2 if parity == "even" else 1 - (sum(bits) % 2)
        segs.append((p, 1.0))
        fields.append((x, x + 1, f"PAR={p}"))
        x += 1
    for _ in range(stop_bits):
        segs.append((1, 1.0))
        fields.append((x, x + 1, "STOP"))
        x += 1
    segs.append((1, 0.5))
    frame_bits = 1 + data_bits + (1 if parity != "none" else 0) + stop_bits
    bit_us = 1e6 / baud
    fmt = f"{data_bits}{'E' if parity == 'even' else 'O' if parity == 'odd' else 'N'}{stop_bits}"
    return {
        "title": f"UART frame — 0x{byte_value:02X} ({fmt} @ {baud} baud)",
        "traces": [{"name": "TX", "segments": segs, "markers": markers}],
        "fields": fields,
        "xticks": [(1.5 + i, f"D{i}") for i in range(data_bits)],
        "time_label": f"bit periods (1 bit = {bit_us:.1f} µs @ {baud} baud)",
        "stats": {
            "frame_bits": frame_bits + 0.5,  # includes the half-bit of idle shown
            "frame_time_us": frame_bits * bit_us,
            "payload_time_us": data_bits * bit_us,
            "efficiency_pct": 100.0 * data_bits / frame_bits,
        },
    }


def i2c_waveform(address=0x50, write=True, data_byte=0xA5):
    """I2C frame: START, 7-bit address + R/W, ACK, one data byte, ACK, STOP.

    SDA/SCL are open-drain: the line only falls actively and rises through the
    pull-up — which is exactly what the rise-time calculator sizes.
    """
    addr = address & 0x7F
    addr_bits = [(addr >> i) & 1 for i in range(6, -1, -1)]
    data_bits = [(data_byte >> i) & 1 for i in range(7, -1, -1)]
    rw = 0 if write else 1

    # Cell layout (width 1 per bit): START cell, 7 addr cells, R/W, ACK,
    # 8 data cells, ACK, STOP cell — SDA level held across each cell.
    sda = [(1.0, 0.5), (0.0, 0.5)]
    fields = [(0.0, 1.0, "START")]
    x = 1.0
    for b in addr_bits:
        sda.append((float(b), 1.0))
        x += 1
    sda.append((float(rw), 1.0))
    fields.append((1.0, 9.0, f"ADDRESS 0x{addr:02X}"))
    x += 1
    sda.append((0.0, 1.0))  # receiver ACK
    fields.append((x, x + 1, "ACK"))
    x += 1
    data_start = x
    for b in data_bits:
        sda.append((float(b), 1.0))
        x += 1
    fields.append((data_start, x, f"DATA 0x{data_byte:02X}"))
    sda.append((0.0, 1.0))  # receiver ACK
    fields.append((x, x + 1, "ACK"))
    x += 1
    sda.append((1.0, 0.5))
    fields.append((x, x + 0.5, "STOP"))

    # SCL: high during idle/START/STOP definition, clock pulses over the bits.
    scl = [(1.0, 1.0)]
    n_clocks = 9 + 9  # addr+rw+ack, data+ack
    for _ in range(n_clocks):
        scl += [(0.0, 0.5), (1.0, 0.5)]
    scl.append((1.0, 0.5))
    return {
        "title": f"I²C {'WRITE' if write else 'READ'} — addr 0x{addr:02X}, data 0x{data_byte:02X}",
        "traces": [
            {"name": "SCL", "segments": scl},
            {"name": "SDA", "segments": sda},
        ],
        "fields": fields,
        "time_label": "bit periods (SCL low = data valid window; SDA may only change while SCL is low)",
        "stats": {"address": addr, "rw": "write" if write else "read", "bytes": 1},
    }


def spi_waveform(mosi_byte=0x5A, miso_byte=0xA5, cpol=0, cpha=0):
    """SPI burst: CS low, 8 SCLK pulses, MOSI/MISO MSB-first.

    Sample markers sit on the sampling edge (leading when CPHA=0, trailing
    when CPHA=1), matching how real controllers latch the line.
    """
    miso = [(miso_byte >> i) & 1 for i in range(7, -1, -1)]
    mosi = [(mosi_byte >> i) & 1 for i in range(7, -1, -1)]
    idle = float(cpol)
    clk = [(idle, 0.5)]
    segs_mosi = [(float(mosi[0]), 1.0)]
    segs_miso = [(float(miso[0]), 1.0)]
    segs_cs = [(1.0, 0.5)]
    markers = []
    x = 0.5
    for i in range(8):
        active = 1.0 - idle
        clk += [(active, 1.0), (idle, 1.0)]
        segs_mosi.append((float(mosi[i]), 2.0))
        segs_miso.append((float(miso[i]), 2.0))
        segs_cs.append((0.0, 2.0))
        markers.append(x + (0.5 if (cpol ^ cpha) == 0 else 1.5))
        x += 2.0
    clk.append((idle, 0.5))
    segs_mosi.append((1.0, 0.5))
    segs_miso.append((1.0, 0.5))
    segs_cs.append((1.0, 0.5))
    return {
        "title": f"SPI burst — MOSI 0x{mosi_byte:02X}, MISO 0x{miso_byte:02X} (CPOL={cpol}, CPHA={cpha})",
        "traces": [
            {"name": "CS", "segments": segs_cs},
            {"name": "SCLK", "segments": clk},
            {"name": "MOSI", "segments": segs_mosi},
            {"name": "MISO", "segments": segs_miso, "markers": markers},
        ],
        "fields": [(0.5, 16.5, "8 clocks — MSB first")],
        "time_label": "half SCLK periods (markers = sampling edge)",
        "stats": {"mosi": mosi_byte, "miso": miso_byte, "bits": 8},
    }


def can_waveform(frame_id=0x123, data_byte=0x42, extended=False):
    """CAN 2.0 base/extended data frame on the differential pair.

    CAN_H/CAN_L show recessive (both ~2.5 V) vs dominant (3.5 V / 1.5 V);
    the CRC sequence is drawn as a representative bit pattern.
    """
    id_bits = 29 if extended else 11
    value = frame_id & ((1 << id_bits) - 1)
    bits = [0]  # SOF (dominant)
    bits += [(value >> i) & 1 for i in range(id_bits - 1, -1, -1)]
    bits += [0, 0]  # RTR / IDE control bits (dominant)
    bits += [(data_byte >> i) & 1 for i in range(7, -1, -1)]
    bits += [1] * 15  # CRC sequence (illustrative)
    bits += [1, 0, 1]  # CRC delim, ACK slot, ACK delim
    bits += [1] * 7  # EOF

    segs_h, segs_l = [], []
    for b in bits:
        dominant = b == 0
        segs_h.append((3.5 if dominant else 2.5, 1.0))
        segs_l.append((1.5 if dominant else 2.5, 1.0))

    x = 0.0
    fields = [(0.0, 1.0, "SOF")]
    x = 1.0
    fields.append((x, x + id_bits, f"ID 0x{value:X}"))
    x += id_bits
    fields.append((x, x + 2, "CTRL"))
    x += 2
    fields.append((x, x + 8, "DATA"))
    x += 8
    fields.append((x, x + 15, "CRC"))
    x += 15
    fields.append((x, x + 3, "ACK"))
    x += 3
    fields.append((x, x + 7, "EOF"))
    return {
        "title": f"CAN frame — ID 0x{value:X}, data 0x{data_byte:02X}" + (" (29-bit)" if extended else " (11-bit)"),
        "traces": [
            {"name": "CAN_H", "segments": segs_h},
            {"name": "CAN_L", "segments": segs_l},
        ],
        "fields": fields,
        "time_label": "bit periods (dominant: H≈3.5 V / L≈1.5 V; recessive: both ≈2.5 V)",
        "stats": {"id": value, "extended": extended, "data": data_byte},
    }


def rs485_waveform(byte_value=0x55, baud=115200):
    """RS-485 A/B pair carrying UART framing: the two wires are complementary."""
    base = uart_waveform(byte_value, baud=baud)
    segs = base["traces"][0]["segments"]
    a_segs = [(float(lv), w) for lv, w in segs]
    b_segs = [(1.0 - float(lv), w) for lv, w in segs]
    return {
        "title": base["title"].replace("UART frame", "RS-485 pair A/B"),
        "traces": [
            {"name": "A (non-inv)", "segments": a_segs},
            {"name": "B (inv)", "segments": b_segs},
        ],
        "fields": base["fields"],
        "xticks": base["xticks"],
        "time_label": base["time_label"] + " — A>B is logic 1 (mark), B>A is logic 0 (space)",
        "stats": base["stats"],
    }


def ethernet_waveform():
    """10BASE-T frame opening: Manchester-coded preamble + SFD on the pair.

    IEEE 802.3 Manchester: '1' = high→low transition mid-bit, '0' = low→high.
    The alternating preamble reads as a square wave — that is the receiver's
    clock-recovery training signal; the SFD's double '1' marks where the real
    MAC fields (destination address) begin.
    """
    pre = [1, 0] * 6  # 12 of the 56 preamble bits
    sfd = [1, 0, 1, 0, 1, 0, 1, 1]  # ...10101011 — double '1' ends it
    dst0 = [1] * 8  # first dest-MAC byte (0xFF broadcast)
    bits = pre + sfd + dst0

    def manchester(bits, invert=False):
        segs = []
        for b in bits:
            hi = 2.5 if b else -2.5  # first half level
            lo = -hi  # mid-bit transition
            if invert:
                hi, lo = -hi, -lo
            segs += [(hi, 0.5), (lo, 0.5)]
        return segs

    fields = [
        (0.0, 12.0, "PREAMBLE (7 bytes)"),
        (12.0, 20.0, "SFD"),
        (20.0, 28.0, "DEST MAC byte 0 (0xFF)"),
    ]
    return {
        "title": "Ethernet 10BASE-T frame opening — Manchester preamble + SFD",
        "traces": [
            {"name": "TD+", "segments": manchester(bits)},
            {"name": "TD−", "segments": manchester(bits, invert=True)},
        ],
        "fields": fields,
        "time_label": "half-bit periods (10 Mbps → 100 ns/bit; a mid-bit transition is guaranteed)",
        "stats": {"bit_time_ns": 100.0, "preamble_bits": 56, "sfd_bits": 8},
    }


def i2s_waveform(left=0x1234, right=0x5678, bits=16, rate=48000):
    """I²S stereo frame: WS selects the channel, MSB lags the WS edge by one BCK.

    BCK toggles every cell; WS low = left slot, high = right slot; the sample
    is clocked MSB-first starting one bit-clock after the WS transition.
    """
    left_bits = [(left >> i) & 1 for i in range(bits - 1, -1, -1)]
    right_bits = [(right >> i) & 1 for i in range(bits - 1, -1, -1)]

    lead = 2  # idle lead-in cells
    slot = 1 + bits  # delay cell + MSB-first data cells
    total = lead + 2 * slot

    ws = [(0.0, float(lead))] + [(0.0, float(slot)), (1.0, float(slot))]
    sd = [(0.0, float(lead))]
    sd.append((0.0, 1.0))  # delay cell before the left MSB
    for b in left_bits:
        sd.append((float(b), 1.0))
    sd.append((0.0, 1.0))  # delay cell before the right MSB
    for b in right_bits:
        sd.append((float(b), 1.0))

    bck = []
    level = 1.0
    for _ in range(total):
        bck.append((level, 1.0))
        level = 0.0 if level else 1.0

    fields = [
        (float(lead + 1), float(lead + slot), f"LEFT 0x{left:04X}"),
        (float(lead + slot + 1), float(total), f"RIGHT 0x{right:04X}"),
    ]
    return {
        "title": f"I²S stereo frame — {bits}-bit samples MSB-first (WS low = left)",
        "traces": [
            {"name": "BCK", "segments": bck},
            {"name": "WS", "segments": ws},
            {"name": "SD", "segments": sd},
        ],
        "fields": fields,
        "time_label": f"bit-clock periods (BCK = 64 × {rate / 1000:g} kHz = {64 * rate / 1e6:g} MHz)",
        "stats": {"left": left, "right": right, "bit_clock_hz": 64 * rate},
    }


def arinc429_waveform(label=0o205, sdi=0):
    """ARINC 429 word opening: bipolar RZ on the A/B pair (±5 V, 100 kb/s).

    The label goes out first, LSB-first (ARINC's famous quirk). Every bit is
    return-to-zero: the pair drives ±5 V for the first half of the bit period
    and floats back to 0 V for the second.
    """
    label_bits = [(label >> i) & 1 for i in range(8)]  # LSB first
    sdi_bits = [(sdi >> i) & 1 for i in range(2)]
    data_bits = [1, 0, 0, 1]  # first data bits (illustrative)
    bits = label_bits + sdi_bits + data_bits

    a_segs, b_segs = [], []
    for b in bits:
        drive = 5.0 if b else -5.0
        a_segs += [(drive, 0.5), (0.0, 0.5)]
        b_segs += [(-drive, 0.5), (0.0, 0.5)]

    fields = [
        (0.0, 8.0, f"LABEL 0o{label:03o} (LSB first)"),
        (8.0, 10.0, "SDI"),
        (10.0, 14.0, "DATA"),
    ]
    return {
        "title": f"ARINC 429 word opening — label 0o{label:03o}, bipolar RZ",
        "traces": [
            {"name": "A", "segments": a_segs},
            {"name": "B", "segments": b_segs},
        ],
        "fields": fields,
        "time_label": "half-bit periods (100 kb/s → 10 µs/bit; pair returns to 0 V every second half)",
        "stats": {"label": label, "sdi": sdi, "bit_rate_bps": 100000},
    }
