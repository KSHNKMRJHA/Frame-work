# -*- coding: utf-8 -*-
import streamlit as st
from utils import science
from utils.data_loader import load_protocols as science_load_protocols

from utils import branding

branding.page_config("Science & Math Lab", "🔬")
branding.sidebar_identity()

st.title("🔬 Science & Math Lab")
st.caption(
    "The real engineering formulas behind every protocol you just read about — fully interactive, "
    "using standard textbook equations verified against known reference values."
)

# ── SELECTBOX: pick a calculator ──────────────────────────────────────
calculators = [
    "⏱️ UART Baud/Bit-Timing",
    "📡 Shannon & Nyquist Capacity",
    "🔢 CRC Calculator",
    "📶 Frequency ↔ Wavelength",
    "🚌 CAN Bit Timing",
    "🔌 I²C Pull-Up Designer",
    "⚡ RS-485 Fail-Safe Biasing",
    "📊 CAN Bus Load",
    "📶 RF Link Budget",
    "🔀 Noise Margin",
    "🚀 Throughput & Efficiency",
    "🔀 RS-485 Stub",
    "🌐 Ethernet Efficiency",
    "📐 Frame Overhead Analyzer",
]

choice = st.selectbox(
    "Select a calculator:",
    calculators,
    help="Choose an engineering calculator. Each one opens in an expandable section with labeled inputs and results.",
)

# ── SHOW THE SELECTED CALCULATOR inside an expander ───────────────────
if choice == calculators[0]:
    with st.expander("UART Baud Rate & Bit-Timing"):
        st.caption("Calculate divisor, actual baud rate, error %, and bit time for a given MCU clock, baud rate, and oversampling factor.")
        st.subheader("UART Baud Rate & Bit-Timing Calculator")
        st.write(
            "Every UART needs to divide its clock down to the target baud rate. Because the divisor "
            "must be an integer, there's almost always a small rounding error — too much error and "
            "framing/parity errors occur. This is the exact calculation your MCU's UART peripheral performs."
        )
        c1, c2, c3 = st.columns(3)
        f_clk = c1.number_input(
            "MCU Clock Frequency (Hz)",
            min_value=1_000,
            max_value=1_000_000_000,
            value=16_000_000,
            step=1_000_000,
            format="%d",
            help="Controller clock frequency in hertz",
        )
        baud = c2.selectbox(
            "Target Baud Rate",
            [1200, 2400, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600],
            index=6,
            help="Desired serial baud rate",
        )
        oversample = c3.selectbox(
            "Oversampling factor",
            [8, 16],
            index=1,
            help="Number of samples per bit the UART uses",
        )

        r = science.uart_bit_timing(f_clk, baud, oversample)
        # 2x2 instead of 1x4: at tablet widths the sidebar leaves ~440px, so a
        # 4-up row squeezed each metric to 90px and ellipsised the values -
        # "-3.55%" rendered as "-3....". Streamlit stacks 2-up to 1-up on phones.
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)
        m1.metric("Divisor (rounded)", r["divisor"])
        m2.metric("Actual Baud Rate", f"{r['actual_baud']:.1f}")
        m3.metric("Error", f"{r['error_pct']:.2f}%")
        m4.metric("Bit Time", f"{r['bit_time_us']:.2f} µs")
        if r["acceptable"]:
            st.success("✅ Error is within the typical ±2% tolerance most UARTs can handle reliably.")
        else:
            st.error(
                "⚠️ Error exceeds ~2% — this combination may cause framing errors on real hardware. Try a different clock or baud rate."
            )
        st.latex(
            r"\text{Divisor} = \frac{F_{CLK}}{\text{Oversampling} \times \text{Baud}}, \quad \text{Actual Baud} = \frac{F_{CLK}}{\text{Oversampling} \times \text{Divisor}_{rounded}}"
        )

