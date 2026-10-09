# -*- coding: utf-8 -*-
"""Structured electrical characteristics: volts, ohms, and nanoseconds.

`technical` holds prose; this holds *numbers*. Every physical protocol can
answer, without the reader guessing:

  * How big is the signal?  VOH/VOL single-ended, Vdiff for differential
  * What is the common-mode voltage? (why USB idles at 3.0 V, not 0 V)
  * How fast are the edges?  rise/fall time sets the maximum usable rate
  * What does one bit cost in time?  bit period at a stated bit rate
  * What is the Z0?  termination value, so the right resistor can be chosen
  * Which conductors form a differential pair, and in which direction?

Differential pairs are declared explicitly so the UI can draw TX+/TX- and
RX+/RX- as separate traces instead of a vague "A/B".

Levels for a differential pair (used by the waveform builder):
    TX+ = VCM + Vdiff/2      TX- = VCM - Vdiff/2
which is why a 200 mV USB differential rides on a 3.0 V common mode.
"""


def _spec(signaling, coding, pairs=(), vcm=None, vdiff_high=None, vdiff_low=None,
          voh=None, vol=None, impedance=None, rise_ns=None, bit_ns=None,
          prop_ns_per_m=None, termination="", jitter_ps=None, notes="",
          logic_1_is_vdiff_high=True):
    """Build one electrical spec record.

    signaling: "differential" | "single_ended" | "open_drain" | "bipolar" |
              "rf" | "passive"
    coding:    a key from utils.signal_engine.LINE_CODINGS, or "" if N/A
    pairs:     (positive, negative, role) triples; role is "transmit",
               "receive" or "bidirectional"
    """
    spec = {
        "signaling": signaling,
        "coding": coding,
        "pairs": [{"a": a, "b": b, "role": role} for a, b, role in pairs],
        "vcm_volts": vcm,
        "vdiff_high_volts": vdiff_high,
        "vdiff_low_volts": vdiff_low,
        "voh_volts": voh,
        "vol_volts": vol,
        "impedance_ohm": impedance,
        "rise_time_ns": rise_ns,
        "bit_period_ns": bit_ns,
        "prop_delay_ns_per_m": prop_ns_per_m,
        "termination": termination,
        "jitter_ps": jitter_ps,
        "notes": notes,
    }
    if not logic_1_is_vdiff_high:
        spec["logic_1_is_vdiff_high"] = False
    return spec


