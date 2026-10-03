# -*- coding: utf-8 -*-
"""Symptom -> likely cause -> fix for the flagship buses.

Ordered by how often each failure actually bites: wiring first, then
configuration, then protocol. Every entry is one bench-tested check.
"""

TROUBLE = {
    "uart": [
        {
            "symptom": "Garbage characters on the terminal",
            "cause": "Baud-rate mismatch (or 5 V into a 3.3 V RX)",
            "fix": "Match 8N1 + baud on both ends; verify error <2% in the Science Lab UART tab; level-shift mismatched rails.",
        },
        {
            "symptom": "Nothing received at all",
            "cause": "TX-TX / RX-RX wiring, or missing common ground",
            "fix": "Cross TX->RX, RX->TX, and join grounds. Loop back TX to RX on one board to prove the port works.",
        },
        {
            "symptom": "Works at 9600, fails at 115200",
            "cause": "Clock-divisor rounding error grows with baud",
            "fix": "Recompute the divisor for your exact crystal in the UART calculator; switch to a crystal that divides cleanly.",
        },
    ],
    "i2c": [
        {
            "symptom": "No ACK from any address (scanner finds nothing)",
            "cause": "Missing pull-ups, or wrong bus voltage",
            "fix": "Fit one pull-up pair per segment sized by the Science Lab pull-up designer; confirm every device tolerates the rail.",
        },
        {
            "symptom": "Works with one sensor, fails with two",
            "cause": "Address collision, or doubled pull-ups in parallel",
            "fix": "Scan each module alone; remove extra on-module pull-ups so only one pair remains; check solder-jumper address options.",
        },
        {
            "symptom": "Random NACKs at 400 kHz, fine at 100 kHz",
            "cause": "Bus capacitance too high — rise time violates the 300 ns limit",
            "fix": "Shorten wiring, lower Rp toward Rp_min, or drop to Standard-mode until the designer tab shows margin.",
        },
    ],
    "spi": [
        {
            "symptom": "Reads back 0xFF / 0x00 always",
            "cause": "Wrong CPOL/CPHA mode, or MISO not tri-stating",
            "fix": "Confirm mode 0-3 in the peripheral datasheet; check CS actually goes low; verify MISO with a scope during SCLK.",
        },
        {
            "symptom": "Data shifted by one bit",
            "cause": "Sampling on the wrong clock edge",
            "fix": "Flip CPHA (mode 0<->1, 2<->3); compare against the Encyclopedia SPI waveform sampling markers.",
        },
        {
            "symptom": "Fails above ~20 MHz only",
            "cause": "Ringing / crosstalk on long SCLK runs",
            "fix": "Shorten to <10 cm, add 22-33 ohm series damping at the source, keep SCLK over a solid ground return.",
        },
    ],
    "can": [
        {
            "symptom": "Bus off / error-passive immediately",
            "cause": "Bit-rate or sample-point mismatch, or a single node at the wrong rate",
            "fix": "Verify every node in the bit-timing calculator (integer prescaler, 75-87.5% sample point); isolate nodes one by one.",
        },
        {
            "symptom": "Works on the bench, fails in the vehicle",
            "cause": "Missing termination, stubs, or transients",
            "fix": "120 ohm at BOTH physical ends only; stubs under 0.3 m at 1 Mbps; add common-mode choke + TVS; split termination for EMI.",
        },
        {
            "symptom": "High-priority messages delayed under load",
            "cause": "Bus load past ~50-70% — queueing, not a bug",
            "fix": "Measure with the CAN Bus Load tab; cut DLC, lower cycle rates, or move to CAN FD.",
        },
    ],
    "rs485": [
        {
            "symptom": "First byte of every reply corrupted",
            "cause": "TX-enable turnaround too slow — driver still enabling",
            "fix": "Assert DE before the start bit with margin; add the 3.5-char silent interval Modbus requires.",
        },
        {
            "symptom": "Random framing errors, worse with motor running",
            "cause": "No termination/bias, star wiring, or missing shield ground",
            "fix": "Daisy-chain only, 120 ohm both ends, bias for 200 mV+ idle (bias calculator tab), shield grounded at ONE end.",
        },
        {
            "symptom": "Some nodes deaf, others fine",
            "cause": "A/B swapped on those nodes, or >32 unit loads",
            "fix": "Check polarity end-to-end; count unit loads and add a repeater past 32 (or use 1/8-load transceivers).",
        },
    ],
    "modbus_rtu": [
        {
            "symptom": "Timeout on every poll",
            "cause": "Slave ID, parity, or baud mismatch — or reply gap too short",
            "fix": "Match 8E1 vs 8N1 exactly (mismatch looks like CRC errors); enforce 3.5-char silence; confirm the slave ID.",
        },
        {
            "symptom": "CRC errors that come and go",
            "cause": "RS-485 wiring marginal (see rs485 entries above)",
            "fix": "Fix the wire layer first — Modbus has no retransmission to hide behind.",
        },
        {
            "symptom": "Poll cycle too slow for 30 slaves",
            "cause": "3.5-char silence per transaction is the latency floor",
            "fix": "Raise baud, shorten payloads, poll slow registers less often, or segment with a second master.",
        },
    ],
    "ethernet": [
        {
            "symptom": "Link up, no traffic (or 10 Mbps fallback)",
            "cause": "Bad pair (split pair), autonegotiation conflict, or forced duplex mismatch",
            "fix": "Re-terminate T568B both ends and test pairs; leave autonegotiation ON; check switch port errors.",
        },
        {
            "symptom": "Cyclic control jitter on a shared LAN",
            "cause": "Bulk traffic queueing in a dumb switch",
            "fix": "VLAN + priority, a TSN/real-time capable switch, or a physically separate control network.",
        },
        {
            "symptom": "Works on the bench, dies across buildings",
            "cause": "Ground-potential difference / surge on copper between buildings",
            "fix": "Fibre between buildings, or isolated PoE/magnetics with proper surge protection.",
        },
    ],
    "usb20": [
        {
            "symptom": "Device enumerates then disconnects under load",
            "cause": "Drawing 500 mA before configuration, or thin cable droop",
            "fix": "Stay under 100 mA until configured; use a short, thick cable; add bulk capacitance at the device.",
        },
        {
            "symptom": "High-speed device falls back to full-speed",
            "cause": "Chirp fails on bad cable/connector/ESD layout",
            "fix": "90-ohm diff routing, no stubs, USBLC6-class ESD array AT the connector, quality cable under 5 m.",
        },
    ],
    "lin": [
        {
            "symptom": "Slave never answers the header",
            "cause": "Wrong baud (LIN needs ~1-2% clock), or slave in sleep",
            "fix": "Send the wake-up break first; verify master schedule timing; check the 1k/30k pull-up split (exactly one master resistor).",
        },
        {
            "symptom": "Intermittent checksum errors",
            "cause": "Classic vs enhanced checksum mismatch",
            "fix": "Match checksum version on every node; re-verify after any LIN description file change.",
        },
    ],
    "wifi": [
        {
            "symptom": "Throughput far below the link rate",
            "cause": "Congestion, weak RSSI forcing low MCS, or 2.4 GHz overlap",
            "fix": "Check RSSI vs sensitivity margin (link-budget tab); move to 5/6 GHz; widen to 40/80 MHz only if the spectrum is clean.",
        },
        {
            "symptom": "IoT device won't join",
            "cause": "WPA3-only AP, PMF requirement, or 5 GHz steering",
            "fix": "Offer WPA2 transitional mode; keep a 2.4 GHz SSID for legacy sensors; check DHCP pool exhaustion.",
        },
    ],
}


def get_troubleshooting(pid):
    """Return the troubleshooting list for a protocol id, or []."""
    return TROUBLE.get(pid, [])


def has_troubleshooting(pid):
    """Whether troubleshooting entries exist for this protocol id."""
    return pid in TROUBLE
