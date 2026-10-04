# -*- coding: utf-8 -*-
"""Deterministic, offline origin normalisation for protocol `place` strings.

FrameWork is offline-first: nothing here may call a geocoding service. Every
mapping is a static table, so the same input always produces the same country.

Why this module exists
----------------------
The Geography page used to do::

    place.split("/")[0].split(",")[0].strip()

which assumes the FIRST token of a place string is a country. That is wrong for
any "City, State, Country" value - "Cambridge, Massachusetts, USA" became
"Cambridge", a place with no map entry, and the protocol silently vanished from
the choropleth. This resolver reads the whole string, understands aliases and
city/region qualifiers, and - importantly - reports what it could NOT resolve
instead of dropping the record.
"""

import re

MAPPED = "mapped"
INTERNATIONAL = "international"
UNKNOWN = "unknown"

UNKNOWN_LABEL = "Unknown / insufficient data"

# Canonical country name -> name Plotly's "country names" mode expects.
COUNTRIES = {
    "United States": "United States",
    "United Kingdom": "United Kingdom",
    "Netherlands": "Netherlands",
    "Japan": "Japan",
    "France": "France",
    "Germany": "Germany",
    "Canada": "Canada",
    "Austria": "Austria",
    "Switzerland": "Switzerland",
    "Sweden": "Sweden",
    "Finland": "Finland",
    "Denmark": "Denmark",
    "Belgium": "Belgium",
    "Norway": "Norway",
    "South Korea": "South Korea",
    "Italy": "Italy",
    "Spain": "Spain",
    "India": "India",
    "China": "China",
    "Brazil": "Brazil",
    "Australia": "Australia",
    "Ireland": "Ireland",
    "Poland": "Poland",
    "Russia": "Russia",
    "Israel": "Israel",
}

# Tokens that mean "not attributable to one country".
REGIONAL_TOKENS = {
    "international": "International",
    "global": "International",
    "worldwide": "International",
    "europe": "Europe (multi-country)",
    "european": "Europe (multi-country)",
}

ALIASES = {
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s": "United States",
    "u.s.a.": "United States",
    "u.s.a": "United States",
    "united states": "United States",
    "united states of america": "United States",
    "america": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "northern ireland": "United Kingdom",
    "czech republic": "Czechia",
    "czechia": "Czechia",
    "republic of korea": "South Korea",
    "korea": "South Korea",
    "russian federation": "Russia",
    "the netherlands": "Netherlands",
    "holland": "Netherlands",
}

# City / region -> country. Deliberately small and explicit: FrameWork must not
# guess, so only entries the dataset (and the documented example) can produce.
CITY_TO_COUNTRY = {
    "cambridge": "United States",
    "massachusetts": "United States",
    "silicon valley": "United States",
    "palo alto": "United States",
    "san jose": "United States",
    "austin": "United States",
    "seattle": "United States",
    "new york": "United States",
    "boston": "United States",
    "menlo park": "United States",
    "hillsboro": "United States",
    "st petersburg": "Russia",
    "zurich": "Switzerland",
    "geneva": "Switzerland",
    "cern": "Switzerland",
    "lausanne": "Switzerland",
    "haifa": "Israel",
    "bangalore": "India",
    "bengaluru": "India",
}

_PAREN = re.compile(r"\(([^)]*)\)")
_SLASH_SPLIT = re.compile(r"[/;]| and ")


def _clean(token):
    return token.strip().strip(".,").strip()


def _match_country_token(token):
    """Resolve one comma-free token to a canonical country, or None."""
    t = _clean(token).lower()
    if not t:
        return None
    if t in REGIONAL_TOKENS:
        return REGIONAL_TOKENS[t]
    if t in ALIASES:
        return ALIASES[t]
    for canon in COUNTRIES:
        if t == canon.lower():
            return canon
    if t in CITY_TO_COUNTRY:
        return CITY_TO_COUNTRY[t]
    return None


def _resolve_segment(segment):
    """Resolve a segment, which may itself be "City, State, Country".

    The country is conventionally LAST in that form, so segments are tried
    right-to-left first: that is what turns "Cambridge, Massachusetts, USA"
    into "United States" rather than "Cambridge". Trying every part, not just
    the first, is the whole fix.
    """
    parts = [_clean(p) for p in segment.split(",") if _clean(p)]
    if not parts:
        return None
    for part in reversed(parts):
        hit = _match_country_token(part)
        if hit:
            return hit
    return None


def resolve_origin(place):
    """Classify one protocol `place` string.

    Returns kind (mapped | international | unknown), the display label, every
    country named, and any parenthetical note preserved for display. Nothing
    raises and nothing is discarded: an unrecognised string becomes UNKNOWN
    rather than vanishing from the map and the totals.
    """
    raw = place or ""
    notes = _PAREN.findall(raw)
    base = _PAREN.sub("", raw).strip()

    countries, regional, unresolved = [], [], []
    segments = [s for s in _SLASH_SPLIT.split(base) if _clean(s)]
    for seg in segments:
        hit = _resolve_segment(seg)
        if hit is None:
            unresolved.append(_clean(seg))
        elif hit in ("International", "Europe (multi-country)"):
            regional.append(hit)
        else:
            countries.append(hit)

    countries = list(dict.fromkeys(countries))
    regional = list(dict.fromkeys(regional))
    note = "; ".join(n.strip() for n in notes if n.strip())

    if regional or len(countries) > 1:
        if len(countries) == 1 and regional:
            label = f"{countries[0]} + {regional[0]}"
        elif len(countries) == 1:
            label = countries[0]
        else:
            label = regional[0] if regional else " / ".join(countries)
        kind = INTERNATIONAL
    elif len(countries) == 1:
        label, kind = countries[0], MAPPED
    else:
        label, kind = UNKNOWN_LABEL, UNKNOWN

    return {
        "kind": kind,
        "label": label,
        "countries": countries,
        "regions": regional,
        "note": note,
        "unresolved": unresolved or ([_clean(base)] if base and not countries else []),
    }


def iso_name(country):
    """Canonical name for the choropleth, or None if it has no polygon."""
    return COUNTRIES.get(country)


def summarize(protocols):
    """Bucket every protocol into mapped / international / unknown.

    The three counts always sum to len(protocols) - nothing is silently
    dropped, which is exactly what the old alias-table-only choropleth did.

    ``per_country`` is separate and deliberately broader: it includes every
    CONCRETE country named, including inside a multi-country entry. KNX is
    recorded as "Belgium/Germany", so it is accounted as international but still
    shades Belgium and Germany on the map. Buckets describe provenance; the map
    describes geography.
    """
    mapped, international, unknown = [], [], []
    per_country = {}

    for p in protocols:
        info = resolve_origin(p.get("place", ""))
        info["protocol"] = p

        if info["kind"] == MAPPED:
            mapped.append(info)
        elif info["kind"] == INTERNATIONAL:
            international.append(info)
        else:
            unknown.append(info)

        for country in info["countries"]:
            per_country.setdefault(country, []).append(p)

    return {
        "mapped": mapped,
        "international": international,
        "unknown": unknown,
        "per_country": per_country,
        "total": len(protocols),
        "mapped_count": len(mapped),
        "international_count": len(international),
        "unknown_count": len(unknown),
    }
