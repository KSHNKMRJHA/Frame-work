# API: Science

`utils.science` — Verified engineering calculators for communication protocols.

## CRC Calculators

### `crc16_ccitt_false(data: bytes) -> int`

```python
def crc16_ccitt_false(data: bytes) -> int:
    """CRC-16/CCITT-FALSE (poly=0x1021, init=0xFFFF, refin=True, refout=True, xorout=0x0000).
    
    Args:
        data: Input bytes.
        
    Returns:
        16-bit CRC value.
        
    Verification:
        crc16_ccitt_false(b"123456789") == 0x29B1  # reveng catalogue
    """
```

**Aliases:** `crc16_ccitt`, `crc16_xmodem`

---

### `crc16_modbus(data: bytes) -> int`

```python
def crc16_modbus(data: bytes) -> int:
    """CRC-16/MODBUS (poly=0x8005, init=0xFFFF, refin=True, refout=True, xorout=0x0000).
    
    Args:
        data: Input bytes.
        
    Returns:
        16-bit CRC value.
        
    Verification:
        crc16_modbus(b"123456789") == 0x4B37  # reveng catalogue
    """
```

---

### `crc32_ieee(data: bytes) -> int`

```python
def crc32_ieee(data: bytes) -> int:
    """CRC-32/ISO-HDLC (poly=0x04C11DB7, init=0xFFFFFFFF, refin=True, refout=True, xorout=0xFFFFFFFF).
    
    Args:
        data: Input bytes.
        
    Returns:
        32-bit CRC value.
        
    Verification:
        crc32_ieee(b"123456789") == 0xCBF43926  # reveng catalogue
    """
```

**Aliases:** `crc32`, `crc32_ethernet`, `crc32_zip`

---

### `parse_user_bytes(text: str) -> bytes`

```python
def parse_user_bytes(text: str) -> bytes:
    """Parse user input for CRC calculator.
    
    Handles:
    - Empty string → b""
    - Plain text → UTF-8 bytes
    - Hex with spaces: "48 65 6C 6C 6F" → b"Hello"
    - Hex with commas: "48,65,6C" → b"Hel"
    - Mixed: "Test123" → b"Test123" (not interpreted as hex)
    
    Args:
        text: User input string.
        
    Returns:
        Bytes for CRC calculation.
    """
```

---

## UART Calculator

### `uart_bit_timing(f_clk: int, baud: int, oversampling: int = 16) -> dict`

```python
def uart_bit_timing(
    f_clk: int,
    baud: int,
    oversampling: int = 16
) -> dict:
    """Calculate UART baud rate divisor and error.
    
    Formula (AVR/STM32 style):
        divisor = round(f_clk / (oversampling * baud))
        actual_baud = f_clk / (oversampling * divisor)
        error_pct = 100 * (actual_baud - baud) / baud
        acceptable = abs(error_pct) <= 2.0
    
    Args:
        f_clk: Clock frequency in Hz (e.g., 16_000_000).
        baud: Target baud rate (e.g., 9600, 115200).
        oversampling: Oversampling factor (default 16).
        
    Returns:
        Dict with:
        - divisor: int (register value)
        - actual_baud: float
        - error_pct: float
        - acceptable: bool (±2% tolerance)
        
    Raises:
        ValueError: If f_clk <= 0, baud <= 0, or oversampling <= 0.
        
    Verification:
        uart_bit_timing(16_000_000, 9600, 16)["divisor"] == 104
        uart_bit_timing(16_000_000, 9600, 16)["error_pct"] ≈ 0.16%
        uart_bit_timing(16_000_000, 115200, 16)["acceptable"] == False
    """
```

---

## CAN Calculator

### `can_bit_timing(f_clk: float, bitrate: int, tq_prop: int = 3, tq_ps1: int = 3, tq_ps2: int = 2, sjw: int = 1) -> dict`

```python
def can_bit_timing(
    f_clk: float,
    bitrate: int,
    tq_prop: int = 3,
    tq_ps1: int = 3,
    tq_ps2: int = 2,
    sjw: int = 1
) -> dict:
    """Calculate CAN bit timing parameters.
    
    Time Quantum (TQ) = 1 / (f_clk / prescaler)
    Nominal Bit Time = sync_seg + prop_seg + phase_seg1 + phase_seg2
    Sample Point = (sync_seg + prop_seg + phase_seg1) / total_tq * 100%
    
    Args:
        f_clk: Clock frequency in Hz (e.g., 16e6).
        bitrate: Target bitrate in bps (e.g., 500_000).
        tq_prop: Propagation segment (TQs).
        tq_ps1: Phase segment 1 (TQs).
        tq_ps2: Phase segment 2 (TQs).
        sjw: Synchronization jump width (TQs).
        
    Returns:
        Dict with:
        - prescaler: int
        - total_tq: int (sync + prop + ps1 + ps2)
        - sample_point_pct: float
        - time_quantum_ns: float
        - actual_bitrate: float
        - error_pct: float
        
    Raises:
        ValueError: If f_clk <= 0, bitrate <= 0, or no valid prescaler found.
        
    Verification:
        can_bit_timing(16e6, 500_000, 3, 3, 2)["total_tq"] == 9
        can_bit_timing(16e6, 500_000, 3, 3, 2)["sample_point_pct"] ≈ 77.78%
    """
```

