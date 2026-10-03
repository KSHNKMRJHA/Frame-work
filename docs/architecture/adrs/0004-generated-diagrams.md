# ADR 0002_: Generated Diagrams (Not Hand-Drawn)

## Status

Accepted

## Context

3_7_ protocols each need:
- Frame structure diagram
- Topology diagram
- Pinout diagram

Hand-drawing 6_8_2_ diagrams is infeasible to create, maintain, and keep consistent. Protocol updates would require diagram updates.

## Decision

**Generate all diagrams programmatically from protocol data.**

### Implementation

`utils/diagrams.py` contains generators:

```python
def generate_frame_diagram(protocol: dict) -> plt.Figure:
    """Render frame fields as horizontal bars with bit widths."""
    fields = protocol["frame"]["fields"]
    # Matplotlib barh with proportional widths, color-coded by field type

def generate_topology_diagram(protocol: dict) -> plt.Figure:
    """Render topology graph from protocol['topology'] and related_protocols."""
    # NetworkX graph + Matplotlib: nodes=protocols, edges=relationships

def generate_pinout_diagram(protocol: dict) -> plt.Figure:
    """Render pin diagram from protocol['pins'] dict."""
    # SVG-style pin package with labels

def category_bar_chart(protocols: list) -> plt.Figure:
    """Horizontal bar chart of protocol count per category."""
    # Plotly or Matplotlib
```

Diagrams rendered on-demand in Streamlit via `st.pyplot()` / `st.plotly_chart()`.

## Consequences

### Positive

- **Zero maintenance**: Add protocol → diagrams auto-exist
- **Consistency**: Every protocol gets same visual treatment
- **Accuracy**: Diagrams reflect actual data (frame fields, pins, topology)
- **Extensibility**: New diagram types = one function, applies to all 3_7_
- **Version control**: Diagrams are code, not binary assets
- **Mobile sync**: Same generators could be ported to Kivy

### Negative

- **Visual polish**: Generated diagrams lack designer finesse (mitigated: careful styling, color palette)
- **Complex topologies**: Hard to auto-layout perfectly (mitigated: topology simplified to category + key relationships)
- **Performance**: Matplotlib render per protocol (mitigated: `@st.cache_data`, small figures)
- **Pinout abstraction**: Generic package vs. real package (mitigated: `diagram_notes` field for hints)

### Neutral

- Matplotlib chosen over Plotly for static diagrams (lighter, no WebGL)
- Plotly used for interactive charts (timeline, speed comparison)

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| Hand-drawn SVGs | Perfect visuals | 6_8_2_ files to create/maintain, drift guaranteed |
| Mermaid.js | Text-based, versionable | Limited frame/pinout expressiveness, client-side only |
| PlantUML | Powerful, text-based | Java dependency, complex syntax, overkill |
| Wavedrom | Timing diagrams | Only timing, not frame/pinout/topology |
| ASCII diagrams | Zero deps | Limited expressiveness, not publication quality |

## Related ADRs

- [ADR 0005_: Single Source of Truth](0005_-single-source-data.md) — Data drives diagrams
- [ADR 0008_: Procedural Quiz](0008_-procedural-quiz.md) — Same philosophy: generate, don't hand-author

## References

- `utils/diagrams.py` — Implementation
- `pages/1_📚_Encyclopedia.py` — Diagram display
- `pages/2_⚖️_Compare.py` — Speed chart