elif choice == calculators[1]:
    with st.expander("Shannon & Nyquist Capacity"):
        st.caption("Compute Shannon channel capacity and Nyquist maximum symbol rate for a given bandwidth, SNR, and modulation order.")
        st.subheader("Shannon Capacity & Nyquist Rate")
        st.write(
            "Claude Shannon's 1948 theorem defines the absolute maximum error-free data rate of any "
            "noisy channel. Harry Nyquist's earlier (1928) theorem gives the maximum symbol rate of a "
            "noiseless channel of a given bandwidth. Together they explain why WiFi, cellular, and even "
            "your DSL line have hard physical speed limits."
        )
        c1, c2, c3 = st.columns(3)
        bw = c1.number_input(
            "Channel Bandwidth (Hz)",
            min_value=1,
            max_value=100_000_000_000,
            value=20_000_000,
            step=1_000_000,
            format="%d",
            help="Channel bandwidth in hertz",
        )
        snr = c2.slider(
            "SNR (dB)",
            0,
            60,
            30,
            help="Signal-to-noise ratio in decibels",
        )
        levels = c3.slider(
            "Signal levels (M, for Nyquist)",
            2,
            256,
            4,
            help="Number of discrete signal levels for Nyquist formula",
        )

        cap = science.shannon_capacity(bw, snr)
        nyq = science.nyquist_max_rate(bw, levels)
        m1, m2 = st.columns(2)
        m1.metric("Shannon Capacity", f"{cap / 1e6:.2f} Mbps")
        m2.metric("Nyquist Max Rate", f"{nyq / 1e6:.2f} Mbps")
        st.latex(r"C = B \cdot \log_2(1 + SNR)")
        st.latex(r"R_{max} = 2B \cdot \log_2(M)")
        st.info(
            "💡 A 20 MHz Wi-Fi channel with 30 dB SNR has a Shannon limit around 200 Mbps — which is why real Wi-Fi standards use sophisticated modulation (OFDM/MIMO) to approach, but never exceed, this limit."
        )

elif choice == calculators[2]:
    with st.expander("CRC Calculator"):
        st.caption("Compute CRC-16/CCITT-FALSE, CRC-16/MODBUS, and CRC-32/ISO-HDLC checksums. Input as plain text or space-separated hex bytes.")
        st.subheader("CRC Calculator (used by Modbus, CAN, Ethernet, and more)")
        st.write(
            "Cyclic Redundancy Checks detect transmission errors. Enter plain text, or space-separated "
            "hex bytes (e.g. `31 32 33 34 35 36 37 38 39`), to compute common CRCs used across the "
            "protocols in this Academy."
        )
        txt = st.text_input(
            "Input data",
            value="123456789",
            help="Try '123456789' — the standard CRC catalogue test vector. Input is read as hex only when unambiguously hex: two or more separated 1-2 digit hex tokens (e.g. '48 65 6C'), or with 0x prefix. Anything else is treated as UTF-8 text.",
        )
        data = science.parse_user_bytes(txt)
        read_as = "hex bytes" if data != txt.strip().encode("utf-8") else "text"
        st.caption(f"Interpreted as **{read_as}** — {len(data)} byte(s): `{data.hex(' ')}`")
        if data:
            c1, c2, c3 = st.columns(3)
            c1.metric("CRC-16/CCITT-FALSE", f"0x{science.crc16_ccitt_false(data):04X}")
            c2.metric("CRC-16/MODBUS", f"0x{science.crc16_modbus(data):04X}")
            c3.metric("CRC-32 (Ethernet/IEEE)", f"0x{science.crc32_ieee(data):08X}")
            st.caption(
                "Verified against standard test vectors: input '123456789' → CCITT-FALSE 0x29B1, MODBUS 0x4B37, CRC-32 0xCBF43926."
            )
        st.markdown(
            "- **CRC-16/MODBUS** is used by Modbus RTU for error checking.\n"
            "- **CRC-16/CCITT** variants appear in many telecom and industrial protocols.\n"
            "- **CRC-32** protects every Ethernet frame's Frame Check Sequence (FCS)."
        )

elif choice == calculators[3]:
    with st.expander("Frequency ↔ Wavelength"):
        st.caption("Convert between frequency and wavelength; compute quarter-wave antenna length using a velocity factor.")
        st.subheader("Frequency ↔ Wavelength & Antenna Length")
        st.write(
            "Radio waves travel at the speed of light. This relationship determines antenna sizing for every wireless protocol — from 433 MHz LoRa to 6 GHz Wi-Fi."
        )
        mode = st.radio(
            "Convert:",
            ["Frequency → Wavelength", "Wavelength → Frequency"],
            horizontal=True,
            help="Direction of the conversion",
        )
        if mode == "Frequency → Wavelength":
            freq_mhz = st.number_input(
                "Frequency (MHz)",
                min_value=0.001,
                max_value=300_000.0,
                value=2400.0,
                step=1.0,
                help="Frequency in megahertz",
            )
            wl = science.freq_to_wavelength(freq_mhz * 1e6)
            qw = science.quarter_wave_antenna_length(freq_mhz * 1e6)
            c1, c2 = st.columns(2)
            c1.metric("Wavelength", f"{wl * 100:.2f} cm", help="Wavelength in centimetres")
            c2.metric(
                "Quarter-Wave Antenna Length (VF=0.95)",
                f"{qw * 100:.2f} cm",
                help="Quarter-wavelength monopole length with velocity factor 0.95",
            )
        else:
            wl_cm = st.number_input(
                "Wavelength (cm)",
                min_value=0.001,
                max_value=1_000_000.0,
                value=12.5,
                step=0.1,
                help="Wavelength in centimetres",
            )
            freq = science.wavelength_to_freq(wl_cm / 100)
            st.metric("Frequency", f"{freq / 1e6:.2f} MHz", help="Computed frequency from wavelength")

        st.latex(r"\lambda = \frac{c}{f}, \quad c = 299\,792\,458\ m/s")
        st.caption(
            "Common reference bands: 433 MHz (LoRa/SRD), 868/915 MHz (LoRaWAN region bands), 2.4 GHz (Wi-Fi/BLE/Zigbee), 5-6 GHz (Wi-Fi)."
        )

