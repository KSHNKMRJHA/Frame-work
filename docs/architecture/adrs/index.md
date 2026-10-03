# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for FrameWork.

## What is an ADR?

An **Architecture Decision Record** captures a significant architectural decision, its context, and consequences. ADRs are immutable once written — if a decision changes, a new ADR supersedes the old one.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-offline-first.md) | Offline-First Architecture | Accepted | 2024-01-15 |
| [0002](0002-single-source-data.md) | Single Source of Truth: build_data.py | Accepted | 2024-01-15 |
| [0003](0003-streamlit-framework.md) | Streamlit as Application Framework | Accepted | 2024-01-20 |
| [0004](0004-generated-diagrams.md) | Generated Diagrams (Not Hand-Drawn) | Accepted | 2024-02-01 |
| [0005](0005-procedural-quiz.md) | Procedural Quiz Engine | Accepted | 2024-02-10 |
| [0006](0006-verified-calculators.md) | Verified Engineering Calculators | Accepted | 2024-02-15 |
| [0007](0007-three-deployment-forms.md) | Three Deployment Forms | Accepted | 2024-03-01 |
| [0008](0008-atomic-persistence.md) | Atomic JSON Persistence | Accepted | 2024-03-10 |
| [0009](0009-mobile-companion.md) | Kivy Mobile Companion | Accepted | 2024-04-01 |
| [0010](0010-versioning-build-stamp.md) | Git Commit as Build Number | Accepted | 2024-04-15 |

---

## ADR Template

Use this template for new ADRs. Save as `NNNN-short-title.md` in this directory.

```markdown
# ADR NNNN: Title

## Status

Proposed | Accepted | Superseded | Deprecated

## Context

What is the issue that we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

### Positive

- Benefit 1
- Benefit 2

### Negative

- Drawback 1
- Drawback 2

### Neutral

- Observation 1

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| Option A | ... | ... |
| Option B | ... | ... |

## Related ADRs

- ADR XXXX: Related decision
- ADR YYYY: Superseded by this

## References

- Links to issues, PRs, external docs
```

---

## How to Add an ADR

1. Copy the template above
2. Fill in the next sequential number (0011, 0012, ...)
3. Write the ADR
4. Add entry to the index table above
5. Commit

---

## When to Write an ADR

Write an ADR for decisions that:

- Affect multiple modules or the overall architecture
- Are difficult to reverse
- Have significant trade-offs
- Would confuse future contributors without context
- Involve technology/framework selection

**Don't** write ADRs for:
- Small implementation details
- Decisions already obvious from code
- Temporary workarounds

---

## ADR Status Lifecycle

```
Proposed → Accepted → (Superseded | Deprecated)
```

- **Proposed**: Under discussion, not yet implemented
- **Accepted**: Implemented and current
- **Superseded**: Replaced by a newer ADR (link to it)
- **Deprecated**: No longer relevant, not replaced

---

## Reading ADRs

ADRs are written for **future contributors** (including future you). They answer:

> "Why did we do it this way?"

Not:

> "What did we do?" — that's in the code
> "How does it work?" — that's in docs/code comments

---

## Next Steps

- Read [ADR 0001: Offline-First](0001-offline-first.md)
- Browse all ADRs in this directory
- Propose new ADRs for significant changes