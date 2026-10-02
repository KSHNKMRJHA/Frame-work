# -*- coding: utf-8 -*-
"""One-stop glossary: every jargon term in the Academy, defined once.

Groups keep the page browsable; `see` links each term to the protocol ids
where it matters most (resolved to names by the Glossary page).
"""

GLOSSARY = [
    # ------------------------- Signalling -------------------------
    {
        "term": "Single-ended",
        "group": "Signalling",
        "definition": "One wire carries the signal voltage referenced to ground. Cheap and simple (UART, SPI) but every millivolt of ground noise lands in the signal.",
        "see": ["uart", "spi", "rs232"],
    },
    {
        "term": "Differential",
        "group": "Signalling",
        "definition": "Information lives in the voltage DIFFERENCE between two wires (A/B, CAN_H/L). Noise hitting both wires equally cancels at the receiver.",
        "see": ["rs485", "can", "ethernet", "lvds"],
    },
    {
        "term": "Dominant / recessive",
        "group": "Signalling",
        "definition": "CAN's wired-AND trick: any node can pull the bus dominant (0), which overwrites recessive (1). Arbitration and ACK both exploit this.",
        "see": ["can", "can_fd", "can_xl"],
    },
    {
        "term": "Open-drain / open-collector",
        "group": "Signalling",
        "definition": "Drivers can only pull low; a pull-up resistor makes the high. Lets many devices share one line (I2C) and enables wired-AND.",
        "see": ["i2c", "smbus", "1wire"],
    },
    {
        "term": "Push-pull",
        "group": "Signalling",
        "definition": "Driver actively drives both high and low (SPI, CMOS outputs). Fast edges, but two drivers fighting will damage silicon.",
        "see": ["spi", "qspi"],
    },
    {
        "term": "Common-mode voltage",
        "group": "Signalling",
        "definition": "The average of the two differential wires relative to ground. Receivers tolerate a range (RS-485: -7 to +12 V); exceed it and they die.",
        "see": ["rs485", "can"],
    },
    {
        "term": "Noise margin",
        "group": "Signalling",
        "definition": "VOHmin-VIHmin (high) and VILmax-VOLmax (low): how much noise the link absorbs before misreading a bit. Compute it in the Science Lab.",
        "see": ["uart", "i2c", "spi"],
    },
    {
        "term": "Fail-safe biasing",
        "group": "Signalling",
        "definition": "Pull-up/down resistors holding an idle RS-485 pair above +200 mV so receivers read a guaranteed recessive instead of noise.",
        "see": ["rs485", "modbus_rtu", "profibus"],
    },
    {
        "term": "Termination",
        "group": "Signalling",
        "definition": "A resistor matching the cable impedance (CAN/RS-485: 120 ohm) at the bus ends that swallows reflections. Mid-bus terminators cause the problems they pretend to fix.",
        "see": ["can", "rs485", "ethernet"],
    },
    {
        "term": "AC coupling",
        "group": "Signalling",
        "definition": "Series capacitors blocking DC on high-speed lanes (PCIe, USB3, Ethernet) so transmitter and receiver can use different common-mode voltages.",
        "see": ["pcie", "usb3x", "sgmii"],
    },
    {
        "term": "Pre-emphasis / equalization",
        "group": "Signalling",
        "definition": "Boosting fast edges at the transmitter (pre-emphasis) or re-sharpening them at the receiver (equalization) to survive lossy channels.",
        "see": ["pcie", "usb3x", "serdes"],
    },
    {
        "term": "Eye diagram",
        "group": "Signalling",
        "definition": "Overlapped bits on a scope: the open 'eye' is your margin. Closed eye = jitter/noise eating the sampling window; fix the channel, not the software.",
        "see": ["usb20", "pcie", "ethernet"],
    },
    # ---------------------- Timing & clocking ----------------------
    {
        "term": "Baud vs bit rate",
        "group": "Timing & Clocking",
        "definition": "Baud = symbols/second; bit rate = bits/second. Equal only for 1-bit symbols (UART). PAM-3/4 and QAM pack multiple bits per symbol.",
        "see": ["uart", "ethernet", "automotive_ethernet"],
    },
    {
        "term": "Oversampling",
        "group": "Timing & Clocking",
        "definition": "Sampling each UART bit 8-16x and voting near the centre. The divisor rounding this forces is what the baud calculator computes.",
        "see": ["uart", "lin"],
    },
    {
        "term": "Sample point",
        "group": "Timing & Clocking",
        "definition": "Where inside a CAN bit the receiver latches (Bosch/CiA: 75-87.5%). Late point = noise immunity; early point = long-bus tolerance.",
        "see": ["can", "can_fd"],
    },
    {
        "term": "Time quanta (TQ)",
        "group": "Timing & Clocking",
        "definition": "CAN's atomic time unit: Sync + Prop + Phase1 + Phase2 segments, 8-25 TQ per bit. The bit-timing calculator builds them.",
        "see": ["can"],
    },
    {
        "term": "Bit stuffing",
        "group": "Timing & Clocking",
        "definition": "Inserting an opposite bit after five identical ones (CAN, USB) to force edges for clock recovery. Budget the worst case in schedulers.",
        "see": ["can", "usb20"],
    },
    {
        "term": "Clock recovery (CDR)",
        "group": "Timing & Clocking",
        "definition": "Rebuilding the clock from data edges instead of a wire (USB, Ethernet, SERDES). Needs guaranteed transitions — hence encoding and stuffing.",
        "see": ["usb20", "ethernet", "serdes"],
    },
    {
        "term": "Spread-spectrum clocking",
        "group": "Timing & Clocking",
        "definition": "Wobbling the clock a fraction of a percent to smear EMI peaks below regulatory limits. Free on most MCU PLLs; verify UART error impact.",
        "see": ["pcie", "usb3x"],
    },
    {
        "term": "gPTP / time sync",
        "group": "Timing & Clocking",
        "definition": "Generalized Precision Time Protocol: sub-microsecond clock alignment across a TSN network, the foundation every schedule stands on.",
        "see": ["tsn", "ntp"],
    },
    # --------------------------- Bus access ---------------------------
    {
        "term": "Arbitration",
        "group": "Bus Access",
        "definition": "Deciding who talks when two nodes start together. Destructive (Ethernet collisions, retries) vs non-destructive (CAN priority wins, zero data lost).",
        "see": ["can", "i2c", "ethernet"],
    },
    {
        "term": "Master / slave",
        "group": "Bus Access",
        "definition": "One node commands (SPI master, LIN master, Modbus master); the rest obey. Simple, but the master is a single point of failure.",
        "see": ["spi", "lin", "modbus_rtu"],
    },
    {
        "term": "Multi-master",
        "group": "Bus Access",
        "definition": "Any node may start a transfer (I2C, CAN). Requires arbitration and clock synchronization rules.",
        "see": ["i2c", "can"],
    },
    {
        "term": "CSMA/CD vs CSMA/CA",
        "group": "Bus Access",
        "definition": "Listen-before-talk with collision DETECTION+retry (old Ethernet hubs) vs collision AVOIDANCE (Wi-Fi RTS/CTS, backoff). Switches made CD history.",
        "see": ["ethernet", "wifi"],
    },
    {
        "term": "TDMA / token passing",
        "group": "Bus Access",
        "definition": "Time slots (FlexRay static segment, TSN Qbv) or a circulating token (PROFIBUS masters) guarantee turns. Deterministic, but slots idle when owners are quiet.",
        "see": ["flexray", "profibus", "tsn"],
    },
    {
        "term": "PLCA",
        "group": "Bus Access",
        "definition": "Physical Layer Collision Avoidance: round-robin transmit turns giving 10BASE-T1S multidrop determinism without a switch.",
        "see": ["t1s"],
    },
    {
        "term": "Daisy-chain vs star",
        "group": "Bus Access",
        "definition": "Daisy-chain (RS-485 done right) keeps one controlled impedance path; stars branch it and every branch reflects. Stubs follow the stub-length rule in the Science Lab.",
        "see": ["rs485", "can", "dmx512"],
    },
    # -------------------------- Error handling --------------------------
    {
        "term": "Parity",
        "group": "Error Handling",
        "definition": "One extra bit making the 1-count even or odd. Catches single-bit flips, blind to double flips — a tripwire, not a guarantee.",
        "see": ["uart", "can", "lin"],
    },
    {
        "term": "Checksum",
        "group": "Error Handling",
        "definition": "Arithmetic sum over a message (LIN, NMEA *, IP header). Cheap, catches accidents, useless against malice.",
        "see": ["lin", "nmea", "modbus_rtu"],
    },
    {
        "term": "CRC",
        "group": "Error Handling",
        "definition": "Polynomial division remainder (CRC-16/Modbus, CRC-32/Ethernet). Catches burst errors up to the polynomial degree — verify yours in the CRC tab.",
        "see": ["modbus_rtu", "can", "ethernet"],
    },
    {
        "term": "ACK / NACK",
        "group": "Error Handling",
        "definition": "Per-byte (I2C) or per-frame (CAN, TCP) receipt handshake. A NACK is the cheapest possible error signal — design what happens on it.",
        "see": ["i2c", "can", "tcp"],
    },
    {
        "term": "FEC (forward error correction)",
        "group": "Error Handling",
        "definition": "Redundant coding that FIXES errors without retransmission (deep-space links, 5G, 100G+ Ethernet). Costs bandwidth to save round trips.",
        "see": ["5g", "spacewire", "ethernet"],
    },
    {
        "term": "ARQ / retransmission",
        "group": "Error Handling",
        "definition": "Detect, discard, ask again (TCP, Wi-Fi, Zigbee). Simple and reliable, fatal for hard deadlines — determinism and ARQ are enemies.",
        "see": ["tcp", "wifi", "zigbee"],
    },
    {
        "term": "Error confinement",
        "group": "Error Handling",
        "definition": "CAN's transmit/receive error counters that demote a babbling node to error-passive, then bus-off — the network amputates the faulty limb itself.",
        "see": ["can", "can_fd"],
    },
    {
        "term": "Watchdog (protocol)",
        "group": "Error Handling",
        "definition": "Timeout supervision: SMBus packet-error timers, LIN schedule monitors, DDS deadline QoS. A silent node must become a KNOWN-dead node fast.",
        "see": ["smbus", "lin", "dds"],
    },
    # ------------------------- RF & wireless -------------------------
    {
        "term": "Link budget",
        "group": "RF & Wireless",
        "definition": "TX power + gains - path loss - losses vs receiver sensitivity. Positive margin = the link closes. Compute it in the RF tab before buying antennas.",
        "see": ["lora", "wifi", "sigfox"],
    },
    {
        "term": "FSPL",
        "group": "RF & Wireless",
        "definition": "Free-space path loss: 20log(d) + 20log(f) + 32.44 dB. Doubling distance OR frequency costs 6 dB — physics, non-negotiable.",
        "see": ["wifi", "lora", "5g"],
    },
    {
        "term": "RSSI vs sensitivity",
        "group": "RF & Wireless",
        "definition": "RSSI is what you HAVE; sensitivity is what you NEED. Design for 10-20 dB fade margin above sensitivity, not equality.",
        "see": ["ble", "zigbee", "lorawan"],
    },
    {
        "term": "Duty cycle (regulatory)",
        "group": "RF & Wireless",
        "definition": "EU sub-GHz law: typically 1% airtime per device per hour. Your clever 10-second reporting loop may be illegal — LoRaWAN enforces this.",
        "see": ["lorawan", "sigfox"],
    },
    {
        "term": "Spreading factor",
        "group": "RF & Wireless",
        "definition": "LoRa's range-vs-speed dial (SF7 fast/short … SF12 slow/far). Each step up roughly halves the rate and doubles the range.",
        "see": ["lora", "lorawan"],
    },
    {
        "term": "Mesh vs star",
        "group": "RF & Wireless",
        "definition": "Star: every node talks to one gateway (LoRaWAN, normalsimple). Mesh: nodes relay for each other (Zigbee, Thread, WirelessHART) — self-healing, but routing overhead.",
        "see": ["zigbee", "thread", "lorawan"],
    },
    {
        "term": "MCS index",
        "group": "RF & Wireless",
        "definition": "Wi-Fi's modulation dial: higher MCS = denser QAM = faster but needs cleaner signal. Weak RSSI silently downshifts you to 1990s speeds.",
        "see": ["wifi"],
    },
    # ---------------------------- Networking ----------------------------
    {
        "term": "OSI layers",
        "group": "Networking",
        "definition": "The 7-layer map (Physical … Application) every entry in this Academy is tagged with. Most confusion is two people arguing about different layers.",
        "see": ["ethernet", "tcp", "mqtt"],
    },
    {
        "term": "MTU / fragmentation",
        "group": "Networking",
        "definition": "Biggest packet a link carries (Ethernet 1500, 15.4 radio 127). Exceed it and something must fragment — 6LoWPAN exists because IPv6 headers alone overflow a radio frame.",
        "see": ["6lowpan", "ethernet", "ip"],
    },
    {
        "term": "Broker vs brokerless",
        "group": "Networking",
        "definition": "MQTT routes everything through a broker (simple, one throat to choke); DDS discovers peers directly (no single failure, multicast chatter).",
        "see": ["mqtt", "dds"],
    },
    {
        "term": "QoS (messaging)",
        "group": "Networking",
        "definition": "Delivery contracts: MQTT 0/1/2 (at-most/at-least/exactly-once), DDS deadlines/durability/ownership. Pick the guarantee your safety case needs.",
        "see": ["mqtt", "dds"],
    },
    {
        "term": "Service discovery",
        "group": "Networking",
        "definition": "Finding services without hardcoding addresses: mDNS, SOME/IP-SD, DDS discovery, OPC UA LDS. Static IPs are a deployment time bomb.",
        "see": ["mdns", "someip", "dds"],
    },
    {
        "term": "Time-triggered vs event-triggered",
        "group": "Networking",
        "definition": "Time-triggered (FlexRay static, TSN Qbv, LIN schedule): slots guarantee timing. Event-triggered (CAN arbitration, interrupts): fast response, provable worst case required.",
        "see": ["flexray", "tsn", "lin"],
    },
    # ------------------------ Hardware & cabling ------------------------
    {
        "term": "Characteristic impedance",
        "group": "Hardware & Cabling",
        "definition": "The AC resistance a signal sees (twisted pair ~100-120 ohm, USB 90 ohm). Terminate WITH it or reflections return as ghost bits.",
        "see": ["rs485", "ethernet", "usb20"],
    },
    {
        "term": "Stub",
        "group": "Hardware & Cabling",
        "definition": "An unterminated branch off the bus. Keep it under ~1/10 of the edge length (Science Lab stub tab) or daisy-chain properly.",
        "see": ["rs485", "can"],
    },
    {
        "term": "Galvanic isolation",
        "group": "Hardware & Cabling",
        "definition": "Breaking the electrical path (optocouplers, digital isolators, transformers) so ground differences and surges stop at the barrier. Mandatory between buildings and near high voltage.",
        "see": ["rs485", "can", "ethernet"],
    },
    {
        "term": "ESD protection",
        "group": "Hardware & Cabling",
        "definition": "TVS diode arrays at every exposed connector (USBLC6 for USB, bus-level TVS for CAN/RS-485). The cheapest insurance in the BOM.",
        "see": ["usb20", "can", "usbc"],
    },
    {
        "term": "Pull-up sizing",
        "group": "Hardware & Cabling",
        "definition": "Rp must be small enough for rise time (Rpmax = tr/0.8473Cb) yet large enough for the driver to sink (Rpmin = (VDD-VOL)/IOL). The I2C designer tab solves both.",
        "see": ["i2c", "smbus", "1wire"],
    },
    {
        "term": "Level shifting",
        "group": "Hardware & Cabling",
        "definition": "Translating between voltage domains (TXB0104 auto-sense, 74LVC245 driven). Never join 5 V outputs to 3.3 V-only inputs and hope.",
        "see": ["uart", "spi", "i2c"],
    },
    {
        "term": "VTref",
        "group": "Hardware & Cabling",
        "definition": "The target-voltage reference pin on debug probes: the probe follows YOUR rail instead of imposing its own. Wrong VTref = misread bits.",
        "see": ["jtag", "swd"],
    },
    {
        "term": "PoE (Power over Ethernet)",
        "group": "Hardware & Cabling",
        "definition": "15-90 W delivered with data over the same cable (af/at/bt). Negotiate the class — assuming power is how cameras brown out at night.",
        "see": ["ethernet", "bacnet"],
    },
    # ------------------------------ Security ------------------------------
    {
        "term": "Mutual authentication",
        "group": "Security",
        "definition": "Both ends prove identity (TLS client certs, WPA-Enterprise, OPC UA app certs). One-sided auth invites impersonation from either direction.",
        "see": ["tls", "opcua", "wpa"],
    },
    {
        "term": "Secure boot / attestation",
        "group": "Security",
        "definition": "Verifying firmware signatures at reset (USB DFU signing, ECU secure boot). Unsigned bootloaders make every protocol security above them decorative.",
        "see": ["usbdfu", "uds"],
    },
    {
        "term": "Replay protection",
        "group": "Security",
        "definition": "Sequence numbers/timestamps rejecting recorded-and-replayed commands (MAVLink v2 signing, car key fobs). Encryption without it replays just fine.",
        "see": ["mavlink", "tls"],
    },
    # ------------------------------- Concepts -------------------------------
    {
        "term": "Determinism",
        "group": "Concepts",
        "definition": "Bounded worst-case latency, not speed. A 9.6 kbps deterministic bus beats gigabit Ethernet for control — the Selector ranks capability, YOU judge determinism per profile.",
        "see": ["ethercat", "flexray", "tsn"],
    },
    {
        "term": "Jitter",
        "group": "Concepts",
        "definition": "Variation in arrival time. Sub-microsecond (EtherCAT/TSN) vs milliseconds (Wi-Fi under load) decides which physics you may close the loop on.",
        "see": ["ethercat", "tsn", "wifi"],
    },
    {
        "term": "Full / half / simplex",
        "group": "Concepts",
        "definition": "Full-duplex: both ways at once (SPI, switched Ethernet). Half: one way at a time (RS-485 2-wire, CAN). Simplex: one way ever (ARINC 429, 4-20 mA).",
        "see": ["spi", "rs485", "arinc429"],
    },
    {
        "term": "Latency vs throughput",
        "group": "Concepts",
        "definition": "Latency = how fast ONE message arrives; throughput = how many per second. Small CAN frames win latency; big NVMe queues win throughput.",
        "see": ["can", "nvme", "ethercat"],
    },
    {
        "term": "Backpressure / flow control",
        "group": "Concepts",
        "definition": "Telling the sender to slow down: RTS/CTS, XON/XOFF, ISO-TP FlowControl, TCP windowing, DDS QoS. Every fast-producer/slow-consumer pair needs one.",
        "see": ["uart", "isotp", "tcp"],
    },
    {
        "term": "Endianness / byte order",
        "group": "Concepts",
        "definition": "Which byte of a multi-byte value goes first. Mixed-endian buses (looking at you, Modbus 32-bit floats) corrupt values that LOOK plausible.",
        "see": ["modbus_rtu", "ethernet"],
    },
]

GROUPS = [
    "Signalling",
    "Timing & Clocking",
    "Bus Access",
    "Error Handling",
    "RF & Wireless",
    "Networking",
    "Hardware & Cabling",
    "Security",
    "Concepts",
]


def search_glossary(query):
    """Case-insensitive substring search over terms + definitions."""
    q = (query or "").lower().strip()
    if not q:
        return GLOSSARY
    return [g for g in GLOSSARY if q in g["term"].lower() or q in g["definition"].lower()]