elif choice == calculators[4]:
    with st.expander("CAN Bit Timing"):
        st.caption("Compute total time quanta, sample point position, and prescaler for a CAN controller given clock, bitrate, and segment lengths.")
        st.subheader("CAN Bit Timing Calculator")
        st.write(
            "A CAN bit is divided into time quanta (TQ) across four segments: Sync, Propagation, Phase "
            "Segment 1, and Phase Segment 2. Where you place the 'sample point' inside the bit affects "
            "noise immunity and maximum bus length."
        )
        c1, c2 = st.columns(2)
        f_clk_can = c1.number_input(
            "CAN Controller Clock (Hz)",
            min_value=1_000,
            max_value=1_000_000_000,
            value=16_000_000,
            step=1_000_000,
            format="%d",
            key="can_clk",
            help="Controller clock frequency in hertz",
        )
        bitrate = c2.selectbox(
            "Target Bitrate (bps)",
            [125_000, 250_000, 500_000, 1_000_000],
            index=2,
            help="Desired CAN bit rate",
        )
        c3, c4, c5 = st.columns(3)
        prop = c3.slider(
            "Prop Segment (TQ)",
            1,
            8,
            3,
            help="Propagation segment length in time quanta",
        )
        ps1 = c4.slider(
            "Phase Segment 1 (TQ)",
            1,
            8,
            3,
            help="Phase segment 1 length in time quanta",
        )
        ps2 = c5.slider(
            "Phase Segment 2 (TQ)",
            1,
            8,
            2,
            help="Phase segment 2 length in time quanta",
        )

        ct = science.can_bit_timing(f_clk_can, bitrate, tq_prop=prop, tq_ps1=ps1, tq_ps2=ps2)
        # 2x2 instead of 1x4: at tablet widths the sidebar leaves ~440px, so a
        # 4-up row squeezed each metric to 90px and ellipsised the values -
        # "-3.55%" rendered as "-3....". Streamlit stacks 2-up to 1-up on phones.
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)
        m1.metric("Total Time Quanta / Bit", ct["total_tq"])
        m2.metric("Bit Time", f"{ct['bit_time_ns']:.0f} ns")
        m3.metric("Sample Point", f"{ct['sample_point_pct']:.1f}%")
        m4.metric("Prescaler (BRP)", f"{ct['prescaler_exact']:.3f}")

        if 75 <= ct["sample_point_pct"] <= 87.5:
            st.success("✅ Sample point is in the 75-87.5% range recommended by the Bosch CAN specification and CiA.")
        else:
            st.warning(
                "⚠️ The Bosch CAN specification and CiA recommend a 75-87.5% sample point, trading noise immunity against propagation-delay tolerance."
            )
        if not ct["tq_count_in_spec"]:
            st.warning(
                f"⚠️ {ct['total_tq']} time quanta per bit. ISO 11898-1 expects 8-25 TQ per bit — "
                "fewer leaves no room for resynchronisation jitter, and no real controller will accept it."
            )
        if not ct["prescaler_realizable"]:
            st.error(
                f"❌ This combination needs a prescaler of {ct['prescaler_exact']:.3f} clock cycles per time "
                "quantum, but a real controller's BRP register holds an integer. Change the clock, the bitrate, "
                "or the segment lengths until the prescaler comes out whole."
            )
        else:
            st.caption(
                f"Prescaler is a whole number ({int(round(ct['prescaler_exact']))} clock cycles per TQ), "
                "so this configuration is realizable on hardware."
            )

