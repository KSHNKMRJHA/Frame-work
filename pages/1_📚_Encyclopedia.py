# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from utils.data_loader import load_protocols, get_categories, get_by_id
from utils import state as state_utils
from utils.technical_deep import get_deep_spec
from utils.code_snippets import get_snippets
from utils.troubleshooting import get_troubleshooting
from utils import signal_engine
import electrical_specs
from parametric import format_bps, format_m
from utils import ui_state
from utils import branding
from utils import components




from utils.diagrams import (
    frame_diagram,
    topology_diagram,
    pinout_diagram,
    waveform_diagram,
    uart_waveform,
    i2c_waveform,
    spi_waveform,
    can_waveform,
    rs485_waveform,
    ethernet_waveform,
    i2s_waveform,
    arinc429_waveform,
)


def _signal_rows(selected):
    """One table row per conductor, annotated with its differential pair."""
    spec = selected.get("electrical") or {}
    mate = {}
    for pr in spec.get("pairs") or []:
        mate[pr["a"]] = (pr["b"], pr["role"])
        mate[pr["b"]] = (pr["a"], pr["role"])
    arrow = {"O": "→ out", "I": "← in", "B": "↔ bidirectional", "I/O": "↔ bidirectional",
             "P": "⚡ power", "G": "⏚ ground", "-": "n/a"}
    rows = []
    for sig in selected.get("signals") or []:
        pair = mate.get(sig["name"])
        rows.append({
            "Signal": sig["name"],
            "Direction": arrow.get(sig["dir"], sig["dir"]),
            "Differential pair": f"{pair[0]} ({pair[1]})" if pair else "—",
            "Carries": sig["description"],
        })
    return rows


def _signal_table(selected):
    """Heading text that says whether the wiring is intrinsic or inherited."""
    path = selected.get("signal_path", "")
    src = selected.get("signal_source", "")
    if path and src and src != selected["id"]:
        return f"Conductor table — carried over {path}"
    return "Conductor table"


def _named_trace(engine_name, segments, pair_labels):
    """Label a differential trace with its real pin names and voltage range.

    The engine names traces generically (V+/V-/VDiff); a reader needs to see
    D+/D- or TxP/TxN and the actual volts, since that is what a scope probe
    would be clipped onto.
    """
    base = engine_name.split(" (")[0]          # drop the "(RX, delayed)" suffix
    alias = {"V+": None, "V-": None, "VDiff": "VDiff (what the receiver sees)",
             "line": "line"}.get(base, base)
    # Find which real pair this generic name corresponds to.
    for positive, negative in pair_labels.items():
        if base == "V+":
            alias = f"{positive} ({negative} inverted)"
            break
        if base == "V-":
            alias = f"{negative} ({positive} inverted)"
            break
    label = alias or base
    if base == "VDiff":
        label = f"VDiff = {positive} - {negative}" if pair_labels else "VDiff"
    suffix = " (RX, delayed)" if "(RX, delayed)" in engine_name else ""
    levels = [s[2] for s in segments]
    if levels:
        lo, hi = min(levels), max(levels)
        volts = f"{lo:.2f}…{hi:.2f} V" if lo != hi else f"{lo:.2f} V"
        label = f"{label}  [{volts}]{suffix}"
    # waveform_diagram consumes (level, width); the engine emits
    # absolute (t_start, t_end, level).
    return {"name": label, "segments": [(s[2], s[1] - s[0]) for s in segments]}


branding.page_config("Encyclopedia", "📚")
branding.sidebar_identity()

protocols = load_protocols()
categories = ["All"] + get_categories(protocols)

if "user_state" not in st.session_state:
    st.session_state.user_state = state_utils.load_state()
us = st.session_state.user_state

st.title("📚 Protocol Encyclopedia")
st.caption(
    "Every field below — history, diagrams, pinouts, use-cases, limitations, and real-world examples — is generated live from the master protocol database."
)

# ------------------------------------------------------------- FILTERS -----
# Search gets the first row; category pills need the FULL width because there
# are 14 of them and they were being clipped inside a quarter-width column.
query = st.text_input("Search", placeholder="Search by name, keyword, inventor...",
                      key="fw_encyclopedia_query")

components.info_badge("Category")
# `categories` already begins with "All"; do not prepend it again.
cat = st.pills("Category", categories, default="All",
               selection_mode="single", key="fw_cat", label_visibility="collapsed")

# An explicit width replaces the old `st.columns([1, 3])[0]`, whose remaining
# three quarters were an empty placeholder. That layout left the selectbox at
# ~102px at tablet widths, too narrow to read the option. A fixed 240px is
# comfortable at every viewport and needs no breakpoint.
diffs = ["All"] + sorted(set(p.get("difficulty", "Beginner") for p in protocols))
diff = st.selectbox("Difficulty", diffs, key="fw_diff", width=240)

