# -*- coding: utf-8 -*-
"""Central, cached data loading for the whole app."""

import json
import os
import streamlit as st

from utils.code_snippets import get_snippets
from utils.troubleshooting import get_troubleshooting

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "protocols.json")


@st.cache_data(show_spinner=False)
def load_protocols():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_categories(protocols):
    return sorted(set(p["category"] for p in protocols))


def get_by_id(protocols, pid):
    for p in protocols:
        if p["id"] == pid:
            return p
    return None


def search_protocols(protocols, query):
    q = query.lower().strip()
    if not q:
        return protocols
    results = []
    for p in protocols:
        pid = p.get("id", "")
        snippet_text = " ".join(s.get("title", "") + " " + s.get("code", "") for s in get_snippets(pid))
        trouble_text = " ".join(
            t.get("symptom", "") + " " + t.get("cause", "") + " " + t.get("fix", "") for t in get_troubleshooting(pid)
        )
        haystack = " ".join(
            [
                p.get("name", ""),
                p.get("category", ""),
                p.get("description", ""),
                p.get("inventor", ""),
                str(p.get("year", "")),
                " ".join(p.get("use_cases", [])),
                " ".join(str(v) for v in p.get("technical", {}).values()),
                p.get("lifecycle", ""),
                p.get("osi_layer", ""),
                p.get("standard_doc", ""),
                snippet_text,
                trouble_text,
            ]
        ).lower()
        if q in haystack:
            results.append(p)
    return results
