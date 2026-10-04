# -*- coding: utf-8 -*-
"""Regression tests for frame-diagram readability (Bug #2).

Browser sweeps cannot see inside a Matplotlib canvas, so text overlap in long
frames was invisible to CI. These tests render the real figure and measure the
actual glyph bounding boxes.

Run: python build_scripts/check_diagrams.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from utils import diagrams  # noqa: E402

# Representative frames, one per shape that used to break the layout.
SMALL = [
    {"name": "Start", "bits": 1},
    {"name": "Data", "bits": 8},
    {"name": "Stop", "bits": 1},
]

MANY_NARROW = [
    {"name": "SOF", "bits": 1},
    {"name": "ID", "bits": 11},
    {"name": "RTR", "bits": 1},
    {"name": "IDE", "bits": 1},
    {"name": "r0", "bits": 1},
    {"name": "DLC", "bits": 4},
    {"name": "Data", "bits": 64},
    {"name": "CRC", "bits": 15},
    {"name": "CRC del", "bits": 1},
    {"name": "ACK", "bits": 1},
    {"name": "ACK del", "bits": 1},
    {"name": "EOF", "bits": 7},
    {"name": "IFS", "bits": 3},
]

LONG_NAMES = [
    {"name": "Start of Frame Delimiter", "bits": 1},
    {"name": "Destination MAC Address", "bits": 48},
    {"name": "Source MAC Address", "bits": 48},
    {"name": "802.1Q VLAN Tag Identifier", "bits": 16},
    {"name": "EtherType / Length Field", "bits": 16},
    {"name": "Payload (variable length)", "bits": "0-1500"},
    {"name": "Frame Check Sequence", "bits": 32},
    {"name": "Inter-Packet Gap", "bits": 12},
]

VARIABLE = [
    {"name": "Preamble", "bits": "0-64"},
    {"name": "Header", "bits": "var"},
    {"name": "Payload", "bits": 8},
]


def _overlaps(artists, tolerance=1.0):
    """Count overlapping label pairs using rendered bounding boxes.

    Tolerance is in display (pixel) units: a sub-pixel touch is anti-aliasing,
    not a real collision.
    """
    fig = artists[0].figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    boxes = []
    for a in artists:
        try:
            bb = a.get_window_extent(renderer=renderer)
        except Exception:  # noqa: BLE001
            continue
        boxes.append((a.get_text(), bb))

    collisions = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            t1, b1 = boxes[i]
            t2, b2 = boxes[j]
            if (
                b1.x0 + tolerance < b2.x1
                and b2.x0 + tolerance < b1.x1
                and b1.y0 + tolerance < b2.y1
                and b2.y0 + tolerance < b1.y1
            ):
                collisions.append((t1, t2))
    return collisions


def _render(fields):
    fig, meta = diagrams.frame_diagram(fields, return_meta=True)
    return fig, meta


FRAMES = (
    ("small", SMALL),
    ("many_narrow", MANY_NARROW),
    ("long_names", LONG_NAMES),
    ("variable", VARIABLE),
)


def test_small_frame_single_row():
    fig, meta = _render(SMALL)
    assert meta["rows"] == 1, f"a 3-field frame should stay on one row, got {meta['rows']}"
    plt.close(fig)


def test_all_fields_preserved_in_legend():
    for name, fields in FRAMES:
        fig, meta = _render(fields)
        assert len(meta["legend"]) == len(fields), (
            f"{name}: legend lost fields ({len(meta['legend'])} of {len(fields)})"
        )
        for i, f in enumerate(fields, start=1):
            entry = meta["legend"][i - 1]
            assert entry[0] == i and entry[1] == f["name"], (
                f"{name}: legend entry {i} mismatch: {entry}"
            )
        plt.close(fig)


def test_no_label_collisions():
    """The core Bug #2 detector."""
    for name, fields in FRAMES:
        fig, meta = _render(fields)
        collisions = _overlaps(meta["artists"])
        plt.close(fig)
        assert not collisions, f"{name}: {len(collisions)} overlapping labels: {collisions[:3]}"


def test_long_frame_uses_multiple_rows():
    """A frame this wide must not be squeezed onto one strip."""
    fig, meta = _render(LONG_NAMES)
    plt.close(fig)
    assert meta["rows"] >= 2, f"expected wrapping, got {meta['rows']} row(s)"


EXTREME = (
    [{"name": "Payload (jumbo)", "bits": 512}]
    + [{"name": f"Flag {i}", "bits": 1} for i in range(1, 12)]
)

DMX512_LIKE = [
    {"name": "Break", "bits": ""},
    {"name": "MAB", "bits": ""},
    {"name": "Start Code", "bits": 8},
    {"name": "Channels 1-512", "bits": 4096},
    {"name": "End / Inter-frame", "bits": ""},
]


def _fracs(fields):
    return diagrams._balanced_fracs([diagrams._bit_weight(f.get("bits", 8)) for f in fields])