filtered = protocols
if cat != "All":
    filtered = [p for p in filtered if p["category"] == cat]
if diff != "All":
    filtered = [p for p in filtered if p.get("difficulty") == diff]
if query:
    from utils.data_loader import search_protocols

    matching_ids = {p["id"] for p in search_protocols(filtered, query)}
    filtered = [p for p in filtered if p["id"] in matching_ids]

st.caption(f"Showing **{len(filtered)}** of {len(protocols)} protocols.")

by_id = {p["id"]: p for p in protocols}

# An explicitly requested protocol must stay visible even when the active
# filters exclude it. Showing a different protocol than the one the user asked
# for is worse than showing it with a note, so the deep-linked target wins and
# the filters are relaxed just enough to include it.
requested = ui_state.requested_protocol_id()
hinted = requested or st.session_state.get("_fw_protocol_handoff")
if hinted and hinted in by_id and hinted not in {p["id"] for p in filtered}:
    target = by_id[hinted]
    st.info(
        f"**{target['name']}** was opened directly, so the active filters were "
        "cleared to show it."
    )
    st.session_state["fw_cat"] = "All"
    st.session_state["fw_diff"] = "All"
    if query:
        st.session_state["fw_encyclopedia_query"] = ""
    cat = "All"
    diff = "All"
    query = ""
    filtered = protocols

if not filtered:
    st.warning("No protocols match your filters. Try clearing search or category.")
    st.stop()

# The widget is ALWAYS rendered, including on a deep-linked visit. It used to be
# built inside the fallback branch of a conditional expression, so a deep link
# meant the dropdown was never created at all - and since the page then wrote
# ?p=<id> on every rerun, the user could never leave that protocol.
option_ids = [p["id"] for p in filtered]
labels = {p["id"]: f"{p['name']}  ·  {p['category']} ({p['year']})" for p in filtered}

# Phase 1: decide which protocol this visit is about, before the widget exists.
seeded_id = ui_state.ensure_active_protocol(protocols)
start = option_ids.index(seeded_id) if seeded_id in option_ids else 0

picked = st.selectbox(
    "Select a protocol to open its full profile:",
    option_ids,
    index=start,
    format_func=lambda pid: labels.get(pid, pid),
    key="fw_proto_pick",
)

# Phase 2: the widget is now authoritative. Because it was built with `index`
# pointing at the seeded protocol, its value only differs when the user actually
# changed it - so a difference is a real user action, never a stale URL.
active_id = ui_state.active_protocol_id(protocols, widget_value=picked)

# If the stored protocol is filtered out of the current view, fall back to the
# dropdown rather than silently rendering some unrelated protocol.
selected = by_id.get(active_id) if active_id in {p["id"] for p in filtered} else None
if selected is None:
    selected = by_id[picked]

# The selection now flows one way: widget -> state -> URL + memory.
ui_state.sync_active_protocol(selected["id"])
st.caption(f"🔗 Sharing this page: `?p={selected['id']}`")

state_utils.mark_protocol_viewed(us, selected["id"])
state_utils.save_state(us)

st.divider()

# ---- Export for offline study notes -------------------------------------
with st.expander("🖨️ Export this protocol", expanded=False):
    st.caption("A one-page PNG summary — conductors, differential pairs and "
               "signal levels — for pasting into notes.")
    if st.button("Generate summary PNG", key=f"fw_png_{selected['id']}"):
        st.session_state[f"fw_pngdata_{selected['id']}"] = \
            branding.protocol_summary_card(selected)
    png = st.session_state.get(f"fw_pngdata_{selected['id']}")
    if png:
        st.image(png, width="stretch")
        st.download_button(
            "⬇️ Download PNG",
            data=png,
            file_name=f"{selected['id']}-summary.png",
            mime="image/png",
            key=f"fw_dl_{selected['id']}",
        )

# --------------------------------------------------------------- PROFILE ---
# Single-column, full width. This used to be st.columns([2.2, 1]), but
# Streamlit only auto-stacks columns below ~640px, so at tablet widths the
# sidebar left barely ~450px of usable content and the split squeezed every
# metric until values truncated to "Begin..." / "Star (...". With injected CSS
# unavailable there is no viewport hook, so the layout is built for the narrow
# case instead: full width reads correctly everywhere and costs only vertical
# space on wide screens.
components.protocol_hero(
        selected["name"],
        category=selected.get("category", ""),
        year=selected.get("year", ""),
        inventor=selected.get("inventor", ""),
        difficulty=selected.get("difficulty", ""),
        lifecycle=selected.get("lifecycle") or "",
    )