elif choice == calculators[5]:
    with st.expander("I²C Pull-Up Resistor Designer"):
        st.caption("Compute the feasible pull-up resistor window for an I²C bus given voltage, speed mode, capacitance, and receiver thresholds.")
        st.subheader("I²C Pull-Up Resistor Designer")
        st.write(
            "An I²C line only rises because of its pull-up resistor: too small and the "
            "open-drain driver can't sink the current (V_OL rises above spec), too large "
            "and the RC rise time eats the clock. Rp must land between both limits."
        )
        c1, c2, c3 = st.columns(3)
        vdd = c1.selectbox(
            "Bus voltage (V)",
            [1.8, 2.5, 3.3, 5.0],
            index=2,
            help="I²C bus supply voltage",
        )
        mode = c2.selectbox(
            "Speed mode",
            list(science.I2C_MODES),
            index=1,
            help="I²C speed standard",
        )
        cb = c3.slider(
            "Bus capacitance (pF)",
            10,
            550,
            150,
            help="Total bus capacitance including all devices",
        )
        c4, c5 = st.columns(2)
        vol = c4.number_input(
            "V_OL max (V)",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.05,
            help="Maximum low-level voltage the driver guarantees (0.4 V is standard/fast-mode figure from UM10204)",
        )
        iol = c5.number_input(
            "I_OL (mA)",
            min_value=0.5,
            max_value=20.0,
            value=3.0,
            step=0.5,
            help="Sink current the device must absorb (3 mA for Sm/Fm, 20 mA for Fm+)",
        )

        r = science.i2c_recommended_pullups(vdd, cb, mode, vol=vol, iol=iol / 1000.0)
        # 2x2 instead of 1x4: at tablet widths the sidebar leaves ~440px, so a
        # 4-up row squeezed each metric to 90px and ellipsised the values -
        # "-3.55%" rendered as "-3....". Streamlit stacks 2-up to 1-up on phones.
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)
        m1.metric("R_p minimum", f"{r['rp_min_ohm']:.0f} Ω")
        m2.metric("R_p maximum", f"{r['rp_max_ohm']:.0f} Ω")
        m3.metric("Suggested (E24)", f"{r['suggested_ohm']:.0f} Ω" if r["suggested_ohm"] else "—")
        m4.metric("Rise time @ R_p min", f"{r['tr_at_min_ns']:.0f} ns")

        if not r["feasible"]:
            st.error(
                f"❌ No feasible pull-up: R_p min ({r['rp_min_ohm']:.0f} Ω) exceeds R_p max "
                f"({r['rp_max_ohm']:.0f} Ω). Reduce bus capacitance or slow the mode."
            )
        elif r["suggested_ohm"]:
            st.success(
                f"✅ Any resistor between {r['rp_min_ohm']:.0f} Ω and {r['rp_max_ohm']:.0f} Ω works. "
                f"**{r['suggested_ohm']:.0f} Ω** is the largest E24 value in range (lowest standby current)."
            )
        else:
            st.success(f"✅ Feasible window {r['rp_min_ohm']:.0f} – {r['rp_max_ohm']:.0f} Ω (no E24 value fits exactly).")
        if not r["cap_within_spec"]:
            st.warning(
                f"⚠️ {cb} pF exceeds this mode's {r['cb_max_pf']:.0f} pF bus-capacitance limit "
                "(UM10204) — shorten the wiring or add a bus buffer."
            )
        st.latex(r"R_{p\min} = \frac{V_{DD} - V_{OL}}{I_{OL}}, \qquad R_{p\max} = \frac{t_r}{0.8473 \cdot C_b}")
        st.caption(
            "R_p max derives from the rise-time spec (t_r = 0.8473·R_p·C_b, TI SLVA689). "
            "Mode limits: t_r = 1000/300/120 ns (Sm/Fm/Fm+); C_b max = 400 pF (Sm/Fm), 550 pF (Fm+)."
        )

elif choice == calculators[6]:
    with st.expander("RS-485 Fail-Safe Biasing"):
        st.caption("Compute idle differential voltage from external bias resistors; check TIA/EIA-485 +200 mV fail-safe requirement.")
        st.subheader("RS-485 Fail-Safe Biasing Calculator")
        st.write(
            "When every RS-485 driver is in high-Z (nobody transmitting), the pair floats and "
            "the receivers would see noise. External bias resistors hold a positive idle "
            "differential — TIA/EIA-485 requires at least **+200 mV** for a guaranteed recessive state."
        )
        c1, c2, c3, c4 = st.columns(4)
        bvcc = c1.selectbox(
            "Bias supply (V)",
            [3.3, 5.0],
            index=1,
            key="b485_vcc",
            help="Bias supply voltage",
        )
        rpu = c2.number_input(
            "Pull-up R_A→Vcc (Ω)",
            min_value=100,
            max_value=10000,
            value=680,
            step=10,
            help="Pull-up resistor connected from A to bias supply",
        )
        rpd = c3.number_input(
            "Pull-down R_B→GND (Ω)",
            min_value=100,
            max_value=10000,
            value=680,
            step=10,
            help="Pull-down resistor connected from B to ground",
        )
        nodes = c4.slider(
            "Receivers (12 kΩ unit loads each)",
            1,
            64,
            1,
            help="Number of receivers on the bus; each loads the pair by 12 kΩ",
        )

        b = science.rs485_fail_safe_bias(bvcc, rpu, rpd, r_load=12000.0 / nodes)
        max_r = science.rs485_max_equal_bias(bvcc, r_load=12000.0 / nodes)
        m1, m2, m3 = st.columns(3)
        m1.metric("Idle V_os", f"{b['vos_mv']:.0f} mV")
        m2.metric("Margin over 200 mV", f"{b['margin_mv']:+.0f} mV")
        m3.metric("Bias current", f"{b['quiescent_ma']:.2f} mA")

        if b["meets_fail_safe"]:
            st.success(
                f"✅ {b['vos_mv']:.0f} mV ≥ 200 mV — idle state is guaranteed recessive. "
                f"Equal resistors can go as high as {max_r:.0f} Ω with this supply and load."
            )
        else:
            st.error(
                f"❌ {b['vos_mv']:.0f} mV < 200 mV — the bus can idle indeterminate. "
                f"Use equal pull-up/pulldown of at most {max_r:.0f} Ω."
            )
        st.latex(r"V_{os} = V_{CC} \cdot \frac{R_T \parallel R_L}{R_{PU} + R_{PD} + R_T \parallel R_L}")
        st.caption(
            "R_T = 120 Ω termination at both cable ends; each receiver loads the pair by "
            "12 kΩ (one standard unit load), so N receivers give R_L = 12 kΩ / N. "
            "Many modern transceivers have true fail-safe receivers and need no external bias."
        )

