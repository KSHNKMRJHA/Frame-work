# API: Data Loader

`utils.data_loader` — Protocol database loading, search, and filtering utilities.

## Functions

### `load_protocols()`

```python
@st.cache_data(show_spinner=False)
def load_protocols() -> list[dict]:
    """Load and cache the protocol database from data/protocols.json.
    
    Returns:
        List of protocol dicts (118 entries). Cached via @st.cache_data.
    """
```

**Returns:** `list[dict]` — All protocols with full schema (see [Schema](../protocol-database/schema.md))

**Caching:** Decorated with `@st.cache_data` — loads once per session.

---

### `get_categories(protocols)`

```python
def get_categories(protocols: list[dict]) -> list[str]:
    """Extract sorted unique categories from protocol list.
    
    Args:
        protocols: List from load_protocols()
        
    Returns:
        Sorted list of 12 category strings.
    """
```

**Returns:** `list[str]` — `["Aerospace", "Audio/Video", "Automotive", "Cellular", "High-Speed/FPGA", "Industrial", "Networking", "On-Board", "Security", "Sensor-Specific", "USB", "Wireless"]`

---

### `search_protocols(protocols, query)`

```python
def search_protocols(
    protocols: list[dict],
    query: str
) -> list[dict]:
    """Search protocols by name, keyword, inventor, or year.
    
    Args:
        protocols: List from load_protocols()
        query: Search string (case-insensitive, partial match)
        
    Returns:
        Filtered list of matching protocols.
    """
```

**Search Fields:** `name`, `description`, `inventor`, `organization`, `year` (as string), `category`, `use_cases`, `technical` profile fields

**Example:**
```python
results = search_protocols(protocols, "CAN")      # CAN, CAN FD, CANopen
results = search_protocols(protocols, "1996")     # Protocols from 1996
results = search_protocols(protocols, "Bosch")    # Bosch-invented protocols
```

---

### `get_by_id(protocols, protocol_id)`

```python
def get_by_id(protocols: list[dict], protocol_id: str) -> dict | None:
    """Get single protocol by ID.
    
    Args:
        protocols: List from load_protocols()
        protocol_id: Protocol ID (e.g., "uart", "can-fd")
        
    Returns:
        Protocol dict or None if not found.
    """
```

---

## Usage in Streamlit Pages

```python
# Typical page header
from utils.data_loader import load_protocols, get_categories, search_protocols

protocols = load_protocols()
categories = get_categories(protocols)

# Search box
query = st.text_input("Search protocols...")
if query:
    results = search_protocols(protocols, query)
    # Display results...
```

---

## Caching Behavior

| Function | Cache | Invalidation |
|----------|-------|--------------|
| `load_protocols()` | `@st.cache_data` | File mtime change |
| `get_categories()` | No | N/A (fast) |
| `search_protocols()` | No | N/A (fast) |
| `get_by_id()` | No | N/A (fast) |

---

## Error Handling

- `load_protocols()` raises `FileNotFoundError` if `data/protocols.json` missing
- `search_protocols()` returns empty list on no matches (no exception)
- All functions assume valid protocol schema (validated by `check_data.py`)

---

## See Also

- [Protocol Database Schema](../protocol-database/schema.md)
- [Adding Protocols](../protocol-database/adding-protocols.md)
- [Quiz Engine](quiz_engine.md) — Uses data_loader for question generation