# Two columns per row: readable at tablet, and Streamlit stacks 2-up to 1-up
# on phones by itself. Only short values go in a metric - st.metric renders a
# large font and clips with an ellipsis, which turned "Star (Host + Hub)" into
# "Star (Host ...". Long free-text fields are printed as text below so they
# wrap instead of truncating.
# Key-spec band: compact parameter/value grid (mono values, wraps to one
# column on phones). Short values only - long free text stays as wrapping
# prose below so it never truncates inside a metric.
_impedance = (selected.get("electrical") or {}).get("impedance_ohm")
components.spec_table([
    ("Max rate", format_bps(selected.get("data_rate_max_bps"))),
    ("Max reach", format_m(selected.get("distance_max_m"))),
    ("Max nodes",
     str(selected.get("nodes_max")) if selected.get("nodes_max") is not None else "carrier-defined"),
    ("Topology", selected.get("topology") or "-"),
    ("OSI layer", selected.get("osi_layer") or "-"),
    ("Standard", selected.get("standard_doc") or "-"),
])
st.caption("Maxima are representative and never simultaneous.")

st.markdown("#### 🚀 Speed")
st.success(selected.get("speed", "Not specified"))

st.markdown("#### 📖 Overview")
st.write(selected["description"])

st.markdown("#### ⚙️ How It Works")
st.write(selected.get("how_it_works", "—"))

st.markdown("#### 🕰️ Origin Story")
origin_bits = []
if selected.get("inventor"):
    origin_bits.append(f"**Inventor / Organization:** {selected['inventor']}")
if selected.get("organization"):
    origin_bits.append(f"**Standards Body:** {selected['organization']}")
if selected.get("place"):
    origin_bits.append(f"**Origin:** {selected['place']}")
st.markdown("  \n".join(origin_bits))
if selected.get("fun_fact"):
    st.info(f"💡 **Fun fact:** {selected['fun_fact']}")

if selected.get("pins"):
    st.markdown("#### 🔌 Pins / Wires")
    st.code(", ".join(selected["pins"]))

st.markdown("#### 🌍 Real-World Example")
st.write(selected.get("real_world_example", "—"))

st.divider()

