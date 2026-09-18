# -*- coding: utf-8 -*-
import streamlit as st
from utils import science

from utils import branding

branding.page_config("Science & Math Lab", "🔬")
branding.sidebar_identity()

st.title("🔬 Science & Math Lab")
st.caption("The real engineering formulas behind every protocol you just read about — fully interactive, using standard textbook equations verified against known reference values.")

tabs = st.tabs([
    "⏱️ UART Baud/Bit-Timing", "📡 Shannon & Nyquist Capacity", "🔢 CRC Calculator",
    "📶 Frequency ↔ Wavelength", "🚌 CAN Bit Timing",
])

# ================================================================ TAB 1 ====
with tabs[0]:
    st.subheader("UART Baud Rate & Bit-Timing Calculator")
    st.write(
        "Every UART needs to divide its clock down to the target baud rate. Because the divisor "
        "must be an integer, there's almost always a small rounding error — too much error and "
        "framing/parity errors occur. This is the exact calculation your MCU's UART peripheral performs."
    )
    c1, c2, c3 = st.columns(3)
    f_clk = c1.number_input("MCU Clock Frequency (Hz)", min_value=1_000, max_value=1_000_000_000,
                            value=16_000_000, step=1_000_000, format="%d")
    baud = c2.selectbox("Target Baud Rate", [1200, 2400, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600], index=6)
    oversample = c3.selectbox("Oversampling factor", [8, 16], index=1)

    r = science.uart_bit_timing(f_clk, baud, oversample)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Divisor (rounded)", r["divisor"])
    m2.metric("Actual Baud Rate", f"{r['actual_baud']:.1f}")
    m3.metric("Error", f"{r['error_pct']:.2f}%")
    m4.metric("Bit Time", f"{r['bit_time_us']:.2f} µs")
    if r["acceptable"]:
        st.success("✅ Error is within the typical ±2% tolerance most UARTs can handle reliably.")
    else:
        st.error("⚠️ Error exceeds ~2% — this combination may cause framing errors on real hardware. Try a different clock or baud rate.")
    st.latex(r"\text{Divisor} = \frac{F_{CLK}}{\text{Oversampling} \times \text{Baud}}, \quad \text{Actual Baud} = \frac{F_{CLK}}{\text{Oversampling} \times \text{Divisor}_{rounded}}")

# ================================================================ TAB 2 ====
with tabs[1]:
    st.subheader("Shannon Capacity & Nyquist Rate")
    st.write(
        "Claude Shannon's 1948 theorem defines the absolute maximum error-free data rate of any "
        "noisy channel. Harry Nyquist's earlier (1928) theorem gives the maximum symbol rate of a "
        "noiseless channel of a given bandwidth. Together they explain why WiFi, cellular, and even "
        "your DSL line have hard physical speed limits."
    )
    c1, c2, c3 = st.columns(3)
    bw = c1.number_input("Channel Bandwidth (Hz)", min_value=1, max_value=100_000_000_000,
                         value=20_000_000, step=1_000_000, format="%d")
    snr = c2.slider("SNR (dB)", 0, 60, 30)
    levels = c3.slider("Signal levels (M, for Nyquist)", 2, 256, 4)

    cap = science.shannon_capacity(bw, snr)
    nyq = science.nyquist_max_rate(bw, levels)
    m1, m2 = st.columns(2)
    m1.metric("Shannon Capacity", f"{cap/1e6:.2f} Mbps")
    m2.metric("Nyquist Max Rate", f"{nyq/1e6:.2f} Mbps")
    st.latex(r"C = B \cdot \log_2(1 + SNR)")
    st.latex(r"R_{max} = 2B \cdot \log_2(M)")
    st.info("💡 A 20 MHz Wi-Fi channel with 30 dB SNR has a Shannon limit around 200 Mbps — which is why real Wi-Fi standards use sophisticated modulation (OFDM/MIMO) to approach, but never exceed, this limit.")

