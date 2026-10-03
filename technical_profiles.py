# -*- coding: utf-8 -*-
"""Normalized electrical and hardware details for every protocol record."""

from copy import deepcopy

OLD_FIELDS = (
    "scope",
    "signaling",
    "logic_high",
    "logic_low",
    "voltage_reference",
    "clocking",
    "termination_and_biasing",
    "design_notes",
)

# Deep parametric layer — every protocol also reports bus-level engineering
# data so the Encyclopedia and Compare pages can show distance, fan-out,
# duplex, addressing, error handling, line coding, power and EMC guidance
# instead of prose alone. All new fields are plain strings (like the original
# seven) so logical/RF layers can honestly say "not defined here".
NEW_FIELDS = (
    "max_distance",
    "max_nodes",
    "duplex_mode",
    "addressing",
    "error_detection",
    "line_encoding",
    "power_profile",
    "emc_isolation",
)

FIELDS = OLD_FIELDS + NEW_FIELDS

_PHYSICAL = {
    "scope": "Board/link physical layer — implementation-dependent",
    "signaling": "Device-to-device digital signaling; exact thresholds depend on the selected controller, peripheral, and I/O voltage.",
    "logic_high": "Typically near the device I/O supply; confirm VOH/VIH in the device datasheet.",
    "logic_low": "Typically near ground; confirm VOL/VIL in the device datasheet.",
    "voltage_reference": "Common rails include 1.8 V, 3.3 V, and 5 V; do not mix incompatible domains.",
    "clocking": "Synchronous, asynchronous, or encoded per the interface; check setup/hold and rise/fall limits.",
    "termination_and_biasing": "Pull-ups, series resistors, and termination depend on the interface; follow its reference design.",
    "design_notes": ["The protocol name alone does not set a voltage; the concrete device datasheet is authoritative."],
    "max_distance": "Board-level: centimetres to a few metres unless a line driver / transceiver is added.",
    "max_nodes": "Point-to-point unless the interface defines multi-drop (see addressing).",
    "duplex_mode": "Interface-dependent; check whether the link is half- or full-duplex.",
    "addressing": "No universal scheme at the electrical layer; addressing (if any) is defined by the protocol layer.",
    "error_detection": "No error detection at the wire layer; framing errors, parity or CRC (if any) belong to the protocol.",
    "line_encoding": "Typically NRZ single-ended or differential; encoded variants are protocol-specific.",
    "power_profile": "I/O supply domain (1.8/3.3/5 V); quiescent current is transceiver/MCU dependent.",
    "emc_isolation": "Keep high-speed traces short, reference to a solid ground plane; add ESD protection on off-board links.",
}

_CARRIER = {
    "scope": "Protocol layer — carrier-dependent",
    "signaling": "No physical signaling defined here; bytes are carried by a lower physical/link layer.",
    "logic_high": "Not defined by this protocol; inherited from the selected carrier PHY/link.",
    "logic_low": "Not defined by this protocol; inherited from the selected carrier PHY/link.",
    "voltage_reference": "No fixed voltage; inspect the selected physical medium and transceiver.",
    "clocking": "Protocol timing is carrier-independent; physical timing follows the lower link layer.",
    "termination_and_biasing": "Follow the carrier specification, not the application protocol.",
    "design_notes": ["Identify the physical and link layers before selecting wiring or a transceiver."],
    "max_distance": "Inherited from the selected carrier (metres to kilometres).",
    "max_nodes": "Inherited from the selected carrier / network topology.",
    "duplex_mode": "Inherited from the selected carrier; most network carriers are full-duplex.",
    "addressing": "Protocol-level addressing (e.g. IP address, node ID); physical addressing follows the carrier.",
    "error_detection": "Protocol-level checks (checksum/CRC, sequence numbers, retransmission); PHY errors are detected below.",
    "line_encoding": "Inherited from the carrier PHY (e.g. PAM, 8b/10b, OFDM subcarriers).",
    "power_profile": "No power defined here; budget the carrier PHY plus host processor.",
    "emc_isolation": "Follow the carrier medium rules (Ethernet magnetics, RF shielding, mains isolation).",
}