ELECTRICAL = {
    # ------------------------------------------------ USB / Type-C ---------
    "usb20": _spec(
        "differential", "nrz", pairs=[("D+", "D-", "bidirectional")],
        vcm=3.0, vdiff_high=0.2, vdiff_low=-0.2, impedance=90, rise_ns=20.0,
        bit_ns=83.3, prop_ns_per_m=5.0, jitter_ps=100,
        termination="90 Ohm differential on the host; 1.5 kOhm pull-up on D+ selects speed",
        notes="Full-Speed is 12 Mbit/s (83.3 ns/bit); High-Speed is 480 Mbit/s "
              "(2.083 ns/bit) with a 4 ns rise time. The 3.0 V common mode means "
              "the idle state is NOT 0 V - a scope shows D+ and D- both near 3 V.",
    ),
    "usb3x": _spec(
        "differential", "4b5b_nrzi",
        pairs=[("TxP", "TxN", "transmit"), ("RxP", "RxN", "receive")],
        vcm=2.0, vdiff_high=0.2, vdiff_low=-0.2, impedance=90, rise_ns=2.2,
        bit_ns=0.25, prop_ns_per_m=5.0, jitter_ps=50,
        termination="90 Ohm differential; AC coupling with 100 nF-1 uF on the lane",
        notes="5 Gbit/s per lane (200 mUI = 0.25 ns/bit). 64b/66b coding keeps "
              "the run-length low so the 7.5 GHz DDR receiver can recover clock.",
    ),
    "usb4": _spec(
        "differential", "4b5b_nrzi",
        pairs=[("TxP", "TxN", "transmit"), ("RxP", "RxN", "receive")],
        vcm=2.0, vdiff_high=0.25, vdiff_low=-0.25, impedance=90, rise_ns=1.5,
        bit_ns=0.1, prop_ns_per_m=4.5, jitter_ps=30,
        termination="90 Ohm differential per lane; lane rates up to 20 Gbit/s",
        notes="Up to 20 Gbit/s per lane (40 Gbit/s bidirectionally) using PAM4 "
              "at 40-80 GBd, which is why the swing shrinks to keep EMI down.",
    ),
    # ------------------------------------------------------ Networking ------
    "ethernet": _spec(
        "differential", "manchester",
        pairs=[("TX+", "TX-", "transmit"), ("RX+", "RX-", "receive")],
        vcm=0.0, vdiff_high=1.0, vdiff_low=-1.0, impedance=100, rise_ns=10.0,
        bit_ns=20.0, prop_ns_per_m=5.0, jitter_ps=10,
        termination="100 Ohm (95 Ohm nominal) at both ends via a MagJack",
        notes="10BASE-T at 10 Mbit/s is 100 ns/bit; 1000BASE-T is 1 ns/bit with "
              "4D-PAM5 instead of Manchester. Manchester guarantees a transition "
              "every bit, which is why 10BASE-T needs no separate clock lane.",
    ),
    # ------------------------------------------------------- Automotive -----
    "can": _spec(
        "differential", "nrz", pairs=[("CAN_H", "CAN_L", "bidirectional")],
        vcm=2.5, vdiff_high=2.0, vdiff_low=0.0, impedance=120, rise_ns=60.0,
        bit_ns=2000.0, prop_ns_per_m=5.0, jitter_ps=250,
        logic_1_is_vdiff_high=False,
        termination="120 Ohm at both ends (two 60 Ohm); split termination for stubs",
        notes="Classic CAN recessive = both lines near 2.5 V (VDiff about 0 V); "
              "dominant pulls CAN_H to about 3.5 V and CAN_L to about 1.5 V "
              "(VDiff about +2 V). Dominant is logical 0; recessive is logical 1. "
              "The configured 2 us bit period is a 500 kbit/s example; 1 Mbit/s "
              "uses a 1 us bit. These are nominal classic-CAN levels, not guaranteed "
              "limits; use the transceiver specifications. Typical high-speed "
              "termination is 120 Ohm at each physical end.",
    ),
    "lin": _spec(
        "single_ended", "nrz", vcm=0.0, voh=12.0, vol=0.0, impedance=1000,
        rise_ns=10000.0, bit_ns=500.0, prop_ns_per_m=10.0,
        termination="1 kOhm pull-up to VBAT; diode clamp to the transceiver",
        notes="Single wire on VBAT (6-18 V). Break is a dominant bit and there is "
              "no separate clock: the master's sync field is 0x55 so slaves re-time.",
    ),
    "flexray": _spec(
        "differential", "nrz", pairs=[("BP", "BN", "bidirectional")],
        vcm=2.5, vdiff_high=1.0, vdiff_low=-1.0, impedance=120, rise_ns=30.0,
        bit_ns=200.0, prop_ns_per_m=5.0, jitter_ps=100,
        termination="120 Ohm at both ends",
        notes="5 Mbit/s = 200 ns/bit. BP/BN sit at 3.5/1.5 V for one state and "
              "2.5/2.5 V (zero differential) for the other.",
    ),
    # ----------------------------------------------- Industrial / balanced --
    "rs485": _spec(
        "differential", "nrz", pairs=[("A", "B", "bidirectional")],
        vcm=0.0, vdiff_high=2.0, vdiff_low=-2.0, impedance=120, rise_ns=100.0,
        bit_ns=100.0, prop_ns_per_m=10.0, jitter_ps=100,
        termination="120 Ohm at each end; failsafe bias 450-650 Ohm to the rails",
        notes="Up to 10 Mbit/s at 12 m, 100 kbit/s at 1200 m. The standard "
              "specifies a +/-2 V receiver threshold, so a 200 mV RS-422 signal "
              "would NOT be read reliably here.",
    ),
    "rs422": _spec(
        "differential", "nrz",
        pairs=[("TX+", "TX-", "transmit"), ("RX+", "RX-", "receive")],
        vcm=0.0, vdiff_high=2.0, vdiff_low=-2.0, impedance=100, rise_ns=100.0,
        bit_ns=100.0, prop_ns_per_m=10.0, jitter_ps=100,
        termination="100-120 Ohm; receiver often failsafe-biases to >=200 mV",
        notes="+/-200 mV guaranteed threshold. Full duplex: separate transmit and "
              "receive pairs mean there is no turnaround delay.",
    ),
    "rs232": _spec(
        "single_ended", "nrz", vcm=0.0, voh=5.0, vol=-5.0, impedance=100,
        rise_ns=250.0, bit_ns=41600.0, prop_ns_per_m=10.0,
        termination="Capacitive load only; no termination resistor",
        notes="Single-ended bipolar +/-5 V to +/-15 V at 2400 baud (41.6 us/bit). "
              "The more negative voltage marks a 1, so the logic is inverted.",
    ),
    # ----------------------------------------------------- On-board buses ---
    "i2c": _spec(
        "open_drain", "nrz", vcm=3.3, voh=3.3, vol=0.4, impedance=1000,
        rise_ns=300.0, bit_ns=4700.0, prop_ns_per_m=10.0,
        termination="No terminator; 2.2-10 kOhm pull-ups to VCC on SDA and SCL",
        notes="Open-drain: the master only ever pulls LOW, so a slave can hold "
              "SDA low to stretch the clock. 100 kbit/s = 10 us/bit; the 1.5 us "
              "rise time limits how much bus capacitance can be tolerated.",
    ),
    "spi": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=50,
        rise_ns=20.0, bit_ns=37.0, prop_ns_per_m=10.0, jitter_ps=100,
        termination="Series 22-33 Ohm at the driver if traces are long",
        notes="Single-ended CMOS. 27 MHz gives 37 ns/bit (MSB first, CPOL/CPHA "
              "variants). No clock stretching and no acknowledge - only CS tells "
              "the slave it is selected.",
    ),
    "i2s": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=50,
        rise_ns=20.0, bit_ns=41.7, prop_ns_per_m=10.0,
        termination="Series damping resistor if the FPC is long",
        notes="Left-aligned data MSB first with 1 BCLK delay after WS changes. "
              "48 kHz 16-bit stereo = 3.072 Mbit/s = 326 ns per stereo frame.",
    ),
    # ------------------------------------------------- High-speed / FPGA ----
    "lvds": _spec(
        "differential", "nrz",
        pairs=[("Tx+", "Tx-", "transmit"), ("Rx+", "Rx-", "receive")],
        vcm=2.5, vdiff_high=0.35, vdiff_low=-0.35, impedance=100, rise_ns=0.2,
        bit_ns=8.3, prop_ns_per_m=5.0, jitter_ps=15,
        termination="100 Ohm across the pair (100 Ohm differential)",
        notes="Only a 350 mV swing, which is the whole point: low swing means low "
              "EMI. 400 mV at 100 MHz is 120 Mbit/s, so 8.3 ns/bit with 0.2 ns "
              "edges - roughly 50x faster than the bit rate would suggest.",
    ),
    "pcie": _spec(
        "differential", "4b5b_nrzi",
        pairs=[("TxP", "TxN", "transmit"), ("RxP", "RxN", "receive")],
        vcm=3.0, vdiff_high=0.85, vdiff_low=-0.85, impedance=100, rise_ns=0.5,
        bit_ns=0.5, prop_ns_per_m=4.5, jitter_ps=15,
        termination="On-die 100 Ohm termination; AC-coupled lanes",
        notes="Gen3 8 GT/s = 0.5 ns/bit (2 GT/s per lane, 128b/130b encoded). "
              "Gen4 doubles it with PAM4 at 16 GT/s. RX is clocked 2-3 UI later "
              "than TX - that skew is the whole design constraint.",
    ),
    "serdes": _spec(
        "differential", "nrz",
        pairs=[("TxP", "TxN", "transmit"), ("RxP", "RxN", "receive")],
        vcm=2.5, vdiff_high=0.4, vdiff_low=-0.4, impedance=100, rise_ns=0.3,
        bit_ns=1.0, prop_ns_per_m=4.5, jitter_ps=20,
        termination="100 Ohm differential, usually on-die",
        notes="1 Gbit/s = 1 ns/bit. Transmitter and receiver are separate "
              "differential pairs, so full duplex needs 4 wires plus a clock "
              "(forward clock or CDR recovery).",
    ),
    "jesd204": _spec(
        "differential", "nrz", pairs=[("LANE+", "LANE-", "bidirectional")],
        vcm=1.2, vdiff_high=0.4, vdiff_low=-0.4, impedance=100, rise_ns=0.2,
        bit_ns=0.8, prop_ns_per_m=4.5, jitter_ps=10,
        termination="100 Ohm differential; AC coupling caps on the link",
        notes="Class A: 12.5 Gbit/s over 1.5 ns UI (8b/10b) or 6.25 Gbit/s per "
              "lane at 32b/10b with an 80 % jitter budget.",
    ),
    "rapidio": _spec(
        "differential", "nrz",
        pairs=[("TxP", "TxN", "transmit"), ("RxP", "RxN", "receive")],
        vcm=2.5, vdiff_high=0.4, vdiff_low=-0.4, impedance=100, rise_ns=0.2,
        bit_ns=0.5, prop_ns_per_m=4.5, jitter_ps=15,
        termination="100 Ohm differential; parallel or serial RapidIO",
        notes="RapidIO 3.0 at 25 Gbit/s uses 80+ lanes of 250 MBd; each symbol "
              "lane is a separate differential pair.",
    ),
    # ------------------------------------------------------- Aerospace ------
    "arinc429": _spec(
        "bipolar", "bipolar_rz", pairs=[("A", "B", "bidirectional")],
        vcm=0.0, vdiff_high=10.0, vdiff_low=-10.0, impedance=78, rise_ns=160.0,
        bit_ns=10000.0, prop_ns_per_m=8.0, jitter_ps=50,
        termination="78-100 Ohm across A and B",
        notes="+/-10 V differential, 100 kbit/s (10 us/bit), pulse width "
              "0.2-2.0 us. A 1 is a +10 V pulse lasting 75 % of the bit time, a 0 "
              "is -10 V lasting 25 %, then the line returns to 0 - a single wire "
              "carries data AND clock, so ARINC 429 needs no clock line.",
    ),
    "arinc664": _spec(
        "differential", "nrz",
        pairs=[("TX+", "TX-", "transmit"), ("RX+", "RX-", "receive")],
        vcm=0.0, vdiff_high=0.5, vdiff_low=-0.5, impedance=100, rise_ns=2.0,
        bit_ns=10.0, prop_ns_per_m=6.0, jitter_ps=50,
        termination="100 Ohm differential; fibre optic on long segments",
        notes="AFDX, 100 Mbit/s per Virtual Link (10 us/bit). The reduced swing "
              "of +/-0.5 V keeps emissions below the avionics AXT limits.",
    ),
    "mil1553": _spec(
        "bipolar", "bipolar_rz", pairs=[("A", "B", "bidirectional")],
        vcm=0.0, vdiff_high=6.0, vdiff_low=-6.0, impedance=78, rise_ns=200.0,
        bit_ns=20000.0, prop_ns_per_m=8.0,
        termination="78 Ohm across the bus",
        notes="1 Mbit/s, 20 us/bit. Bipolar triple pulse in Manchester II; "
              "16-bit words with an optional command discrete.",
    ),
    "spacewire": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=100,
        rise_ns=20.0, bit_ns=20.0, prop_ns_per_m=10.0,
        termination="Series termination; typically short cable runs",
        notes="LVDS variant used on spacecraft: up to 400 Mbit/s, full duplex "
              "with an out-of-band handshake pin (HSK).",
    ),
    # ------------------------------------------------------ Video/display ---
    "hdmi": _spec(
        "differential", "nrz",
        pairs=[("TMDS0+", "TMDS0-", "transmit"), ("TMDS1+", "TMDS1-", "transmit"),
               ("TMDS2+", "TMDS2-", "transmit")],
        vcm=2.5, vdiff_high=0.4, vdiff_low=-0.4, impedance=100, rise_ns=0.5,
        bit_ns=0.5, prop_ns_per_m=5.0, jitter_ps=15,
        termination="100 Ohm differential; the TMDS clock lane is separate",
        notes="TMDS-125: 250 MBd on 3 data lanes plus 1 clock lane. The clock is "
              "forwarded on a dedicated lane rather than recovered from data.",
    ),
    "dp": _spec(
        "differential", "nrz",
        pairs=[("Main0+", "Main0-", "transmit"), ("Main1+", "Main1-", "transmit"),
               ("Main2+", "Main2-", "transmit"), ("Main3+", "Main3-", "transmit")],
        vcm=2.5, vdiff_high=0.4, vdiff_low=-0.4, impedance=100, rise_ns=0.3,
        bit_ns=0.25, prop_ns_per_m=5.0, jitter_ps=15,
        termination="100 Ohm differential per lane; AC coupling on Main",
        notes="HBR3: 4 lanes x 8.1 Gbit/s = 32.4 Gbit/s (0.125 ns/bit). The AUX "
              "channel is a separate low-speed differential pair.",
    ),
    "mipi_dsi": _spec(
        "differential", "nrz", pairs=[("CLK+", "CLK-", "transmit")],
        vcm=1.2, vdiff_high=0.2, vdiff_low=-0.2, impedance=100, rise_ns=0.2,
        bit_ns=1.0, prop_ns_per_m=5.0, jitter_ps=20,
        termination="100 Ohm on the clock lane; data lanes are unterminated",
        notes="The clock lane carries the forwarded clock (up to 1.5 Gbit/s); data "
              "lanes are DDR, so each data lane moves 2 bits per clock edge.",
    ),
    "mipi_csi": _spec(
        "differential", "nrz", pairs=[("CLK+", "CLK-", "transmit")],
        vcm=1.2, vdiff_high=0.2, vdiff_low=-0.2, impedance=100, rise_ns=0.2,
        bit_ns=1.0, prop_ns_per_m=5.0, jitter_ps=20,
        termination="100 Ohm on the clock lane only",
        notes="Camera link, 2.5 Gbit/s per lane; D-PHY uses C-PHY for about 2.5x.",
    ),
    # -------------------------------------------- Automotive single-wire ---
    "uart": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=100,
        rise_ns=100.0, bit_ns=10000.0, prop_ns_per_m=10.0, jitter_ps=1000,
        termination="Series 33-100 Ohm with the logic ground; no terminator",
        notes="A bare UART is logic levels, not a standard: idle HIGH, start bit "
              "LOW, data LSB-first, then optional parity and stop bit(s). 9600 "
              "baud = 104 us/bit, but 10 bits per byte means 960 bytes/s. It has "
              "no clock line, which is why both ends must agree on the baud rate "
              "and why a wrong baud rate gives framing errors rather than garbage.",
    ),
    "most": _spec(
        "single_ended", "nrz", vcm=0.0, voh=12.0, vol=0.0, impedance=100,
        rise_ns=3000.0, bit_ns=250.0, prop_ns_per_m=10.0,
        termination="Series 100 Ohm at the master; MCLR controls low-power mode",
        notes="Single data line at up to 50 Mbit/s (20 ns/bit), plus MCLR for "
              "wake-up. Blocks are 32 data + 4 control bits in 5 bit periods.",
    ),
    "sent": _spec(
        "single_ended", "nrz", vcm=0.0, voh=12.0, vol=0.0, impedance=10000,
        rise_ns=20000.0, bit_ns=500.0, prop_ns_per_m=10.0,
        termination="10 kOhm pull-up to VBAT",
        notes="Sentronic single-wire: the pulse *width* encodes 2 or 4 bits, so "
              "it sends about 100 kbit/s on one wire with no return path.",
    ),
    "psi5": _spec(
        "single_ended", "nrz", vcm=0.0, voh=12.0, vol=0.0, impedance=100,
        rise_ns=1000.0, bit_ns=250.0, prop_ns_per_m=10.0,
        termination="Series resistor in the sensor return path",
        notes="Sensor-to-ECU serial link; pulse-width-modulated nibbles in a sync "
              "frame at up to 500 kbit/s.",
    ),
    "kline": _spec(
        "single_ended", "nrz", vcm=0.0, voh=12.0, vol=0.0, impedance=1000,
        rise_ns=20000.0, bit_ns=20000.0, prop_ns_per_m=10.0,
        termination="1 kOhm pull-up to B+ through a resistor; 4.7 kOhm in circuit",
        notes="ISO 9141 single wire at 10.4 kbit/s (96 us/bit) - used for OBD-II "
              "diagnosis. Dominant is a low pulse, so the logic is inverted.",
    ),
    # --------------------------------------------------------- On-board -----
    "jtag": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=50,
        rise_ns=5.0, bit_ns=50.0, prop_ns_per_m=10.0,
        termination="Series 33 Ohm on TCK/TDI if the chain is long",
        notes="TCK/TMS/TDI are driven by the host, TDO by the target - TDO is the "
              "only bidirectional pin, and it is tri-stated when not selected.",
    ),
    "swd": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=50,
        rise_ns=5.0, bit_ns=26.0, prop_ns_per_m=10.0,
        termination="Series 33 Ohm on SWDIO",
        notes="2-wire debug. 3V3 is an *input* to the probe: it lets the host "
              "detect target voltage and avoid back-powering a dead chip.",
    ),
    "sdio": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=50,
        rise_ns=10.0, bit_ns=20.0, prop_ns_per_m=10.0,
        termination="Pull-ups of 10-50 kOhm on CMD and DAT lines",
        notes="Up to 50 MHz = 20 ns/bit. CMD/DAT are push-pull at HS but "
              "open-drain at low speed, so pull-ups are always fitted.",
    ),
    "emmc": _spec(
        "single_ended", "nrz", vcm=1.8, voh=1.8, vol=0.0, impedance=50,
        rise_ns=5.0, bit_ns=4.0, prop_ns_per_m=5.0,
        termination="Series 33 Ohm and per-line 33 Ohm pull-ups on DAT",
        notes="HS400 at 200 MHz with DDR: 2 bits per 5 ns clock = 4 ns/bit. "
              "1.8 V signalling on DAT, 3.3 V on CMD in some devices.",
    ),
    "mdio": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=50,
        rise_ns=10.0, bit_ns=100000.0, prop_ns_per_m=10.0,
        termination="1.5 kOhm pull-ups on MDC and MDIO (Clause 22)",
        notes="Management interface for PHYs at up to 2.5 MHz (400 ns/bit); MDIO "
              "is open-drain and tri-stated between transactions.",
    ),
    "firewire": _spec(
        "differential", "4b5b_nrzi", pairs=[("TPA", "TPB", "bidirectional")],
        vcm=1.3, vdiff_high=0.265, vdiff_low=-0.265, impedance=110, rise_ns=3.0,
        bit_ns=4.0, prop_ns_per_m=5.0, jitter_ps=30,
        termination="110 Ohm differential at both ports",
        notes="IEEE 1394b at 400 Mbit/s = 2.5 ns/bit (S100 beta doubles it). "
              "Strobe/ESB add a second pair; 8b/10b keeps the DC balanced.",
    ),
    "one_wire": _spec(
        "open_drain", "nrz", vcm=3.3, voh=3.3, vol=0.4, impedance=5000,
        rise_ns=15000.0, bit_ns=15000.0, prop_ns_per_m=10.0,
        termination="4.7 kOhm pull-up to VCC on DQ",
        notes="Very slow: 16.3 kbit/s over 100 m (15 us/bit). Reset pulses and "
              "presence detection are timed by the master stretching the low.",
    ),
    "iolink": _spec(
        "single_ended", "nrz", vcm=24.0, voh=24.0, vol=0.0, impedance=100,
        rise_ns=1000.0, bit_ns=1667.0, prop_ns_per_m=10.0,
        termination="Series resistor in C/Q; L+/L- carry the 24 V supply",
        notes="Single-wire COM3 data plus 24 V on L+/L-. 38.4 kbit/s = 26 us/bit.",
    ),
    "dsi3": _spec(
        "single_ended", "nrz", vcm=1.8, voh=1.8, vol=0.0, impedance=50,
        rise_ns=1.0, bit_ns=1.0, prop_ns_per_m=5.0, jitter_ps=20,
        termination="Series termination on the bidirectional data lane",
        notes="D-PHY style: 1.8 V, up to 1 Gbit/s per lane (1 ns/bit). CLK is "
              "forwarded and DATA toggles both ways.",
    ),
    "spdif": _spec(
        "passive", "bipolar_rz", pairs=[("D+", "D-", "bidirectional")],
        vcm=0.0, vdiff_high=0.55, vdiff_low=-0.55,
        impedance=75, rise_ns=100.0, bit_ns=100.0, prop_ns_per_m=6000.0,
        termination="75 Ohm coax termination at the receiver",
        notes="Bipolar return-to-zero at +/-0.55 V over 75 Ohm coax. The BNC "
              "shell is the return path, so there is no separate ground conductor.",
    ),
    "midi": _spec(
        "passive", "nrz", vcm=5.0, voh=5.0, vol=0.0, impedance=220,
        rise_ns=20000.0, bit_ns=2000.0, prop_ns_per_m=10.0,
        termination="220 Ohm to +5 V at the receiver, opto-isolated",
        notes="31.25 kbit/s (32 us/bit) current loop at 5 mA. Active-low: a low "
              "pulses the opto LED on the receiver side.",
    ),
    "sata_phy": _spec(
        "differential", "4b5b_nrzi",
        pairs=[("Tx+", "Tx-", "transmit"), ("Rx+", "Rx-", "receive")],
        vcm=0.7, vdiff_high=0.25, vdiff_low=-0.25, impedance=100, rise_ns=0.5,
        bit_ns=2.0, prop_ns_per_m=5.0, jitter_ps=20,
        termination="On-die 100 Ohm; AC coupling 750 nF on the TX lanes",
        notes="SATA 3.0 at 6 Gbit/s (2 GT/s, 1 ns/UI after 8b/10b) over 4 pairs "
              "of 100 Ohm differential.",
    ),
    "parallel_bus": _spec(
        "single_ended", "nrz", vcm=3.3, voh=3.3, vol=0.0, impedance=33,
        rise_ns=10.0, bit_ns=10.0, prop_ns_per_m=10.0,
        termination="Series 33-50 Ohm; stubs must stay under 1/4 wavelength",
        notes="Memory/LCD parallel buses: e.g. 8080 at 100 MHz (10 ns/bit). No "
              "differential signalling, so edge rate is set by bus length.",
    ),
    "isotp": _spec(
        "passive", "nrz", vcm=2.5, voh=3.5, vol=1.5, impedance=120, rise_ns=60.0,
        bit_ns=2000.0, prop_ns_per_m=5.0, jitter_ps=250,
        logic_1_is_vdiff_high=False,
        termination="120 Ohm at both ends of the underlying CAN bus",
        notes="ISO-TP defines no conductors of its own: multi-frame payloads are "
              "carried inside CAN frames using SF/FF/FC/BS flow control.",
    ),
    # --------------------------------------------------- RF (no wire pairs) ---
    # RF is described in dBm and antenna gain, not volts on a pin; Z0 = 50 Ohm.
    "cellular_radio": _spec(
        "rf", "", vcm=0.0, vdiff_high=23.0, vdiff_low=23.0, impedance=50,
        rise_ns=0.5, bit_ns=4.0, prop_ns_per_m=3.5,
        termination="50 Ohm characteristic impedance on the antenna feed",
        notes="Levels are dBm, not volts. A 50 Ohm match is mandatory - any "
              "mismatch reflects power back into the PA and reduces range.",
    ),
    "wifi_radio": _spec(
        "rf", "", vcm=0.0, vdiff_high=20.0, vdiff_low=20.0, impedance=50,
        rise_ns=0.5, bit_ns=0.4, prop_ns_per_m=3.5,
        termination="50 Ohm matched feed, usually a u.FL connector to the antenna",
        notes="2.4/5/6 GHz OFDM. Modulation varies per PHY (BPSK through "
              "4096-QAM), so there is no single level - this is dBm.",
    ),
    "ble_radio": _spec(
        "rf", "", vcm=0.0, vdiff_high=10.0, vdiff_low=10.0, impedance=50,
        rise_ns=0.5, bit_ns=0.625, prop_ns_per_m=3.5,
        termination="50 Ohm antenna feed",
        notes="GFSK at 1 or 2 Msymbol/s in the 2.4 GHz ISM band. The constant "
              "envelope lets the PA be nonlinear, which is why BLE is cheap.",
    ),
    "nfc_radio": _spec(
        "rf", "", vcm=0.0, vdiff_high=20.0, vdiff_low=20.0, impedance=50,
        rise_ns=100.0, bit_ns=100000.0, prop_ns_per_m=3.5,
        termination="13.56 MHz coil tuned with a parallel capacitor",
        notes="13.56 MHz inductive coupling at 106 kbit/s. Range follows coil "
              "geometry and field strength, not from a wire length.",
    ),
    "sub_ghz_radio": _spec(
        "rf", "", vcm=0.0, vdiff_high=14.0, vdiff_low=14.0, impedance=50,
        rise_ns=10.0, bit_ns=100000.0, prop_ns_per_m=3.5,
        termination="50 Ohm matched antenna feed",
        notes="433/868/915 MHz. Power is usually capped by regulation (14 dBm "
              "EIRP in the EU at 868 MHz).",
    ),
    "lora_radio": _spec(
        "rf", "", vcm=0.0, vdiff_high=14.0, vdiff_low=14.0, impedance=50,
        rise_ns=10.0, bit_ns=40000.0, prop_ns_per_m=3.5,
        termination="50 Ohm matched antenna feed",
        notes="Chirp spread spectrum at 0.3-50 kbit/s with very high processing "
              "gain; duty cycle is legally restricted to 1 % in many bands.",
    ),
    "ieee802154": _spec(
        "rf", "", vcm=0.0, vdiff_high=14.0, vdiff_low=14.0, impedance=50,
        rise_ns=0.5, bit_ns=40000.0, prop_ns_per_m=3.5,
        termination="50 Ohm antenna feed",
        notes="250 kbit/s at 2.4 GHz (O-QPSK with 1/2-chip DSSS) - this is the "
              "physical half of both Zigbee and Thread.",
    ),
    "thread_802154": _spec(
        "rf", "", vcm=0.0, vdiff_high=14.0, vdiff_low=14.0, impedance=50,
        rise_ns=0.5, bit_ns=40000.0, prop_ns_per_m=3.5,
        termination="50 Ohm antenna feed",
        notes="The same IEEE 802.15.4 radio as Zigbee; Thread adds an IPv6/6LoWPAN "
              "stack and a low-power border-router role.",
    ),
    "uwb_radio": _spec(
        "rf", "", vcm=0.0, vdiff_high=10.0, vdiff_low=10.0, impedance=50,
        rise_ns=1.0, bit_ns=7.8, prop_ns_per_m=3.5,
        termination="50 Ohm antenna feed",
        notes="3.5-10.5 GHz with 0.8 ns pulses giving about 10 cm ranging "
              "resolution. Range comes from time-of-flight, not signal strength.",
    ),
    "rf_radio": _spec(
        "rf", "", vcm=0.0, vdiff_high=27.0, vdiff_low=27.0, impedance=50,
        rise_ns=100.0, bit_ns=40000.0, prop_ns_per_m=3.5,
        termination="50 Ohm matched antenna feed",
        notes="UHF passive/active RFID at 860-960 MHz. A passive tag has no source "
              "at all, so it is powered entirely by the reader's field.",
    ),
    # ------------------------------------------- Bus power as the signal ----
    "twisted_pair_knx": _spec(
        "single_ended", "nrz", vcm=30.0, voh=30.0, vol=0.0, impedance=100,
        rise_ns=1000.0, bit_ns=10240.0, prop_ns_per_m=10.0,
        termination="1 kOhm to +30 V at the bus end; no terminator resistor",
        notes="KNX TP puts 29 V DC on a single twisted pair at 9.6 kbit/s "
              "(10.24 us/bit). Bus power and data share the same wire.",
    ),
    "dali_pair": _spec(
        "single_ended", "nrz", vcm=16.5, voh=16.5, vol=0.0, impedance=100,
        rise_ns=10000.0, bit_ns=416000.0, prop_ns_per_m=10.0,
        termination="Parallel 250 Ohm at both ends of the bus",
        notes="DALI-2 runs at 1200 baud (833 us/bit) using 16.5 V forward and "
              "8-11.5 V reverse bias on the same pair.",
    ),
}
def apply_electrical(protocols):
    """Attach structured electrical specs, resolving through the carrier chain.

    A logical protocol has the same voltages and the same edge rate as whatever
    carries it, so HTTP inherits Ethernet's 100 Ohm and Manchester numbers
    rather than inventing electrical characteristics of its own.

    Returns (protocols, with_spec, with_pairs) coverage counts.
    """
    n_spec = n_pairs = 0
    for p in protocols:
        spec = ELECTRICAL.get(p["id"])
        if spec is None:
            chain = p.get("signal_path", "")
            for candidate in reversed(chain.split(" \u2192 ") if chain else []):
                if candidate in ELECTRICAL:
                    spec = dict(ELECTRICAL[candidate])
                    spec["inherited_from"] = candidate
                    break
        if spec:
            p["electrical"] = spec
            n_spec += 1
            if spec.get("pairs"):
                n_pairs += 1
        else:
            p["electrical"] = {}
    return protocols, n_spec, n_pairs


