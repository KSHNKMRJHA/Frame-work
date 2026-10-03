# -*- coding: utf-8 -*-
"""
check_logic.py
Regression tests for the calculation and generator logic. Run by CI and safe
to run locally:

    python build_scripts/check_logic.py

The CRC block is the important one: these three hex values are the published
"check" values from the reveng CRC catalogue for the input "123456789", so a
regression in _crc16 cannot pass unnoticed.
"""

import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils import science as sc  # noqa: E402
from utils import quiz_engine as qe  # noqa: E402
from utils import diagrams  # noqa: E402
from utils import signal_engine as sc_engine  # noqa: E402
import electrical_specs as e_specs  # noqa: E402

DATA_PATH = os.path.join(ROOT, "data", "protocols.json")
CHECK_INPUT = b"123456789"


def test_crc_check_values():
    assert sc.crc16_ccitt_false(CHECK_INPUT) == 0x29B1, "CRC-16/IBM-3740 (CCITT-FALSE)"
    assert sc.crc16_modbus(CHECK_INPUT) == 0x4B37, "CRC-16/MODBUS"
    assert sc.crc32_ieee(CHECK_INPUT) == 0xCBF43926, "CRC-32/ISO-HDLC"


def test_formulas():
    # Shannon against the closed form, Nyquist against the textbook value.
    assert abs(sc.shannon_capacity(20e6, 30) - 20e6 * math.log2(1001)) < 1e-6
    assert sc.nyquist_max_rate(3000, 2) == 6000
    # c / 2.4 GHz = 12.49135 cm
    assert abs(sc.freq_to_wavelength(2.4e9) - 0.1249135) < 1e-6
    # AVR/STM32 form: UBRR+1 = round(F_CLK / (16 * baud))
    r = sc.uart_bit_timing(16_000_000, 9600, 16)
    assert r["divisor"] == 104, r["divisor"]
    assert abs(r["error_pct"] - 0.16) < 0.01, r["error_pct"]
    assert r["acceptable"] is True
    # 16 MHz / 115200 is the classic case that exceeds the +/-2% tolerance
    assert sc.uart_bit_timing(16_000_000, 115200, 16)["acceptable"] is False
    # CAN: sync(1) + prop(3) + ps1(3) + ps2(2) = 9 TQ, sample point at 7/9
    ct = sc.can_bit_timing(16e6, 500_000, tq_prop=3, tq_ps1=3, tq_ps2=2)
    assert ct["total_tq"] == 9
    assert abs(ct["sample_point_pct"] - 700 / 9) < 1e-9


def test_boundary_guards():
    """Zero and negative inputs must raise ValueError, not ZeroDivisionError."""
    cases = [
        (sc.uart_bit_timing, (0, 115200, 16)),
        (sc.uart_bit_timing, (16_000_000, 0, 16)),
        (sc.uart_bit_timing, (-16_000_000, 115200, 16)),
        (sc.shannon_capacity, (-1, 30)),
        (sc.nyquist_max_rate, (20e6, 1)),
        (sc.nyquist_max_rate, (20e6, 0)),
        (sc.freq_to_wavelength, (0,)),
        (sc.wavelength_to_freq, (0,)),
        (sc.quarter_wave_antenna_length, (0,)),
        (sc.can_bit_timing, (16e6, 0)),
        (sc.can_bit_timing, (0, 500_000)),
    ]
    for fn, args in cases:
        try:
            fn(*args)
        except ValueError:
            continue
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


def test_parse_user_bytes():
    assert sc.parse_user_bytes("") == b""
    # The CRC test vector must stay text, not be read as hex nibbles.
    assert sc.parse_user_bytes("123456789") == b"123456789"
    # Plain text containing digits must not be misread as hex.
    assert sc.parse_user_bytes("Test123") == b"Test123"
    assert sc.parse_user_bytes("48 65 6C 6C 6F") == b"Hello"
    assert sc.parse_user_bytes("48,65,6C") == b"Hel"


def test_frame_puzzle_solvable(protocols):
    """Every reachable frame puzzle must be solvable from field names alone."""
    for seed in range(200):
        pz = qe.generate_frame_order_puzzle(protocols, seed=seed)
        order = pz["correct_order"]
        assert len(set(order)) == len(order), f"seed {seed}: {pz['protocol']} has duplicate field names {order}"
        assert pz["scrambled"] != order, f"seed {seed}: scramble equals the answer"
        assert sorted(pz["scrambled"]) == sorted(order)


