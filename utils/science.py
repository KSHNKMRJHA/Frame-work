# -*- coding: utf-8 -*-
"""
science.py
Real, working engineering calculators used by the Science & Math Lab page.
All formulas are standard textbook/industry formulas — nothing simulated.

The CRC functions are verified against the published "check" values in the
reveng CRC catalogue (input "123456789"):
    CRC-16/IBM-3740 (CCITT-FALSE) -> 0x29B1
    CRC-16/MODBUS                 -> 0x4B37
    CRC-32/ISO-HDLC               -> 0xCBF43926
build_scripts/check_logic.py asserts these on every CI run, so a regression in
_crc16 cannot pass unnoticed.

Every function that divides by a caller-supplied value raises ValueError on a
non-positive input rather than letting a ZeroDivisionError escape into the UI.
"""

import math
import binascii
import re


# --------------------------------------------------------------- UART -----
def uart_bit_timing(f_clk_hz, target_baud, oversampling=16):
    """Classic UART baud-rate generator calculation (used in most MCUs).

    Equivalent to the AVR/STM32 form: divisor = round(F_CLK / (OS * baud)),
    i.e. UBRR + 1 on an AVR.

    Raises:
        ValueError: if any argument is not strictly positive.
    """
    if f_clk_hz <= 0:
        raise ValueError("MCU clock frequency must be greater than zero")
    if target_baud <= 0:
        raise ValueError("target baud rate must be greater than zero")
    if oversampling <= 0:
        raise ValueError("oversampling factor must be greater than zero")

    divisor_exact = f_clk_hz / (oversampling * target_baud)
    divisor = max(1, round(divisor_exact))
    actual_baud = f_clk_hz / (oversampling * divisor)
    error_pct = (actual_baud - target_baud) / target_baud * 100
    bit_time_us = 1e6 / actual_baud
    return {
        "divisor_exact": divisor_exact,
        "divisor": divisor,
        "actual_baud": actual_baud,
        "error_pct": error_pct,
        "bit_time_us": bit_time_us,
        "acceptable": abs(error_pct) < 2.0,  # most UARTs tolerate ~2% error
    }


# --------------------------------------------------------- SHANNON/NYQUIST -
def shannon_capacity(bandwidth_hz, snr_db):
    """Shannon-Hartley channel capacity: C = B * log2(1 + SNR).

    Raises:
        ValueError: if bandwidth is negative.
    """
    if bandwidth_hz < 0:
        raise ValueError("bandwidth cannot be negative")
    snr_linear = 10 ** (snr_db / 10)
    return bandwidth_hz * math.log2(1 + snr_linear)


def nyquist_max_rate(bandwidth_hz, levels):
    """Nyquist maximum symbol rate: R = 2B * log2(M).

    Raises:
        ValueError: if bandwidth is negative or fewer than 2 signal levels are
            given (log2(1) = 0 carries no information; log2(0) is undefined).
    """
    if bandwidth_hz < 0:
        raise ValueError("bandwidth cannot be negative")
    if levels < 2:
        raise ValueError("at least 2 signal levels are required to carry information")
    return 2 * bandwidth_hz * math.log2(levels)


# --------------------------------------------------------- FREQ/WAVELENGTH
SPEED_OF_LIGHT = 299_792_458  # m/s


def freq_to_wavelength(freq_hz):
    """Wavelength in metres for a frequency in Hz.

    Raises:
        ValueError: if frequency is not strictly positive.
    """
    if freq_hz <= 0:
        raise ValueError("frequency must be greater than zero")
    return SPEED_OF_LIGHT / freq_hz


def wavelength_to_freq(wavelength_m):
    """Frequency in Hz for a wavelength in metres.

    Raises:
        ValueError: if wavelength is not strictly positive.
    """
    if wavelength_m <= 0:
        raise ValueError("wavelength must be greater than zero")
    return SPEED_OF_LIGHT / wavelength_m


def quarter_wave_antenna_length(freq_hz, velocity_factor=0.95):
    """Approximate quarter-wave monopole antenna length.

    The velocity factor is an approximation, not a physical constant: it
    accounts for the wave travelling slightly slower along a real conductor
    than in free space. 0.95 is a common rule-of-thumb for thin wire.

    Raises:
        ValueError: if frequency is not strictly positive, or the velocity
            factor is outside (0, 1].
    """
    if not 0 < velocity_factor <= 1:
        raise ValueError("velocity factor must be greater than 0 and at most 1")
    wl = freq_to_wavelength(freq_hz)  # raises on freq <= 0
    return (wl / 4) * velocity_factor


