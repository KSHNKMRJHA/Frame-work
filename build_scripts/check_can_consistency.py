#!/usr/bin/env python3
"""Regression gate for CAN electrical, logical, and rendered states."""
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import electrical_specs  # noqa: E402
import technical_profiles  # noqa: E402
from utils import branding, diagrams, signal_engine  # noqa: E402


def close(actual, expected):
    assert math.isclose(actual, expected, abs_tol=1e-9), (actual, expected)


def main():
    source = electrical_specs.ELECTRICAL["can"]
    close(source["vcm_volts"], 2.5)
    close(source["vdiff_high_volts"], 2.0)
    close(source["vdiff_low_volts"], 0.0)
    assert source["logic_1_is_vdiff_high"] is False
    assert "120 Ohm at both ends" in source["termination"]

    profile_input = [{"id": "can", "category": "Automotive"}]
    technical_profiles.apply_technical_profiles(profile_input)
    profile = profile_input[0]["technical"]
    assert "Recessive (logical 1)" in profile["logic_high"]
    assert "Dominant (logical 0)" in profile["logic_low"]

    traces = dict(signal_engine.differential_levels(source, "01"))
    close(traces["V+"][0][2], 3.5)
    close(traces["V-"][0][2], 1.5)
    close(traces["V+"][1][2], 2.5)
    close(traces["V-"][1][2], 2.5)

    bars = branding.differential_rail_extrema(2.5, 2.0, 0.0)
    expected = {"vplus_max": 3.5, "vplus_min": 2.5,
                "vminus_max": 2.5, "vminus_min": 1.5,
                "floor": 1.5, "ceiling": 3.5}
    for key, value in expected.items():
        close(bars[key], value)

    # Exercise every differential/bipolar/passive authoring source, including
    # USB, RS-485, LVDS, and ARINC 429, against the generic rail ordering.
    exercised = set()
    for protocol_id, spec in electrical_specs.ELECTRICAL.items():
        hi, lo = spec.get("vdiff_high_volts"), spec.get("vdiff_low_volts")
        if spec.get("signaling") not in ("differential", "bipolar", "passive") or hi is None or lo is None:
            continue
        rails = branding.differential_rail_extrema(spec.get("vcm_volts") or 0.0, hi, lo)
        assert rails["vplus_max"] >= rails["vplus_min"], protocol_id
        assert rails["vminus_max"] >= rails["vminus_min"], protocol_id
        exercised.add(protocol_id)
    for protocol_id in ("usb20", "rs485", "lvds", "arinc429"):
        assert protocol_id in exercised, f"expected coverage for {protocol_id}"

    wave = diagrams.can_waveform(frame_id=0, data_byte=0)
    can_h = wave["traces"][0]["segments"]
    can_l = wave["traces"][1]["segments"]
    close(can_h[0][0], 3.5)  # SOF logical 0 is dominant.
    close(can_l[0][0], 1.5)
    close(can_h[-1][0], 2.5)  # EOF logical 1 is recessive.
    close(can_l[-1][0], 2.5)

    data = json.loads((ROOT / "data" / "protocols.json").read_text(encoding="utf-8"))
    indexed = {p["id"]: p for p in data}
    for protocol_id in ("can", "canopen", "j1939", "obd2", "can_fd", "can_xl", "devicenet", "xcp"):
        if protocol_id not in indexed:
            continue
        spec = indexed[protocol_id]["electrical"]
        close(spec["vcm_volts"], 2.5)
        close(spec["vdiff_high_volts"], 2.0)
        close(spec["vdiff_low_volts"], 0.0)
        assert spec["logic_1_is_vdiff_high"] is False
    for protocol_id in ("isotp", "uds"):
        spec = indexed[protocol_id]["electrical"]
        assert spec["logic_1_is_vdiff_high"] is False
        close(spec["bit_period_ns"], 2000.0)
    can_data = indexed["can"]
    assert "Recessive (logical 1)" in can_data["technical"]["logic_high"]
    assert "Dominant (logical 0)" in can_data["technical"]["logic_low"]
    assert "500 kbit/s example" in can_data["electrical"]["notes"]
    print(f"CAN consistency passed; checked {len(exercised)} differential authoring sources")


if __name__ == "__main__":
    main()
