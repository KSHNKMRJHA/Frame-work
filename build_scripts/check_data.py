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
DATA_PATH = os.path.join(ROOT, "data", "protocols.json")

CATEGORIES = {
    "On-Board", "Industrial", "Automotive", "Networking", "Wireless",
    "Cellular", "Audio/Video", "USB", "High-Speed/FPGA",
    "Sensor-Specific", "Security", "Aerospace",
}
DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}
YEAR_MILESTONES = {"invented", "published", "standardized", "deployed"}
REQUIRED = (
    "id", "name", "category", "topology", "year", "inventor", "description",
    "how_it_works", "use_cases", "advantages", "limitations",
    "real_world_example", "difficulty",
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
            errors.append(f"{pid}: unknown year_milestone {milestone!r} "
                          f"(expected one of {sorted(YEAR_MILESTONES)})")

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

        # An unsourced fun_fact is how a wrong fun_fact gets published.
        if p.get("fun_fact") and not p.get("fun_fact_source"):
            errors.append(f"{pid}: fun_fact is set but fun_fact_source is missing")

    return errors


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        protocols = json.load(f)

    if not isinstance(protocols, list):
        print(f"::error::{DATA_PATH} must contain a JSON array")
        return 1

    errors = check(protocols)
    if errors:
        for e in errors:
            print(f"::error::{e}")
        print(f"\n{len(errors)} data integrity error(s)", file=sys.stderr)
        return 1

    ids = {p["id"] for p in protocols}
    cats = Counter(p["category"] for p in protocols)
    print(f"Data integrity OK: {len(protocols)} protocols, {len(ids)} unique ids, "
          f"{len(cats)} categories")
    for cat, n in sorted(cats.items()):
        print(f"  {cat}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