elif choice == calculators[7]:
    with st.expander("CAN Bus Load"):
        st.caption("Compute bus load percentage for a steady stream of CAN frames, including worst-case with bit stuffing.")
        st.subheader("CAN Bus Load & Frame Timing")
        st.write(
            "CAN bus load is the number you size a network by: past ~50-70 % load, "
            "worst-case latency for the highest-priority message grows sharply. This "
            "counts every field of the frame plus the worst case added by bit stuffing."
        )
        c1, c2, c3, c4 = st.columns(4)
        can_br = c1.selectbox(
            "Bitrate (kbps)",
            [125, 250, 500, 1000],
            index=2,
            help="CAN bit rate in kilobits per second",
        )
        fps = c2.number_input(
            "Frames per second",
            min_value=1,
            max_value=20000,
            value=100,
            step=10,
            help="Frame transmission rate",
        )
        dlc = c3.slider(
            "Data bytes (DLC)",
            0,
            8,
            8,
            help="Number of data bytes in the CAN frame (0-8 for classic CAN)",
        )
        ext = c4.checkbox(
            "Extended (29-bit) frame",
            value=False,
            help="Use 29-bit CAN identifier instead of 11-bit",
        )

        load = science.can_bus_load(can_br * 1000, fps, data_bytes=dlc, extended=ext)
        # 2x2 instead of 1x4: at tablet widths the sidebar leaves ~440px, so a
        # 4-up row squeezed each metric to 90px and ellipsised the values -
        # "-3.55%" rendered as "-3....". Streamlit stacks 2-up to 1-up on phones.
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)
        m1.metric("Frame (nominal)", f"{load['total_bits']} bits")
        m2.metric("Frame time", f"{load['frame_time_us']:.1f} µs")
        m3.metric("Bus load", f"{load['bus_load_pct']:.1f} %")
        m4.metric("Worst case (w/ stuffing)", f"{load['worst_bus_load_pct']:.1f} %")

        pct = load["worst_bus_load_pct"]
        if pct > 70:
            st.error(
                f"❌ {pct:.1f} % worst-case load — beyond the usual 70 % ceiling. "
                "Reduce the frame rate, shorten payloads, or raise the bitrate."
            )
        elif pct > 50:
            st.warning(
                f"⚠️ {pct:.1f} % worst-case load — above the 50 % guideline; queueing delay will be noticeable under bursty traffic."
            )
        else:
            st.success(f"✅ {pct:.1f} % worst-case load leaves comfortable headroom.")
        st.latex(
            r"\text{Frame}_{\text{base}} = 44 + 8D \ (64 + 8D \text{ extended}), \quad \text{Load} = \frac{\text{frames/s} \times \text{bits}}{\text{bitrate}}"
        )
        st.caption(
            "44 + 8D counts SOF + arbitration + control + data + CRC + ACK + EOF (+3 bits of "
            "intermission on the wire); bit stuffing can add one bit per four bits in the "
            "SOF→CRC region, which is the 'worst case' column."
        )