# ------------------------------------------------- TECHNICAL PROFILE -------
technical = selected.get("technical", {})
if technical:
    with st.container(border=True):
        st.markdown("### ⚡ Electrical & Hardware Profile")
        st.caption(
            f"**Scope:** {technical.get('scope', '—')} · "
            "Values marked as implementation-specific must be confirmed in the device datasheet."
        )
        tech_cols = st.columns(2)
        with tech_cols[0]:
            st.markdown("**Signaling**")
            st.write(technical.get("signaling", "—"))
            st.markdown("**Logic high / 1**")
            st.write(technical.get("logic_high", "—"))
            st.markdown("**Logic low / 0**")
            st.write(technical.get("logic_low", "—"))
            st.markdown("**Voltage / reference**")
            st.write(technical.get("voltage_reference", "—"))
        with tech_cols[1]:
            st.markdown("**Clocking / timing**")
            st.write(technical.get("clocking", "—"))
            st.markdown("**Termination / biasing**")
            st.write(technical.get("termination_and_biasing", "—"))
        notes = technical.get("design_notes", [])
        if notes:
            st.markdown("**Implementation notes**")
            for note in notes:
                st.markdown(f"- {note}")
        transceivers = technical.get("transceivers", [])
        if transceivers:
            st.markdown("**Interface silicon / transceivers**")
            for t in transceivers:
                st.markdown(f"- {t}")
        st.divider()

        # ---- Wiring / signals -------------------------------------------
        signals = selected.get("signals") or []
        if signals:
            st.markdown("### 🔌 Wiring & signals")
            src = selected.get("signal_source", "")
            path = selected.get("signal_path", "")
            inherited = src and src != selected["id"]
            st.caption(
                f"Physical conductors for {selected['name']}."
                + (f" **Carried over {path.replace(' → ', ' → ')}** — these are the wires "
                   "you actually plug in." if inherited else "")
            )
            # Cards before the table: the differential pairing is the thing
            # readers miss, and it is obvious on a card but not in a row.
            branding.conductor_cards(selected)
            arrow = {"O": "→ out", "I": "← in", "B": "↔ bidirectional", "I/O": "↔ bidirectional",
                     "P": "⚡ power", "G": "⏚ ground", "-": "n/a"}
            st.dataframe(
                [{"Signal": sig["name"], "Direction": arrow.get(sig["dir"], sig["dir"]),
                  "Carries": sig["description"], **({"Notes": sig["extra"]} if sig.get("extra") else {})}
                 for sig in signals],
                width="stretch", hide_index=True,
            )

        # ---- Addressing --------------------------------------------------
        addressing = selected.get("addressing", "")
        if addressing:
            st.markdown("**Addressing**")
            st.write(addressing)

        # ---- Command vocabulary ------------------------------------------
        commands = selected.get("commands") or []
        if commands:
            # A modal rather than an inline table: command sets are reference
            # material, and 6 of 140 protocols carry one, so most readers would
            # scroll past it to reach the waveform.
            st.button(f"📋 Command / opcode vocabulary ({len(commands)})",
                      key=f"fw_cmds_{selected['id']}")
            if st.session_state.get(f"fw_cmds_{selected['id']}") and branding._runtime_available():
                branding.commands_dialog(selected)
        # ---- Electrical characteristics (volts / ohms / ns) --------------
        spec = selected.get("electrical") or {}
        if spec:
            st.markdown("### ⚡ Electrical characteristics")
            inh = spec.get("inherited_from")
            st.caption(
                f"Signalling: **{spec.get('signaling', 'n/a')}**"
                + (f" · inherited from **{inh}**" if inh else "")
            )
            lvl_txt = electrical_specs.format_levels(spec)
            if lvl_txt:
                st.markdown(f"**Levels:** {lvl_txt}")
            # Proportional bars: numbers alone hide how small an LVDS swing is
            # next to RS-485's, which is the whole point of low-swing signalling.
            branding.level_bars(spec)

            # Differential pairs get their own explicit TX+/TX- table, which is
            # what a reader actually needs to know: which wire is which.
            pairs = spec.get("pairs") or []
            if pairs:
                st.markdown("**Differential pairs**")
                arrow = {"transmit": "TX (A → B)", "receive": "RX (B → A)",
                         "bidirectional": "half duplex"}
                st.dataframe(
                    [{"Positive": p["a"], "Negative": p["b"], "Direction": arrow.get(p["role"], p["role"])}
                     for p in pairs],
                    width="stretch", hide_index=True,
                )

            rows = []
            if spec.get("impedance_ohm"):
                rows.append({"Parameter": "Characteristic impedance Z0",
                             "Value": f"{spec['impedance_ohm']:g} Ω"})
            if spec.get("rise_time_ns"):
                rows.append({"Parameter": "Rise time (10–90 %)",
                             "Value": f"{spec['rise_time_ns']:g} ns"})
            if spec.get("bit_period_ns"):
                rows.append({"Parameter": "Bit period",
                             "Value": f"{spec['bit_period_ns']:g} ns "
                                      f"({1000.0 / spec['bit_period_ns']:,.1f} Mbit/s)"})
            if spec.get("prop_delay_ns_per_m"):
                rows.append({"Parameter": "Propagation delay",
                             "Value": f"{spec['prop_delay_ns_per_m']:g} ns/m"})
            if spec.get("jitter_ps"):
                rows.append({"Parameter": "Total jitter (budget)",
                             "Value": f"{spec['jitter_ps']:g} ps"})
            if spec.get("termination"):
                rows.append({"Parameter": "Termination", "Value": spec["termination"]})
            # Derived values make the raw numbers actionable.
            derived = electrical_specs.derive_derived(spec, cable_length_m=100.0)
            if derived.get("bandwidth_mhz"):
                rows.append({"Parameter": "Edge-limited bandwidth",
                             "Value": f"≈{derived['bandwidth_mhz']:,.0f} MHz (0.35/tr)"})
            if derived.get("round_trip_delay_ns"):
                rows.append({"Parameter": "TX→RX flight time over 100 m",
                             "Value": f"{derived['one_way_delay_ns']:,.0f} ns one way, "
                                      f"{derived['round_trip_delay_ns']:,.0f} ns round trip"})
            if rows:
                st.dataframe(rows, width="stretch", hide_index=True)
            if spec.get("notes"):
                st.caption(spec["notes"])
        st.divider()
        st.markdown("### 🚌 Bus & protocol parameters")
        st.caption(
            "Distance, fan-out, duplex, addressing, error handling, line coding, "
            "power and EMC — the numbers that decide whether a protocol fits your design."
        )
        deep_rows = [
            ("Max distance", technical.get("max_distance", "—")),
            ("Max nodes", technical.get("max_nodes", "—")),
            ("Duplex mode", technical.get("duplex_mode", "—")),
            ("Addressing", technical.get("addressing", "—")),
            ("Error detection", technical.get("error_detection", "—")),
            ("Line encoding", technical.get("line_encoding", "—")),
            ("Power profile", technical.get("power_profile", "—")),
            ("EMC / isolation", technical.get("emc_isolation", "—")),
        ]
        st.dataframe(
            pd.DataFrame(deep_rows, columns=["Parameter", "Value"]),
            width="stretch",
            hide_index=True,
        )
        deep = get_deep_spec(selected["id"])
        if deep:
            st.markdown("### 📊 Parametric deep-dive (specification values)")
            st.caption(
                "Absolute levels, timing limits and bus rules with the defining "
                "standard for each row. Confirm against the linked standard before "
                "taping out."
            )
            st.markdown("**Signal levels**")
            st.dataframe(pd.DataFrame(deep["signal_levels"]), width="stretch", hide_index=True)
            st.markdown("**Timing**")
            st.dataframe(pd.DataFrame(deep["timing"]), width="stretch", hide_index=True)
            st.markdown("**Bus rules**")
            st.dataframe(pd.DataFrame(deep["bus"]), width="stretch", hide_index=True)
            if deep.get("standards"):
                st.markdown("**Governing standards**")
                for s in deep["standards"]:
                    st.markdown(f"- {s}")
            if deep.get("checklist"):
                st.markdown("**Board bring-up checklist**")
                for c in deep["checklist"]:
                    st.markdown(f"- [ ] {c}")
        else:
            st.caption(
                "No flagship parametric table for this protocol yet — the bus & "
                "protocol parameters above are the category-level engineering guidance."
            )

        snippets = get_snippets(selected["id"])
        if snippets:
            st.divider()
            st.markdown("### 💻 Bring-up code")
            st.caption("Smallest program that proves the bus is alive — copy, run, then extend.")
            for sn in snippets:
                with st.expander(f"{sn['platform']} — {sn['title']}", expanded=False):
                    st.code(sn["code"], language=sn["language"])

        trouble = get_troubleshooting(selected["id"])
        if trouble:
            st.divider()
            st.markdown("### 🛠 Troubleshooting")
            st.caption("Ordered by how often each failure actually bites: wiring first, then config, then protocol.")
            for i, t in enumerate(trouble, 1):
                with st.expander(f"{i}. {t['symptom']}", expanded=(i == 1)):
                    st.markdown(f"**Likely cause:** {t['cause']}")
                    st.markdown(f"**Fix:** {t['fix']}")
        st.info(
            "A protocol may be a logical/RF layer and therefore not define a connector voltage. "
            "In that case, follow the selected physical/link layer and its transceiver datasheet."
        )