_RF = {
    "scope": "RF physical/link layer",
    "signaling": "RF modulation; symbols are transmitted over the air rather than as fixed wire voltages.",
    "logic_high": "No direct logic-high voltage; high-level state is represented by a modulation/symbol.",
    "logic_low": "No direct logic-low voltage; low-level state is represented by a modulation/symbol.",
    "voltage_reference": "Use radio frequency, transmit-power, antenna, and regulatory limits instead.",
    "clocking": "PHY symbol timing and clock recovery depend on the radio generation.",
    "termination_and_biasing": "RF matching, antenna impedance, and link budget replace wire termination.",
    "design_notes": ["Document frequency, modulation, antenna interface, and regional power limits."],
    "max_distance": "Link-budget dependent: metres (short-range) to kilometres (LoRa/cellular) line-of-sight.",
    "max_nodes": "Star/mesh dependent; check gateway capacity and duty-cycle regulations.",
    "duplex_mode": "Typically half-duplex TDD; full-duplex via paired bands or time slots on cellular.",
    "addressing": "Network address (MAC/short address/IMSI); check join/provisioning procedure.",
    "error_detection": "PHY CRC plus link-layer ARQ/FEC; see the Science Lab link-budget calculator.",
    "line_encoding": "RF modulation (FSK, O-QPSK, OFDM, QAM, CSS); spreading/ FEC per standard.",
    "power_profile": "Sleep current (µA) vs TX current (mA–A); duty cycle dominates battery life — budget with the link margin.",
    "emc_isolation": "50 Ω antenna match, keep-out zone, shielding; certify to regional radio regulations (ETSI/FCC).",
}

_CATEGORY = {
    "Industrial": (
        "Fieldbus/link layer — carrier-dependent",
        "Industrial protocol carried by RS-485, Ethernet, current loop, or another transceiver.",
        "Not universal; use the selected carrier/transceiver's high threshold.",
        "Not universal; use the selected carrier/transceiver's low threshold.",
        "No single fieldbus voltage; isolate and rate transceivers for the installation.",
        "Frame timing follows the physical/link layer; some fieldbus protocols add deterministic scheduling.",
        "Twisted-pair buses commonly need controlled impedance, biasing, end termination, and protection.",
        ["Name the electrical carrier separately from the industrial application protocol."],
    ),
    "Automotive": (
        "Vehicle network/link layer",
        "Automotive transceiver signaling; physical levels depend on CAN, LIN, FlexRay, Ethernet, or the selected vehicle network.",
        "Not one universal level; use the vehicle network transceiver thresholds.",
        "Not one universal level; use the vehicle network transceiver thresholds.",
        "Vehicle power is commonly 12 V or 24 V; signal levels are set by the network transceiver.",
        "Bit timing and synchronization follow the selected vehicle network protocol.",
        "Use specified termination, biasing, shielding, and transient protection.",
        ["Also budget for load dump, reverse battery, ESD, and automotive transients."],
    ),
    "Audio/Video": (
        "Board-level or link physical layer",
        "Digital audio/video signaling; CMOS, differential, encoded, or optical depending on the interface.",
        "Usually near the interface supply for CMOS; differential/encoded interfaces use receiver thresholds.",
        "Usually near ground for CMOS; differential/encoded interfaces use receiver thresholds.",
        "Typical board signaling is 1.8 V or 3.3 V CMOS; professional differential/optical interfaces use their own standards.",
        "Usually synchronous with a bit clock, or clock-recovered from an encoded stream.",
        "Use series damping, pull-ups/down, AC coupling, or 100 Ω differential termination as specified.",
        ["Timing, impedance, and connector requirements are often more important than the label."],
    ),
    "USB": (
        "USB physical/link layer",
        "Universal Serial Bus uses differential data pairs and separate control/clock signaling in newer generations.",
        "USB data is encoded differential signaling; D+/D− are not a simple fixed logic-high rail.",
        "USB data is encoded differential signaling; D+/D− are not a simple fixed logic-low rail.",
        "USB 1.1/2.0 use 3.3 V transceiver signaling; USB 3.x adds high-speed differential lanes.",
        "Clock recovery is standard; USB 3.x adds separate high-speed transmit/receive lanes.",
        "USB 2.0 uses a 1.5 kΩ pull-up; USB 3.x requires controlled differential impedance and AC coupling.",
        ["Use a USB controller/PHY and follow connector, ESD, cable, and impedance requirements."],
    ),
    "High-Speed/FPGA": (
        "High-speed physical/link layer",
        "High-speed differential or encoded SERDES signaling implemented through transceiver/PHY hardware.",
        "Not a universal logic-high voltage; receivers decode symbols or differential thresholds.",
        "Not a universal logic-low voltage; receivers decode symbols or differential thresholds.",
        "Voltage swing and common-mode are PHY/standard-specific; consult the transceiver design guide.",
        "Embedded, forwarded, or recovered clock; equalization and deskew may be required.",
        "Controlled differential impedance, AC coupling, biasing, and termination are required.",
        ["PCB stack-up, lane matching, reference clock, jitter, and channel loss are first-order constraints."],
    ),
    "Aerospace": (
        "Mission-critical physical/link layer",
        "Aviation/aerospace signaling commonly uses differential, current-loop, or redundant wired links.",
        "Not universally defined; use the approved transceiver and interface specification.",
        "Not universally defined; use the approved transceiver and interface specification.",
        "Aircraft buses may use 12/28 V power and specialized signal levels; do not infer them from bus names.",
        "Deterministic scheduling, redundancy, and fault containment are primary constraints.",
        "Follow qualified wiring, termination, isolation, shielding, and redundancy requirements.",
        ["Certification, radiation tolerance, and fault containment are part of the hardware design."],
    ),
    "Sensor-Specific": (
        "Sensor physical/link layer",
        "Purpose-built sensor/actuator signaling, commonly a switched 24 V line, current loop, or synchronous sensor bus.",
        "Use the sensor standard's high threshold; it may be voltage, current, or an encoded pulse.",
        "Use the sensor standard's low threshold; it may be voltage, current, or an encoded pulse.",
        "Industrial sensors commonly use 24 V DC, but signal levels and tolerances are interface-specific.",
        "May be edge-timed, current-modulated, or master-clocked; timing windows are part of the specification.",
        "Use the specified pull-up/current path, load, shielding, and cable protection.",
        ["Check parasitic power limits and inrush as well as data timing."],
    ),
}


