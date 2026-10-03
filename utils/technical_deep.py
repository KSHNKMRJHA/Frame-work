# -*- coding: utf-8 -*-
"""Deep parametric tables for flagship protocols.

These are the numbers engineers actually design against: absolute signal
levels, timing limits, bus loading, and the standard document that defines
them. Values are textbook / specification figures (NXP UM10204 for I2C,
TIA/EIA-485-A, Bosch CAN 2.0, IEEE 802.3, USB 2.0, TIA-232-F, LIN 2.x).

Each entry is a dict with:
  signal_levels: [{Parameter, Min, Typ, Max, Unit, Notes}, ...]
  timing:        [{Parameter, Value, Unit, Notes}, ...]
  bus:           [{Parameter, Value, Notes}, ...]
  standards:     [str, ...]
  checklist:     [str, ...]  (board bring-up checks)

Only well-established flagship buses are listed here; every other protocol
still gets the generic deep fields from technical_profiles.py.
"""

DEEP_SPECS = {
    "uart": {
        "signal_levels": [
            {
                "Parameter": "VIH (CMOS, VDD=3.3 V)",
                "Min": "2.31",
                "Typ": "—",
                "Max": "3.6",
                "Unit": "V",
                "Notes": "0.7×VDD rule; confirm in MCU datasheet",
            },
            {
                "Parameter": "VIL (CMOS, VDD=3.3 V)",
                "Min": "-0.3",
                "Typ": "—",
                "Max": "0.99",
                "Unit": "V",
                "Notes": "0.3×VDD rule",
            },
            {
                "Parameter": "Baud error tolerance",
                "Min": "—",
                "Typ": "±1",
                "Max": "±2",
                "Unit": "%",
                "Notes": "8N1 needs <2%; use Science Lab calculator",
            },
            {
                "Parameter": "Oversampling",
                "Min": "8",
                "Typ": "16",
                "Max": "16",
                "Unit": "×",
                "Notes": "Receiver samples near bit centre",
            },
        ],
        "timing": [
            {"Parameter": "Bit time @ 115200 baud", "Value": "8.68", "Unit": "µs", "Notes": "1/115200"},
            {
                "Parameter": "Byte time 8N1 @ 115200",
                "Value": "86.8",
                "Unit": "µs",
                "Notes": "10 bit times (start+8+stop)",
            },
            {"Parameter": "Byte time 8N1 @ 9600", "Value": "1.04", "Unit": "ms", "Notes": "10/9600"},
        ],
        "bus": [
            {
                "Parameter": "Topology",
                "Value": "Point-to-point, full-duplex (TX/RX+GND)",
                "Notes": "Add RS-485 transceiver for buses",
            },
            {
                "Parameter": "Flow control",
                "Value": "RTS/CTS hardware or XON/XOFF software",
                "Notes": "Needed above ~115.2 kbps without FIFOs",
            },
        ],
        "standards": ["MCU reference manual (baud generator)", "TIA-232-F (when RS-232 transceiver is used)"],
        "checklist": [
            "Both ends share baud, data bits, parity, stop bits (e.g. 115200 8N1).",
            "Common ground between boards; level-shift 5 V ↔ 3.3 V domains.",
            "Verify baud error <2% with the Science Lab UART calculator.",
        ],
    },
    "rs485": {
        "signal_levels": [
            {
                "Parameter": "Driver differential output (54 Ω load)",
                "Min": "1.5",
                "Typ": "2.5",
                "Max": "5.0",
                "Unit": "V",
                "Notes": "|VA−VB|, TIA-485-A §",
            },
            {
                "Parameter": "Receiver threshold",
                "Min": "-0.2",
                "Typ": "—",
                "Max": "+0.2",
                "Unit": "V",
                "Notes": "Fail-safe needs ≥ +200 mV idle",
            },
            {
                "Parameter": "Common-mode range",
                "Min": "-7",
                "Typ": "—",
                "Max": "+12",
                "Unit": "V",
                "Notes": "Exceeding this destroys receivers",
            },
            {
                "Parameter": "Receiver input resistance",
                "Min": "12",
                "Typ": "—",
                "Max": "—",
                "Unit": "kΩ",
                "Notes": "1 unit load; 1/8-load PHYs allow 256 nodes",
            },
        ],
        "timing": [
            {
                "Parameter": "Length × speed rule",
                "Value": "1200 m @ 100 kbps → 12 m @ 10 Mbps",
                "Unit": "—",
                "Notes": "Inverse trade-off, standard curve",
            },
            {
                "Parameter": "Stub length @ 1 Mbps",
                "Value": "< 0.3",
                "Unit": "m",
                "Notes": "Keep stubs < 1/10 of edge length — see stub calculator",
            },
            {
                "Parameter": "Turnaround delay",
                "Value": "Driver enable + 3.5 chars",
                "Unit": "—",
                "Notes": "Application must schedule TX/RX switch",
            },
        ],
        "bus": [
            {
                "Parameter": "Termination",
                "Value": "120 Ω at both physical ends",
                "Notes": "Only the two ends — never mid-bus",
            },
            {
                "Parameter": "Fail-safe bias",
                "Value": "≈680 Ω pull-up/down @ 5 V → ~400 mV idle",
                "Notes": "Size with the Science Lab bias calculator",
            },
            {
                "Parameter": "Wiring",
                "Value": "Shielded twisted pair, daisy-chain only",
                "Notes": "No star branches; ground the shield at one end",
            },
        ],
        "standards": ["TIA/EIA-485-A", "Modbus over Serial Line V1.02 (when carrying Modbus)"],
        "checklist": [
            "120 Ω at both ends, bias sized for ≥200 mV idle.",
            "A/B polarity consistent across all nodes; verify idle polarity.",
            "TVS + isolated transceiver (ADM2483/ISO) between buildings.",
        ],
    },
    "i2c": {
        "signal_levels": [
            {
                "Parameter": "VIH",
                "Min": "0.7×VDD",
                "Typ": "—",
                "Max": "VDD+0.5",
                "Unit": "V",
                "Notes": "UM10204; 2.31 V @ 3.3 V rail",
            },
            {
                "Parameter": "VIL",
                "Min": "-0.5",
                "Typ": "—",
                "Max": "0.3×VDD",
                "Unit": "V",
                "Notes": "0.99 V @ 3.3 V rail",
            },
            {
                "Parameter": "VOL @ 3 mA sink",
                "Min": "—",
                "Typ": "—",
                "Max": "0.4",
                "Unit": "V",
                "Notes": "Standard/Fast-mode driver spec",
            },
            {
                "Parameter": "Pull-up supply",
                "Min": "1.8",
                "Typ": "3.3",
                "Max": "5.0",
                "Unit": "V",
                "Notes": "Must suit every device on the bus",
            },
        ],
        "timing": [
            {"Parameter": "tr max (Standard 100 kHz)", "Value": "1000", "Unit": "ns", "Notes": "UM10204"},
            {
                "Parameter": "tr max (Fast 400 kHz)",
                "Value": "300",
                "Unit": "ns",
                "Notes": "Sizes Rp — see pull-up designer",
            },
            {"Parameter": "tr max (Fast+ 1 MHz)", "Value": "120", "Unit": "ns", "Notes": "Needs 20 mA sink drivers"},
            {
                "Parameter": "Cb max",
                "Value": "400 (Sm/Fm), 550 (Fm+)",
                "Unit": "pF",
                "Notes": "Trace + pin + cable capacitance",
            },
        ],
        "bus": [
            {
                "Parameter": "Address space",
                "Value": "7-bit (112 usable) / 10-bit",
                "Notes": "Avoid reserved 0x00–0x07, 0x78–0x7F",
            },
            {
                "Parameter": "Pull-up formula",
                "Value": "Rpmin=(VDD−VOL)/IOL; Rpmax=tr/(0.8473·Cb)",
                "Notes": "Live in the Science Lab designer",
            },
        ],
        "standards": ["NXP UM10204 I2C-bus specification", "SMBus 3.x (for SMBus/PMBus variants)"],
        "checklist": [
            "Size Rp for BOTH current (min) and rise time (max) — use the designer tab.",
            "One pull-up pair per bus segment; remove extra pull-ups on modules.",
            "Scan for address collisions before layout (two sensors, same address).",
        ],
    },
    "spi": {
        "signal_levels": [
            {
                "Parameter": "VIH / VIL",
                "Min": "0.7×VDD / −0.3",
                "Typ": "—",
                "Max": "VDD+0.3 / 0.3×VDD",
                "Unit": "V",
                "Notes": "CMOS per controller datasheet",
            },
            {
                "Parameter": "SCLK range",
                "Min": "0.1",
                "Typ": "10–40",
                "Max": "135",
                "Unit": "MHz",
                "Notes": "Peripheral-limited; flash often ≤ 104 MHz",
            },
        ],
        "timing": [
            {
                "Parameter": "SPI mode 0",
                "Value": "CPOL=0, CPHA=0 — sample on rising",
                "Unit": "—",
                "Notes": "Most common (flash, sensors)",
            },
            {
                "Parameter": "SPI mode 3",
                "Value": "CPOL=1, CPHA=1 — sample on rising",
                "Unit": "—",
                "Notes": "Idle-high variant of mode 0",
            },
            {"Parameter": "Byte time @ 10 MHz", "Value": "0.8", "Unit": "µs", "Notes": "8 clocks, no overhead"},
            {
                "Parameter": "CS setup/hold",
                "Value": "≥ 1 SCLK + peripheral spec",
                "Unit": "—",
                "Notes": "Check flash tSLCH/tCHSH",
            },
        ],
        "bus": [
            {
                "Parameter": "Fan-out",
                "Value": "1 CS per slave; MISO needs tri-state or mux",
                "Notes": "Series 22–33 Ω on SCLK for long runs",
            },
            {
                "Parameter": "Throughput",
                "Value": "fSCLK × 1 bit (×4 QSPI, ×8 OctoSPI)",
                "Unit": "bps",
                "Notes": "Use the Science Lab SPI calculator",
            },
        ],
        "standards": [
            "Motorola AN991 / MC68HC11 (original description)",
            "Peripheral datasheet (mode, max fSCLK, CS behaviour)",
        ],
        "checklist": [
            "Confirm CPOL/CPHA mode on BOTH ends — wrong edge = shifted data.",
            "MISO tri-states when CS idle; never tie two push-pull MISOs together.",
            "Keep SCLK < 10 cm at 40 MHz+; add series damping and ground return.",
        ],
    },
    "can": {
        "signal_levels": [
            {
                "Parameter": "Dominant CAN_H / CAN_L",
                "Min": "—",
                "Typ": "3.5 / 1.5",
                "Max": "—",
                "Unit": "V",
                "Notes": "Nominal; transceiver limits rule",
            },
            {
                "Parameter": "Recessive CAN_H / CAN_L",
                "Min": "—",
                "Typ": "2.5 / 2.5",
                "Unit": "V",
                "Notes": "Both near common mode",
            },
            {
                "Parameter": "Sample point",
                "Min": "75",
                "Typ": "80",
                "Max": "87.5",
                "Unit": "%",
                "Notes": "Bosch/CiA recommendation",
            },
            {
                "Parameter": "Time quanta per bit",
                "Min": "8",
                "Typ": "—",
                "Max": "25",
                "Unit": "TQ",
                "Notes": "ISO 11898-1",
            },
        ],
        "timing": [
            {
                "Parameter": "Bit time @ 500 kbps",
                "Value": "2000",
                "Unit": "ns",
                "Notes": "9 TQ example: sync1+prop3+ps1_3+ps2_2",
            },
            {
                "Parameter": "Base frame 8-byte",
                "Value": "111",
                "Unit": "bits on wire",
                "Notes": "108 frame + 3 intermission, pre-stuffing",
            },
            {
                "Parameter": "Worst-case stuffing",
                "Value": "+1 bit per 4",
                "Unit": "—",
                "Notes": "Size schedulers on worst case, not nominal",
            },
        ],
        "bus": [
            {
                "Parameter": "Termination",
                "Value": "120 Ω both ends (split 60 Ω + 4.7 nF typical)",
                "Notes": "Split termination suppresses common-mode EMI",
            },
            {"Parameter": "Node count", "Value": "~30 @ 1 Mbps", "Notes": "Stub + transceiver capacitance limited"},
            {
                "Parameter": "Arbitration",
                "Value": "11/29-bit ID = priority (dominant 0 wins)",
                "Notes": "Lowest ID wins without data loss",
            },
        ],
        "standards": ["Bosch CAN 2.0A/B", "ISO 11898-1/2", "CiA 301 (CANopen) / J1939 as applicable"],
        "checklist": [
            "Prescaler must be an integer — verify in the bit-timing calculator.",
            "Sample point 75–87.5%; stub < 0.3 m at 1 Mbps.",
            "Terminate both ends; never mid-bus; add common-mode choke + ESD.",
        ],
    },
    "lin": {
        "signal_levels": [
            {
                "Parameter": "Supply (VBAT)",
                "Min": "8",
                "Typ": "12",
                "Max": "18",
                "Unit": "V",
                "Notes": "12 V nominal vehicle rail",
            },
            {
                "Parameter": "Recessive (high)",
                "Min": "0.6×VBAT",
                "Typ": "VBAT",
                "Max": "—",
                "Unit": "V",
                "Notes": "Pulled up via master 1 kΩ + slave 30 kΩ",
            },
            {
                "Parameter": "Dominant (low)",
                "Min": "—",
                "Typ": "0",
                "Max": "0.2×VBAT",
                "Unit": "V",
                "Notes": "Driven low by transmitting node",
            },
        ],
        "timing": [
            {"Parameter": "Bit rate", "Value": "1–20", "Unit": "kbps", "Notes": "UART framing; master schedule table"},
            {"Parameter": "Bus length", "Value": "40", "Unit": "m max", "Notes": "Total capacitance limited"},
        ],
        "bus": [
            {"Parameter": "Nodes", "Value": "1 master + 16 slaves max", "Notes": "Single-wire + ground"},
            {
                "Parameter": "Protection",
                "Value": "Never to MCU pins directly — always via TJA1021/MCP2003A",
                "Notes": "VBAT-level transients",
            },
        ],
        "standards": ["LIN 2.2A", "SAE J2602 (US variant)"],
        "checklist": [
            "Master pull-up 1 kΩ + diode; slaves 30 kΩ — exactly one master resistor.",
            "Verify checksum version (classic vs enhanced) matches all nodes.",
        ],
    },
    "ethernet": {
        "signal_levels": [
            {
                "Parameter": "Diff impedance (copper)",
                "Min": "—",
                "Typ": "100",
                "Max": "—",
                "Unit": "Ω",
                "Notes": "Length-matched pairs, magnetics at jack",
            },
            {
                "Parameter": "100BASE-TX signalling",
                "Min": "—",
                "Typ": "MLT-3, 125 MBd",
                "Max": "—",
                "Unit": "—",
                "Notes": "Scrambler + 4B/5B",
            },
            {
                "Parameter": "1000BASE-T signalling",
                "Min": "—",
                "Typ": "PAM-5, 4 pairs",
                "Max": "—",
                "Unit": "—",
                "Notes": "Echo/crosstalk cancellers in PHY",
            },
        ],
        "timing": [
            {"Parameter": "Min frame", "Value": "64", "Unit": "bytes", "Notes": "512-bit slot time @ 10/100 Mbps"},
            {
                "Parameter": "Interframe gap",
                "Value": "96",
                "Unit": "bit times",
                "Notes": "12 bytes idle between frames",
            },
            {
                "Parameter": "100 m segment",
                "Value": "100",
                "Unit": "m",
                "Notes": "Cat5e+ @ 1 Gbps; propagation ≈ 5 ns/m",
            },
        ],
        "bus": [
            {
                "Parameter": "Topology",
                "Value": "Switched star; full-duplex; autonegotiated",
                "Notes": "No bus arbitration — switch buffers decide",
            },
            {
                "Parameter": "PoE budget",
                "Value": "15 W (af) / 30 W (at) / 60–90 W (bt)",
                "Unit": "W",
                "Notes": "Negotiate class before drawing",
            },
        ],
        "standards": ["IEEE 802.3 (100BASE-TX/1000BASE-T/100BASE-T1)", "RFC 894 (IP over Ethernet)"],
        "checklist": [
            "Magnetics + Bob Smith termination on every copper port.",
            "100 Ω diff, length-matched ±50 mils intra-pair @ 1 Gbps.",
            "Size switch buffers/schedulers for real-time variants (TSN/Profinet IRT).",
        ],
    },
    "modbus_rtu": {
        "signal_levels": [
            {
                "Parameter": "Wire levels",
                "Min": "—",
                "Typ": "RS-485 differential",
                "Max": "—",
                "Unit": "—",
                "Notes": "See RS-485 table for volts/termination",
            },
            {
                "Parameter": "Framing silence",
                "Min": "3.5",
                "Typ": "—",
                "Max": "—",
                "Unit": "char times",
                "Notes": "Inter-frame gap defines message boundary",
            },
        ],
        "timing": [
            {
                "Parameter": "Char time @ 9600 8E1",
                "Value": "1.15",
                "Unit": "ms",
                "Notes": "11 bits per char with parity",
            },
            {
                "Parameter": "Turnaround @ 9600",
                "Value": "~4",
                "Unit": "ms",
                "Notes": "3.5 chars — the latency floor of polling",
            },
            {
                "Parameter": "Poll cycle (30 slaves)",
                "Value": "~0.2–1",
                "Unit": "s",
                "Notes": "Request + response + silences per node",
            },
        ],
        "bus": [
            {
                "Parameter": "Address range",
                "Value": "1–247 slaves (0 broadcast)",
                "Notes": "Function code + 16-bit register address",
            },
            {
                "Parameter": "Integrity",
                "Value": "CRC-16/Modbus (check 0x4B37)",
                "Notes": "Verify live in the Science Lab CRC tab",
            },
        ],
        "standards": ["Modbus over Serial Line V1.02", "Modbus Application Protocol V1.1b3"],
        "checklist": [
            "Enforce 3.5-char silence in the master driver — short gaps split frames.",
            "Match parity/stop (8E1 vs 8N1) on every node; mismatches look like CRC errors.",
            "Terminate + bias the RS-485 segment; add repeaters past 32 unit loads.",
        ],
    },
    "usb20": {
        "signal_levels": [
            {
                "Parameter": "Diff impedance",
                "Min": "76.5",
                "Typ": "90",
                "Max": "103.5",
                "Unit": "Ω",
                "Notes": "USB 2.0 ±15%",
            },
            {
                "Parameter": "Speed detect",
                "Min": "—",
                "Typ": "1.5 kΩ to 3.3 V",
                "Unit": "Ω",
                "Notes": "On D− (full-speed) or D+ (low-speed)",
            },
            {
                "Parameter": "VBUS",
                "Min": "4.75",
                "Typ": "5.0",
                "Max": "5.25",
                "Unit": "V",
                "Notes": "100 mA → 500 mA after configuration",
            },
        ],
        "timing": [
            {
                "Parameter": "Low/full/high speeds",
                "Value": "1.5 / 12 / 480",
                "Unit": "Mbps",
                "Notes": "Chirp handshake negotiates high-speed",
            },
            {"Parameter": "Max cable", "Value": "5", "Unit": "m", "Notes": "Hubs/active cables beyond that"},
        ],
        "bus": [
            {
                "Parameter": "Addressing",
                "Value": "7-bit device + 4-bit endpoint",
                "Notes": "127 devices via hubs; host-scheduled",
            },
            {
                "Parameter": "Integrity",
                "Value": "CRC-5/CRC-16 + ACK/NAK/NYET/STALL retries",
                "Notes": "Guaranteed delivery per transfer type",
            },
        ],
        "standards": ["USB 2.0 (USB-IF)", "USB BC 1.2 (charging) / USB-C where applicable"],
        "checklist": [
            "90 Ω diff routing, no stubs; ESD array (USBLC6-2) at the connector.",
            "Enumerate power descriptors — never draw 500 mA before configuration.",
            "Chirp + eye-diagram pass on high-speed designs before certification.",
        ],
    },
    "i2s": {
        "signal_levels": [
            {
                "Parameter": "Logic levels",
                "Min": "GND",
                "Typ": "1.8/3.3 V CMOS",
                "Max": "VDD IO",
                "Unit": "V",
                "Notes": "Codec thresholds rule, not the protocol",
            },
            {
                "Parameter": "BCLK rate",
                "Min": "—",
                "Typ": "SR × channels × bits",
                "Max": "—",
                "Unit": "Hz",
                "Notes": "48 kHz×2×16 = 1.536 MHz example",
            },
        ],
        "timing": [
            {
                "Parameter": "WS (LRCLK)",
                "Value": "Sample rate (e.g. 48 kHz)",
                "Unit": "Hz",
                "Notes": "Left/right indicated by WS level",
            },
            {
                "Parameter": "Data alignment",
                "Value": "MSB-first, 1-BCLK delay (Philips)",
                "Unit": "—",
                "Notes": "Left/right-justified and DSP variants exist",
            },
        ],
        "bus": [
            {
                "Parameter": "Lines",
                "Value": "BCLK + WS + SD (×N channels)",
                "Notes": "Short PCB runs; MCLK often added for codec PLL",
            },
        ],
        "standards": ["Philips I2S bus specification (1986, rev. 1996)", "Codec datasheet (alignment, TDM slots)"],
        "checklist": [
            "Confirm alignment (I2S vs left-justified vs DSP) on both ends.",
            "Derive BCLK/WS from one master — two clock masters drift apart.",
        ],
    },
    "jtag": {
        "signal_levels": [
            {
                "Parameter": "TCK frequency",
                "Min": "1",
                "Typ": "10–50",
                "Max": "100",
                "Unit": "MHz",
                "Notes": "Divide down for long chains",
            },
            {
                "Parameter": "VTref (probe follows target)",
                "Min": "1.8",
                "Typ": "3.3",
                "Max": "5.0",
                "Unit": "V",
                "Notes": "Probe never drives the rail",
            },
            {
                "Parameter": "TAP states",
                "Min": "—",
                "Typ": "16",
                "Max": "—",
                "Unit": "states",
                "Notes": "TMS sequence navigates; TLR reset = 5× TMS=1",
            },
        ],
        "timing": [
            {
                "Parameter": "Chain shift cost",
                "Value": "N devices × IR/DR length",
                "Unit": "TCK cycles",
                "Notes": "Long chains slow every transaction",
            },
            {
                "Parameter": "Typical chain length",
                "Value": "20–30",
                "Unit": "cm ribbon",
                "Notes": "Buffer pods beyond that",
            },
        ],
        "bus": [
            {
                "Parameter": "Topology",
                "Value": "Daisy-chain TDI→TDO through every TAP",
                "Notes": "BYPASS unused devices to shorten the chain",
            },
            {
                "Parameter": "Key registers",
                "Value": "IDCODE / BYPASS / BOUNDARY / DEBUG",
                "Notes": "IDCODE first: proves the chain is alive",
            },
        ],
        "standards": ["IEEE 1149.1-2013", "IEEE 1149.7 (compact 2-wire variant)"],
        "checklist": [
            "Read IDCODE on every TAP before anything else.",
            "VTref wired to the target rail; TRST pulled as the datasheet demands.",
            "Keep TCK away from switching regulators; series-terminate long TCK.",
        ],
    },
    "usb4": {
        "signal_levels": [
            {
                "Parameter": "Lane rates (Gen 2/3/4)",
                "Min": "10",
                "Typ": "20",
                "Max": "40",
                "Unit": "Gbps/lane",
                "Notes": "USB4 v2 doubles to 80G via PAM-3",
            },
            {
                "Parameter": "Cable reach @ 40G",
                "Min": "—",
                "Typ": "0.8",
                "Max": "2",
                "Unit": "m",
                "Notes": "Active cable/retimer beyond that",
            },
        ],
        "timing": [
            {
                "Parameter": "Link training",
                "Value": "Lane bond + speed negotiate",
                "Unit": "—",
                "Notes": "Falls back gracefully, not silently",
            },
        ],
        "bus": [
            {
                "Parameter": "Tunnels",
                "Value": "USB3 + DisplayPort + PCIe simultaneously",
                "Notes": "Bandwidth shared dynamically, not partitioned",
            },
            {
                "Parameter": "Topology",
                "Value": "Router-to-router tree over USB-C",
                "Notes": "Backward compatible to USB 2.0 wiring",
            },
        ],
        "standards": ["USB4 v1.0/v2.0 (USB-IF)", "USB Type-C R2.4; USB PD R3.2"],
        "checklist": [
            "Budget retimers on every board-to-board hop at 40G+.",
            "Certify the CABLE, not just the ports — cable roulette is real.",
            "Test dock/SSD/display concurrency, not one function at a time.",
        ],
    },
    "can_xl": {
        "signal_levels": [
            {
                "Parameter": "Arbitration phase",
                "Min": "—",
                "Typ": "500 kbps – 1 Mbps",
                "Max": "—",
                "Unit": "bps",
                "Notes": "Classic levels, all nodes participate",
            },
            {
                "Parameter": "Data phase",
                "Min": "2",
                "Typ": "10",
                "Max": "20",
                "Unit": "Mbps",
                "Notes": "SIC-XL transceiver mode switch",
            },
            {
                "Parameter": "Payload",
                "Min": "1",
                "Typ": "—",
                "Max": "2048",
                "Unit": "bytes",
                "Notes": "32-bit CRCs (preamble + frame)",
            },
        ],
        "timing": [
            {
                "Parameter": "Mode switch gap",
                "Value": "Transceiver-dependent",
                "Unit": "ns",
                "Notes": "No classic-CAN node may hear the fast phase",
            },
        ],
        "bus": [
            {
                "Parameter": "Compatibility",
                "Value": "No mixed segments with classic/CAN-FD-only nodes",
                "Notes": "Fast phase looks like errors to old transceivers",
            },
            {
                "Parameter": "Ethernet tunneling",
                "Value": "Full 100BASE-T1 frame fits in one XL payload",
                "Notes": "The zonal-gateway use case",
            },
        ],
        "standards": ["CiA 610-1 (CAN XL data link layer)", "ISO 11898-1 (arbitration phase)"],
        "checklist": [
            "Every transceiver on the segment must be SIC-XL capable.",
            "Re-verify stub/termination rules at 10 Mbps+ edges.",
            "Size schedulers on 2048-byte worst cases, not 8-byte habits.",
        ],
    },
}


def get_deep_spec(pid):
    """Return the deep parametric table for a protocol id, or None."""
    return DEEP_SPECS.get(pid)


def has_deep_spec(pid):
    """Whether a flagship deep table exists for this protocol id."""
    return pid in DEEP_SPECS