st.divider()

# ------------------------------------------------------------ USE CASES ----
uc1, uc2 = st.columns(2)
with uc1:
    st.markdown("#### ✅ Use Cases")
    for u in selected.get("use_cases", []):
        st.markdown(f"- {u}")
    st.markdown("#### 👍 Advantages")
    for a in selected.get("advantages", []):
        st.markdown(f"- {a}")
with uc2:
    st.markdown("#### ⚠️ Limitations")
    for limitation in selected.get("limitations", []):
        st.markdown(f"- {limitation}")
    if selected.get("related"):
        st.markdown("#### 🔗 Related Protocols")
        rel_names = []
        for rid in selected["related"]:
            rp = get_by_id(protocols, rid)
            if rp:
                rel_names.append(rp["name"])
        st.markdown(", ".join(rel_names) if rel_names else "—")

st.divider()
st.markdown("### 🖼️ Interactive Diagrams")
d1, d2, d3, d4, d5 = st.tabs(
    ["📦 Frame / Packet Structure", "🕸️ Network Topology", "🔌 Pinout / Wiring",
     "📈 Signal Waveform", "⚡ Line Coding Explorer"]
)

with d1:
    fig = frame_diagram(selected.get("frame_fields", []), title=f"{selected['name']} — Frame Structure")
    if fig:
        st.pyplot(fig, width="stretch")
        # Caveats a bit-level bar chart cannot show: variable-length fields
        # that only move in 8-bit steps, conditions that occupy no clock
        # cycle, interframe gaps that are not fields, and so on.
        if selected.get("frame_note"):
            st.caption(f"ℹ️ {selected['frame_note']}")
        st.caption(
            "Segment widths are compressed and bounded for readability; exact bit "
            "counts are preserved in the legend. Fields with a range (e.g. `0-64`) "
            "use a fixed nominal width because their real size varies per frame."
        )
        # The unchanged 12-inch figure scales down on phones. Keep its exact
        # field identities/counts available as readable, wrapping native text.
        with st.expander("Frame field values"):
            components.spec_table([
                (f"{index} · {field['name']}", f"{field.get('bits', '')} bit")
                for index, field in enumerate(selected.get("frame_fields", []), start=1)
            ])
    else:
        st.info(
            "This protocol doesn't define a fixed bit-level frame structure (e.g., it's a networking/application-layer or wireless protocol without a simple fixed frame)."
        )