# Deep bus-level parameters per category, aligned positionally with NEW_FIELDS:
# (max_distance, max_nodes, duplex_mode, addressing, error_detection,
#  line_encoding, power_profile, emc_isolation)
_CATEGORY_EXTRA = {
    "On-Board": (
        "Centimetres to ~1 m on PCB; use drivers/repeaters beyond that.",
        "1 master + 1–8 slaves typical; bus variants allow up to 128 with addressing.",
        "SPI full-duplex master/slave; I²C/UART half-duplex; check per interface.",
        "Chip-select, 7/10-bit address, or 64-bit ROM ID depending on the bus.",
        "Parity / ACK-NACK / CRC-8/16 depending on the protocol layer.",
        "NRZ single-ended (CMOS/TTL) or open-drain; differential only via transceiver.",
        "Logic supply 1.8–5 V; sleep µA to active mA — check MCU + peripheral datasheets.",
        "Solid ground return, short stubs, series damping on fast edges; ESD array on connectors.",
    ),
    "Industrial": (
        "RS-485: 1200 m @ 100 kbps down to 12 m @ 10 Mbps; Ethernet: 100 m per segment.",
        "RS-485: 32 unit loads (up to 256 with 1/8-load PHYs); Ethernet: switch-limited.",
        "RS-485 half-duplex 2-wire (full-duplex 4-wire); Ethernet full-duplex switched.",
        "Slave/node address, station number, or IP address per protocol.",
        "CRC-16 (Modbus RTU), 32-bit FCS (Ethernet), token/error counters per fieldbus.",
        "NRZ differential (RS-485) or PAM / MLT-3 / 4D-PAM5 (Ethernet).",
        "24 V field power common; bus-powered nodes must respect segment current limits.",
        "Shielded twisted pair, 120 Ω termination, TVS + galvanic isolation in harsh plants.",
    ),
    "Automotive": (
        "CAN: 40 m @ 1 Mbps up to 1000 m @ 50 kbps; LIN: 40 m; Automotive Ethernet: 15 m.",
        "CAN: ~30 nodes; LIN: 1 master + 16 slaves; Ethernet: ECU + switch ports.",
        "CAN/LIN half-duplex shared bus; Automotive Ethernet full-duplex point-to-point.",
        "CAN 11/29-bit message ID (priority); LIN 6-bit ID + master schedule.",
        "CAN 15-bit CRC + ACK + error frames; LIN checksum + parity; Ethernet FCS.",
        "CAN NRZ differential dominant/recessive; LIN UART-coded single-wire; Ethernet PAM-3.",
        "12/24 V vehicle rail via transceiver; sleep/wake-up current critical for battery drain.",
        "Twisted/shielded harness, common-mode choke, load-dump / reverse-battery / ESD protection.",
    ),
    "Audio/Video": (
        "I²S/parallel: <10 cm on PCB; HDMI/DP: 2–15 m passive; SDI/optical: 100+ m.",
        "Point-to-point or source + sink; distribution via switch/splitter.",
        "I²S full-duplex clocks + data; HDMI/DP unidirectional video + bidirectional control.",
        "Stream/channel select, device address, or EDID-negotiated endpoint.",
        "Parity/channel-status (S/PDIF), ECC + CRC (HDMI/DP), retransmission on control channel.",
        "NRZ CMOS, biphase-mark (S/PDIF), TMDS / 8b/10b / 128b/132b (video links).",
        "Codec 1.8/3.3 V; phantom power (mics) or 5 V (HDMI) per standard — never back-feed.",
        "Continuous ground plane, 90/100 Ω diff routing, ESD on user-facing connectors.",
    ),
    "USB": (
        "USB 2.0: 5 m; USB 3.x: 1–3 m passive (longer with active cable/retimer).",
        "127 devices per host controller via hubs (shared bandwidth).",
        "Half-duplex broadcast (USB 2.0); dual-simplex SuperSpeed pairs (USB 3.x).",
        "7-bit device address assigned at enumeration; endpoint numbers per function.",
        "CRC-5/CRC-16 on tokens/data + handshake retries (ACK/NAK/NYET/STALL).",
        "NRZI + bit stuffing (USB 2.0); 8b/10b or 128b/132b (USB 3.x).",
        "5 V VBUS: 100 mA (unconfigured) to 900 mA–5 A (BC/PD); negotiate before drawing.",
        "90 Ω diff routing, common-mode choke + ESD array, VBUS over-current protection.",
    ),
    "High-Speed/FPGA": (
        "PCB traces: centimetres to ~50 cm; backplane/cable per loss budget (dB).",
        "Point-to-point lanes; fan-out via switch/retimer/redriver.",
        "Full-duplex lane pairs (TX/RX); multi-lane bonding for throughput.",
        "Lane/endpoint enumeration per standard (e.g. PCIe BDF); no multi-drop addressing.",
        "CRC + sequence numbers + link retraining / equalization handshake.",
        "8b/10b, 64b/66b, 128b/130b scrambled NRZ or PAM-4 (per generation).",
        "Transceiver + core rails (0.8–1.2 V) plus I/O; hundreds of mW per lane at speed.",
        "100 Ω diff, length-matched, AC-coupled; reference-clock jitter < 1 ps RMS typical.",
    ),
    "Aerospace": (
        "ARINC 429: 100+ m twisted/shielded; qualified harness per airframe.",
        "ARINC 429: 1 transmitter + up to 20 receivers; redundant channels per criticality.",
        "Simplex (ARINC 429) or redundant dual-channel; higher layers add duplex.",
        "Label/SDI addressing plus system integration tables.",
        "Parity + CRC + voter/monitor logic; redundancy management detects babbling units.",
        "Bipolar RZ (ARINC 429), Manchester/differential per avionics standard.",
        "28 V aircraft power via qualified converters; hold-up and lightning margins required.",
        "Shielded/qualified wiring, lightning (DO-160) + HIRF protection, isolation barriers.",
    ),
    "Sensor-Specific": (
        "Metres (on-machine) to 100 m+ (current loop); check cable capacitance.",
        "Single sensor to multi-drop (e.g. IO-Link master with 8 ports).",
        "Half-duplex interrogation; analog 4–20 mA is simplex continuous.",
        "Sensor address, channel number, or current-level signalling.",
        "Checksum/CRC frame + out-of-range diagnostics; analog loops use live-zero (4 mA).",
        "Switched 24 V, 4–20 mA current loop, or synchronous serial per sensor bus.",
        "24 V industrial rail; M12 connector power classes; parasitic-power limits on 1-Wire.",
        "Shielded cable, surge protection, separate analog/digital returns; IP-rated connectors.",
    ),
    "Debug & Trace": (
        "Centimetres on the bench (20–30 cm ribbon typical); buffer for longer pods.",
        "Daisy-chained TAPs (JTAG) or star/multidrop (SWD); one debug probe drives the chain.",
        "Half-duplex command/response; trace streaming is target-to-host simplex.",
        "TAP/IR selection (JTAG) or AP/DP register addressing (SWD).",
        "Sticky error flags + parity on SWD data phase; retry on protocol error.",
        "TCK-gated NRZ (JTAG) or request/turnaround/acknowledge phases (SWD).",
        "Target-powered VTref — the probe follows the target I/O voltage, never drives it.",
        "Short ground return (multidrop ground on ribbon); never hot-plug powered targets.",
    ),
}