def test_quiz_shape(protocols):
    for seed in range(200):
        quiz = qe.generate_quiz(protocols, n=10, seed=seed)
        assert len(quiz) == 10, f"seed {seed}: got {len(quiz)} questions"
        for q in quiz:
            assert len(q["options"]) == 4, f"seed {seed}: {len(q['options'])} options"
            assert q["answer"] in q["options"], f"seed {seed}: answer not among options"
            assert q["options"].count(q["answer"]) == 1, (
                f"seed {seed}: correct answer appears twice — question is unanswerable"
            )
            assert q["explain"], f"seed {seed}: empty explanation"


def test_engineering_calculators():
    """I²C pull-ups, RS-485 biasing, CAN load, RF link budget — textbook values."""
    # I²C: 3.3 V, 0.4 V, 3 mA -> Rp_min = 966.7 Ω; Fm @150 pF -> Rp_max ≈ 2360 Ω.
    r = sc.i2c_recommended_pullups(3.3, 150, "Fast-mode (400 kHz)")
    assert abs(r["rp_min_ohm"] - 966.67) < 0.1, r["rp_min_ohm"]
    assert r["rp_min_ohm"] < r["rp_max_ohm"] and r["feasible"]
    assert r["suggested_ohm"] and r["rp_min_ohm"] <= r["suggested_ohm"] <= r["rp_max_ohm"]
    assert abs(sc.i2c_rise_time_ns(r["rp_max_ohm"], 150) - 300.0) < 1e-6
    # Rise-time constant: 1 kΩ × 100 pF = 84.73 ns.
    assert abs(sc.i2c_rise_time_ns(1000, 100) - 84.73) < 0.01

    # RS-485: 5 V, 680/680 Ω bias with 120 Ω termination -> 405 mV > 200 mV.
    b = sc.rs485_fail_safe_bias(5, 680, 680)
    assert b["meets_fail_safe"] and b["vos_mv"] > 400, b["vos_mv"]
    # Weak 10k/10k bias -> below the +200 mV fail-safe threshold.
    weak = sc.rs485_fail_safe_bias(5, 10000, 10000)
    assert not weak["meets_fail_safe"], weak["vos_mv"]
    # Solver round-trips: max equal pair must itself meet the target.
    rmax = sc.rs485_max_equal_bias(5)
    assert sc.rs485_fail_safe_bias(5, rmax, rmax)["vos_mv"] >= 199.9

    # CAN: 8-byte base frame = 44 + 64 + 3 = 111 bits on the wire.
    cb = sc.can_frame_bits(8)
    assert cb["frame_bits"] == 108 and cb["total_bits"] == 111, cb
    ext = sc.can_frame_bits(8, extended=True)
    assert ext["frame_bits"] == 128 and ext["total_bits"] == 131, ext
    load = sc.can_bus_load(500_000, 100, data_bytes=8)
    assert abs(load["bus_load_pct"] - 2.22) < 0.01, load["bus_load_pct"]
    assert load["worst_bus_load_pct"] > load["bus_load_pct"]

    # RF: FSPL 2.4 GHz @ 1 km = 100.04 dB (classic textbook figure).
    assert abs(sc.fspl_db(2400, 1) - 100.04) < 0.01
    lb = sc.link_budget_db(20, 2, 2, 2400, 0.1, sensitivity_dbm=-95)
    assert lb["link_ok"] and lb["eirp_dbm"] == 22
    # Prx = EIRP(22) + Rx gain(2) - FSPL(80.04) = -56.04 dBm
    assert abs(lb["rx_power_dbm"] - (22 + 2 - sc.fspl_db(2400, 0.1))) < 1e-9