# --------------------------------------------------------------- CRC ------
def _crc16(data: bytes, poly, init, refin, refout, xorout):
    """Bit-at-a-time CRC-16 engine.

    Computes reflected CRCs (refin/refout) using an MSB-first shift over a
    non-reflected polynomial: input bytes are bit-reversed on the way in and
    the register is bit-reversed on the way out. This is correct here because
    the only reflected variant used (CRC-16/MODBUS) has a bit-symmetric init
    value of 0xFFFF; a reflected variant with an asymmetric init would also
    need its init reversed.
    """
    crc = init
    for byte in data:
        b = byte
        if refin:
            b = int(f"{b:08b}"[::-1], 2)
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ poly) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    if refout:
        crc = int(f"{crc:016b}"[::-1], 2)
    return crc ^ xorout


def crc16_ccitt_false(data: bytes):
    """CRC-16/IBM-3740, widely known as CRC-16/CCITT-FALSE. Check: 0x29B1."""
    return _crc16(data, poly=0x1021, init=0xFFFF, refin=False, refout=False, xorout=0x0000)


def crc16_modbus(data: bytes):
    """CRC-16/MODBUS, used by Modbus RTU. Check: 0x4B37."""
    return _crc16(data, poly=0x8005, init=0xFFFF, refin=True, refout=True, xorout=0x0000)


def crc32_ieee(data: bytes):
    """CRC-32/ISO-HDLC, the Ethernet FCS polynomial. Check: 0xCBF43926."""
    return binascii.crc32(data) & 0xFFFFFFFF


_HEX_DIGITS = set("0123456789abcdefABCDEF")


def parse_user_bytes(text: str) -> bytes:
    """Accept either plain text ('Hello') or separated hex bytes ('48 65 6C').

    The input is read as hex only when it is unambiguously hex: two or more
    whitespace/comma-separated tokens that are each one or two hex digits.
    Anything else is encoded as UTF-8 text, so 'Test123' stays text and the
    standard CRC test vector '123456789' stays text rather than being read as
    nibbles.

    Single-token input is deliberately treated as text: '48' is far more likely
    to mean the two characters "48" than the single byte 0x48, and there is no
    way to tell. Use '48 00' or the 0x form if you mean bytes.
    """
    text = text.strip()
    if not text:
        return b""

    tokens = text.replace(",", " ").split()

    # Optional 0x prefixes, as long as every token carries one.
    if len(tokens) > 1 and all(t[:2].lower() == "0x" for t in tokens):
        stripped = [t[2:] for t in tokens]
        if all(1 <= len(t) <= 2 and set(t) <= _HEX_DIGITS for t in stripped):
            return bytes(int(t, 16) for t in stripped)

    if len(tokens) > 1 and all(1 <= len(t) <= 2 and set(t) <= _HEX_DIGITS for t in tokens):
        return bytes(int(t, 16) for t in tokens)

    return text.encode("utf-8")


# --------------------------------------------------------- CAN BIT TIMING -
def can_bit_timing(f_clk_hz, bitrate_bps, tq_prop=1, tq_ps1=1, tq_ps2=1, tq_sync=1):
    """Simplified CAN bit timing: total time quanta per bit, sample point %.

    Real controllers let you tune prescaler + segment lengths; this shows the
    underlying relationship. `prescaler_exact` is the number of controller
    clock cycles per time quantum — a real controller needs an integer here,
    so `prescaler_realizable` reports whether this combination is achievable.

    Raises:
        ValueError: if the clock or bitrate is not positive, or any segment
            length is less than 1 time quantum.
    """
    if f_clk_hz <= 0:
        raise ValueError("controller clock frequency must be greater than zero")
    if bitrate_bps <= 0:
        raise ValueError("bitrate must be greater than zero")
    for name, value in (("tq_sync", tq_sync), ("tq_prop", tq_prop), ("tq_ps1", tq_ps1), ("tq_ps2", tq_ps2)):
        if value < 1:
            raise ValueError(f"{name} must be at least 1 time quantum")

    total_tq = tq_sync + tq_prop + tq_ps1 + tq_ps2
    bit_time_s = 1 / bitrate_bps
    tq_time_s = bit_time_s / total_tq
    prescaler = tq_time_s * f_clk_hz
    sample_point_pct = 100 * (tq_sync + tq_prop + tq_ps1) / total_tq
    return {
        "total_tq": total_tq,
        "bit_time_ns": bit_time_s * 1e9,
        "tq_time_ns": tq_time_s * 1e9,
        "prescaler_exact": prescaler,
        # A real controller's baud-rate prescaler is an integer register.
        "prescaler_realizable": abs(prescaler - round(prescaler)) < 1e-9 and prescaler >= 1,
        "sample_point_pct": sample_point_pct,
        # ISO 11898-1 / CiA recommend 8-25 TQ per bit; fewer leaves no room
        # for resynchronisation jitter.
        "tq_count_in_spec": 8 <= total_tq <= 25,
    }


