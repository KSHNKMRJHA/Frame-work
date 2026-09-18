# -*- coding: utf-8 -*-
"""Central, cached data loading for the whole app."""
import json
import os
import streamlit as st

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
        haystack = " ".join([
            p.get("name", ""), p.get("category", ""), p.get("description", ""),
            p.get("inventor", ""), str(p.get("year", "")), " ".join(p.get("use_cases", [])),
        ]).lower()
        if q in haystack:
            results.append(p)
    return results
