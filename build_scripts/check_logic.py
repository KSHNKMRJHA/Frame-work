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

from utils import science as sc          # noqa: E402
from utils import quiz_engine as qe      # noqa: E402
from utils import diagrams              # noqa: E402

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
        assert len(set(order)) == len(order), \
            f"seed {seed}: {pz['protocol']} has duplicate field names {order}"
        assert pz["scrambled"] != order, f"seed {seed}: scramble equals the answer"
        assert sorted(pz["scrambled"]) == sorted(order)


def test_quiz_shape(protocols):
    for seed in range(200):
        quiz = qe.generate_quiz(protocols, n=10, seed=seed)
        assert len(quiz) == 10, f"seed {seed}: got {len(quiz)} questions"
        for q in quiz:
            assert len(q["options"]) == 4, f"seed {seed}: {len(q['options'])} options"
            assert q["answer"] in q["options"], f"seed {seed}: answer not among options"
            assert q["options"].count(q["answer"]) == 1, \
                f"seed {seed}: correct answer appears twice — question is unanswerable"
            assert q["explain"], f"seed {seed}: empty explanation"


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        protocols = json.load(f)

    tests = [
        ("CRC catalogue check values", test_crc_check_values, ()),
        ("engineering formulas", test_formulas, ()),
        ("boundary guards", test_boundary_guards, ()),
        ("parse_user_bytes edge cases", test_parse_user_bytes, ()),
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
