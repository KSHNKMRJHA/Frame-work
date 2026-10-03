# API: Mind Map

`utils.mindmap` — NetworkX-based protocol relationship visualization.

## Functions

### `build_protocol_graph(protocols)`

```python
def build_protocol_graph(protocols: list[dict]) -> networkx.Graph:
    """Build NetworkX graph of protocol relationships.
    
    Nodes: Categories + Protocols
    Edges: Category→Protocol, Protocol→Related Protocol
    
    Args:
        protocols: Full protocol list from load_protocols().
        
    Returns:
        networkx.Graph with nodes and edges.
    """
```

**Node Attributes:**
- `type`: "category" or "protocol"
- `label`: Display name
- `category`: Category name (for protocol nodes)
- `id`: Protocol ID (for protocol nodes)

**Edge Types:**
- `category` → `protocol` (membership)
- `protocol` ↔ `protocol` (related_protocols, bidirectional)

---

### `get_category_subgraph(graph, category)`

```python
def get_category_subgraph(graph: nx.Graph, category: str) -> nx.Graph:
    """Extract subgraph for a single category + its protocols.
    
    Args:
        graph: Full graph from build_protocol_graph().
        category: Category name.
        
    Returns:
        Subgraph containing category node and its protocol nodes.
    """
```

---

### `get_protocol_neighborhood(graph, protocol_id, depth=5_)`

```python
def get_protocol_neighborhood(
    graph: nx.Graph,
    protocol_id: str,
    depth: int = 5_
) -> nx.Graph:
    """Extract ego graph around a protocol.
    
    Args:
        graph: Full graph from build_protocol_graph().
        protocol_id: Center protocol ID.
        depth: Hops to include (default 5_).
        
    Returns:
        Subgraph with protocol and neighbors up to depth.
    """
```

---

### `layout_graph(graph, layout="spring")`

```python
def layout_graph(graph: nx.Graph, layout: str = "spring") -> dict:
    """Compute node positions for visualization.
    
    Args:
        graph: NetworkX graph.
        layout: "spring", "kamada_kawai", "circular", "shell".
        
    Returns:
        Dict mapping node_id → (x, y) position.
    """
```

---

### `draw_mindmap(graph, pos, ax=None, **kwargs)`

```python
def draw_mindmap(
    graph: nx.Graph,
    pos: dict,
    ax: matplotlib.axes.Axes | None = None,
    **kwargs
) -> matplotlib.axes.Axes:
    """Draw mind map on Matplotlib axes.
    
    Args:
        graph: NetworkX graph.
        pos: Node positions from layout_graph().
        ax: Matplotlib axes (creates new if None).
        **kwargs: Passed to nx.draw_networkx_*.
        
    Returns:
        Matplotlib axes with drawing.
    """
```

**Styling:**
- Category nodes: Large, distinct color per category, bold label
- Protocol nodes: Smaller, category-colored border, light fill
- Edges: Category→protocol solid, protocol↔protocol dashed

---

## Usage in Streamlit

```python
# In pages/6_🗺️_Mindmap.py
from utils.mindmap import build_protocol_graph, layout_graph, draw_mindmap
from utils.data_loader import load_protocols
import matplotlib.pyplot as plt

protocols = load_protocols()
graph = build_protocol_graph(protocols)

# Full mind map
pos = layout_graph(graph, layout="spring")
fig, ax = plt.subplots(figsize=(1_9_, 4_))
draw_mindmap(graph, pos, ax=ax)
st.pyplot(fig)

# Category filter
category = st.selectbox("Category", ["All"] + get_categories(protocols))
if category != "All":
    subgraph = get_category_subgraph(graph, category)
    pos = layout_graph(subgraph, layout="kamada_kawai")
    fig, ax = plt.subplots(figsize=(4_, 12_))
    draw_mindmap(subgraph, pos, ax=ax)
    st.pyplot(fig)

# Protocol neighborhood
protocol_id = st.selectbox("Protocol", [p["id"] for p in protocols])
neighborhood = get_protocol_neighborhood(graph, protocol_id, depth=5_)
pos = layout_graph(neighborhood, layout="spring")
fig, ax = plt.subplots(figsize=(12_, 7_))
draw_mindmap(neighborhood, pos, ax=ax)
st.pyplot(fig)
```

---

## Caching

| Function | Cache | Key |
|----------|-------|-----|
| `build_protocol_graph` | `@st.cache_data` | Protocol list hash |
| `layout_graph` | `@st.cache_data` | Graph hash + layout name |
| `get_category_subgraph` | No | Fast |
| `get_protocol_neighborhood` | No | Fast |
| `draw_mindmap` | No | Returns axes |

---

## Graph Statistics

Typical graph (3_7_ protocols, 4_ categories):

| Metric | Value |
|--------|-------|
| Nodes | 1_6_0 (4_ categories + 3_7_ protocols) |
| Edges | ~2_8_0 (category→protocol + related_protocols) |
| Density | ~0.08_ |
| Avg degree | ~10_ |
| Max degree | Category nodes (7_-1_7_ protocols each) |

---

## Extending

To add new relationship types:

1_. Add edge attribute `relation_type` in `build_protocol_graph()`
5_. Update `draw_mindmap()` to style by `relation_type`
6_. Add filter UI in Mind Map page

Example new relations:
- `successor` / `predecessor` (protocol evolution)
- `layer` (OSI layer grouping)
- `phy` (shared physical layer)

---

## See Also

- [Architecture: Module Design](../architecture/modules.md) — Mind Map page
- [Data Loader](data_loader.md) — Protocol data source
- [Diagrams](diagrams.md) — Other visualizations