# ================================================================ TAB 3 ====
with tabs[2]:
    st.subheader("CRC Calculator (used by Modbus, CAN, Ethernet, and more)")
    st.write(
        "Cyclic Redundancy Checks detect transmission errors. Enter plain text, or space-separated "
        "hex bytes (e.g. `31 32 33 34 35 36 37 38 39`), to compute common CRCs used across the "
        "protocols in this Academy."
    )
    txt = st.text_input(
        "Input data", value="123456789",
        help="Try '123456789' — the standard CRC catalogue test vector. Input is read as hex "
             "only when it is unambiguously hex: two or more separated 1-2 digit hex tokens "
             "(e.g. '48 65 6C', '0x48 0x65'). Anything else is treated as UTF-8 text, so "
             "'123456789' and 'Test123' stay text.",
    )
    data = science.parse_user_bytes(txt)
    read_as = "hex bytes" if data != txt.strip().encode("utf-8") else "text"
    st.caption(f"Interpreted as **{read_as}** — {len(data)} byte(s): `{data.hex(' ')}`")
    if data:
        c1, c2, c3 = st.columns(3)
        c1.metric("CRC-16/CCITT-FALSE", f"0x{science.crc16_ccitt_false(data):04X}")
        c2.metric("CRC-16/MODBUS", f"0x{science.crc16_modbus(data):04X}")
        c3.metric("CRC-32 (Ethernet/IEEE)", f"0x{science.crc32_ieee(data):08X}")
        st.caption("Verified against standard test vectors: input '123456789' → CCITT-FALSE 0x29B1, MODBUS 0x4B37, CRC-32 0xCBF43926.")
    st.markdown(
        "- **CRC-16/MODBUS** is used by Modbus RTU for error checking.\n"
        "- **CRC-16/CCITT** variants appear in many telecom and industrial protocols.\n"
        "- **CRC-32** protects every Ethernet frame's Frame Check Sequence (FCS)."
    )

# ================================================================ TAB 4 ====
with tabs[3]:
    st.subheader("Frequency ↔ Wavelength & Antenna Length")
    st.write("Radio waves travel at the speed of light. This relationship determines antenna sizing for every wireless protocol — from 433 MHz LoRa to 6 GHz Wi-Fi.")
    mode = st.radio("Convert:", ["Frequency → Wavelength", "Wavelength → Frequency"], horizontal=True)
    if mode == "Frequency → Wavelength":
        freq_mhz = st.number_input("Frequency (MHz)", min_value=0.001, max_value=300_000.0,
                                   value=2400.0, step=1.0)
        wl = science.freq_to_wavelength(freq_mhz * 1e6)
        qw = science.quarter_wave_antenna_length(freq_mhz * 1e6)
        c1, c2 = st.columns(2)
        c1.metric("Wavelength", f"{wl*100:.2f} cm")
        c2.metric("Quarter-Wave Antenna Length (VF=0.95)", f"{qw*100:.2f} cm")
    else:
        wl_cm = st.number_input("Wavelength (cm)", min_value=0.001, max_value=1_000_000.0,
                                value=12.5, step=0.1)
        freq = science.wavelength_to_freq(wl_cm / 100)
        st.metric("Frequency", f"{freq/1e6:.2f} MHz")
    st.latex(r"\lambda = \frac{c}{f}, \quad c = 299{,}792{,}458\ m/s")
    st.caption("Common reference bands: 433 MHz (LoRa/SRD), 868/915 MHz (LoRaWAN region bands), 2.4 GHz (Wi-Fi/BLE/Zigbee), 5-6 GHz (Wi-Fi).")

# ================================================================ TAB 5 ====
with tabs[4]:
    st.subheader("CAN Bit Timing Calculator")
    st.write(
        "A CAN bit is divided into time quanta (TQ) across four segments: Sync, Propagation, Phase "
        "Segment 1, and Phase Segment 2. Where you place the 'sample point' inside the bit affects "
        "noise immunity and maximum bus length."
    )
    c1, c2 = st.columns(2)
    f_clk_can = c1.number_input("CAN Controller Clock (Hz)", min_value=1_000, max_value=1_000_000_000,
                                value=16_000_000, step=1_000_000, format="%d", key="can_clk")
    bitrate = c2.selectbox("Target Bitrate (bps)", [125_000, 250_000, 500_000, 1_000_000], index=2)
    c3, c4, c5 = st.columns(3)
    prop = c3.slider("Prop Segment (TQ)", 1, 8, 3)
    ps1 = c4.slider("Phase Segment 1 (TQ)", 1, 8, 3)
    ps2 = c5.slider("Phase Segment 2 (TQ)", 1, 8, 2)

    ct = science.can_bit_timing(f_clk_can, bitrate, tq_prop=prop, tq_ps1=ps1, tq_ps2=ps2)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Time Quanta / Bit", ct["total_tq"])
    m2.metric("Bit Time", f"{ct['bit_time_ns']:.0f} ns")
    m3.metric("Sample Point", f"{ct['sample_point_pct']:.1f}%")
    m4.metric("Prescaler (BRP)", f"{ct['prescaler_exact']:.3f}")

    if 75 <= ct["sample_point_pct"] <= 87.5:
        st.success("✅ Sample point is in the 75-87.5% range recommended by the Bosch CAN specification and CiA.")
    else:
        st.warning("⚠️ The Bosch CAN specification and CiA recommend a 75-87.5% sample point, trading noise immunity against propagation-delay tolerance.")

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

branding.page_footer()