with d2:
    fig = topology_diagram(selected.get("topology", "Point-to-Point"), selected["name"])
    # The topology canvas stays square-circled, so it is centred in a narrower
    # column rather than stretched across the full page width — otherwise the
    # diagram overflows the content area on a wide screen.
    _tc = st.columns([1, 2.4, 1])
    with _tc[1]:
        st.pyplot(fig, width="stretch")
    st.caption(
        "Illustrative layout — the node count and wiring shown are representative "
        "of this topology class, not the exact device list of the protocol."
    )

with d3:
    # Prefer the structured signals; fall back to the legacy pins string. Every
    # protocol now has signals, so the "no pinout" branch is a real fallback.
    _pins = [s["name"] for s in (selected.get("signals") or [])]
    if not _pins:
        _pins = [p for p in (selected.get("pins") or []) if p]
    fig = pinout_diagram(_pins, selected["name"]) if _pins else None
    if fig:
        _pc = st.columns([1, 2.4, 1])
        with _pc[1]:
            st.pyplot(fig, width="stretch")
        _path = selected.get("signal_path", "")
        if _path and selected.get("signal_source") != selected["id"]:
            st.caption(f"Wiring inherited along: **{_path}**.")
        else:
            st.caption("Wiring is intrinsic to this protocol.")
        st.markdown(f"##### 📋 {_signal_table(selected)}")
        st.dataframe(_signal_rows(selected), width="stretch", hide_index=True)
    else:
        st.info(
            "No physical conductors are defined for this protocol — it is defined "
            "entirely in software, with no dedicated bus or interface of its own."
        )

