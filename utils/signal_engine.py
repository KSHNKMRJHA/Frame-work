# -*- coding: utf-8 -*-
"""Generic line-coding / signal engine.

Every protocol's electrical waveform is *derived*, not hand-drawn: you declare
the line coding (NRZ, NRZI, Manchester, 4B5B, bipolar-RZ, MLT-3, FSK...) and this
module encodes a bit stream into the electrical levels you would see on a scope.
A new protocol therefore gets a correct waveform for free once its coding is
declared, instead of needing a bespoke matplotlib function.

Coordinate system
-----------------
Time is measured in **bit periods**, so any bit rate can be plotted by scaling
the axis. Each encoder returns ``(t_start, t_end, level)`` segments; ``level``
is a plain number so one renderer draws logic (0/1), volts (2.5/3.5) or dBm
(-30/0) with no special-casing.

Conventions are explicit because inverted encodings are the classic source of
"my Manchester looks like yours but backwards":
  * Manchester IEEE 802.3 (Ethernet): 1 = low->high
  * Manchester G.E. Thomas:            1 = high->low
Pass ``invert=True`` to flip whichever the standard uses.
"""


# --------------------------------------------------------------- helpers ---
def _seg(segments, t, width, level):
    """Append one segment, skipping zero-width markers."""
    if width <= 0:
        return
    segments.append((t, t + width, level))


def _bit_value(bit):
    """Accept 0/1, "0"/"1", True/False."""
    if isinstance(bit, str):
        return 1 if bit.strip().lower() in ("1", "true", "high") else 0
    return 1 if bit else 0


def bits_from_bytes(data):
    """MSB-first bit string from bytes, e.g. b'\\x55' -> '01010101'."""
    return "".join(f"{byte:08b}" for byte in data)