def test_engineering_boundary_guards():
    """New calculators must raise ValueError, not crash."""
    cases = [
        (sc.i2c_rise_time_ns, (0, 100)),
        (sc.i2c_rise_time_ns, (1000, 0)),
        (sc.i2c_recommended_pullups, (0, 150, "Fast-mode (400 kHz)")),
        (sc.i2c_recommended_pullups, (3.3, 150, "Turbo-mode")),
        (sc.rs485_fail_safe_bias, (0, 680, 680)),
        (sc.rs485_fail_safe_bias, (5, 0, 680)),
        (sc.rs485_max_equal_bias, (0,)),
        (sc.can_frame_bits, (9,)),
        (sc.can_bus_load, (0, 100)),
        (sc.fspl_db, (0, 1)),
        (sc.fspl_db, (2400, 0)),
        (sc.link_budget_db, (20, 2, 2, 2400, 1, -1)),
    ]
    for fn, args in cases:
        try:
            fn(*args)
        except ValueError:
            continue
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


def test_waveform_builders():
    """Every waveform builder returns renderable traces with sane geometry."""
    builders = [
        lambda: diagrams.uart_waveform(0x55),
        lambda: diagrams.i2c_waveform(),
        lambda: diagrams.spi_waveform(),
        lambda: diagrams.can_waveform(),
        lambda: diagrams.rs485_waveform(),
        lambda: diagrams.ethernet_waveform(),
        lambda: diagrams.i2s_waveform(),
        lambda: diagrams.arinc429_waveform(),
    ]
    for build in builders:
        model = build()
        assert model["traces"], "no traces in waveform model"
        assert model["fields"], "no field labels in waveform model"
        for tr in model["traces"]:
            segs = tr["segments"]
            assert segs and all(w > 0 for _, w in segs), f"bad segments in {tr['name']}"
        fig = diagrams.waveform_diagram(model)
        assert fig is not None, f"waveform_diagram failed for {model['title']}"
        import matplotlib.pyplot as plt

        plt.close(fig)
    # 8N1 UART frame = 10 bit times regardless of the payload.
    uart = diagrams.uart_waveform(0x00, baud=115200)
    assert abs(uart["stats"]["frame_time_us"] - 10 * 1e6 / 115200) < 1e-6


def test_frame_overhead():
    """parse_bit_count must handle every literal form in the database."""
    cases = [
        (8, (8, 8)),
        ("8", (8, 8)),
        ("0-32", (0, 32)),
        ("0+", (0, None)),
        ("0-1500+", (0, None)),
        ("8*n", (8, None)),
        ("8*512B", (4096, 4096)),
        ("—", None),
        (True, None),          # bool is an int subclass; must not be accepted
        (-1, None),
    ]
    for spec, expected in cases:
        assert sc.parse_bit_count(spec) == expected, f"{spec!r} -> {sc.parse_bit_count(spec)}"

    # A classic Ethernet II frame: 14 B header + 4 B FCS = 144 bits fixed.
    eth = [
        {"name": "Destination MAC", "bits": 48},
        {"name": "Source MAC", "bits": 48},
        {"name": "Ethertype", "bits": 16},
        {"name": "Data", "bits": "46-1500"},
        {"name": "FCS", "bits": 32},
    ]
    r = sc.frame_overhead(eth, payload_bits=512)
    assert r["fixed_overhead_bits"] == 144, r["fixed_overhead_bits"]
    assert r["total_bits"] == 144 + 512
    assert "Data" in r["variable_fields"]          # payload excluded from overhead
    assert 77 < r["efficiency_pct"] < 79            # 512 / 656

    # A 64-bit header with an 8-byte payload must report 128 bits total.
    two = sc.frame_overhead([{"name": "Hdr", "bits": 64}], payload_bits=64)
    assert two["total_bits"] == 128 and two["efficiency_pct"] == 50.0


def test_frame_overhead_all_protocols(protocols):
    """Every protocol with frame_fields must produce a sane overhead result."""
    checked = 0
    for p in protocols:
        fields = p.get("frame_fields") or []
        if not fields:
            continue
        r = sc.frame_overhead(fields, payload_bits=64)
        assert r["total_bits"] >= 64, f"{p['id']}: total_bits {r['total_bits']}"
        assert 0 < r["efficiency_pct"] <= 100, f"{p['id']}: {r['efficiency_pct']}%"
        assert r["fixed_overhead_bits"] >= 0
        checked += 1
    assert checked >= 100, f"expected most protocols to have frames, got {checked}"


