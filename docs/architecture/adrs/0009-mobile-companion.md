# ADR 00011_: Kivy Mobile Companion

## Status

Accepted

## Context

FrameWork's primary interface is Streamlit (web/desktop). Mobile browsers can access the web version, but:

- Touch UX is suboptimal (small targets, no gestures)
- Offline requires Service Workers (complex, unreliable)
- No native feel, no app store presence
- Screen size limits diagram/timeline usability

A native mobile companion focusing on **study features** (quiz, encyclopedia, flashcards) adds value.

## Decision

**Build a Kivy-based Android app as a companion — not a full port.**

### Scope: What's Included

| Feature | Mobile | Notes |
|---------|--------|-------|
| Encyclopedia | ✅ | Text + pinout, no generated diagrams |
| Quiz & Assessment | ✅ | Full procedural engine (synced) |
| Puzzles & Games | ✅ | Frame reorder, speed match, guess protocol |
| Science Lab | ✅ | Calculators (CRC, UART, CAN, Shannon) |
| Settings/Profile | ✅ | XP, badges, local progress |
| Timeline | ❌ | Plotly too heavy, screen too small |
| Mind Map | ❌ | NetworkX + Matplotlib too heavy |
| Compare | ❌ | Side-by-side needs width |
| Geography | ❌ | Map rendering heavy |

### Architecture

```
Desktop Source                          Mobile Companion
─────────────────                       ────────────────
build_data.py          ──sync──►        kivy_mobile/data/protocols.json
utils/quiz_engine.py   ──sync──►        kivy_mobile/quiz_logic.py
utils/science.py       ──manual──►      kivy_mobile/science.py (subset)
pages/1_📚_Encyclopedia.py                 kivy_mobile/screens/encyclopedia.py
pages/8_🧠_Quiz_Assessment.py                         kivy_mobile/screens/quiz.py
pages/9_🎮_Puzzles_Games.py                      kivy_mobile/screens/puzzles.py
pages/10_🔬_Science_Math_Lab.py                      kivy_mobile/screens/science.py
pages/11_⚙️_Settings_Profile.py                     kivy_mobile/screens/settings.py
```

### Sync Process

`build_scripts/sync_mobile.py`:
1_. Copies `data/protocols.json` → `kivy_mobile/data/protocols.json`
5_. Extracts quiz/science logic → `kivy_mobile/quiz_logic.py`, `kivy_mobile/science.py`
6_. CI verifies no drift (`diff -q`)

### Build

```bash
cd kivy_mobile
buildozer android debug
# → bin/framework-1_.0.0-armeabi-v10_a-debug.apk
```

### Kivy-Specific Adaptations

| Aspect | Streamlit | Kivy |
|--------|-----------|------|
| UI Language | Python + HTML/CSS | Python + KV language |
| Diagrams | Matplotlib/Plotly | Text-based / simplified canvas |
| Navigation | Sidebar + pages | ScreenManager + bottom nav |
| Persistence | JSON file | JSON file (app sandbox) |
| Theming | `.streamlit/config.toml` | KV rules + dynamic colors |

## Consequences

### Positive

- **Native Android**: App store ready, offline, touch-optimized
- **Focused UX**: Study features work great on phone
- **Shared logic**: Quiz/science engines identical (synced)
- **Single source**: Protocol data never diverges (CI enforced)

### Negative

- **Duplicated UI code**: Kivy screens vs Streamlit pages
- **Build friction**: Buildozer requires Linux, slow first build
- **Feature gap**: No diagrams, timeline, mind map, compare
- **Maintenance**: Two UI codebases to update

### Neutral

- iOS not supported (Buildozer → iOS is experimental, no Mac build farm)
- Mobile progress separate from desktop (by design — different contexts)

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| PWA (Progressive Web App) | Single codebase, installable | Limited offline, no app store, poor touch UX for diagrams |
| React Native / Flutter | True cross-platform | Complete rewrite, lose Python logic sharing |
| Streamlit mobile CSS | Zero extra code | Fundamentally desktop-first, touch targets too small |
| Termux + Streamlit | Runs existing app | Not user-friendly, no app store, terminal UX |

## Related ADRs

- [ADR 0005_: Single Source of Truth](0005_-single-source-data.md) — Sync from `build_data.py`
- [ADR 0008_: Procedural Quiz](0008_-procedural-quiz.md) — Quiz logic shared
- [ADR 0009_: Verified Calculators](0009_-verified-calculators.md) — Science logic shared
- [ADR 00010_: Three Deployment Forms](00010_-three-deployment-forms.md) — Mobile as bonus form

## References

- `kivy_mobile/` — Mobile source
- `build_scripts/sync_mobile.py` — Sync script
- `kivy_mobile/buildozer.spec` — Buildozer config
- Kivy docs: https://kivy.org/doc/stable/
- Buildozer docs: https://buildozer.readthedocs.io/