# Deep per-protocol overrides for the flagship buses engineers ask about most.
# Only the fields that differ from the category base need to be listed.
_OVERRIDES_EXTRA = {
    "uart": {
        "max_distance": "Logic-level: <1 m; RS-232 transceiver: 15 m; RS-485 transceiver: 1200 m.",
        "max_nodes": "2 (point-to-point); use RS-485/Multidrop variants for buses.",
        "duplex_mode": "Full-duplex (separate TX/RX); flow control via RTS/CTS or XON/XOFF.",
        "addressing": "No addressing — use a higher layer or 9-bit multiprocessor mode.",
        "error_detection": "Parity bit + framing/overrun flags; add CRC/XMODEM at the application layer.",
        "line_encoding": "NRZ (idle-high, start-low), LSB-first; 8N1 most common.",
        "power_profile": "MCU UART peripheral µA–mA; USB-UART bridge ~8–25 mA active.",
        "emc_isolation": "Common ground required; series 22–33 Ω + ESD diode on exposed RX/TX.",
    },
    "rs232": {
        "max_distance": "15 m @ 20 kbps per TIA-232-F; shorter at 115.2 kbps+.",
        "max_nodes": "2 (point-to-point only).",
        "duplex_mode": "Full-duplex (TXD/RXD) plus hardware handshake lines.",
        "addressing": "No addressing.",
        "error_detection": "UART parity/framing only; no link CRC defined.",
        "line_encoding": "Bipolar NRZ: mark (−V) = 1, space (+V) = 0.",
        "power_profile": "Charge-pump transceiver (MAX232 ~5–10 mA) plus cable load.",
        "emc_isolation": "Shielded cable, common ground; TVS on exposed DB-9 lines.",
    },
    "rs485": {
        "max_distance": "1200 m @ 100 kbps; 12 m @ 10 Mbps (length × speed trade-off).",
        "max_nodes": "32 unit loads; 128–256 with 1/4- or 1/8-load transceivers.",
        "duplex_mode": "Half-duplex 2-wire (typical) or full-duplex 4-wire.",
        "addressing": "No addressing — supplied by Modbus/PROFIBUS/etc. above it.",
        "error_detection": "None at the wire layer — CRC supplied by the upper protocol.",
        "line_encoding": "Differential NRZ (A−B > +200 mV = recessive/idle).",
        "power_profile": "Transceiver ~0.5 mA idle, 20–60 mA driving 120 Ω load.",
        "emc_isolation": "120 Ω both ends + 680 Ω fail-safe bias typical; shield + TVS + isolation in plants.",
    },
    "spi": {
        "max_distance": "<10 cm @ 50 MHz; <1 m @ 1 MHz; buffer for longer runs.",
        "max_nodes": "1 master; slaves = available CS lines (or daisy-chain shift registers).",
        "duplex_mode": "Full-duplex (MOSI + MISO shift simultaneously).",
        "addressing": "Per-slave chip-select; no in-band address.",
        "error_detection": "None in hardware — add CRC in the payload if needed.",
        "line_encoding": "NRZ push-pull; CPOL/CPHA (modes 0–3) define the sampling edge.",
        "power_profile": "CMOS switching power ∝ C·V²·f; gate SCLK when idle to save energy.",
        "emc_isolation": "Short star routing, 22–33 Ω series damping; keep SCLK away from analog.",
    },
    "i2c": {
        "max_distance": "<50 cm @ 400 kHz typical; bus capacitance (400 pF) is the real limit.",
        "max_nodes": "112 (7-bit) / 1008 (10-bit) minus reserved addresses; capacitance-limited in practice.",
        "duplex_mode": "Half-duplex (shared SDA); multi-master arbitration supported.",
        "addressing": "7-bit (standard) or 10-bit address + R/W bit; check for collisions.",
        "error_detection": "ACK/NACK per byte; SMBus adds packet error checking (CRC-8).",
        "line_encoding": "Open-drain NRZ with pull-ups; START/STOP are SDA-while-SCL-high conditions.",
        "power_profile": "Pull-up current VDD/Rp per line when low; budget for low-power sleep addressing.",
        "emc_isolation": "Rp sized by rise-time budget (see Science Lab); route SDA/SCL together with ground.",
    },
    "can": {
        "max_distance": "40 m @ 1 Mbps; 1000 m @ 50 kbps (propagation-delay limited).",
        "max_nodes": "~30 @ 1 Mbps (transceiver + stub limits); fewer at high speed.",
        "duplex_mode": "Half-duplex multi-master with non-destructive arbitration.",
        "addressing": "11-bit (2.0A) or 29-bit (2.0B) message ID = priority, not node address.",
        "error_detection": "15-bit CRC + ACK slot + error frames + fault confinement counters.",
        "line_encoding": "NRZ differential with bit stuffing (dominant = 0). Sample point 75–87.5%.",
        "power_profile": "Transceiver ~5–50 mA; split-termination (60 Ω + 4.7 nF) cuts EMI.",
        "emc_isolation": "Twisted pair + 120 Ω both ends; common-mode choke + ESD; isolated ISO1042 for HV.",
    },
    "lin": {
        "max_distance": "40 m total bus length per LIN 2.x.",
        "max_nodes": "1 master + up to 16 slaves.",
        "duplex_mode": "Half-duplex single-wire, master-scheduled.",
        "addressing": "6-bit frame ID + parity; master schedule table defines slots.",
        "error_detection": "Parity-protected ID + classic/enhanced checksum.",
        "line_encoding": "UART-coded NRZ (recessive = VBAT, dominant = 0).",
        "power_profile": "VBAT-powered transceiver with sleep/wake; ultra-low sleep current for parked cars.",
        "emc_isolation": "Single-wire + ground; series diode/resistor network + TVS for transients.",
    },
    "ethernet": {
        "max_distance": "100 m Cat5e/Cat6 @ 1 Gbps; fibre kilometres; automotive T1 15 m.",
        "max_nodes": "Switched — port-count limited; no bus-loading limit.",
        "duplex_mode": "Full-duplex switched (legacy half-duplex hubs obsolete).",
        "addressing": "48-bit MAC + 32/128-bit IP; autonegotiation selects speed/duplex.",
        "error_detection": "32-bit FCS CRC per frame; TCP adds end-to-end retransmission.",
        "line_encoding": "MLT-3 (100BASE-TX), PAM-5 (1000BASE-T), PAM-3 (100BASE-T1).",
        "power_profile": "PHY ~100–500 mW; PoE can deliver 15–90 W to powered devices.",
        "emc_isolation": "Magnetics + Bob Smith termination; shielded jack + ESD on exposed ports.",
    },
    "modbus_rtu": {
        "max_distance": "As RS-485 carrier: up to 1200 m @ 9600–115.2 kbps.",
        "max_nodes": "247 slave addresses (1–247); 32 unit loads per segment without repeater.",
        "duplex_mode": "Half-duplex master/slave polling; 3.5-char silent interval frames messages.",
        "addressing": "1-byte slave address + function code + register address.",
        "error_detection": "16-bit CRC (Modbus variant); silent-interval framing check.",
        "line_encoding": "UART 8E1/8N1 over differential RS-485.",
        "power_profile": "RS-485 transceiver power plus PLC scan-cycle budget.",
        "emc_isolation": "Daisy-chain shielded pair, 120 Ω ends, bias; isolate segments between buildings.",
    },
    "usb20": {
        "max_distance": "5 m (USB 2.0); use hubs/active cables beyond that.",
        "max_nodes": "127 per host controller including hubs.",
        "duplex_mode": "Half-duplex broadcast D+/D− pair, host-scheduled.",
        "addressing": "7-bit device address + 4-bit endpoint number.",
        "error_detection": "CRC-5/CRC-16 + handshake (ACK/NAK/STALL) with retries.",
        "line_encoding": "NRZI + bit stuffing; J/K/chirp states on D+/D−.",
        "power_profile": "5 V: 100 mA (unconfigured) / 500 mA (configured); suspend 2.5 mA.",
        "emc_isolation": "90 Ω diff, 1.5 kΩ speed-detect pull-up, ESD array at connector.",
    },
}