# ---------------------------------------------------- I2C PULL-UP DESIGN ---
# Limits from the NXP I2C-bus specification (UM10204):
#   tr_max: Sm 1000 ns, Fm 300 ns, Fm+ 120 ns.
#   Cb_max: Sm/Fm 400 pF, Fm+ 550 pF.
# Rp_max comes from TI SLVA689: tr = 0.8473 * Rp * Cb  =>  Rp = tr / (0.8473 * Cb).
I2C_MODES = {
    "Standard-mode (100 kHz)": {"tr_max_ns": 1000.0, "cb_max_pf": 400.0},
    "Fast-mode (400 kHz)": {"tr_max_ns": 300.0, "cb_max_pf": 400.0},
    "Fast-mode Plus (1 MHz)": {"tr_max_ns": 120.0, "cb_max_pf": 550.0},
}

# Nearest preferred values (E24 series) used to suggest a real resistor.
_E24 = (10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91)


def i2c_rise_time_ns(rp_ohms, bus_cap_pf):
    """I2C rise time tr = 0.8473 * Rp * Cb (TI SLVA689, 10%-90% definition).

    Raises:
        ValueError: if Rp or bus capacitance is not strictly positive.
    """
    if rp_ohms <= 0:
        raise ValueError("pull-up resistance must be greater than zero")
    if bus_cap_pf <= 0:
        raise ValueError("bus capacitance must be greater than zero")
    return 0.8473 * rp_ohms * bus_cap_pf * 1e-3


def i2c_recommended_pullups(vdd, bus_cap_pf, mode, vol=0.4, iol=0.003):
    """Feasible pull-up window for an I2C bus.

    Rp_min = (Vdd - Vol) / Iol          (driver must sink current with Vol <= spec)
    Rp_max = tr_max / (0.8473 * Cb)     (rise time must meet the mode limit)

    Defaults: Vol = 0.4 V and Iol = 3 mA are the standard/fast-mode figures
    from UM10204; fast-mode Plus sinks 20 mA, so pass iol=0.02 for Fm+ designs.

    Raises:
        ValueError: non-positive Vdd/Cb/Iol, Vol outside [0, Vdd), or unknown mode.
    """
    if vdd <= 0:
        raise ValueError("supply voltage must be greater than zero")
    if not 0 <= vol < vdd:
        raise ValueError("Vol must be at least 0 and less than the supply voltage")
    if iol <= 0:
        raise ValueError("sink current must be greater than zero")
    if bus_cap_pf <= 0:
        raise ValueError("bus capacitance must be greater than zero")
    if mode not in I2C_MODES:
        raise ValueError(f"unknown I2C mode {mode!r} (expected one of {sorted(I2C_MODES)})")

    rp_min = (vdd - vol) / iol
    limits = I2C_MODES[mode]
    rp_max = (limits["tr_max_ns"] * 1e-9) / (0.8473 * bus_cap_pf * 1e-12)

    # Preferred value inside the window: largest E24 step <= Rp_max, clamped
    # to Rp_min when the window is narrow.
    candidates = [e * 10**exp for exp in range(-2, 7) for e in _E24]
    in_range = [c for c in candidates if rp_min <= c <= rp_max]
    return {
        "rp_min_ohm": rp_min,
        "rp_max_ohm": rp_max,
        "feasible": rp_min <= rp_max,
        "suggested_ohm": max(in_range) if in_range else None,
        "tr_max_ns": limits["tr_max_ns"],
        "cb_max_pf": limits["cb_max_pf"],
        "cap_within_spec": bus_cap_pf <= limits["cb_max_pf"],
        "tr_at_min_ns": i2c_rise_time_ns(rp_min, bus_cap_pf),
        "tr_at_max_ns": i2c_rise_time_ns(rp_max, bus_cap_pf),
    }