with d4:
    # Map the selected protocol onto a waveform renderer. Protocols that share
    # a physical layer reuse that layer's waveform (Modbus RTU rides on RS-485,
    # J1939/CANopen on CAN, ...).
    _WAVE_MAP = {
        "uart": "uart",
        "rs232": "uart",
        "midi": "uart",
        "nmea": "uart",
        "mavlink": "uart",
        "kline": "uart",
        "iolink": "uart",
        "rs485": "rs485",
        "modbus_rtu": "rs485",
        "profibus": "rs485",
        "dmx512": "rs485",
        "i2c": "i2c",
        "smbus": "i2c",
        "pmbus": "i2c",
        "spi": "spi",
        "qspi": "spi",
        "microwire": "spi",
        "can": "can",
        "can_fd": "can",
        "can_xl": "can",
        "isotp": "can",
        "j1939": "can",
        "canopen": "can",
        "devicenet": "can",
        "obd2": "can",
        "uds": "can",
        "xcp": "can",
        "ethernet": "ethernet",
        "modbus_tcp": "ethernet",
        "profinet": "ethernet",
        "ethercat": "ethernet",
        "ethernetip": "ethernet",
        "bacnet": "ethernet",
        "powerlink": "ethernet",
        "sercos": "ethernet",
        "automotive_ethernet": "ethernet",
        "t1s": "ethernet",
        "doip": "ethernet",
        "someip": "ethernet",
        "arinc664": "ethernet",
        "tsn": "ethernet",
        "ip": "ethernet",
        "arp": "ethernet",
        "icmp": "ethernet",
        "tcp": "ethernet",
        "udp": "ethernet",
        "http": "ethernet",
        "ftp": "ethernet",
        "telnet_ssh": "ethernet",
        "snmp": "ethernet",
        "mqtt": "ethernet",
        "coap": "ethernet",
        "websocket": "ethernet",
        "ntp": "ethernet",
        "mdns": "ethernet",
        "dhcp": "ethernet",
        "dns": "ethernet",
        "opcua": "ethernet",
        "dnp3": "ethernet",
        "dds": "ethernet",
        "macsec": "ethernet",
        "i2s": "i2s",
        "tdm": "i2s",
        "arinc429": "arinc429",
    }
    kind = _WAVE_MAP.get(selected["id"])
    if kind == "uart":
        model = uart_waveform(baud=9600)
    elif kind == "rs485":
        model = rs485_waveform(baud=9600)
    elif kind == "i2c":
        model = i2c_waveform()
    elif kind == "spi":
        model = spi_waveform()
    elif kind == "can":
        model = can_waveform()
    elif kind == "ethernet":
        model = ethernet_waveform()
    elif kind == "i2s":
        model = i2s_waveform()
    elif kind == "arinc429":
        model = arinc429_waveform()
    else:
        model = None

    # No bespoke renderer for this protocol - fall back to the generic
    # engine, which can draw any protocol that has an electrical spec (every
    # protocol now does) instead of showing a dead end.
    if model is None:
        _esp = selected.get("electrical") or {}
        _dw = signal_engine.differential_waveform(_esp, "10110100", length_m=1.0) \
            if _esp else []
        if _dw:
            _pairs = {p["a"]: p["b"] for p in (_esp.get("pairs") or [])}
            model = {
                "title": f"{selected['name']} — {'RF link' if _esp.get('signaling') == 'rf' else 'electrical'} waveform",
                "traces": [_named_trace(nm, segs, _pairs) for nm, segs in _dw],
                "fields": [],
                "time_label": (f"bit periods ({_esp['bit_period_ns']:g} ns each)"
                               if _esp.get("bit_period_ns") else "bit periods"),
            }
            _src = _esp.get("inherited_from")
            if _src and _src != selected["id"]:
                st.caption(
                    f"No bespoke waveform exists for {selected['name']}; this is the "
                    f"physical layer of **{_src}** that carries it, with real voltages."
                )
            else:
                st.caption(
                    f"Generated from the {selected['name']} electrical profile "
                    "(voltages, bit period and propagation delay)."
                )

    if model:
        fig = waveform_diagram(model)
        st.pyplot(fig, width="stretch")
        stats = model.get("stats", {})
        if kind in ("uart", "rs485"):
            st.caption(
                f"Frame = {stats.get('frame_bits', 0):g} bit times → "
                f"{stats.get('frame_time_us', 0):.1f} µs per byte; "
                f"{stats.get('efficiency_pct', 0):.0f} % of the wire carries payload "
                "(the rest is start/parity/stop overhead). Markers show where the "
                "receiver samples each bit."
            )
        st.caption(
            "Waveform is generated live from the same framing rules the protocol uses — "
            "levels are logical (0/1) except CAN/RS-485/Ethernet/ARINC 429, which show "
            "the differential pair. Rider protocols (Modbus RTU on RS-485, UDS on CAN, "
            "MQTT on Ethernet …) display their carrier's physical layer."
        )
    else:
        # Only genuinely wire-less layers land here (RF). Show the real link
        # parameters instead of an apology.
        _esp = selected.get("electrical") or {}
        if _esp.get("signaling") == "rf":
            _d = electrical_specs.derive_derived(_esp)
            st.markdown(f"##### 📡 {selected['name']} — RF link parameters")
            st.caption(
                f"{selected['name']} has no wire-level voltage to plot: it is a radio "
                "link, so its budget is expressed in dBm, antenna gain and path loss."
            )
            _rows = [
                {"Parameter": "Transmit power", "Value": f"{_esp.get('vdiff_high_volts') or 0:g} dBm"},
                {"Parameter": "Characteristic impedance", "Value": f"{_esp.get('impedance_ohm') or 0:g} Ω"},
            ]
            if _d.get("bandwidth_mhz"):
                _rows.append({"Parameter": "Occupied bandwidth", "Value": f"≈{_d['bandwidth_mhz']:,.0f} MHz"})
            if _d.get("bit_rate_mbps"):
                _rows.append({"Parameter": "Bit rate", "Value": f"{_d['bit_rate_mbps']:,.3f} Mbit/s"})
            if _esp.get("rise_time_ns"):
                _rows.append({"Parameter": "Symbol/edge time", "Value": f"{_esp['rise_time_ns']:g} ns"})
            if _esp.get("termination"):
                _rows.append({"Parameter": "Antenna feed", "Value": _esp["termination"]})
            st.dataframe(_rows, width="stretch", hide_index=True)
            _psd = float(_d.get("bit_rate_mbps") or 0)
            if _psd:
                st.caption(
                    f"Spectral efficiency ≈{_psd / (_d['bandwidth_mhz']):.3f} bit/s/Hz "
                    f"({_psd:,.3f} Mbit/s in {_d['bandwidth_mhz']:,.0f} MHz). "
                    "Values shown are regulatory/FCC/EU limits where they differ."
                )
            if _esp.get("notes"):
                st.caption(_esp["notes"])
        else:
            st.info(
                "No waveform could be derived: this protocol has neither a bespoke "
                "renderer nor enough electrical detail. See the ⚡ Electrical "
                "characteristics section for what is known."
            )

st.divider()
st.caption("Tip: use the ⚖️ Compare page to put this protocol head-to-head against alternatives.")

