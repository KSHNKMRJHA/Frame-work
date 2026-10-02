# -*- coding: utf-8 -*-
"""
check_data.py
Data-integrity gate for data/protocols.json. Run by CI and safe to run locally:

    python build_scripts/check_data.py

Every check here corresponds to a defect that actually reached the repository
at some point, so none of them are hypothetical:

  * broken `related` references silently shorten the Encyclopedia's "Related
    Protocols" list and drop edges from the category mind map, with no error
  * duplicate `frame_fields` names make generate_frame_order_puzzle
    unsolvable, because the grader compares field-name lists
  * a stray category value would create a thirteenth colour-less mind-map node
  * an unsourced `fun_fact` is how a wrong "fun fact" gets published
"""

import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frame_specs import NO_FIXED_FRAME  # noqa: E402

DATA_PATH = os.path.join(ROOT, "data", "protocols.json")
SCHEMA_PATH = os.path.join(ROOT, "docs", "protocol-database", "schema.json")

CATEGORIES = {
    "On-Board",
    "Industrial",
    "Automotive",
    "Networking",
    "Wireless",
    "Cellular",
    "Audio/Video",
    "USB",
    "High-Speed/FPGA",
    "Sensor-Specific",
    "Security",
    "Aerospace",
    "Debug & Trace",
}
DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}
YEAR_MILESTONES = {"invented", "published", "standardized", "deployed"}
REQUIRED = (
    "id",
    "name",
    "category",
    "topology",
    "year",
    "inventor",
    "description",
    "how_it_works",
    "use_cases",
    "advantages",
    "limitations",
    "real_world_example",
    "difficulty",
)