def bytes_from_bits(bits):
    """Inverse of bits_from_bytes (left-pads to a byte boundary)."""
    bits = str(bits)
    if len(bits) % 8:
        bits = bits.zfill(((len(bits) + 7) // 8) * 8)
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


# ------------------------------------------------------- line encodings ----
def _nrz(bits, invert=False):
    """Non-Return-to-Zero: the level directly carries the bit value."""
    segs = []
    for i, b in enumerate(bits):
        _seg(segs, i, 1.0, float(_bit_value(b) ^ int(invert)))
    return segs


def _nrz_mark(bits, invert=False):
    """NRZ-Mark (J/K coding): inverted NRZ, as used by USB."""
    return _nrz(bits, invert=not invert)


def _nrzi(bits, invert=False, init=0.0):
    """NRZI: a 1 transitions at the start of the bit, a 0 holds."""
    segs = []
    level = float(init)
    for i, b in enumerate(bits):
        if _bit_value(b) ^ int(invert):
            level = 1.0 - level
        _seg(segs, i, 1.0, level)
    return segs


def _manchester(bits, invert=False):
    """Manchester: a mid-bit transition always, carrying clock + data.

    invert=False follows IEEE 802.3 (Ethernet): 1 = low->high.
    invert=True  follows G.E. Thomas:              1 = high->low.
    """
    segs = []
    for i, b in enumerate(bits):
        one_is_up = not invert
        if _bit_value(b):
            lo, hi = (0.0, 1.0) if one_is_up else (1.0, 0.0)
        else:
            lo, hi = (1.0, 0.0) if one_is_up else (0.0, 1.0)
        _seg(segs, i, 0.5, lo)
        _seg(segs, i + 0.5, 0.5, hi)
    return segs


def _diff_manchester(bits, invert=False, init=1.0):
    """Differential Manchester: mid-bit transition always; a *start* transition
    means 0, no start transition means 1 (Token Ring)."""
    segs = []
    level = float(init)
    for i, b in enumerate(bits):
        if not _bit_value(b):          # a 0 toggles at the bit start
            level = 1.0 - level
        _seg(segs, i, 0.5, level)
        _seg(segs, i + 0.5, 0.5, 1.0 - level)
        level = 1.0 - level
    return segs


def _ami(bits, invert=False):
    """Alternate Mark Inversion: 1 alternates +/-V, 0 is zero volts.

    The alternation is what keeps the signal DC-balanced, so a long run of 1s
    still averages to zero current.
    """
    segs = []
    last = -1
    for i, b in enumerate(bits):
        if not _bit_value(b):
            level = 0.0
        else:
            last = -last
            level = float(last)
        _seg(segs, i, 1.0, -level if invert else level)
    return segs


def _bipolar_rz(bits, invert=False, high=1.0, low=-1.0):
    """Bipolar return-to-zero (ARINC 429 / IEEE 802.6 style).

    Every bit starts with a pulse and the *duty cycle* carries the value, then
    the line returns to zero - which is why ARINC 429 needs no clock line.
    """
    segs = []
    for i, b in enumerate(bits):
        if _bit_value(b) ^ int(invert):
            _seg(segs, i, 0.75, high)
            _seg(segs, i + 0.75, 0.25, 0.0)
        else:
            _seg(segs, i, 0.25, low)
            _seg(segs, i + 0.25, 0.75, 0.0)
    return segs


def _mlt3(bits, invert=False):
    """MLT-3: 3 levels with a 4-step cycle, so duty cycle never exceeds 31.25 %."""
    segs = []
    steps = [0, 1, 0, -1]
    k = 0
    prev = 0.0
    for i, b in enumerate(bits):
        if _bit_value(b) ^ int(invert):
            level = float(steps[k % 4])
            k += 1
        else:
            level = prev                     # a zero holds the level
        _seg(segs, i, 1.0, level)
        prev = level
    return segs


def _miller(bits, invert=False, init=1.0):
    """Miller / biphase-M (DVD, ISO 14496 optical disc)."""
    segs = []
    level = float(init)
    prev = _bit_value(bits[0]) if bits else 0
    for i, b in enumerate(bits):
        cur = _bit_value(b)
        if i == 0 or cur != prev:
            level = 1.0 - level
        _seg(segs, i, 0.5, level)
        if cur:
            level = 1.0 - level
        _seg(segs, i + 0.5, 0.5, level)
        prev = cur
    return segs


def _pam4(symbols, invert=False):
    """PAM-4: four voltage levels per symbol (-3, -1, +1, +3)."""
    segs = []
    for i, s in enumerate(symbols):
        level = [-3.0, -1.0, 1.0, 3.0][int(s) % 4]
        _seg(segs, i, 1.0, -level if invert else level)
    return segs


def _fsk(bits, invert=False, low=-20.0, high=-10.0):
    """Binary FSK: frequency (plotted as a power level) carries the bit."""
    segs = []
    for i, b in enumerate(bits):
        _seg(segs, i, 1.0, high if _bit_value(b) ^ int(invert) else low)
    return segs


def _ask(bits, invert=False, off=-60.0, on=-20.0):
    """ASK / on-off keying: carrier amplitude carries the bit."""
    segs = []
    for i, b in enumerate(bits):
        _seg(segs, i, 1.0, on if _bit_value(b) ^ int(invert) else off)
    return segs


def _psk(bits, invert=False, low=-20.0, high=-20.0):
    """BPSK: the carrier phase flips on a 1."""
    segs = []
    phase = 1
    for i, b in enumerate(bits):
        if _bit_value(b) ^ int(invert):
            phase = -phase
        _seg(segs, i, 1.0, high if phase > 0 else low)
    return segs


def _nrzi_4b5b(bits, invert=False, init=1.0):
    """4B/5B line code followed by NRZI (FireWire, USB data toggling)."""
    segs = []
    level = float(init)
    for i, b in enumerate(bits):
        if _bit_value(b):
            level = 1.0 - level
        _seg(segs, i, 1.0, level)
    return segs


# Registry: name -> (encoder, human description, level labels)
LINE_CODINGS = {
    "nrz": (_nrz, "Non-Return-to-Zero: the level is the bit value.", ("0", "1")),
    "nrz_mark": (_nrz_mark, "NRZ-Mark (J/K coding): inverted NRZ, as used by USB.", ("K", "J")),
    "nrzi": (_nrzi, "NRZI: a 1 transitions at the bit start, a 0 holds.", ("hold low", "toggle")),
    "manchester": (_manchester, "Manchester: a mid-bit transition carries clock + data.", ("high->low", "low->high")),
    "diff_manchester": (_diff_manchester, "Differential Manchester: a start transition means 0.", ("hold", "transition")),
    "ami": (_ami, "Alternate Mark Inversion: 1 alternates +/-V, 0 is zero volts.", ("0 V", "+/-V")),
    "bipolar_rz": (_bipolar_rz, "Bipolar return-to-zero: the duty cycle carries the bit.", ("-V pulse", "+V pulse")),
    "mlt3": (_mlt3, "MLT-3: three levels on a 4-step cycle, max 31.25 % duty.", ("-1/0/+1", "")),
    "miller": (_miller, "Miller / biphase-M: DVD and ISO 14496 optical disc.", ("", "")),
    "pam4": (_pam4, "PAM-4: four voltage levels per symbol.", ("-3/-1/+1/+3", "")),
    "fsk": (_fsk, "Binary FSK: frequency carries the bit.", ("low freq", "high freq")),
    "ask": (_ask, "ASK / on-off keying: carrier amplitude carries the bit.", ("carrier off", "carrier on")),
    "psk": (_psk, "BPSK: the carrier phase flips on a 1.", ("phase 0", "phase 180")),
    "4b5b_nrzi": (_nrzi_4b5b, "4B/5B line code followed by NRZI.", ("hold", "toggle")),
}


def encode(coding, bits, invert=False, **kwargs):
    """Encode `bits` with a registered line coding.

    Returns (t_start, t_end, level) segments measured in bit periods.
    Raises:
        ValueError: for an unknown coding name.
    """
    if coding not in LINE_CODINGS:
        raise ValueError(f"unknown line coding {coding!r} (known: {sorted(LINE_CODINGS)})")
    values = [_bit_value(b) for b in bits]
    if not values:
        return []
    return LINE_CODINGS[coding][0](values, invert=invert, **kwargs)


def coding_info(coding):
    """(description, level_labels) for a coding, with a safe placeholder."""
    if coding in LINE_CODINGS:
        return LINE_CODINGS[coding][1], LINE_CODINGS[coding][2]
    return "Unknown line coding.", ("", "")


# ------------------------------------------------------- message analysis --
def analyze_message(bits, fields, label=""):
    """Align a bit stream against a protocol's frame_fields.

    Walks the declared fields in order, consuming each one from the stream, and
    returns one annotation per field with its offset, bit length and decoded
    value. This lets the UI label "ID = 0x123" above the real bits on the wire.

    Fields whose bit count is not a plain integer (ranges, "8*n", annotations)
    are skipped rather than guessed, so nothing is mislabelled.
    """
    stream = "".join("1" if _bit_value(b) else "0" for b in bits)
    out = []
    pos = 0
    for field in fields or []:
        name = str(field.get("name", ""))
        raw = field.get("bits")
        length = raw if isinstance(raw, int) and not isinstance(raw, bool) else None
        if length is None:
            try:
                length = int(str(raw))
            except (TypeError, ValueError):
                out.append({"name": name, "bits": raw, "offset": pos,
                            "length": None, "parsed": False})
                continue
        chunk = stream[pos:pos + length]
        if not chunk:
            out.append({"name": name, "bits": raw, "offset": pos,
                        "length": length, "value": None, "parsed": False})
            continue
        entry = {"name": name, "bits": raw, "offset": pos,
                 "length": length, "value": chunk, "parsed": True}
        entry.update(describe_value(chunk))
        out.append(entry)
        pos += length
    return {"label": label, "total_bits": len(stream), "fields": out}


def describe_value(bits):
    """Represent the same bit string in every base a reader might want.

    Adds decimal / hex / octal / binary and, when the bits form printable
    ASCII, the decoded text. Purely presentational - never changes the value.
    """
    text = str(bits)
    if not text or any(c not in "01" for c in text):
        return {"decimal": None, "hex": None, "binary": None, "ascii": None}
    width = len(text)
    value = int(text, 2)
    out = {
        "binary": text,
        "decimal": value,
        "hex": format(value, "0{}X".format((width + 3) // 4)),
        "octal": format(value, "o"),
    }
    if width % 8 == 0 and width >= 8:
        chars = []
        for i in range(0, width, 8):
            byte = int(text[i:i + 8], 2)
            chars.append(chr(byte) if 32 <= byte < 127 else ".")
        out["ascii"] = "".join(chars)
    else:
        out["ascii"] = None
    return out


def hex_dump(data, width=16):
    """Classic offset | hex | ascii dump, for showing a real byte sequence."""
    lines = []
    for offset in range(0, len(data), width):
        chunk = data[offset:offset + width]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{offset:08X}  {hex_part:<{width * 3 - 1}}  |{ascii_part}|")
    return "\n".join(lines)




# -------------------------------------------------- differential waves ----
def differential_levels(spec, bits, invert=False):
    """Build per-conductor voltage traces for a differential pair.

    For a differential link each bit becomes two voltages about the common
    mode:
        V+ = VCM + Vdiff/2      V- = VCM - Vdiff/2
    so a 200 mV USB differential rides on a 3.0 V common mode and a scope shows
    both lines hovering near 3 V - never a clean 0/1 rail. This is exactly what
    makes "VDiff" the right thing to measure.

    Returns [(trace_name, [(t_start, t_end, volts), ...]), ...] in bit periods.
    """
    sig = spec.get("signaling")
    vcm = spec.get("vcm_volts") or 0.0
    vhi = spec.get("vdiff_high_volts")
    vlo = spec.get("vdiff_low_volts")
    # "passive" media (coax, balanced audio) still carry a differential voltage;
    # only RF genuinely has no wire-level level.
    if sig in ("differential", "bipolar", "passive") and vhi is not None and vlo is not None:
        # A 1 sits at +Vhi across the pair, a 0 at +Vlo. Both conductors are
        # driven about the common mode, which is why they move in opposition.
        pos, neg = [], []
        for i, b in enumerate(bits):
            d = vhi if _bit_value(b) ^ int(invert) else vlo
            pos.append((i, i + 1.0, vcm + d / 2.0))
            neg.append((i, i + 1.0, vcm - d / 2.0))
        return [("V+", pos), ("V-", neg)]
    # Single-ended / open-drain: one driven line between VOL and VOH.
    voh = spec.get("voh_volts")
    vol = spec.get("vol_volts")
    if voh is not None and vol is not None:
        out = []
        for i, b in enumerate(bits):
            out.append((i, i + 1.0, float(voh if _bit_value(b) ^ int(invert) else vol)))
        return [("line", out)]
    return []


def _encode_voltage(bits, low, high=None, invert=False):
    """Map bits onto one or two voltage levels, one segment per bit."""
    if high is None:
        # Bipolar form: (low, low) means a single value per bit.
        high = low
    out = []
    for i, b in enumerate(bits):
        v = high if _bit_value(b) ^ int(invert) else low
        out.append((i, i + 1.0, float(v)))
    return out


def differential_waveform(spec, bits, length_m=1.0, invert=False):
    """A complete differential model: both lines plus the derived VDiff trace.

    The RX traces are the TX traces delayed by the one-way propagation delay,
    which is what makes the TX-to-RX skew visible - the number that decides
    whether a link closes its eye diagram.
    """
    traces = differential_levels(spec, bits, invert=invert)
    if not traces:
        return []
    names = [name for name, _ in traces]

    prop = spec.get("prop_delay_ns_per_m") or 0.0
    bit_ns = spec.get("bit_period_ns") or 1.0
    # Convert ns to bit periods so the delay scales with the actual cable.
    delay_bits = (prop * length_m) / bit_ns if bit_ns else 0.0

    out = []
    for name, segs in traces:
        out.append((name, segs))

    # VDiff is the signal the receiver actually thresholds.
    if len(traces) == 2 and spec.get("signaling") in ("differential", "bipolar", "passive"):
        vdiff = []
        pos, neg = traces[0][1], traces[1][1]
        for (t0, t1, vp), (_, _, vn) in zip(pos, neg):
            vdiff.append((t0, t1, vp - vn))
        out.append(("VDiff", vdiff))

    if delay_bits > 0 and names:
        for name in names:
            src = dict(out)[name]
            out.append((f"{name} (RX, delayed)",
                        [(t0 + delay_bits, t1 + delay_bits, lvl) for t0, t1, lvl in src]))
    return out


def eye_headroom(spec, bits=None):
    """Eye-opening estimate: how much margin a receiver has, in volts.

    For a differential link the eye height is the VDiff swing minus twice the
    noise/ISI allowance. This is a teaching estimate, not a simulator.
    """
    sig = spec.get("signaling")
    if sig in ("differential", "bipolar"):
        hi, lo = spec.get("vdiff_high_volts"), spec.get("vdiff_low_volts")
        if hi is None or lo is None:
            return {}
        swing = hi - lo
        return {"swing_volts": swing, "eye_height_volts": swing * 0.8,
                "basis": "80 % of the differential swing"}
    voh, vol = spec.get("voh_volts"), spec.get("vol_volts")
    if voh is None or vol is None:
        return {}
    swing = abs(voh - vol)
    return {"swing_volts": swing, "eye_height_volts": swing * 0.8,
            "basis": "80 % of the single-ended swing"}