---

## Information Theory

### `shannon_capacity(bandwidth_hz: float, snr_db: float) -> float`

```python
def shannon_capacity(bandwidth_hz: float, snr_db: float) -> float:
    """Shannon-Hartley channel capacity.
    
    Formula: C = B * log2(1 + SNR_linear)
    where SNR_linear = 10^(SNR_dB / 10)
    
    Args:
        bandwidth_hz: Channel bandwidth in Hz.
        snr_db: Signal-to-noise ratio in dB.
        
    Returns:
        Channel capacity in bits/second.
        
    Raises:
        ValueError: If bandwidth_hz <= 0.
        
    Verification:
        shannon_capacity(20e6, 30) ≈ 20e6 * log2(1001) ≈ 199.3 Mbps
    """
```

---

### `nyquist_max_rate(bandwidth_hz: float, signal_levels: int) -> int`

```python
def nyquist_max_rate(bandwidth_hz: float, signal_levels: int) -> int:
    """Nyquist maximum symbol rate (noise-free channel).
    
    Formula: C = 2 * B * log2(M)
    where M = signal levels (e.g., 2 for binary, 4 for QPSK).
    
    Args:
        bandwidth_hz: Channel bandwidth in Hz.
        signal_levels: Number of discrete signal levels (M).
        
    Returns:
        Maximum symbol rate in symbols/second.
        
    Raises:
        ValueError: If bandwidth_hz <= 0 or signal_levels < 2.
        
    Verification:
        nyquist_max_rate(3000, 2) == 6000  # 3 kHz, binary
        nyquist_max_rate(3000, 4) == 12000  # 3 kHz, 4-level
    """
```

---

## RF / Wavelength

### `freq_to_wavelength(freq_hz: float) -> float`

```python
def freq_to_wavelength(freq_hz: float) -> float:
    """Convert frequency to wavelength in meters.
    
    Formula: λ = c / f
    where c = 299,792,458 m/s (speed of light).
    
    Args:
        freq_hz: Frequency in Hz.
        
    Returns:
        Wavelength in meters.
        
    Raises:
        ValueError: If freq_hz <= 0.
        
    Verification:
        freq_to_wavelength(2.4e9) ≈ 0.1249 m (12.49 cm)
    """
```

---

### `wavelength_to_freq(wavelength_m: float) -> float`

```python
def wavelength_to_freq(wavelength_m: float) -> float:
    """Convert wavelength to frequency in Hz.
    
    Formula: f = c / λ
    
    Args:
        wavelength_m: Wavelength in meters.
        
    Returns:
        Frequency in Hz.
        
    Raises:
        ValueError: If wavelength_m <= 0.
    """
```

---

### `quarter_wave_antenna_length(freq_hz: float) -> float`

```python
def quarter_wave_antenna_length(freq_hz: float) -> float:
    """Calculate quarter-wave monopole antenna length.
    
    Formula: L = λ/4 = c / (4 * f)
    Includes velocity factor ≈ 0.95 for typical wire.
    
    Args:
        freq_hz: Frequency in Hz.
        
    Returns:
        Antenna length in meters.
        
    Raises:
        ValueError: If freq_hz <= 0.
    """
```

---

## Boundary Guards

All functions raise `ValueError` (never `ZeroDivisionError`) on invalid input:

```python
# These all raise ValueError:
uart_bit_timing(0, 115200, 16)
uart_bit_timing(16_000_000, 0, 16)
uart_bit_timing(-16_000_000, 115200, 16)
shannon_capacity(-1, 30)
nyquist_max_rate(20e6, 1)
nyquist_max_rate(20e6, 0)
freq_to_wavelength(0)
can_bit_timing(16e6, 0)
can_bit_timing(0, 500_000)
```

---

## Testing

`build_scripts/check_logic.py` runs comprehensive tests:

```python
def test_crc_check_values():
    assert crc16_ccitt_false(b"123456789") == 0x29B1
    assert crc16_modbus(b"123456789") == 0x4B37
    assert crc32_ieee(b"123456789") == 0xCBF43926

def test_formulas():
    assert abs(shannon_capacity(20e6, 30) - 20e6 * math.log2(1001)) < 1e-6
    assert nyquist_max_rate(3000, 2) == 6000
    assert abs(freq_to_wavelength(2.4e9) - 0.1249135) < 1e-6
    r = uart_bit_timing(16_000_000, 9600, 16)
    assert r["divisor"] == 104
    assert abs(r["error_pct"] - 0.16) < 0.01
    assert r["acceptable"] is True
    assert uart_bit_timing(16_000_000, 115200, 16)["acceptable"] is False
    ct = can_bit_timing(16e6, 500_000, 3, 3, 2)
    assert ct["total_tq"] == 9
    assert abs(ct["sample_point_pct"] - 700/9) < 1e-9
```

---

## See Also

- [Architecture: Verified Calculators](../architecture/adrs/0006-verified-calculators.md)
- [Science Lab Page](../getting-started/quickstart.md) — UI usage
- [Quiz Engine](quiz_engine.md) — Uses CRC for frame puzzles