def test_signal_engine():
    """Line codings must produce real, correctly-timed waveforms."""
    # NRZ: one segment per bit, level == bit value.
    segs = sc_engine.encode("nrz", "101")
    assert len(segs) == 3
    assert [s[2] for s in segs] == [1.0, 0.0, 1.0]
    assert segs[0][0] == 0.0 and segs[0][1] == 1.0

    # Manchester always transitions mid-bit: 2 segments per bit, second is the
    # complement of the first.
    m = sc_engine.encode("manchester", "10")
    assert len(m) == 4
    assert m[0][2] != m[1][2] and m[2][2] != m[3][2]
    # IEEE 802.3: bit 1 = low->high.
    assert m[0][2] == 0.0 and m[1][2] == 1.0

    # Bipolar RZ returns to zero after each pulse.
    b = sc_engine.encode("bipolar_rz", "10")
    assert any(seg[2] == 0.0 for seg in b)
    assert any(seg[2] == -1.0 for seg in b)

    # Every registered coding must run without raising.
    for coding in sc_engine.LINE_CODINGS:
        out = sc_engine.encode(coding, "1011")
        assert out, f"{coding} produced no segments"
        for t0, t1, lvl in out:
            assert t1 > t0, f"{coding} produced a non-advancing segment"

    try:
        sc_engine.encode("not-a-coding", "1")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown line coding should raise ValueError")


def test_message_analysis():
    """Bits must decode to hex/decimal/binary/ASCII consistently."""
    d = sc_engine.describe_value("01000001")
    assert d["decimal"] == 65 and d["hex"] == "41" and d["ascii"] == "A"
    assert d["binary"] == "01000001"

    # 0x01 is a control character: rendered as '.' (the hex-dump convention),
    # not None, so it stays visible in a byte table.
    d2 = sc_engine.describe_value("00000001")
    assert d2["decimal"] == 1 and d2["hex"] == "01" and d2["ascii"] == "."
    # 0x7E is '~' - printable, so it must decode to the real character.
    d3 = sc_engine.describe_value("01111110")
    assert d3["decimal"] == 126 and d3["hex"] == "7E" and d3["ascii"] == "~"
    # A bit run that is not a whole number of bytes has no ASCII rendering.
    assert sc_engine.describe_value("0101010")["ascii"] is None

    # Analyze a bit stream against a small frame definition.
    fields = [{"name": "Start", "bits": 1}, {"name": "ID", "bits": 8}, {"name": "CRC", "bits": 8}]
    res = sc_engine.analyze_message("0101010101010", fields)
    assert res["total_bits"] == 13
    assert [f["name"] for f in res["fields"]] == ["Start", "ID", "CRC"]
    # Stream "0 10101010 1010": ID occupies bits 1-8 = 0xAA, CRC = 0x0A.
    assert res["fields"][1]["hex"] == "AA" and res["fields"][1]["decimal"] == 170
    assert res["fields"][2]["offset"] == 9

    # Round trip bytes <-> bits.
    assert sc_engine.bytes_from_bits(sc_engine.bits_from_bytes(b"\x55\xaa")) == b"\x55\xaa"


def test_physical_io_coverage(protocols):
    """Every protocol must document wiring, commands, or addressing."""
    missing_signals = [p["id"] for p in protocols if not p.get("signals")]
    assert not missing_signals, f"protocols with no signals: {missing_signals[:10]}"

    for p in protocols:
        for sig in p["signals"]:
            assert sig.get("name") and sig.get("dir"), f"{p['id']}: bad signal {sig}"
        for cmd in p.get("commands", []):
            assert cmd.get("code") and cmd.get("name"), f"{p['id']}: bad command {cmd}"


def test_electrical_specs(protocols):
    """Voltages, impedances and timings must be present and self-consistent."""
    missing = [p["id"] for p in protocols if not p.get("electrical")]
    assert not missing, f"protocols with no electrical spec: {missing}"

    for p in protocols:
        spec = p["electrical"]
        if spec["signaling"] in ("differential", "bipolar"):
            hi, lo = spec["vdiff_high_volts"], spec["vdiff_low_volts"]
            assert hi > lo, f"{p['id']}: Vdiff_high must exceed Vdiff_low"
            # A negative rail is only wrong when a nonzero common mode is
            # declared: RS-485 at VCM 0 is legitimately bipolar.
            vcm = spec["vcm_volts"]
            if vcm:
                assert vcm - max(abs(hi), abs(lo)) / 2 >= 0, f"{p['id']}: rail goes negative"
            assert spec["pairs"], f"{p['id']}: differential signalling needs declared pairs"
            for pr in spec["pairs"]:
                assert pr["role"] in ("transmit", "receive", "bidirectional")
        for field in ("rise_time_ns", "bit_period_ns"):
            v = spec.get(field)
            assert v is None or v > 0, f"{p['id']}: {field} must be positive"