elif choice == calculators[8]:
    with st.expander("RF Link Budget"):
        st.caption("Free-space path loss link budget: compute FSPL, EIRP, received power, and link margin given TX power, antenna gains, frequency, distance, and sensitivity.")
        st.subheader("RF Link Budget (Free-Space)")
        st.write(
            "Does your wireless link actually close? Free-space path loss gives the "
            "best-case attenuation; add antenna gains and system losses to get received "
            "power, then compare against receiver sensitivity."
        )
        c1, c2, c3 = st.columns(3)
        freq = c1.number_input(
            "Frequency (MHz)",
            min_value=1.0,
            max_value=100000.0,
            value=2400.0,
            step=100.0,
            help="Signal frequency in megahertz",
        )
        dist = c2.number_input(
            "Distance (km)",
            min_value=0.001,
            max_value=1000.0,
            value=0.1,
            step=0.01,
            format="%.3f",
            help="Link distance in kilometres",
        )
        sens = c3.number_input(
            "Sensitivity (dBm)",
            min_value=-140.0,
            max_value=-40.0,
            value=-95.0,
            step=1.0,
            help="Receiver sensitivity threshold",
        )
        c4, c5, c6, c7 = st.columns(4)
        txp = c4.number_input(
            "TX power (dBm)",
            min_value=-30.0,
            max_value=60.0,
            value=20.0,
            step=1.0,
            help="Transmit power",
        )
        tg = c5.number_input(
            "TX antenna gain (dBi)",
            min_value=-5.0,
            max_value=30.0,
            value=2.0,
            step=0.5,
            help="Transmit antenna gain in decibels-isotropic",
        )
        rg = c6.number_input(
            "RX antenna gain (dBi)",
            min_value=-5.0,
            max_value=30.0,
            value=2.0,
            step=0.5,
            help="Receive antenna gain in decibels-isotropic",
        )
        loss = c7.number_input(
            "System losses (dB)",
            min_value=0.0,
            max_value=30.0,
            value=0.0,
            step=0.5,
            help="System losses including cables, connectors, and misalignment",
        )

        lb = science.link_budget_db(txp, tg, rg, freq, dist, losses_db=loss, sensitivity_dbm=sens)
        # 2x2 instead of 1x4: at tablet widths the sidebar leaves ~440px, so a
        # 4-up row squeezed each metric to 90px and ellipsised the values -
        # "-3.55%" rendered as "-3....". Streamlit stacks 2-up to 1-up on phones.
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)
        m1.metric("FSPL", f"{lb['fspl_db']:.1f} dB", help="Free-space path loss")
        m2.metric("EIRP", f"{lb['eirp_dbm']:.1f} dBm", help="Effective isotropic radiated power")
        m3.metric("Received power", f"{lb['rx_power_dbm']:.1f} dBm", help="Received power at antenna terminals")
        m4.metric("Link margin", f"{lb['margin_db']:.1f} dB", help="Margin above receiver sensitivity; positive = link closes")

        if lb["link_ok"]:
            st.success(
                f"✅ Link closes with {lb['margin_db']:.1f} dB of margin. "
                + (
                    "Comfortable fade margin for clear line of sight."
                    if lb["margin_db"] >= 20
                    else "Thin margin — rain, foliage, or misalignment may drop it."
                )
            )
        else:
            st.error(
                f"❌ Link does not close: received {lb['rx_power_dbm']:.1f} dBm is below "
                f"{sens:.0f} dBm sensitivity. Raise power/gain or shorten the range."
            )
        st.latex(r"\text{FSPL} = 20\log_{10}(d_{\text{km}}) + 20\log_{10}(f_{\text{MHz}}) + 32.44 \ \text{dB}")
        st.caption(
            "Free space is a best case: real links add fading, obstruction, and "
            "cable/connector losses — budget 10-20 dB of extra margin for anything outdoors."
        )

elif choice == calculators[9]:
    with st.expander("Logic Noise Margin"):
        st.caption("Compute CMOS noise margins NM_H and NM_L from driver/receiver threshold voltages.")
        st.subheader("Logic Noise Margin (level compatibility)")
        st.write(
            "NM_H = VOHmin − VIHmin and NM_L = VILmax − VOLmax. Both must be positive — "
            "a negative margin means the driver cannot reliably drive the receiver "
            "(e.g. a 5 V sensor into mismatched thresholds). Defaults are 3.3 V CMOS."
        )
        c1, c2, c3, c4 = st.columns(4)
        voh = c1.number_input(
            "VOHmin (V)",
            min_value=0.0,
            max_value=15.0,
            value=2.4,
            step=0.1,
            help="Minimum valid output high voltage",
        )
        vih = c2.number_input(
            "VIHmin (V)",
            min_value=0.0,
            max_value=15.0,
            value=2.31,
            step=0.01,
            help="Minimum valid input high voltage",
        )
        vol = c3.number_input(
            "VOLmax (V)",
            min_value=0.0,
            max_value=15.0,
            value=0.4,
            step=0.05,
            help="Maximum valid output low voltage",
        )
        vil = c4.number_input(
            "VILmax (V)",
            min_value=0.0,
            max_value=15.0,
            value=0.99,
            step=0.01,
            help="Maximum valid input low voltage",
        )
        nm = science.noise_margin(voh, vih, vol, vil)
        m1, m2, m3 = st.columns(3)
        m1.metric("NM_H", f"{nm['nm_high_mv']:.0f} mV")
        m2.metric("NM_L", f"{nm['nm_low_mv']:.0f} mV")
        m3.metric("Worst margin", f"{nm['worst_mv']:.0f} mV")
        if nm["compatible"]:
            st.success("✅ Both margins positive — levels are compatible with noise headroom.")
        else:
            st.error("❌ Negative margin — add a level shifter or pick compatible logic families.")
        st.latex(r"NM_H = V_{OHmin} - V_{IHmin}, \qquad NM_L = V_{ILmax} - V_{OLmax}")
        st.caption("CMOS rule of thumb: VIH ≈ 0.7×VDD, VIL ≈ 0.3×VDD. Always confirm in both datasheets.")