def check(protocols):
    """Return a list of human-readable integrity errors (empty == healthy)."""
    errors = []

    if len(protocols) < 50:
        errors.append(f"protocol database looks too small ({len(protocols)} entries)")

    for field in ("id", "name"):
        dupes = [k for k, n in Counter(p[field] for p in protocols).items() if n > 1]
        if dupes:
            errors.append(f"duplicate {field}: {dupes}")

    ids = {p["id"] for p in protocols}

    # Every record must expose the same core fields. A partially-written record
    # (e.g. a builder appending into the wrong dict) shows up here as a missing
    # key on some records but not others, which is otherwise invisible.
    core = ("id", "name", "category", "description", "how_it_works", "speed",
            "frame_fields", "frame_note", "technical")
    for field in core:
        absent = sorted(p.get("id", "<no id>") for p in protocols if field not in p)
        if absent:
            errors.append(
                f"{len(absent)} record(s) missing {field!r}: {absent[:8]}"
                f"{' ...' if len(absent) > 8 else ''}"
            )

    for p in protocols:
        pid = p.get("id", "<no id>")

        for field in REQUIRED:
            if not p.get(field):
                errors.append(f"{pid}: missing or empty required field {field!r}")

        if p.get("category") not in CATEGORIES:
            errors.append(f"{pid}: unknown category {p.get('category')!r}")
        if p.get("difficulty") not in DIFFICULTIES:
            errors.append(f"{pid}: unknown difficulty {p.get('difficulty')!r}")

        year = p.get("year")
        if not isinstance(year, int) or not 1800 < year <= 2100:
            errors.append(f"{pid}: implausible year {year!r}")
        # year_milestone is optional while the dataset is being labelled, but
        # if present it must name one of the four milestones.
        milestone = p.get("year_milestone")
        if milestone and milestone not in YEAR_MILESTONES:
            errors.append(f"{pid}: unknown year_milestone {milestone!r} (expected one of {sorted(YEAR_MILESTONES)})")

        for rel in p.get("related", []):
            if rel not in ids:
                errors.append(f"{pid}: related -> unknown id {rel!r}")
        if pid in p.get("related", []):
            errors.append(f"{pid}: related contains itself")

        frame_fields = p.get("frame_fields") or []
        if frame_fields:
            names = [f.get("name") for f in frame_fields]
            if len(set(names)) != len(names):
                errors.append(
                    f"{pid}: duplicate frame field names {names} — this makes "
                    f"generate_frame_order_puzzle unsolvable from field names alone"
                )
            if len(frame_fields) < 2:
                errors.append(
                    f"{pid}: only {len(frame_fields)} frame field(s) — "
                    f"generate_frame_order_puzzle cannot produce a scramble"
                )
            for f in frame_fields:
                bits = f.get("bits")
                if not isinstance(bits, (int, str)) or bits == "":
                    errors.append(f"{pid}: frame field {f.get('name')!r} has bad bits {bits!r}")

        # Frame structures: every protocol must either declare frame_fields or be
        # registered in frame_specs.NO_FIXED_FRAME. Without this, a protocol can
        # silently ship with no frame layout and no explanation, which reads as
        # "no data" instead of "carrier-defined" in the Encyclopedia.
        frame_fields = p.get("frame_fields") or []
        if not frame_fields and pid not in NO_FIXED_FRAME:
            errors.append(
                f"{pid}: no frame_fields and not listed in NO_FIXED_FRAME — add a frame "
                f"layout to frame_specs.py or mark it as having no fixed frame"
            )
        if not p.get("frame_note", "").strip():
            errors.append(f"{pid}: missing or empty frame_note")

        # Every protocol has an explicit hardware/electrical profile. Fields are
        # strings (or a list of notes) so logical/RF protocols can accurately
        # say "not defined" instead of inventing a voltage.
        technical = p.get("technical")
        if not isinstance(technical, dict):
            errors.append(f"{pid}: missing technical profile object")
        else:
            for field in (
                "scope",
                "signaling",
                "logic_high",
                "logic_low",
                "voltage_reference",
                "clocking",
                "termination_and_biasing",
            ):
                if not isinstance(technical.get(field), str) or not technical[field].strip():
                    errors.append(f"{pid}: technical.{field} is missing or empty")
            notes = technical.get("design_notes")
            if not isinstance(notes, list) or not notes or not all(isinstance(n, str) and n.strip() for n in notes):
                errors.append(f"{pid}: technical.design_notes must be a non-empty list of strings")
            # Interface silicon list: optional per protocol, but when present it
            # must be a list of non-empty strings (a bare string would render
            # character-by-character in the UI).
            transceivers = technical.get("transceivers", [])
            if not isinstance(transceivers, list) or not all(isinstance(t, str) and t.strip() for t in transceivers):
                errors.append(f"{pid}: technical.transceivers must be a list of non-empty strings")

        # Physical wiring: every protocol must expose a signals list, and each
        # signal must name its direction. A missing list renders as an empty
        # pinout, which reads as "this protocol has no wires" - usually wrong.
        signals = p.get("signals")
        if not isinstance(signals, list) or not signals:
            errors.append(f"{pid}: no signals — every protocol needs documented wiring")
        else:
            for sig in signals:
                if not sig.get("name") or not sig.get("dir"):
                    errors.append(f"{pid}: signal {sig!r} missing name/direction")
                if sig.get("dir") not in {"O", "I", "B", "I/O", "P", "G", "-"}:
                    errors.append(f"{pid}: signal {sig.get('name')!r} has bad direction {sig.get('dir')!r}")

        # Command tables are optional (many protocols have none), but when
        # present each row needs a code and a name.
        for cmd in p.get("commands", []):
            if not cmd.get("code") or not cmd.get("name"):
                errors.append(f"{pid}: command entry missing code/name: {cmd!r}")

        # Electrical specs must be physically coherent. A differential pair whose
        # swing is zero would render as a flat line and teach the wrong thing,
        # and a common mode below the swing would push one rail negative.
        spec = p.get("electrical") or {}
        if spec:
            signaling = spec.get("signaling")
            vhi, vlo = spec.get("vdiff_high_volts"), spec.get("vdiff_low_volts")
            if signaling in ("differential", "bipolar"):
                if vhi is None or vlo is None:
                    errors.append(f"{pid}: {signaling} spec missing Vdiff levels")
                else:
                    # The receiver thresholds Vdiff, so a negative rail is only
                    # a problem when a nonzero common mode is specified (e.g.
                    # USB at 3.0 V). RS-485 at VCM 0 is legitimately bipolar.
                    vcm = spec.get("vcm_volts")
                    if vcm and vcm - max(abs(vhi), abs(vlo)) / 2 < 0:
                        errors.append(
                            f"{pid}: VCM {vcm} too low for swing, a rail goes negative")
                    for pr in spec.get("pairs", []):
                        if not pr.get("a") or not pr.get("b"):
                            errors.append(f"{pid}: differential pair missing a/b: {pr}")
                        if pr.get("role") not in ("transmit", "receive", "bidirectional"):
                            errors.append(f"{pid}: bad pair role {pr.get('role')!r}")
            if signaling == "rf":
                if not spec.get("impedance_ohm"):
                    errors.append(f"{pid}: RF spec must state the match impedance")
            for field in ("rise_time_ns", "bit_period_ns"):
                v = spec.get(field)
                if v is not None and v <= 0:
                    errors.append(f"{pid}: {field} must be positive, got {v}")

        # An unsourced fun_fact is how a wrong fun_fact gets published.
        if p.get("fun_fact") and not p.get("fun_fact_source"):
            errors.append(f"{pid}: fun_fact is set but fun_fact_source is missing")

        # Machine-readable parametric envelope (parametric.py). Numeric fields
        # are numbers or None (None = defined by the carrier, not here).
        for field in ("data_rate_min_bps", "data_rate_max_bps", "distance_max_m", "nodes_max"):
            value = p.get(field)
            # data_rate_min_bps is reserved for future use; only the max and
            # the rest are populated today.
            if field == "data_rate_min_bps":
                if value is not None:
                    errors.append(f"{pid}: {field} is reserved (must stay None for now)")
                continue
            if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0):
                errors.append(f"{pid}: {field} must be a positive number or None, got {value!r}")
        rmin, rmax = p.get("data_rate_min_bps"), p.get("data_rate_max_bps")
        if rmin is not None and rmax is not None and rmin > rmax:
            errors.append(f"{pid}: data_rate_min_bps exceeds data_rate_max_bps")
        if p.get("lifecycle") not in ("emerging", "active", "mature", "legacy"):
            errors.append(f"{pid}: unknown lifecycle {p.get('lifecycle')!r}")
        for field in ("osi_layer", "standard_doc"):
            if not isinstance(p.get(field), str) or not p[field].strip():
                errors.append(f"{pid}: missing or empty parametric field {field!r}")

    return errors