# ------------------------------------------------ RS-485 FAIL-SAFE BIASING -
def _parallel(*resistors):
    """Parallel combination; infinite resistors are ignored."""
    finite = [r for r in resistors if r != float("inf")]
    if not finite:
        return float("inf")
    return 1.0 / sum(1.0 / r for r in finite)


def rs485_fail_safe_bias(vcc, r_pullup, r_pulldown, r_term=120.0, r_load=float("inf")):
    """Idle differential voltage produced by an external RS-485 bias network.

    With every driver in high-Z, the network is a simple series chain:
        Vcc - R_pullup - (A) - (R_term || R_load) - (B) - R_pulldown - GND
    so  Vos = Vcc * R_par / (R_pullup + R_pulldown + R_par),  R_par = R_term || R_load.

    TIA/EIA-485 receivers guarantee a recessive (logic 1) idle state only when
    Vos >= +200 mV with no driver active, so `meets_fail_safe` checks that.

    `r_load` models receiver input resistance: one standard unit load is 12 kOhm,
    so a bus of N full-load receivers is r_load = 12000 / N.

    Raises:
        ValueError: non-positive Vcc/resistances (infinite load is allowed).
    """
    if vcc <= 0:
        raise ValueError("supply voltage must be greater than zero")
    for name, value in (("r_pullup", r_pullup), ("r_pulldown", r_pulldown), ("r_term", r_term)):
        if value <= 0:
            raise ValueError(f"{name} must be greater than zero")
    if r_load <= 0:
        raise ValueError("receiver load must be greater than zero (use float('inf') for none)")

    r_par = _parallel(r_term, r_load)
    total = r_pullup + r_pulldown + r_par
    vos = vcc * r_par / total
    return {
        "vos_v": vos,
        "vos_mv": vos * 1000.0,
        "meets_fail_safe": vos >= 0.2,
        "quiescent_ma": (vcc / total) * 1000.0,
        "r_parallel_ohm": r_par,
        "margin_mv": (vos - 0.2) * 1000.0,
    }


def rs485_max_equal_bias(vcc, r_term=120.0, r_load=float("inf"), vos_target=0.2):
    """Largest equal pull-up/pulldown pair that still reaches `vos_target`.

    Inverts the divider: R_each = (Vcc * R_par / vos_target - R_par) / 2.

    Raises:
        ValueError: non-positive inputs, or a target the network cannot reach.
    """
    if vcc <= 0 or r_term <= 0 or vos_target <= 0:
        raise ValueError("vcc, r_term and vos_target must be greater than zero")
    if r_load <= 0:
        raise ValueError("receiver load must be greater than zero")
    r_par = _parallel(r_term, r_load)
    r_each = (vcc * r_par / vos_target - r_par) / 2.0
    if r_each <= 0:
        raise ValueError("vos_target is unachievable with this supply and termination")
    return r_each


# ------------------------------------------------------- CAN BUS LOAD ------
def can_frame_bits(data_bytes=8, extended=False):
    """Nominal (unstuffed) CAN frame length in bits, interframe space included.

    Base format (11-bit ID):   44 + 8*D bits frame, +3 bit IFS on the wire.
    Extended format (29-bit):  64 + 8*D bits frame, +3 bit IFS on the wire.
    The 44/64 figures count SOF + arbitration + control + data + CRC(15+delim)
    + ACK(2) + EOF(7); bit stuffing is NOT included here.

    Raises:
        ValueError: data length outside 0..8.
    """
    if not 0 <= data_bytes <= 8:
        raise ValueError("classic CAN data length must be 0-8 bytes (CAN FD reaches 64)")
    frame = (64 if extended else 44) + 8 * data_bytes
    # Stuffed region = SOF through the CRC sequence (CRC delim, ACK, EOF, IFS
    # are fixed format and never stuffed): 34 + 8*D base, 54 + 8*D extended.
    stuffed_region = (54 if extended else 34) + 8 * data_bytes
    return {
        "frame_bits": frame,
        "total_bits": frame + 3,  # frame + intermission occupies the wire
        "stuffed_region_bits": stuffed_region,
        # Worst case: a stuff bit can follow every 4 real bits (5 identical
        # bits trigger an inserted opposite bit, which restarts the run).
        "worst_case_stuff_bits": math.ceil(stuffed_region / 4),
        "extended": extended,
        "data_bytes": data_bytes,
    }


