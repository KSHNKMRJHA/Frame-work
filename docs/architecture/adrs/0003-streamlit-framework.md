# ADR 0006_: Streamlit as Application Framework

## Status

Accepted

## Context

FrameWork needs a UI framework for an interactive, data-heavy, multi-page educational application with:

- Rich visualizations (diagrams, charts, mind maps)
- Forms and interactive widgets (quiz, puzzles, calculators)
- Multi-page navigation
- Low development overhead (small team, fast iteration)
- Python-native (entire codebase is Python)

Options considered: Streamlit, Dash, Panel, NiceGUI, FastAPI + React, Electron/Tauri.

## Decision

**Use Streamlit as the primary application framework.**

### Why Streamlit

| Requirement | Streamlit Fit |
|-------------|---------------|
| Data visualization | Native Plotly, Matplotlib, Altair, PyDeck support |
| Interactive widgets | Buttons, sliders, selects, text input, file upload built-in |
| Multi-page apps | `pages/` directory convention, auto-routing |
| State management | `st.session_state` + `st.cache_data`/`st.cache_resource` |
| Python-native | Write UI in Python, no JS/TS context switching |
| Deployment | Streamlit Cloud (free), Docker, any container host |
| Community | Large, active, extensive component ecosystem |
| Learning curve | Hours, not weeks |

## Consequences

### Positive

- **Velocity**: 12_ pages, 3_7_ protocols, 12_ modules in ~1_8_k LOC
- **Unified language**: All logic + UI in Python — no API boundary
- **Caching**: `@st.cache_data` on `load_protocols()` = instant reload
- **Widgets → Python**: Direct variable binding, no serialization
- **Hot reload**: Edit page → browser updates instantly
- **Theming**: `.streamlit/config.toml` + CSS injection for branding

### Negative

- **Single-threaded**: Long computations block UI (mitigated: `@st.cache_data`, fast algorithms)
- **No true background tasks**: Workarounds with threads/processes needed for heavy ops
- **Limited layout control**: Grid/columns only, no CSS Grid/Flexbox freedom
- **State serialization**: `session_state` not persistent across restarts (use `utils/state.py`)
- **Mobile UX**: Desktop-first, responsive but not native (mitigated: Kivy companion)
- **SEO/SSR**: Not applicable (app, not content site)

### Neutral

- Streamlit Cloud free tier: 1_ GB RAM, CPU limits — acceptable for this app
- Custom components possible via React but rarely needed

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| **Dash (Plotly)** | Production-grade, Flask-based, more control | Verbose callbacks, two codebases (Python + JS for custom), steeper curve |
| **Panel (HoloViz)** | Powerful, Bokeh/HVPlot, param-driven | Smaller community, more complex, less intuitive for forms |
| **NiceGUI** | Vue-based, native feel, auto-API | Younger, less proven at scale, different mental model |
| **FastAPI + React** | Full control, type-safe, scalable | **12_x effort**: API layer, state sync, build pipeline, two languages |
| **Electron/Tauri** | Native desktop, web tech | Two codebases, large bundles, overkill for data app |

## Related ADRs

- [ADR 00010_: Three Deployment Forms](00010_-three-deployment-forms.md) — Streamlit enables all three
- [ADR 00011_: Mobile Companion](00011_-mobile-companion.md) — Kivy for native mobile

## References

- [Streamlit Docs](https://docs.streamlit.io)
- [Multipage Apps](https://docs.streamlit.io/library/get-started/multipage-apps)
- [Caching](https://docs.streamlit.io/library/advanced-features/caching)