_OVERRIDES = {
    "uart": (
        "Single-ended CMOS/TTL UART; idle high and start bit low.",
        "Logic 1/idle near VCC (commonly 3.3 V or 5 V).",
        "Logic 0/start near ground (0 V).",
        "MCU I/O supply, commonly 1.8–5 V.",
        "Asynchronous; both ends agree on baud rate and frame format such as 8N1.",
        "No clock or bus termination; use a common ground and level shifter for mismatched rails.",
        ["Use a level shifter when a 3.3 V UART meets a 5 V-only peripheral."],
    ),
    "rs232": (
        "Single-ended bipolar RS-232 referenced to signal ground.",
        "Mark/logic 1 is negative, typically −5 V to −15 V.",
        "Space/logic 0 is positive, typically +5 V to +15 V.",
        "Transmitter swing is commonly ±5–12 V; receiver thresholds follow TIA/EIA-232.",
        "Asynchronous UART framing; no separate clock line.",
        "Common ground is required; use a level-shifting transceiver between MCU pins and the cable.",
        ["MAX232/MAX3232-style transceivers convert CMOS UART levels to RS-232."],
    ),
    "rs485": (
        "Balanced differential half-duplex signaling on a twisted A/B pair.",
        "Positive differential state: A is above B.",
        "Negative differential state: B is above A.",
        "Differential cable signal; common-mode voltage must remain within transceiver limits.",
        "Asynchronous; the application controls transmit/receive turnaround.",
        "Typically 120 Ω at both physical ends plus fail-safe biasing; avoid long star branches.",
        ["Keep the pair twisted and add common-mode/ESD protection for industrial environments."],
    ),
    "spi": (
        "Synchronous, push-pull, single-ended SCLK/data lines with per-slave CS.",
        "Logic 1 near the selected I/O VCC.",
        "Logic 0 near ground.",
        "Controller-specific CMOS domain, commonly 1.8 V, 3.3 V, or 5 V.",
        "Master-generated SCLK; CPOL/CPHA define sampling edges.",
        "No pull-ups normally; use series damping for long/high-speed traces.",
        ["SPI has no universal voltage table or maximum cable length; use the peripheral datasheet."],
    ),
    "i2c": (
        "Two-wire open-drain SDA/SCL bus with external pull-ups.",
        "Released line pulled high to the bus supply.",
        "Open-drain line pulled low to ground.",
        "Pull-up supply is device-specific, commonly 1.8 V, 3.3 V, or 5 V.",
        "SCL is master-generated; SDA changes while SCL low and is sampled while high.",
        "External pull-ups are required; pull-up resistance and capacitance set rise time and maximum speed.",
        ["Match pull-up voltage to every device on the bus."],
    ),
    "can": (
        "Differential dominant/recessive CAN bus on CAN_H/CAN_L.",
        "Dominant: CAN_H higher than CAN_L, typically about 3.5 V vs 1.5 V.",
        "Recessive: both lines near common mode, typically about 2.5 V each.",
        "Cable levels are transceiver-defined; MCU CAN pins are separate logic signals.",
        "Synchronous bit timing with sample point and arbitration.",
        "120 Ω at both ends is typical; use twisted pair, biasing/fail-safe behavior, and ESD protection.",
        ["The shown levels are nominal classic-CAN values; transceiver limits are authoritative."],
    ),
    "lin": (
        "Single-wire low-cost UART-framed bus with recessive high and dominant low.",
        "Recessive line near vehicle battery voltage, commonly about 12 V.",
        "Dominant line pulled low by the LIN node.",
        "Thresholds are referenced to vehicle supply and defined by the LIN standard.",
        "UART-like character timing; master schedules header and response fields.",
        "Use transceiver pull-up/diode network, ground, and protected wiring.",
        ["Never connect a LIN cable directly to MCU pins."],
    ),
    "ethernet": (
        "Copper Ethernet uses differential pairs and PHY-specific line coding; fiber uses optical signaling.",
        "Not a persistent logic rail; PHY decodes line symbols.",
        "Not a persistent logic rail; PHY decodes line symbols.",
        "Copper PHY levels and optical power are variant-specific; use the selected standard.",
        "10/100/1000BASE-T PHYs recover clock from the stream.",
        "100 Ω differential termination/control is typical for copper; optical uses link budget/connector rules.",
        ["Use an Ethernet MAC/PHY or integrated controller, not raw MCU GPIOs."],
    ),
    "i2s": (
        "Synchronous CMOS serial audio with bit clock, word select, and data.",
        "Logic 1 near the audio I/O supply, commonly 1.8 V or 3.3 V.",
        "Logic 0 near ground.",
        "Codec/controller CMOS rail, commonly 1.8 V or 3.3 V.",
        "Master-generated BCLK with WS/LRCLK framing; sample edge is codec-specific.",
        "Short traces, optional series damping, and power decoupling.",
        ["I2S framing is standardized more than its voltage; check the codec thresholds."],
    ),
    "lvds": (
        "Small-swing differential signaling on balanced pairs.",
        "Positive differential state, typically about +350 mV.",
        "Negative differential state, typically about −350 mV.",
        "Small-swing differential signal with a receiver-defined common-mode range.",
        "Receiver recovers clock or uses forwarded clock per the application.",
        "100 Ω differential termination and controlled impedance are common.",
        ["LVDS is a physical method; framing and connector pinout are separate."],
    ),
    "pcie": (
        "High-speed differential SERDES lanes with encoded symbols and clock recovery.",
        "Not a persistent logic rail; receiver decodes differential symbols.",
        "Not a persistent logic rail; receiver decodes differential symbols.",
        "Lane swing/common-mode are generation/transceiver-specific; use PCI-SIG guidance.",
        "Embedded/forwarded clock and equalization; encoding supports clocking and DC balance.",
        "Controlled impedance, reference planes, AC coupling, loss management, and preset/termination.",
        ["Lane length, loss, jitter, and crosstalk determine margin."],
    ),
    "arinc429": (
        "Unidirectional bipolar differential avionics bus.",
        "Positive differential state, typically about +6.5 to +8 V.",
        "Negative differential state, typically about −6.5 to −8 V.",
        "Bipolar differential levels; exact thresholds and common mode are standard-defined.",
        "Self-clocked data at 12.5 or 100 kbit/s in common implementations.",
        "Qualified characteristic impedance, termination, coax/twisted-pair wiring, and protection.",
        ["ARINC 429 uses bipolar pulse widths; polarity carries the logic state."],
    ),
}


