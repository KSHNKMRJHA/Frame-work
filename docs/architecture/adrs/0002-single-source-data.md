# ADR 0002: Single Source of Truth — build_data.py

## Status

Accepted

## Context

FrameWork has 118 protocols across 12 categories, each with 20+ fields. This data drives:

- Encyclopedia (full profiles)
- Timeline (year, inventor, country)
- Mind Map (categories, relationships)
- Compare (side-by-side fields)
- Quiz (procedural questions from fields)
- Puzzles (frame fields, speed matching)
- Science Lab (electrical params for calculators)
- Geography (country, organization)
- Mobile companion (synced subset)

Maintaining this data in multiple places (JSON + Python + mobile copy) guarantees drift.

## Decision

**All protocol content lives in `build_data.py` as structured Python `add(...)` calls.** Running it regenerates `data/protocols.json`, which is the single runtime artifact consumed by all modules.

### Implementation

```python
# build_data.py
def add(*, id, name, category, year, inventor, country, organization,
        description, speed, topology, difficulty, pins, frame, electrical,
        use_cases, advantages, limitations, related_protocols,
        fun_fact="", standards=None, tags=None):
    # Validates, normalizes, appends to in-memory list
    ...

# 118 calls to add(...)
add(id="uart", name="UART", category="On-Board", year=1960, ...)
add(id="spi", name="SPI", category="On-Board", year=1979, ...)
# ...

if __name__ == "__main__":
    # Write protocols.json with deterministic ordering
    write_json(PROTOCOLS, "data/protocols.json")
```

### Enforcement

CI verifies reproducibility:

```bash
cp data/protocols.json /tmp/committed.json
python build_data.py
diff -u /tmp/committed.json data/protocols.json  # Must be empty
```

Mobile companion sync:

```bash
python build_scripts/sync_mobile.py
diff data/protocols.json kivy_mobile/data/protocols.json  # Must be empty
```

## Consequences

### Positive

- **Zero drift**: Encyclopedia, quiz, mind map, diagrams, timeline, geography, mobile all consistent
- **Type safety**: Python validates structure at edit time (vs. JSON syntax errors at runtime)
- **Diff-friendly**: Git shows semantic changes (`year=1986` → `year=1987`) not JSON noise
- **IDE support**: Autocomplete, refactoring, type checking for protocol entries
- **Single edit point**: Add protocol once, everywhere updated
- **Generative power**: `build_data.py` can compute derived fields, validate cross-refs

### Negative

- **Build step required**: `python build_data.py` after edits (mitigated by CI check)
- **Python required for edits**: Can't edit JSON directly (by design)
- **Learning curve**: Contributors must understand `add()` signature

### Neutral

- `protocols.json` is committed (for web deployment without build step)
- `technical_profiles.py` is separate — implementation details not in main DB

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| JSON only (`protocols.json` as source) | Direct editing, no build step | No validation, drift across modules, poor diffs |
| Database (SQLite) | Queries, relationships | Overkill, not portable, no git diff |
| YAML/TOML files per protocol | Human-readable, modular | Still needs aggregation, validation, sync |
| Headless CMS / Airtable | UI for non-devs | External dependency, offline broken, cost |

## Related ADRs

- [ADR 0001: Offline-First](0001-offline-first.md) — Local JSON enables offline
- [ADR 0009: Mobile Companion](0009-mobile-companion.md) — Sync from single source

## References

- `build_data.py` — Implementation
- `build_scripts/check_data.py` — Validation
- `build_scripts/sync_mobile.py` — Mobile sync