# ADR 0001: Offline-First Architecture

## Status

Accepted

## Context

FrameWork is an educational tool for embedded communication protocols. Target users include students, hobbyists, and engineers who may:

- Work in labs with restricted internet
- Use air-gapped development machines
- Need privacy (no telemetry, no accounts)
- Want guaranteed availability without service dependencies

Traditional web apps require connectivity, accounts, and server infrastructure — all barriers for this use case.

## Decision

**FrameWork is offline-first by default:**

1. **No network calls** in the core application — all data, logic, and assets are local
2. **No user accounts** — progress stored in local JSON file (`data/user_state.json`)
3. **No telemetry** — zero tracking, analytics, or phone-home
4. **Self-contained distribution** — single `.exe` (Windows) or binary (macOS/Linux) runs without installer
5. **Web deployment is optional** — same code runs on Streamlit Cloud for convenience, but local is primary

## Consequences

### Positive

- **Zero friction**: `pip install && streamlit run` — works immediately
- **Privacy**: No data leaves the machine
- **Reliability**: Works on air-gapped systems, planes, secure labs
- **Portability**: USB-stick runnable, no install needed for `.exe`
- **Simplicity**: No backend, database, auth, session management, scaling concerns

### Negative

- **No cloud sync**: Progress tied to machine/file (mitigated by JSON export/import)
- **No collaborative features**: Single-user by design
- **Manual updates**: User must pull/rebuild for new content
- **Web version limitations**: Streamlit Cloud has resource limits, no file persistence

### Neutral

- Local-first doesn't mean local-only — web deployment shares same codebase
- JSON progress file is human-readable and portable

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| Traditional web app (Django/FastAPI + React) | Cloud sync, multi-user, real-time | Requires server, DB, auth, hosting, internet |
| Electron/Tauri desktop app | Native feel, offline | Larger bundle, more complex build, two codebases |
| Progressive Web App (PWA) | Installable, offline cache | Still needs initial online, service worker complexity |

## Related ADRs

- [ADR 0008: Atomic JSON Persistence](0008-atomic-persistence.md) — How local state is saved safely
- [ADR 0007: Three Deployment Forms](0007-three-deployment-forms.md) — Local, desktop, web

## References

- [Offline-First Manifesto](https://offlinefirst.org/)
- Streamlit architecture: single-process, no backend needed