# Typical interface/PHY silicon for each protocol — what an engineer actually
# puts between the MCU and the wire. Only well-established parts are listed;
# protocols absent from this map simply have no canonical transceiver.
_TRANSCEIVERS = {
    "uart": ("USB-UART bridges: CP2102N, CH340, FT232R", "Level shifters: TXB0104, 74LVC1T45"),
    "rs232": ("RS-232 line drivers/receivers: MAX232, MAX3232, SP3232", "Charge-pump caps needed on 5 V MAX232"),
    "rs485": ("RS-485 transceivers: MAX485, MAX3485, SP3485, SN65HVD3082E", "Isolated: ADM2483, MAX1480B"),
    "spi": (
        "No line transceiver — direct CMOS; level shifters TXB0108, 74LVC245",
        "Typical targets: W25Q64 flash, nRF24L01+ radio",
    ),
    "i2c": ("Bus buffer/level shifter: PCA9306, TCA9517, P82B715", "Mux/switch: TCA9548A (8 channels)"),
    "can": ("CAN transceivers: SN65HVD230 (3.3 V), TJA1050 (5 V), MCP2551", "Isolated: ISO1042, MAX14889E"),
    "lin": ("LIN transceivers: TJA1021, MCP2003A", "Single-wire with internal pull-up/diode network"),
    "ethernet": ("10/100 PHYs: LAN8720A, DP83848, KSZ8081", "All-in-one MAC+PHY: W5500, ENC28J60 (SPI)"),
    "usb11": ("Host/device controllers: MAX3421E, SL811HST", "ESD arrays: USBLC6-2SC6"),
    "usb20": ("USB 2.0 PHY/bridge: FT232R, CP2102N, CH340", "ESD arrays: USBLC6-2SC6"),
    "usb3x": (
        "USB 3.x needs a redriver/retimer (e.g. TUSB1046)",
        "Cable/connector ESD and signal-integrity parts dominate",
    ),
    "usbc": ("CC/PD controllers: FUSB302, STUSB4500", "Flip/attach detection via 5.1 kΩ CC pull-downs"),
    "i2s": ("Audio codecs/DACs: PCM5102A, ES8388, UJA1169", "No line transceiver — codec drives BCLK/WS/data"),
    "lvds": ("LVDS driver/receiver pairs: DS90LV047A / DS90LV048A", "100 Ω termination at the receiver"),
    "pcie": (
        "Requires redriver/retimer silicon plus AC coupling caps",
        "Root complex/endpoint PHYs are part of the chipset SoC",
    ),
    "arinc429": ("ARINC 429 line drivers: DDC DEI1016 family", "Avionics-qualified bipolar transmitter/receiver"),
    "flexray": ("FlexRay transceivers: TJA1080, TJA1085", "Dual-channel variants exist for redundant buses"),
    "modbus_rtu": (
        "Runs on RS-485: MAX485, SP3485 (plus 120 Ω termination)",
        "Also runs on RS-232/optical physical layers",
    ),
    "1wire": ("I²C-to-1-Wire bridge: DS2482", "Strong pull-up needed during parasite-powered programming"),
}