def can_bus_load(bitrate_bps, frames_per_second, data_bytes=8, extended=False):
    """CAN bus utilisation for a steady stream of identical frames.

    Returns nominal and worst-case (max bit stuffing) load percentages plus the
    frame duration, which is what a scheduler needs to bound worst-case latency.

    Raises:
        ValueError: non-positive bitrate or negative frame rate.
    """
    if bitrate_bps <= 0:
        raise ValueError("bitrate must be greater than zero")
    if frames_per_second < 0:
        raise ValueError("frame rate cannot be negative")

    frame = can_frame_bits(data_bytes, extended)
    nominal_bits = frame["total_bits"]
    worst_bits = nominal_bits + frame["worst_case_stuff_bits"]
    return {
        **frame,
        "frame_time_us": nominal_bits / bitrate_bps * 1e6,
        "worst_frame_time_us": worst_bits / bitrate_bps * 1e6,
        "bus_load_pct": 100.0 * frames_per_second * nominal_bits / bitrate_bps,
        "worst_bus_load_pct": 100.0 * frames_per_second * worst_bits / bitrate_bps,
    }


# ------------------------------------------------- RF LINK BUDGET ---------
def fspl_db(freq_mhz, distance_km):
    """Free-space path loss: FSPL(dB) = 20*log10(d_km) + 20*log10(f_MHz) + 32.44.

    Raises:
        ValueError: non-positive frequency or distance.
    """
    if freq_mhz <= 0:
        raise ValueError("frequency must be greater than zero")
    if distance_km <= 0:
        raise ValueError("distance must be greater than zero")
    return 20 * math.log10(distance_km) + 20 * math.log10(freq_mhz) + 32.44


def link_budget_db(tx_dbm, tx_gain_db, rx_gain_db, freq_mhz, distance_km, losses_db=0.0, sensitivity_dbm=-95.0):
    """Received power and fade margin for a line-of-sight RF link.

    EIRP = tx + tx gain;  Prx = EIRP + rx gain - FSPL - losses;
    margin = Prx - sensitivity (positive means the link closes).

    Raises:
        ValueError: negative losses, or non-positive frequency/distance.
    """
    if losses_db < 0:
        raise ValueError("losses cannot be negative")
    fspl = fspl_db(freq_mhz, distance_km)
    prx = tx_dbm + tx_gain_db - fspl + rx_gain_db - losses_db
    return {
        "fspl_db": fspl,
        "eirp_dbm": tx_dbm + tx_gain_db,
        "rx_power_dbm": prx,
        "sensitivity_dbm": sensitivity_dbm,
        "margin_db": prx - sensitivity_dbm,
        "link_ok": prx >= sensitivity_dbm,
    }


# ------------------------------------------- LOGIC NOISE MARGIN -----------
# (noise_margin is defined below, alongside the other calculators)

# ------------------------------------------------- FRAME OVERHEAD ANALYSIS -
_BIT_PLAIN = re.compile(r"^(\d+)$")
_BIT_RANGE = re.compile(r"^(\d+)\s*-\s*(\d+)$")
_BIT_OPEN = re.compile(r"^(\d+)\s*\+$")
_BIT_RANGE_K = re.compile(r"^(\d+)\s*-\s*(\d+)\s*k\+$", re.IGNORECASE)
_BIT_OPEN_RANGE = re.compile(r"^(\d+)\s*-\s*(\d+)\+$")