def derive_derived(spec, cable_length_m=1.0):
    """Compute the numbers an engineer actually needs from a raw spec.

    Returns derived values (bit rate, one-way and round-trip flight time,
    edge-limited bandwidth, rise-time-per-bit ratio), or empty when the spec
    lacks the inputs.
    """
    out = {}
    bit_ns = spec.get("bit_period_ns")
    if bit_ns and bit_ns > 0:
        out["bit_rate_mbps"] = 1000.0 / bit_ns        # 1 ns -> 1000 Mbit/s
        out["clock_hz"] = 1e9 / bit_ns
    prop = spec.get("prop_delay_ns_per_m")
    if prop and cable_length_m:
        out["one_way_delay_ns"] = prop * cable_length_m
        out["round_trip_delay_ns"] = 2 * prop * cable_length_m
    rise = spec.get("rise_time_ns")
    if rise and rise > 0:
        out["bandwidth_mhz"] = 350.0 / rise          # 0.35 / tr, first-order
    if bit_ns and rise:
        out["rise_over_bit"] = rise / bit_ns
    return out


def format_levels(spec):
    """Human-readable level summary, chosen per signalling style."""
    sig = spec.get("signaling")
    if sig in ("differential", "bipolar"):
        hi, lo = spec.get("vdiff_high_volts"), spec.get("vdiff_low_volts")
        if hi is None or lo is None:
            return ""
        out = f"VDiff {lo:+.2f} V to {hi:+.2f} V (swing {abs(hi - lo):.2f} V)"
        vcm = spec.get("vcm_volts")
        if vcm:
            out += f", VCM {vcm:.2f} V"
        z = spec.get("impedance_ohm")
        if z:
            out += f", Z0 {z:.0f} Ohm"
        return out
    if sig == "rf":
        d = spec.get("vdiff_high_volts")
        z = spec.get("impedance_ohm")
        parts = []
        if d is not None:
            parts.append(f"{d:.0f} dBm")
        if z:
            parts.append(f"Z0 {z:.0f} Ohm matched")
        return ", ".join(parts)
    voh, vol = spec.get("voh_volts"), spec.get("vol_volts")
    if voh is None or vol is None:
        return ""
    out = f"VOH {voh:+.2f} V / VOL {vol:+.2f} V (swing {abs(voh - vol):.2f} V)"
    z = spec.get("impedance_ohm")
    if z:
        out += f", Z0 {z:.0f} Ohm"
    return out


def pair_names(spec):
    """Every conductor that participates in a differential pair."""
    names = []
    for pr in spec.get("pairs", []):
        names.append(pr["a"])
        names.append(pr["b"])
    return names