def test_differential_waveform():
    """Differential traces must straddle the common mode and show real VDiff."""
    spec = e_specs.ELECTRICAL["usb20"]
    traces = dict((name, segs) for name, segs in
                  sc_engine.differential_waveform(spec, "1010"))
    # USB: VCM 3.0 V, +/-0.2 V differential -> 3.10/2.90, never 0 V.
    assert 3.10 in [round(s[2], 2) for s in traces["V+"]]
    assert 2.90 in [round(s[2], 2) for s in traces["V-"]]

    # VDiff must alternate +/-0.2 V for alternating bits.
    vdiff = [round(s[2], 2) for s in traces["VDiff"]]
    assert vdiff == [0.20, -0.20, 0.20, -0.20], f"bad VDiff: {vdiff}"

    # A 1 must put V+ above V- (and vice versa) - that IS the receiver's signal.
    for (pos, neg) in zip(traces["V+"], traces["V-"]):
        assert (pos[2] - neg[2]) != 0.0, "one line never differs from the other"

    # RX traces must be delayed relative to TX by the propagation delay.
    rx = [name for name in traces if "RX" in name]
    assert rx, "expected delayed RX traces"
    for name in rx:
        base = name.split(" ")[0]
        tx_first = traces[base][0][0]
        assert traces[name][0][0] > tx_first, f"{name} is not delayed"

    # Single-ended protocols collapse to one driven line, still with a delayed RX.
    single = dict((n, s) for n, s in
                  sc_engine.differential_waveform(e_specs.ELECTRICAL["i2c"], "10"))
    assert "line" in single
    # Bits "10": a 1 drives VOH (3.3 V), a 0 drops to VOL (0.4 V).
    assert [round(s[2], 1) for s in single["line"]] == [3.3, 0.4]
    assert any("RX" in n for n in single), "single-ended should still show RX delay"

    # RF has no wire-level volts, so it must yield no traces rather than fakes.
    assert sc_engine.differential_waveform(e_specs.ELECTRICAL["wifi_radio"], "10") == []


def test_derived_electrical():
    """Derived numbers must follow from the spec, not be hard-coded."""
    eth = e_specs.ELECTRICAL["ethernet"]
    d = e_specs.derive_derived(eth, cable_length_m=100)
    # 20 ns/bit -> 50 Mbit/s and a 50 MHz clock.
    assert abs(d["bit_rate_mbps"] - 50.0) < 0.01
    assert abs(d["clock_hz"] - 50e6) < 1e3
    # 5 ns/m over 100 m = 500 ns one way, 1000 ns round trip.
    assert abs(d["one_way_delay_ns"] - 500.0) < 0.01
    assert abs(d["round_trip_delay_ns"] - 1000.0) < 0.01
    # 10 ns rise time -> about 35 MHz first-order bandwidth.
    assert abs(d["bandwidth_mhz"] - 35.0) < 0.01

    lv = e_specs.format_levels(eth)
    assert "VDiff" in lv and "Z0 100" in lv


def test_no_dead_end_tabs(protocols):
    """No protocol may reach a 'nothing to show' branch in Pinout or Waveform.

    Both tabs previously fell back to an apology message for protocols with an
    empty legacy `pins` list or no bespoke waveform renderer - 96 and 76
    protocols respectively. Now every protocol must produce a real render or a
    meaningful RF link table instead.
    """
    from utils import diagrams

    for p in protocols:
        pins = [s["name"] for s in (p.get("signals") or [])]
        if not pins:
            pins = [x for x in (p.get("pins") or []) if x]
        assert pins, f"{p['id']}: no pins at all - Pinout tab would dead-end"
        assert diagrams.pinout_diagram(pins, p["name"]) is not None, \
            f"{p['id']}: pinout_diagram returned None"

        spec = p.get("electrical") or {}
        assert spec, f"{p['id']}: no electrical spec - Waveform tab would dead-end"
        traces = sc_engine.differential_waveform(spec, "10110100", 1.0)
        if traces:
            model = {
                "title": p["id"],
                "traces": [{"name": n, "segments": [(s[2], s[1] - s[0]) for s in g]}
                           for n, g in traces],
                "fields": [],
            }
            assert diagrams.waveform_diagram(model) is not None, \
                f"{p['id']}: waveform failed to render"
        else:
            # The only acceptable no-trace case is RF, which shows a link table.
            assert spec.get("signaling") == "rf", \
                f"{p['id']}: no waveform and not RF ({spec.get('signaling')})"
            assert e_specs.format_levels(spec), f"{p['id']}: RF with no level text"