def check_schema(protocols):
    """Validate against docs/protocol-database/schema.json.

    This is the same file the pre-commit `check-jsonschema` hook uses, so the
    structural contract is enforced identically locally and in CI. Skipped with
    a clear message if jsonschema is unavailable rather than failing the gate.
    """
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("note: jsonschema not installed - skipping schema validation")
        return []

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"schema at {SCHEMA_PATH} could not be read: {exc}"]

    errors = []
    for err in Draft202012Validator(schema).iter_errors(protocols):
        where = "/".join(str(part) for part in err.absolute_path) or "<root>"
        errors.append(f"schema violation at {where}: {err.message}")
    return errors


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        protocols = json.load(f)

    if not isinstance(protocols, list):
        print(f"::error::{DATA_PATH} must contain a JSON array")
        return 1

    errors = check(protocols) + check_schema(protocols)
    if errors:
        for e in errors:
            print(f"::error::{e}")
        print(f"\n{len(errors)} data integrity error(s)", file=sys.stderr)
        return 1

    ids = {p["id"] for p in protocols}
    cats = Counter(p["category"] for p in protocols)
    print(f"Data integrity OK: {len(protocols)} protocols, {len(ids)} unique ids, {len(cats)} categories")
    for cat, n in sorted(cats.items()):
        print(f"  {cat}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