elif choice == calculators[10]:
    with st.expander("Throughput & Efficiency"):
        st.caption("Compute UART frame efficiency and SPI throughput including CS gaps and protocol overhead.")
        st.subheader("Throughput & Efficiency")
        st.write(
            "Every serial byte pays framing overhead. 8N1 wastes 20% on start+stop; "
            "parity and extra stop bits cost more. SPI pays no framing per bit but "
            "loses throughput to CS gaps and command/address overhead."
        )
        c1, c2, c3 = st.columns(3)
        db = c1.selectbox(
            "UART data bits",
            [5, 6, 7, 8, 9],
            index=3,
            help="Number of data bits per UART frame",
        )
        pb = c2.selectbox(
            "Parity bits",
            [0, 1],
            index=0,
            help="Number of parity bits (0 = none, 1 = odd or even)",
        )
        sb = c3.selectbox(
            "Stop bits",
            [1, 1.5, 2],
            index=0,
            help="Number of stop bits (1, 1.5, or 2)",
        )
        eff = science.uart_frame_efficiency(db, pb, sb)
        m1, m2 = st.columns(2)
        m1.metric("UART efficiency", f"{eff['efficiency_pct']:.1f} %")
        m2.metric("Frame size", f"{eff['frame_bits']:g} bits ({eff['overhead_bits']:g} overhead)")
        st.divider()
        c4, c5, c6, c7 = st.columns(4)
        sclk = c4.number_input(
            "SPI SCLK (MHz)",
            min_value=0.1,
            max_value=150.0,
            value=10.0,
            step=1.0,
            help="SPI serial clock frequency in megahertz",
        )
        bits = c5.number_input(
            "Bits per transfer",
            min_value=8,
            max_value=1024,
            value=8,
            step=8,
            help="Number of bits transferred in one SPI transaction",
        )
        gap = c6.number_input(
            "CS gap (µs)",
            min_value=0.0,
            max_value=1000.0,
            value=1.0,
            step=0.5,
            help="Chip-select idle time between transfers in microseconds",
        )
        ovh = c7.number_input(
            "Overhead bits",
            min_value=0,
            max_value=512,
            value=0,
            step=8,
            help="Number of overhead bits (command/address bytes not counted as payload)",
        )
        th = science.spi_throughput(sclk * 1e6, int(bits), gap_us=gap, overhead_bits=int(ovh))
        m3, m4, m5 = st.columns(3)
        m3.metric("Transfer time", f"{th['total_time_us']:.2f} µs")
        m4.metric("Payload rate", f"{th['payload_bps'] / 1e6:.2f} Mbps")
        m5.metric("Efficiency", f"{th['efficiency_pct']:.1f} %")
        st.caption("Gate SCLK when idle and batch registers into bursts — CS gaps dominate at small transfers.")

elif choice == calculators[11]:
    with st.expander("RS-485 Maximum Stub Length"):
        st.caption("Compute the maximum unterminated stub length from driver rise time and cable velocity factor; why RS-485 demands daisy-chaining.")
        st.subheader("RS-485 Maximum Stub Length")
        st.write(
            "Stubs ring back into the bit when they exceed ~1/10 of the driver edge "
            "length. This is why RS-485 demands daisy-chaining: stars and long drops "
            "corrupt sampling even with perfect termination."
        )
        c1, c2 = st.columns(2)
        edge = c1.number_input(
            "Driver rise time (ns)",
            min_value=1.0,
            max_value=200.0,
            value=30.0,
            step=5.0,
            help="Driver output rise/fall time in nanoseconds",
        )
        vf = c2.slider(
            "Cable velocity factor",
            0.5,
            1.0,
            0.66,
            step=0.01,
            help="Velocity factor: 1.0 = free space, ~0.66 = typical CAT5/100Ω coax",
        )
        stub = science.rs485_max_stub_length(edge, vf)
        st.metric("Max stub length", f"{stub['max_stub_cm']:.0f} cm")
        st.latex(r"L_{stub} < \frac{t_r \cdot c \cdot VF}{10}")
        st.caption(
            "MAX485-class edges (~30 ns) give ~60 cm. Faster drivers need SHORTER stubs — slow the edge or daisy-chain."
        )