with d5:
    st.markdown("#### ⚡ Encode a bit stream with any line coding")
    espec = selected.get("electrical") or {}
    if espec.get("signaling") == "rf":
        rf_pwr = espec.get("vdiff_high_volts") or 0
        rf_z = espec.get("impedance_ohm") or 0
        rf_bw = electrical_specs.derive_derived(espec).get("bandwidth_mhz") or 0
        st.info(
            f"**{selected['name']} is an RF protocol** — it has no wire-level volts "
            f"to plot. Its link budget is {rf_pwr:g} dBm into a {rf_z:g} Ω matched "
            f"load across roughly {rf_bw:,.0f} MHz of bandwidth. The trace below shows "
            "the bit-level encoding only."
        )
    st.caption(
        "Every waveform here is *derived*: you choose a line coding, the engine "
        "encodes your bits into the electrical levels a scope would show. "
        "Try the same bits in two codings to see why a clock line exists at all."
    )
    ec1, ec2 = st.columns([1.4, 1])
    coding_name = ec1.selectbox(
        "Line coding",
        list(signal_engine.LINE_CODINGS),
        format_func=lambda c: f"{c} — {signal_engine.coding_info(c)[0]}",
    )
    bits_in = ec2.text_input("Bits", value="10110100", help="A string of 0/1 characters.")

    # ---- Differential TX/RX with real volts and timing ------------------
    @st.fragment
    def _differential_view():
        """Re-render on widget change without rerunning the whole page.

        Streamlit reruns the entire script on any interaction, which for this
        page means re-querying every protocol, re-rendering the profile and
        re-plotting four other diagrams just to move a slider. A fragment
        scopes the rerun to this block.
        """
        cable_m = st.slider("Cable length (m)", 0.0, 200.0, 1.0, step=0.5,
                            help="Sets the propagation delay shown between TX and RX.")
        dw = signal_engine.differential_waveform(espec, bits_in, length_m=cable_m)
        if not dw:
            return
        st.markdown("##### 🔀 Differential TX / RX at the wire")
        lvl = electrical_specs.format_levels(espec)
        st.caption(f"{lvl} · RX traces are delayed by the propagation delay "
                   f"over {cable_m:g} m.")
        # Each trace sits on its own row with no y axis, so the actual volts
        # go in the trace name - that is where a reader will look for them.
        pair_labels = {p["a"]: p["b"] for p in (espec.get("pairs") or [])}
        fig = waveform_diagram({
            "title": f"{selected['name']} — differential signalling",
            "traces": [_named_trace(nm, segs, pair_labels) for nm, segs in dw],
            "fields": [],
            "time_label": (f"bit periods ({espec['bit_period_ns']:g} ns each)"
                           if espec.get("bit_period_ns") else "bit periods"),
        })
        st.pyplot(fig, width="stretch")
        eye = signal_engine.eye_headroom(espec)
        if eye:
            st.caption(f"Receiver eye height ≈{eye['eye_height_volts']:.2f} V "
                       f"({eye['basis']}).")

    if espec and bits_in:
        _differential_view()

    st.divider()
    st.markdown("##### 🧪 Abstract line coding (logic levels)")

    desc, labels = signal_engine.coding_info(coding_name)
    segments = signal_engine.encode(coding_name, bits_in) if bits_in else []
    if not segments:
        st.info("Enter a bit string such as `10110100` to render a waveform.")
    else:
        model = {
            "title": f"{coding_name.upper()} encoding of {bits_in}",
            "traces": [{
                "name": "line",
                # waveform_diagram consumes (level, width); the engine emits
                # absolute (t_start, t_end, level), so convert widths here.
                "segments": [(lvl, t1 - t0) for t0, t1, lvl in segments],
            }],
            "time_label": "bit periods (one bit = one clock edge on a parallel bus)",
        }
        fig = waveform_diagram(model)
        st.pyplot(fig, width="stretch")
        span = segments[-1][1]
        st.caption(f"{desc} · {len(segments)} level segment(s) over {span:g} bit period(s).")

        # Field-by-field decode of the same bits, when the frame is known.
        fields = selected.get("frame_fields") or []
        parsed = [f for f in fields if isinstance(f.get("bits"), int)]
        if fields and bits_in:
            st.markdown("**Field decode of those same bits**")
            analysis = signal_engine.analyze_message(bits_in, fields, selected["name"])
            for row in analysis["fields"]:
                if not row.get("parsed"):
                    st.caption(f"- `{row['name']}` — width `{row['bits']}` (variable, not decoded)")
                    continue
                bits_txt = f"`{row['value']}`"
                reps = []
                if row.get("hex") is not None:
                    reps.append(f"0x{row['hex']}")
                if row.get("decimal") is not None:
                    reps.append(f"{row['decimal']} dec")
                if row.get("ascii"):
                    reps.append(f"'{row['ascii']}'")
                st.markdown(
                    f"- **{row['name']}** ({row['length']} bit @ offset {row['offset']}): "
                    f"{bits_txt} — {', '.join(reps) if reps else 'no numeric value'}"
                )

branding.page_footer()