def apply_technical_profiles(protocols):
    """Attach one complete technical object to every protocol record."""
    for protocol in protocols:
        category = protocol["category"]
        if category in _CATEGORY:
            base = dict(zip(OLD_FIELDS, _CATEGORY[category]))
            extra = _CATEGORY_EXTRA.get(category)
            if extra:
                base.update(dict(zip(NEW_FIELDS, extra)))
            else:
                for field in NEW_FIELDS:
                    base.setdefault(field, _PHYSICAL[field])
        elif category in {"Wireless", "Cellular"}:
            base = deepcopy(_RF)
        elif category in {"Networking", "Security"}:
            base = deepcopy(_CARRIER)
        else:
            base = deepcopy(_PHYSICAL)
        # On-Board and other physical categories fall through to _PHYSICAL
        # above; give them their tailored deep parameters.
        if category in _CATEGORY_EXTRA and category not in _CATEGORY:
            base.update(dict(zip(NEW_FIELDS, _CATEGORY_EXTRA[category])))
        if protocol["id"] in _OVERRIDES:
            values = _OVERRIDES[protocol["id"]]
            base.update(
                signaling=values[0],
                logic_high=values[1],
                logic_low=values[2],
                voltage_reference=values[3],
                clocking=values[4],
                termination_and_biasing=values[5],
                design_notes=list(values[6]),
            )
        if protocol["id"] in _OVERRIDES_EXTRA:
            base.update(_OVERRIDES_EXTRA[protocol["id"]])
        protocol["technical"] = {field: base.get(field, "Not specified") for field in FIELDS}
        # Interface silicon: real part numbers, or an empty list when the
        # protocol is software/RF and has no canonical line transceiver.
        protocol["technical"]["transceivers"] = list(_TRANSCEIVERS.get(protocol["id"], ()))
    return protocols
