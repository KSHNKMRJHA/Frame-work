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
    wl = freq_to_wavelength(freq_hz)   # raises on freq <= 0
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
        crc ^= (b << 8)
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
    for name, value in (("tq_sync", tq_sync), ("tq_prop", tq_prop),
                        ("tq_ps1", tq_ps1), ("tq_ps2", tq_ps2)):
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