def test_bounded_weights_respect_min_and_max():
    """No field may be crushed below readable width or swallow the whole row.

    This is the invariant that fixes DMX512: raw proportional weighting gave the
    4096-bit slot field ~98% of the row and left its neighbours ~1%.
    """
    for name, fields in (
        ("dmx512_like", DMX512_LIKE),
        ("extreme", EXTREME),
        ("1:8:4096:16:1", [
            {"name": "a", "bits": 1}, {"name": "b", "bits": 8},
            {"name": "c", "bits": 4096}, {"name": "d", "bits": 16},
            {"name": "e", "bits": 1},
        ]),
        ("1:1:1:8192:1:1", [
            {"name": "a", "bits": 1}, {"name": "b", "bits": 1},
            {"name": "c", "bits": 1}, {"name": "d", "bits": 8192},
            {"name": "e", "bits": 1}, {"name": "f", "bits": 1},
        ]),
    ):
        fr = _fracs(fields)
        assert abs(sum(fr) - 1.0) < 1e-6, f"{name}: fractions sum to {sum(fr)}, not 1"
        worst = min(fr)
        assert worst >= diagrams.MIN_BOX_FRAC - 1e-9, (
            f"{name}: a field was crushed to {worst:.4f}, below the readable "
            f"floor {diagrams.MIN_BOX_FRAC}"
        )
        assert max(fr) <= diagrams.MAX_BOX_FRAC + 1e-9, (
            f"{name}: a field took {max(fr):.3f}, above the cap "
            f"{diagrams.MAX_BOX_FRAC}"
        )


def test_huge_field_still_reads_as_dominant():
    """Bounded sizing must not flatten the frame: DATA/SLOTS stays clearly biggest."""
    fr = _fracs(DMX512_LIKE)
    biggest = max(fr)
    others = [f for f in fr if f < biggest]
    assert biggest >= 2 * max(others), (
        f"the 4096-bit field is not dominant: {biggest:.3f} vs {max(others):.3f}"
    )


def test_every_field_is_identifiable_by_name_or_index():
    """Each box carries its full name, or an index that the legend resolves."""
    for name, fields in (
        ("dmx512_like", DMX512_LIKE),
        ("extreme", EXTREME),
        ("many_narrow", MANY_NARROW),
        ("long_names", LONG_NAMES),
    ):
        fig, meta = _render(fields)
        texts = [a.get_text() for a in meta["artists"]]
        plt.close(fig)
        assert len(texts) == len(fields), (
            f"{name}: drew {len(texts)} labels for {len(fields)} fields"
        )
        legend_names = {entry[1] for entry in meta["legend"]}
        for idx, t in enumerate(texts):
            if t.isdigit():
                # A numbered box must point at a real legend entry.
                n = int(t)
                assert 1 <= n <= len(fields), f"{name}: index {n} out of range"
                assert meta["legend"][n - 1][1] in legend_names
            else:
                # Otherwise the box must contain the field's real name, possibly
                # wrapped. Compare with all whitespace removed: textwrap breaks
                # "End / Inter-frame" after the hyphen, which is still the same
                # name to a reader.
                def _squash(s):
                    return "".join(s.split())

                shown = _squash(t)
                assert shown == _squash(fields[idx]["name"]), (
                    f"{name}: label {t!r} does not correspond to "
                    f"{fields[idx]['name']!r}"
                )


def test_exact_bit_values_survive_visual_compression():
    """Compression is visual only - the engineering values must remain exact."""
    fig, meta = _render(DMX512_LIKE)
    plt.close(fig)
    legend = {entry[1]: entry[2] for entry in meta["legend"]}
    assert legend["Channels 1-512"] == "4096 bit", legend
    assert legend["Start Code"] == "8 bit", legend
    # Names with no bit width stay listed rather than being dropped.
    assert "Break" in legend and "MAB" in legend


def test_no_collisions_across_every_real_frame():
    """Render every frame_fields set in the shipped dataset and check collisions.

    The fixtures above are synthetic. This proves the fix holds for the frames
    users actually see, including the worst real one.
    """
    import json

    with open(os.path.join(ROOT, "data", "protocols.json"), encoding="utf-8") as fh:
        protocols = json.load(fh)

    worst = None
    checked = 0
    for p in protocols:
        fields = p.get("frame_fields")
        if not fields:
            continue
        checked += 1
        fig, meta = _render(fields)
        collisions = _overlaps(meta["artists"])
        if collisions and (worst is None or len(collisions) > len(worst[1])):
            worst = (p["name"], collisions)
        plt.close(fig)

    assert checked > 0, "no protocol in the dataset has frame_fields"
    assert worst is None, (
        f"{checked} real frames checked; worst overlap in {worst[0]}: "
        f"{worst[1][:3]}"
    )


def test_detector_catches_overlapping_labels():
    """NEGATIVE TEST: prove the collision detector can actually fail.

    Draws two labels at the same point. If _overlaps() cannot see this, it
    cannot be trusted to clear the real frames above.
    """
    fig, ax = plt.subplots(figsize=(4, 2))
    a1 = ax.text(0.5, 0.5, "Delta-Sigma Modulator", ha="center", va="center", fontsize=12)
    a2 = ax.text(0.5, 0.5, "Cyclic Redundancy Check", ha="center", va="center", fontsize=12)
    collisions = _overlaps([a1, a2])
    plt.close(fig)

    assert collisions, (
        "NEGATIVE TEST FAILED: two labels at identical coordinates were not "
        "detected as overlapping, so the frame collision test proves nothing."
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
        print(f"Diagram tests FAILED: {failed} of {len(tests)}")
        sys.exit(1)
    print(f"Diagram tests passed ({len(tests)} checks)")