def test_nav_cards_match_pages():
    """Every nav card must point at a real file, and order must match the sidebar.

    The sidebar is generated from the pages/ filename prefixes, so a stale card
    silently links nowhere. This also keeps app.py's ordering in step with the
    sidebar so the two never drift apart.
    """
    import re
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    pages_dir = root / "pages"

    actual = sorted(
        (int(f.name.split("_", 1)[0]), f.name)
        for f in pages_dir.glob("*.py")
        if f.name.split("_", 1)[0].isdigit()
    )
    expected = [name for _, name in actual]

    app_src = (root / "app.py").read_text(encoding="utf-8")
    # Only the `cards` list is the nav; the file also contains other page_link
    # calls (the resume deep link) that must not be mistaken for nav entries.
    cards_block = app_src[app_src.index("cards = ["):app_src.index("\n]\n", app_src.index("cards = ["))]
    cards = re.findall(r'"pages/([^"]+\.py)"', cards_block)

    assert cards, "no nav cards found in app.py"
    # Page filenames contain emoji, which the Windows console cannot encode;
    # compare on the ASCII stem so a failure message stays printable.
    stem = lambda name: name.split("_", 1)[-1].encode("ascii", "replace").decode()  # noqa: E731
    assert [stem(c) for c in cards] == [stem(e) for e in expected], (
        "app.py nav cards do not match pages/ (sidebar order):\n"
        f"  cards:    {[stem(c) for c in cards]}\n"
        f"  expected: {[stem(e) for e in expected]}"
    )

    # And every referenced path must actually exist on disk.
    for name in cards:
        assert (pages_dir / name).exists(), f"nav card points at missing file: {name}"


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        protocols = json.load(f)

    tests = [
        ("CRC catalogue check values", test_crc_check_values, ()),
        ("engineering formulas", test_formulas, ()),
        ("boundary guards", test_boundary_guards, ()),
        ("parse_user_bytes edge cases", test_parse_user_bytes, ()),
        ("I2C/RS485/CAN/RF calculators", test_engineering_calculators, ()),
        ("calculator boundary guards", test_engineering_boundary_guards, ()),
        ("waveform builders", test_waveform_builders, ()),
        ("frame overhead math", test_frame_overhead, ()),
        ("frame overhead across protocols", test_frame_overhead_all_protocols, (protocols,)),
        ("signal engine line codings", test_signal_engine, ()),
        ("message/address decoding", test_message_analysis, ()),
        ("physical IO coverage", test_physical_io_coverage, (protocols,)),
        ("electrical specs", test_electrical_specs, (protocols,)),
        ("differential waveform", test_differential_waveform, ()),
        ("derived electrical values", test_derived_electrical, ()),
        ("no dead-end tabs", test_no_dead_end_tabs, (protocols,)),
        ("nav cards match sidebar", test_nav_cards_match_pages, ()),
        ("frame puzzle solvability", test_frame_puzzle_solvable, (protocols,)),
        ("quiz question shape", test_quiz_shape, (protocols,)),
    ]

    failures = []
    for name, fn, args in tests:
        try:
            fn(*args)
        except AssertionError as exc:
            failures.append((name, exc))
            print(f"::error::{name}: {exc}")
        else:
            print(f"  ok  {name}")

    assert diagrams.category_bar_chart(protocols) is not None

    if failures:
        print(f"\n{len(failures)} logic test group(s) failed", file=sys.stderr)
        return 1
    print(f"Logic tests passed against {len(protocols)} protocols")
    return 0


if __name__ == "__main__":
    sys.exit(main())