def parse_bit_count(spec):
    r"""Turn a frame_fields ``bits`` value into (min_bits, max_bits), or None.

    Understands the literal forms used across the database:
        8            -> (8, 8)
        "0-32"       -> (0, 32)          inclusive range
        "0+"         -> (0, None)        open-ended (variable length)
        "96-768"     -> (96, 768)        e.g. a 1-Wire reset window
        "8*n"        -> (8, None)        scales with payload; minimum is one unit
        "8*512B"     -> (4096, 4096)     fixed byte blocks
    Non-numeric annotations return None so the caller can report the field as
    "not a fixed bit count" instead of guessing a value.
    """
    if isinstance(spec, bool):          # bool is an int subclass; reject it
        return None
    if isinstance(spec, int):
        return (spec, spec) if spec >= 0 else None
    text = str(spec).strip()
    m = _BIT_PLAIN.match(text)
    if m:
        return (int(m.group(1)), int(m.group(1)))
    m = _BIT_RANGE.match(text)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m = _BIT_OPEN.match(text)
    if m:
        return (int(m.group(1)), None)
    m = _BIT_RANGE_K.match(text) or _BIT_OPEN_RANGE.match(text)
    if m:
        return (int(m.group(1)), None)
    # "8*n" / "n*8": one unit times an unknown count.
    m = re.match(r"^(\d+)\s*\*\s*n$", text, re.IGNORECASE)
    if m:
        return (int(m.group(1)), None)
    # "8*512B" -> fixed product with a byte suffix.
    m = re.match(r"^(\d+)\s*\*\s*(\d+)\s*[Bb]$", text)
    if m:
        total = int(m.group(1)) * int(m.group(2))
        return (total, total)
    return None


