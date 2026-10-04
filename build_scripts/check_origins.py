# -*- coding: utf-8 -*-
"""Regression tests for protocol origin normalisation (Bug #5).

The Geography page used `place.split("/")[0].split(",")[0]`, so
"Cambridge, Massachusetts, USA" resolved to "Cambridge" - not a country, no map
polygon, and the protocol vanished from the choropleth without any warning.

Run: python build_scripts/check_origins.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils import origins  # noqa: E402

DATA = os.path.join(ROOT, "data", "protocols.json")


def _protocols():
    with open(DATA, encoding="utf-8") as fh:
        return json.load(fh)


def test_city_state_country_resolves_to_country():
    """The documented bug case."""
    info = origins.resolve_origin("Cambridge, Massachusetts, USA")
    assert info["label"] == "United States", info
    assert info["kind"] == origins.MAPPED, info


def test_old_parser_would_have_been_wrong():
    """NEGATIVE TEST: the previous implementation must fail this case.

    If the old logic somehow produced the right answer, the regression test
    above would not actually be protecting against the bug.
    """
    place = "Cambridge, Massachusetts, USA"
    old = place.split("/")[0].split(",")[0].strip()   # the removed implementation
    assert old == "Cambridge", f"fixture no longer reproduces the bug (got {old!r})"
    assert old != origins.resolve_origin(place)["label"], (
        "NEGATIVE TEST FAILED: old and new parsers agree, so this case no longer "
        "exercises the fix."
    )


def test_us_and_uk_aliases_normalise():
    for value in ("USA", "US", "United States", "u.s.a."):
        assert origins.resolve_origin(value)["label"] == "United States", value
    for value in ("UK", "United Kingdom", "Britain", "England"):
        assert origins.resolve_origin(value)["label"] == "United Kingdom", value


def test_parliament_qualifier_is_preserved_not_lost():
    info = origins.resolve_origin("Switzerland (CERN)")
    assert info["label"] == "Switzerland", info
    assert "CERN" in info["note"], info


def test_international_entries_are_explicit():
    for value in ("International", "Europe", "Global"):
        info = origins.resolve_origin(value)
        assert info["kind"] == origins.INTERNATIONAL, (value, info)


def test_multi_country_is_classified_and_names_every_country():
    info = origins.resolve_origin("Belgium/Germany")
    assert info["kind"] == origins.INTERNATIONAL, info
    assert set(info["countries"]) == {"Belgium", "Germany"}, info


def test_unresolvable_string_is_reported_not_dropped():
    info = origins.resolve_origin("Somewhere Nowhere Land")
    assert info["kind"] == origins.UNKNOWN, info
    assert info["unresolved"], info


def test_empty_place_does_not_raise():
    for value in ("", None):
        info = origins.resolve_origin(value)
        assert info["kind"] == origins.UNKNOWN, (value, info)


def test_accounting_reconciles_to_every_protocol():
    """mapped + international + unknown must equal the total, exactly."""
    protocols = _protocols()
    s = origins.summarize(protocols)
    total = s["mapped_count"] + s["international_count"] + s["unknown_count"]
    assert s["total"] == len(protocols) == 140
    assert total == 140, (
        f"accounting does not reconcile: {s['mapped_count']} + "
        f"{s['international_count']} + {s['unknown_count']} = {total}"
    )


def test_no_protocol_is_lost_from_the_per_country_index():
    """Every protocol that names a concrete country must be reachable on the map.

    A protocol recorded only as "International" names no country, so it has
    nothing to shade - it is still accounted for, but in the international
    bucket, not the per-country index.
    """
    protocols = _protocols()
    s = origins.summarize(protocols)

    indexed = {p["id"] for plist in s["per_country"].values() for p in plist}
    expected = set()
    for p in protocols:
        if origins.resolve_origin(p.get("place", ""))["countries"]:
            expected.add(p["id"])

    assert indexed == expected, (
        f"{len(indexed)} indexed vs {len(expected)} with a concrete country; "
        f"difference {sorted(indexed ^ expected)[:5]}"
    )
    # And the two groups together must still account for all 140.
    accounted = {info["protocol"]["id"] for info in s["mapped"] + s["international"] + s["unknown"]}
    assert len(accounted) == 140, f"only {len(accounted)} protocols accounted for"

    for country in s["per_country"]:
        assert origins.iso_name(country), f"{country} has no ISO name for the map"


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
        print(f"Origin tests FAILED: {failed} of {len(tests)}")
        sys.exit(1)
    print(f"Origin tests passed ({len(tests)} checks)")
