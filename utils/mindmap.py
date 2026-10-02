# -*- coding: utf-8 -*-
"""
mindmap.py
Builds interactive-feeling mind maps of the protocol universe using networkx
+ matplotlib (no external JS deps needed, works offline in Streamlit).
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

CAT_COLORS = {
    "On-Board": "#2563eb",
    "Industrial": "#059669",
    "Automotive": "#dc2626",
    "Networking": "#7c3aed",
    "Wireless": "#d97706",
    "Cellular": "#0891b2",
    "Audio/Video": "#db2777",
    "USB": "#65a30d",
    "High-Speed/FPGA": "#4f46e5",
    "Sensor-Specific": "#0d9488",
    "Security": "#334155",
    "Aerospace": "#9333ea",
    "Debug & Trace": "#fb7185",
}


def full_mindmap(protocols, root_label="Embedded\nCommunication\nProtocols"):
    """Root -> Category -> Protocol mind map (full universe overview)."""
    G = nx.Graph()
    G.add_node(root_label, kind="root")
    cats = sorted(set(p["category"] for p in protocols))
    for cat in cats:
        G.add_node(cat, kind="cat")
        G.add_edge(root_label, cat)
    for p in protocols:
        G.add_node(p["name"], kind="proto")
        G.add_edge(p["category"], p["name"])

    pos = nx.spring_layout(G, k=0.8, seed=42, iterations=200)
    fig, ax = plt.subplots(figsize=(20, 20), dpi=150)

    root_nodes = [n for n, d in G.nodes(data=True) if d["kind"] == "root"]
    cat_nodes = [n for n, d in G.nodes(data=True) if d["kind"] == "cat"]
    proto_nodes = [n for n, d in G.nodes(data=True) if d["kind"] == "proto"]

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#cbd5e1", width=1.0, alpha=0.6)
    nx.draw_networkx_nodes(G, pos, nodelist=root_nodes, node_color="#0f172a", node_size=4000, ax=ax)
    nx.draw_networkx_nodes(
        G, pos, nodelist=cat_nodes, node_color=[CAT_COLORS.get(c, "#64748b") for c in cat_nodes], node_size=2000, ax=ax
    )
    nx.draw_networkx_nodes(
        G, pos, nodelist=proto_nodes, node_color="#e2e8f0", edgecolors="#94a3b8", node_size=180, ax=ax
    )

    nx.draw_networkx_labels(
        G, pos, labels={n: n for n in root_nodes}, font_size=12, font_color="white", font_weight="bold", ax=ax
    )
    nx.draw_networkx_labels(
        G, pos, labels={n: n for n in cat_nodes}, font_size=10, font_color="white", font_weight="bold", ax=ax
    )
    # Label a subset of protocol nodes with abbreviation to reduce clutter;
    # fall back to showing all if the count is small enough.
    proto_labels = {}
    if len(proto_nodes) > 30:
        # show every third node with a 3-letter abbreviation
        for i, n in enumerate(proto_nodes):
            if i % 3 == 0:
                proto_labels[n] = n[:3].upper()
    else:
        proto_labels = {n: n for n in proto_nodes}
    nx.draw_networkx_labels(G, pos, labels=proto_labels, font_size=7.5, ax=ax)

    ax.set_title("Embedded Communication Protocols — Mind Map", fontsize=16, fontweight="bold")
    ax.axis("off")
    fig.tight_layout()
    return fig


def category_mindmap(protocols, category):
    """Zoomed mind map for a single category, showing each protocol's
    related_protocols as secondary connections."""
    subset = [p for p in protocols if p["category"] == category]
    G = nx.Graph()
    G.add_node(category, kind="cat")
    for p in subset:
        G.add_node(p["name"], kind="proto", pid=p["id"])
        G.add_edge(category, p["name"])
    id_to_name = {p["id"]: p["name"] for p in protocols}
    for p in subset:
        for rel in p.get("related", []):
            rel_name = id_to_name.get(rel)
            if rel_name and rel_name in G.nodes:
                G.add_edge(p["name"], rel_name)

    pos = nx.spring_layout(G, k=1.0, seed=11, iterations=200)
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#cbd5e1", width=1.2)
    cat_nodes = [category]
    proto_nodes = [n for n in G.nodes if n != category]
    nx.draw_networkx_nodes(
        G, pos, nodelist=cat_nodes, node_color=CAT_COLORS.get(category, "#334155"), node_size=3000, ax=ax
    )
    nx.draw_networkx_nodes(
        G, pos, nodelist=proto_nodes, node_color="#e2e8f0", edgecolors="#64748b", node_size=800, ax=ax
    )
    nx.draw_networkx_labels(
        G, pos, labels={category: category}, font_size=11, font_color="white", font_weight="bold", ax=ax
    )
    # Show full names for few protocols; otherwise abbreviate.
    proto_labels = {}
    if len(proto_nodes) > 20:
        for i, n in enumerate(proto_nodes):
            if i % 2 == 0:
                proto_labels[n] = n[:3].upper()
    else:
        proto_labels = {n: n for n in proto_nodes}
    nx.draw_networkx_labels(G, pos, labels=proto_labels, font_size=8, ax=ax)
    ax.set_title(f"{category} — Protocol Relationships", fontsize=14, fontweight="bold")
    ax.axis("off")
    fig.tight_layout()
    return fig