elif choice == calculators[12]:
    with st.expander("Ethernet Efficiency"):
        st.caption("Compute on-wire Ethernet frame efficiency: payload bytes divided by total frame bytes (payload + 38-byte overhead).")
        st.subheader("Ethernet On-Wire Efficiency")
        st.write(
            "Every Ethernet frame pays 38 bytes: 7 preamble + 1 SFD + 12 MAC + 2 type + "
            "4 FCS + 12 interframe gap. Small packets are mostly overhead — the reason "
            "control protocols batch data instead of sending single bytes."
        )
        pay = st.slider(
            "Payload size (bytes)",
            0,
            1500,
            1500,
            help="Payload size in bytes (0 to 1500, the standard MTU)",
        )
        ee = science.ethernet_frame_efficiency(int(pay))
        m1, m2, m3 = st.columns(3)
        m1.metric("On-wire frame", f"{ee['total_on_wire']} bytes")
        m2.metric("Efficiency", f"{ee['efficiency_pct']:.1f} %")
        m3.metric("Overhead", f"{ee['overhead_bytes']} bytes")
        if ee["min_frame_applies"]:
            st.warning("⚠️ Below 46 bytes the frame is padded to the 64-byte minimum — efficiency collapses.")
        else:
            st.success("✅ Full-size frames approach 97.5% efficiency.")
        st.caption("1500 B → 97.5% efficient; 10 B → ~12% efficient. Batch small telemetry.")

elif choice == calculators[13]:
    with st.expander("Frame Overhead Analyzer"):
        st.caption("Pick any protocol with a documented frame layout and compute fixed overhead, total bits, and payload efficiency for a chosen payload size.")
        st.subheader("Frame Overhead Analyzer")
        st.write(
            "Every frame carries addressing, length, integrity and framing fields on top "
            "of the data. This analyzer reads the real `frame_fields` stored for each "
            "protocol and shows how much of the wire is actually useful — the number that "
            "decides whether you batch small messages or not."
        )
        protocols = science_load_protocols()
        framed = [p for p in protocols if p.get("frame_fields")]
        if not framed:
            st.info("No protocols with documented frame layouts are available.")
        else:
            framed.sort(key=lambda p: p["name"])
            c1, c2 = st.columns([2, 1])
            pid = c1.selectbox(
                "Protocol",
                [p["id"] for p in framed],
                format_func=lambda i: next(p["name"] for p in framed if p["id"] == i),
            )
            payload_bytes = c2.number_input("Payload (bytes)", min_value=1, max_value=1500, value=64, step=8)
            sel = next(p for p in framed if p["id"] == pid)
            res = science.frame_overhead(sel["frame_fields"], payload_bytes * 8)

            # 2x2 instead of 1x4: at tablet widths the sidebar leaves ~440px, so a
            # 4-up row squeezed each metric to 90px and ellipsised the values -
            # "-3.55%" rendered as "-3....". Streamlit stacks 2-up to 1-up on phones.
            m1, m2 = st.columns(2)
            m3, m4 = st.columns(2)
            m1.metric("Fixed overhead", f"{res['fixed_overhead_bits']} bits")
            m2.metric("Total frame", f"{res['total_bits']} bits ({res['total_bytes']} B)")
            m3.metric("Payload efficiency", f"{res['efficiency_pct']:.1f}%")
            m4.metric("Overhead per message", f"{res['fixed_overhead_bits'] / 8:.0f} bytes")

            if res["efficiency_pct"] >= 85:
                st.success("✅ Efficient at this payload size — headers amortise well.")
            elif res["efficiency_pct"] >= 60:
                st.warning("⚠️ Moderate overhead. Batching several small messages per frame would help.")
            else:
                st.error("❌ Header-dominated: most of the wire is overhead. Use a larger payload or a leaner protocol.")

            if res["variable_fields"]:
                st.caption(
                    "Variable-length field(s) treated as payload, not overhead: "
                    + ", ".join(res["variable_fields"])
                )
            if res["unparsed_fields"]:
                st.caption(
                    "Fields without a fixed bit count (excluded from the overhead total): "
                    + ", ".join(res["unparsed_fields"])
                )
            if sel.get("frame_note"):
                st.info(f"ℹ️ {sel['frame_note']}")
            st.latex(r"\text{Efficiency} = \frac{\text{payload bits}}{\text{fixed overhead} + \text{payload}} \times 100\%")

branding.page_footer()