def frame_overhead(fields, payload_bits):
    """Overhead of one frame carrying `payload_bits` of useful data.

    Fields that repeat with the payload (data/FRMPayload style) are excluded from
    the fixed overhead because they *are* the payload rather than overhead.
    Fields that cannot be parsed are returned by name so the result stays
    explainable instead of silently dropping them.
    """
    fixed_bits = 0
    variable = []
    unknown = []
    for field in fields or []:
        name = str(field.get("name", ""))
        bits = parse_bit_count(field.get("bits"))
        if bits is None:
            unknown.append(name)
            continue
        lo, hi = bits
        if hi is None or "data" in name.lower() or "payload" in name.lower():
            variable.append(name)
            continue
        fixed_bits += hi
    total_bits = fixed_bits + payload_bits
    return {
        "fixed_overhead_bits": fixed_bits,
        "payload_bits": payload_bits,
        "total_bits": total_bits,
        "variable_fields": variable,
        "unparsed_fields": unknown,
        "efficiency_pct": 100.0 * payload_bits / total_bits if total_bits else 0.0,
        "total_bytes": -(-total_bits // 8),
    }


def noise_margin(voh_min, vih_min, vol_max, vil_max):
    """CMOS/TTL DC noise margins: NM_H = VOHmin − VIHmin, NM_L = VILmax − VOLmax.

    Positive margins mean the driver guarantees enough swing to be read
    correctly even with that much noise on the wire. A negative margin is a
    level incompatibility (e.g. 5 V output into mismatched thresholds).

    Raises:
        ValueError: if VOHmin is not above VOLmax (inverted supply data).
    """
    for name, value in (("voh_min", voh_min), ("vih_min", vih_min), ("vol_max", vol_max), ("vil_max", vil_max)):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite voltage")
    if voh_min <= vol_max:
        raise ValueError("VOHmin must be above VOLmax")
    nm_h = voh_min - vih_min
    nm_l = vil_max - vol_max
    return {
        "nm_high_v": nm_h,
        "nm_low_v": nm_l,
        "nm_high_mv": nm_h * 1000.0,
        "nm_low_mv": nm_l * 1000.0,
        "worst_mv": min(nm_h, nm_l) * 1000.0,
        "compatible": nm_h > 0 and nm_l > 0,
    }


# ------------------------------------------- UART FRAME EFFICIENCY --------
def uart_frame_efficiency(data_bits=8, parity_bits=0, stop_bits=1):
    """Payload efficiency of a UART frame: D / (1 + D + P + S).

    The start bit always costs one bit time; parity and extra stop bits are
    pure overhead. 8N1 = 80%, 8E1 ≈ 73%, 7E2 ≈ 64%.

    Raises:
        ValueError: data bits outside 5..9, parity outside 0..1, or stop
            bits outside {1, 1.5, 2}.
    """
    if data_bits not in (5, 6, 7, 8, 9):
        raise ValueError("UART data bits must be 5-9")
    if parity_bits not in (0, 1):
        raise ValueError("parity bits must be 0 or 1")
    if stop_bits not in (1, 1.5, 2):
        raise ValueError("stop bits must be 1, 1.5 or 2")
    total = 1 + data_bits + parity_bits + stop_bits
    return {
        "frame_bits": total,
        "payload_bits": data_bits,
        "overhead_bits": total - data_bits,
        "efficiency_pct": 100.0 * data_bits / total,
        "overhead_pct": 100.0 * (total - data_bits) / total,
    }


# ------------------------------------------- SPI THROUGHPUT ---------------
def spi_throughput(sclk_hz, bits_per_transfer=8, gap_us=0.0, overhead_bits=0):
    """Effective SPI throughput including CS gaps and protocol overhead.

    transfer_time = bits/SCLK + gap; effective rate = payload_bits / time.
    Use overhead_bits for command/address bytes that are not payload.

    Raises:
        ValueError: non-positive clock, non-positive transfer length,
            negative gap, or overhead exceeding the transfer.
    """
    if sclk_hz <= 0:
        raise ValueError("SCLK frequency must be greater than zero")
    if bits_per_transfer <= 0:
        raise ValueError("bits per transfer must be greater than zero")
    if gap_us < 0:
        raise ValueError("inter-transfer gap cannot be negative")
    if not 0 <= overhead_bits < bits_per_transfer:
        raise ValueError("overhead bits must be in [0, bits_per_transfer)")
    clock_time_us = bits_per_transfer / sclk_hz * 1e6
    total_us = clock_time_us + gap_us
    payload = bits_per_transfer - overhead_bits
    return {
        "clock_time_us": clock_time_us,
        "total_time_us": total_us,
        "raw_bps": bits_per_transfer / (total_us / 1e6),
        "payload_bps": payload / (total_us / 1e6),
        "efficiency_pct": 100.0 * payload / bits_per_transfer
        if gap_us == 0
        else 100.0 * payload / bits_per_transfer * clock_time_us / total_us,
    }


# ------------------------------------------- RS-485 STUB LENGTH -----------
def rs485_max_stub_length(edge_time_ns=30.0, velocity_factor=0.66):
    """Conservative max unterminated stub: L < tr · v / 10.

    A stub longer than ~1/10 of the edge length rings back into the bit and
    corrupts sampling. MAX485-class drivers rise in ~10-30 ns; CAT5 propagation
    is ~5 ns/m (VF 0.66). At 30 ns edges this gives ~0.6 m — the reason
    RS-485 demands daisy-chaining, not stars.

    Raises:
        ValueError: non-positive edge time or velocity factor outside (0, 1].
    """
    if edge_time_ns <= 0:
        raise ValueError("driver edge time must be greater than zero")
    if not 0 < velocity_factor <= 1:
        raise ValueError("velocity factor must be greater than 0 and at most 1")
    length_m = edge_time_ns * 1e-9 * SPEED_OF_LIGHT * velocity_factor / 10.0
    return {
        "max_stub_m": length_m,
        "max_stub_cm": length_m * 100.0,
        "rule": "stub < tr·v/10 (conservative reflection rule)",
    }


# ------------------------------------------- ETHERNET EFFICIENCY ----------
def ethernet_frame_efficiency(payload_bytes=1500):
    """Ethernet on-wire efficiency: payload / (payload + 38).

    Every frame pays 7 preamble + 1 SFD + 12 MAC + 2 type + 4 FCS + 12 IFG =
    38 bytes of overhead. Runt payloads below 46 bytes are padded to 64-byte
    minimum frames, which is why small packets are inefficient.

    Raises:
        ValueError: payload outside 0..9000 bytes.
    """
    if not 0 <= payload_bytes <= 9000:
        raise ValueError("payload must be 0-9000 bytes")
    padded = max(payload_bytes, 46)
    total = padded + 38
    return {
        "padded_payload": padded,
        "total_on_wire": total,
        "overhead_bytes": total - payload_bytes,
        "efficiency_pct": 100.0 * payload_bytes / total if total else 0.0,
        "min_frame_applies": payload_bytes < 46,
    }
