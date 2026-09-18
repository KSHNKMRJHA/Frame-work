# -*- coding: utf-8 -*-
"""
build_data.py
Generates data/protocols.json — the master encyclopedia database for the
FrameWork.

Run:  python build_data.py
"""
import json
import os
from collections import Counter

P = []  # protocol list

def add(**kw):
    kw.setdefault("frame_fields", [])
    kw.setdefault("frame_note", "")       # caveats the bit-level diagram cannot show
    kw.setdefault("pins", [])
    kw.setdefault("related", [])
    kw.setdefault("fun_fact", "")
    kw.setdefault("fun_fact_source", "")  # required whenever fun_fact is set (see check_data.py)
    kw.setdefault("place", "")
    kw.setdefault("organization", "")
    kw.setdefault("year_milestone", "")   # invented | published | standardized | deployed
    kw.setdefault("difficulty", "Beginner")
    P.append(kw)

# =====================================================================
# CATEGORY 1: ON-BOARD / CHIP-TO-CHIP
# =====================================================================
add(id="uart", name="UART / USART", category="On-Board", topology="Point-to-Point",
    year=1960, inventor="Gordon Bell (concept popularized at DEC)", place="USA",
    organization="Digital Equipment Corporation (early adopters)",
    description="Universal Asynchronous Receiver/Transmitter — the oldest and simplest serial protocol, sending data one bit at a time without a shared clock.",
    how_it_works="Data framed with a Start bit (low), 5-9 data bits, optional parity bit, and 1-2 Stop bits (high). Both sides must agree on baud rate in advance since there is no clock line.",
    speed="1200 bps – 1 Mbps (up to ~7-12.5 Mbps on some modern MCUs)",
    pins=["TX", "RX", "GND", "(optional RTS/CTS)"],
    # Field widths are the ranges the framing actually allows, not one example
    # configuration: 8N1 (the most common setting) has no parity bit at all.
    frame_fields=[{"name":"Start","bits":1},{"name":"Data","bits":"5-9"},
                  {"name":"Parity (optional)","bits":"0-1"},{"name":"Stop","bits":"1-2"}],
    frame_note="Widths shown are the configurable ranges. A 1.5-bit stop length is also legal on some UARTs. The line idles high between frames; there is no explicit inter-frame delimiter field.",
    use_cases=["Debug console / serial monitor","GPS modules","Bluetooth serial modules (HC-05)","Bootloaders"],
    advantages=["Extremely simple, only 2 wires","No shared clock needed","Universally supported"],
    limitations=["No built-in multi-device addressing","Speed mismatch causes framing errors","Point-to-point only"],
    real_world_example="ESP32 talking to a PC over USB-to-serial for debug logs.",
    fun_fact="The term 'baud' is named after Émile Baudot, a French telegraph engineer (1870s), not a person named 'Baud'.",
    fun_fact_source="Baudot code / baud unit naming — IEEE and ITU historical references on the Baudot telegraph code.",
    difficulty="Beginner", related=["rs232","rs485","spi"])

add(id="rs232", name="RS-232 (TIA/EIA-232)", category="On-Board", topology="Point-to-Point",
    year=1960, year_milestone="published", inventor="Electronic Industries Association (EIA) engineering committee",
    place="USA", organization="EIA, later TIA/EIA (current revision TIA-232-F, 1997)",
    description="The electrical standard that put UART framing on a cable — single-ended voltage signalling that defined the serial port for four decades.",
    how_it_works="A UART's logic-level TX/RX lines are converted to bipolar single-ended voltages referenced to a common ground: a logic 1 ('mark') is -5 V to -15 V, a logic 0 ('space') is +5 V to +15 V. Receivers must accept ±3 V, so the wide swing buys noise margin. RS-232 defines only the electrical layer and connector — the bit framing is the UART's.",
    speed="Up to 20 kbps over 15 m per the standard; 115.2 kbps – 1 Mbps routinely achieved over short cables in practice",
    pins=["TXD","RXD","GND","RTS","CTS","DTR","DSR","DCD","RI"],
    use_cases=["Legacy PC serial ports and USB-to-serial adapters","Industrial equipment consoles","Router and switch management ports","Lab instruments and bench power supplies"],
    advantages=["Universally understood and supported after 60+ years","Only three wires needed for basic bidirectional traffic","No addressing or protocol stack to implement"],
    limitations=["Single-ended and ground-referenced, so it is far less noise-immune than RS-485","Point-to-point only — no multi-drop","Short cable runs","Requires a level-shifter (MAX232 and similar) between MCU logic and the cable"],
    real_world_example="A MAX3232 level shifter between an STM32's USART pins and a DB-9 console port on an industrial controller.",
    fun_fact="RS-232's inverted logic is a survival from teletype current loops: a 'mark' (idle) is the negative voltage, so an idle RS-232 line sits at -12 V rather than 0 V — which is why probing a quiet serial port with a meter reads negative, not zero.",
    fun_fact_source="TIA/EIA-232-F; the mark/space convention inherited from Baudot-era teleprinter signalling.",
    difficulty="Beginner", related=["uart","rs485","modbus_rtu"])

add(id="rs485", name="RS-485 / RS-422 (TIA/EIA-485, -422)", category="On-Board", topology="Multi-drop Bus",
    year=1983, year_milestone="published", inventor="Electronic Industries Association (EIA) engineering committee",
    place="USA", organization="TIA/EIA (current revisions TIA-485-A, TIA-422-B)",
    description="The differential physical layer underneath most industrial serial networks — the wiring that lets Modbus RTU, PROFIBUS DP and DMX512 run hundreds of metres through electrically hostile plants.",
    how_it_works="Data is carried as a voltage difference between two conductors (A and B) rather than against ground, so noise picked up equally on both wires cancels at the receiver. RS-422 is point-to-point with one driver; RS-485 adds tri-state drivers so up to 32 unit loads (more with modern low-load transceivers) can share one twisted pair, half-duplex, with 120 Ohm termination at both ends.",
    speed="10 Mbps at 12 m down to 100 kbps at 1200 m (the standard's length/speed trade-off); 9.6-115.2 kbps typical in industrial use",
    pins=["A (D+)","B (D-)","GND","(optional Y/Z second pair for 4-wire full duplex)"],
    use_cases=["Modbus RTU and PROFIBUS DP physical layer","Building automation and BACnet MS/TP","DMX512 stage lighting","Conveyor and material-handling sensor runs","Solar inverter and energy-meter networks"],
    advantages=["Differential signalling rejects common-mode noise, so it survives motor drives and long cable runs","Multi-drop: dozens of nodes on one pair","Up to 1200 m without repeaters","Cheap, ubiquitous transceivers (MAX485, SN65HVD series)"],
    limitations=["Half-duplex in the common 2-wire form — the application must manage turnaround timing","Needs correct termination and biasing or the idle state is undefined","No addressing, framing or arbitration of its own — a higher layer such as Modbus must supply them","Daisy-chain topology only; star wiring causes reflections"],
    real_world_example="A Modbus RTU master polling thirty VFDs over a single 800 m shielded twisted pair on an RS-485 bus in a conveyor hall.",
    fun_fact="RS-485 defines no protocol at all — only voltages, drivers and timing. Every RS-485 network you meet is really some other protocol (Modbus RTU, PROFIBUS DP, DMX512, BACnet MS/TP) borrowing the same wiring, which is why two RS-485 devices can be electrically compatible and still unable to exchange a single message.",
    fun_fact_source="TIA/EIA-485-A scope statement (electrical characteristics only); Modbus over Serial Line Specification and Implementation Guide V1.02, which specifies RS-485 as its recommended physical layer.",
    difficulty="Intermediate", related=["uart","rs232","modbus_rtu","profibus"])

add(id="spi", name="SPI (Serial Peripheral Interface)", category="On-Board", topology="Star (single master, multiple slaves via CS)",
    year=1979, inventor="Motorola engineers", place="USA", organization="Motorola",
    description="A synchronous, full-duplex, master-driven bus using a shared clock — one of the fastest simple on-board protocols.",
    how_it_works="Master generates SCLK; data shifts out on MOSI and in on MISO simultaneously (full duplex). Each slave has its own Chip-Select (CS) line to enable communication, so no addressing scheme is required.",
    speed="1 Mbps – 50 Mbps (up to ~135 Mbps on high-end MCUs)",
    pins=["SCLK","MOSI","MISO","CS/SS"],
    frame_fields=[],
    use_cases=["ADC/DAC","SD cards (SPI mode)","TFT/OLED displays","Flash memory (W25Q series)"],
    advantages=["Very high speed","Full duplex","Simple hardware shift-register implementation"],
    limitations=["Needs one CS line per slave (pin-hungry)","No built-in error checking/ACK","Short distance only"],
    real_world_example="STM32 driving an ILI9341 TFT display at 40+ MHz over SPI.",
    fun_fact="SPI has never been formally standardized by any standards body — there is no SPI equivalent of the I²C specification. Motorola did publish its own description (the MC68HC11 reference manual and application note AN991), but because no body owns the 'standard', vendors differ on clock polarity/phase conventions, chip-select behaviour and daisy-chaining.",
    fun_fact_source="Motorola application note AN991 'Using the Serial Peripheral Interface to Communicate Between Multiple Microcomputers'; MC68HC11 Reference Manual.",
    difficulty="Beginner", related=["qspi","i2c","microwire"])

add(id="qspi", name="QSPI / OctoSPI", category="On-Board", topology="Point-to-Point (wide bus)",
    year=1990, inventor="Motorola / later expanded by Cypress, ST", place="USA",
    description="Quad/Octo SPI extends classic SPI with 4 or 8 parallel data lines to dramatically increase throughput, mainly for external Flash/PSRAM.",
    how_it_works="Instead of single MOSI/MISO, 4 (Quad) or 8 (Octo) bidirectional data lines transfer nibbles/bytes per clock — often with DDR (dual data rate) support.",
    speed="50-133 MHz clock → 200+ Mbps effective data rate",
    pins=["CLK","CS","IO0-IO7"],
    use_cases=["External NOR flash for XIP (execute-in-place)","High-speed PSRAM"],
    advantages=["Much higher throughput than SPI","XIP capable — MCU can run code directly from external flash"],
    limitations=["More PCB routing/pins","More complex controller logic"],
    real_world_example="ESP32-S3 executing application code directly from external Octal PSRAM/Flash.",
    difficulty="Intermediate", related=["spi","sdio"])

add(id="i2c", name="I²C (Inter-Integrated Circuit)", category="On-Board", topology="Multi-drop Bus",
    year=1982, inventor="Philips Semiconductors (now NXP)", place="Netherlands", organization="Philips",
    description="A 2-wire multi-master, multi-slave bus originally designed to let TV chips inside a Philips television talk to each other cheaply.",
    how_it_works="SDA (data) and SCL (clock) lines, both open-drain with pull-up resistors. Each device has a 7-bit (or 10-bit) address. Master issues START, address+R/W bit, ACK/NACK handshaking, then data bytes, then STOP.",
    speed="100 kbps (Standard) – 3.4 Mbps (up to 5 Mbps Ultra-Fast mode)",
    pins=["SDA","SCL"],
    # START and STOP are bus *conditions* (an SDA transition while SCL is high),
    # not clocked bits — labelled as such so the diagram doesn't imply a 1-bit
    # field. The two acknowledgements are distinguished by name because
    # identical names make the frame-reorder puzzle unsolvable.
    frame_fields=[{"name":"START condition","bits":"—"},{"name":"Address","bits":7},
                  {"name":"R/W","bits":1},{"name":"ACK (address)","bits":1},
                  {"name":"Data","bits":8},{"name":"ACK/NACK (data)","bits":1},
                  {"name":"STOP condition","bits":"—"}],
    frame_note="18 clocked bits per address+data byte transfer. START/STOP are SDA transitions while SCL is high (NXP UM10204 §3.1.4), so they occupy no clock cycle.",
    use_cases=["EEPROM","RTC (DS3231)","IMUs/accelerometers (MPU6050)","Display controllers (SSD1306)"],
    advantages=["Only 2 wires for many devices","Built-in addressing & ACK","Multi-master capable"],
    limitations=["Slower than SPI","Bus capacitance limits length/speed","Address collisions between similar chips"],
    real_world_example="Raspberry Pi reading temperature from a BME280 sensor over I2C.",
    fun_fact="For years vendors shipped I²C-compatible peripherals under the name 'TWI' (Two-Wire Interface) to avoid Philips' licensing terms — Atmel's AVR datasheets are the best-known example. NXP dropped the I²C licence fee in 2006 and the trademark has since lapsed, so the name is now used freely.",
    fun_fact_source="NXP UM10204 I2C-bus specification and user manual (rev. 6, 2014) — licensing note; Atmel AVR datasheets' use of 'TWI'.",
    difficulty="Beginner", related=["smbus","i3c","spi"])

add(id="i3c", name="I3C (Improved Inter-Integrated Circuit)", category="On-Board", topology="Multi-drop Bus",
    year=2017, inventor="MIPI Alliance", place="USA", organization="MIPI Alliance",
    description="A modern successor to I2C designed to unify sensor buses with higher speed while staying largely pin-compatible.",
    how_it_works="Uses the same 2 wires as I2C but adds in-band interrupts, dynamic addressing, and a push-pull high-speed mode (HDR) alongside the legacy open-drain mode for backward compatibility.",
    speed="Up to 12.5 Mbps (SDR), higher in HDR modes",
    pins=["SDA","SCL"],
    use_cases=["Modern smartphone sensor hubs","Automotive sensor clusters"],
    advantages=["Backward compatible with I2C","In-band interrupts (no extra IRQ pin)","Dynamic addressing"],
    limitations=["Newer — ecosystem/tooling still maturing","More complex controller"],
    real_world_example="Mobile SoCs using I3C to connect multiple sensors with fewer interrupt pins.",
    difficulty="Advanced", related=["i2c"])

add(id="1wire", name="1-Wire", category="On-Board", topology="Bus",
    year=1990, inventor="Dallas Semiconductor (now Maxim/ADI)", place="USA",
    description="A minimalist bus that carries both power and data on a single wire, invented for low-cost ID and sensor chips.",
    how_it_works="Master and slaves communicate via precisely timed voltage pulses on one data line; devices can even be 'parasitically powered' from the line itself.",
    speed="~16 kbps (standard), 142 kbps (overdrive)",
    pins=["DQ (data)","GND","(optional VCC)"],
    use_cases=["DS18B20 temperature sensor","iButton ID tags"],
    advantages=["Single wire for data (+ optional power)","Unique 64-bit ROM ID per device — many devices on one wire"],
    limitations=["Very slow","Strict timing requirements","Complex master-side bit-banging"],
    real_world_example="DS18B20 waterproof temperature probes used in home automation.",
    difficulty="Intermediate", related=["i2c"])

add(id="microwire", name="Microwire", category="On-Board", topology="Point-to-Point",
    year=1980, inventor="National Semiconductor", place="USA",
    description="An early synchronous serial protocol, essentially a simplified predecessor/cousin to SPI, used in legacy EEPROMs and ADCs.",
    how_it_works="Master-only synchronous transfer with CS, SK (clock), SI, SO lines — very similar to SPI but historically not full-duplex in all implementations.",
    speed="~1-2 Mbps typical (legacy devices)",
    pins=["CS","SK","SI","SO"],
    use_cases=["Legacy serial EEPROMs (93Cxx series)"],
    advantages=["Simple, low pin count"],
    limitations=["Largely obsolete, replaced by SPI"],
    real_world_example="Old 93C46 EEPROMs in legacy consumer electronics.",
    difficulty="Beginner", related=["spi"])

add(id="smbus", name="SMBus (System Management Bus)", category="On-Board", topology="Multi-drop Bus",
    year=1995, inventor="Intel/Duracell consortium", place="USA", organization="Intel",
    description="A stricter subset of I2C defined for system/power management communication, notably in laptop batteries.",
    how_it_works="Electrically similar to I2C but with tighter timing/voltage specs, mandatory ACK timeout, and a defined command protocol layer (Packet Error Checking optional).",
    speed="10 kbps – 100 kbps",
    pins=["SMBDAT","SMBCLK"],
    use_cases=["Laptop/smart battery management","Power supply monitoring (PMBus is built on it)"],
    advantages=["Standardized command set","Timeout recovery avoids bus lock-ups"],
    limitations=["Slower than I2C max speeds","Stricter compliance needed"],
    real_world_example="Laptop 'smart battery' reporting charge % to the OS via SMBus.",
    difficulty="Intermediate", related=["i2c","pmbus"])

add(id="pmbus", name="PMBus", category="On-Board", topology="Multi-drop Bus",
    year=2005, inventor="System Management Interface Forum (SMIF)", place="USA",
    description="An open standard built atop SMBus/I2C specifically for digitally monitoring and configuring power supplies.",
    how_it_works="Uses SMBus electrical/protocol layer with a standardized command language for voltage, current, temperature telemetry and control of DC-DC converters.",
    speed="Up to 400 kbps (I2C Fast mode compatible)",
    pins=["SMBDAT","SMBCLK"],
    use_cases=["Digital power supplies","Server/telecom power modules"],
    advantages=["Standard command set across vendors","Enables digital power telemetry"],
    limitations=["Adds cost/complexity vs analog power control"],
    real_world_example="Data-center power modules reporting voltage/current to a BMC.",
    difficulty="Advanced", related=["smbus","i2c"])

add(id="mdio", name="MDIO (Management Data I/O)", category="On-Board", topology="Point-to-Point",
    year=1995, inventor="IEEE 802.3 working group", place="USA", organization="IEEE",
    description="A 2-wire serial bus used exclusively to configure and monitor Ethernet PHY chips from a MAC/MCU.",
    how_it_works="MDC (clock) + MDIO (data) let the MAC read/write PHY registers (e.g., link speed, autonegotiation status).",
    speed="Up to 2.5 MHz clock",
    pins=["MDC","MDIO"],
    use_cases=["Configuring Ethernet PHY chips (e.g., LAN8720)"],
    advantages=["Standardized across virtually all Ethernet PHYs"],
    limitations=["Only for PHY management, not for data transfer itself"],
    real_world_example="An STM32 with an RMII Ethernet MAC configuring a PHY via MDIO before enabling the link.",
    difficulty="Advanced", related=["ethernet"])

add(id="sdio", name="SDIO", category="On-Board", topology="Point-to-Point",
    year=2001, inventor="SD Association", place="Japan/USA", organization="SD Association",
    description="An extension of the SD card bus protocol allowing not just storage but also Wi-Fi/Bluetooth cards to plug into the same interface.",
    how_it_works="1 clock + 1 command line + up to 4 (or 8 in UHS-II) data lines, with a well-defined register/command set for both memory and I/O function cards.",
    speed="25 MB/s (High Speed), UHS-I: 104 MB/s, UHS-II: 312 MB/s",
    pins=["CLK","CMD","DAT0-DAT3"],
    use_cases=["SD memory cards","Wi-Fi/BT SDIO combo cards (e.g., older Raspberry Pi Wi-Fi modules)"],
    advantages=["High throughput","Standardized, widely supported by MCUs"],
    limitations=["More complex controller/driver stack than SPI-mode SD"],
    real_world_example="Raspberry Pi Compute Module using SDIO for its Wi-Fi chip.",
    difficulty="Advanced", related=["spi","emmc"])

add(id="emmc", name="eMMC", category="On-Board", topology="Point-to-Point",
    year=2006, inventor="JEDEC", place="USA", organization="JEDEC",
    description="Embedded MultiMediaCard — a managed NAND flash package with a built-in controller, soldered directly onto the board as primary storage.",
    how_it_works="Similar command/data bus structure to SD/SDIO, but the flash translation layer (wear leveling, bad-block management) is built into the eMMC chip itself.",
    speed="HS400: up to 400 MB/s",
    pins=["CLK","CMD","DAT0-DAT7","RST"],
    use_cases=["Embedded Linux boards (boot storage)","Set-top boxes","Automotive infotainment"],
    advantages=["Higher reliability than raw NAND (managed wear leveling)","Standardized JEDEC interface"],
    limitations=["Slower than modern UFS/NVMe","Limited write endurance vs enterprise storage"],
    real_world_example="A Raspberry Pi CM4 or Android set-top box booting Linux from onboard eMMC.",
    difficulty="Advanced", related=["sdio"])

add(id="parallel", name="Parallel Bus (Memory/LCD)", category="On-Board", topology="Point-to-Point (wide bus)",
    year=1970, inventor="General industry practice (early computing)", place="USA",
    description="The oldest interconnect style — many data/address/control lines run in parallel to transfer a full word every clock.",
    how_it_works="Address and data buses are driven directly, with control lines (WE, OE, CS) telling the memory/device when to latch or output data.",
    speed="10 MB/s – 100+ MB/s (depends on width & clock)",
    pins=["D0-D31","A0-A23","WE","OE","CS"],
    use_cases=["External SRAM","Character/graphic LCDs (8080/6800 interface)"],
    advantages=["Very high throughput per clock cycle","Simple, direct addressing"],
    limitations=["Huge pin count","Poor signal integrity at high speed/long traces"],
    real_world_example="Classic character LCDs (HD44780) using an 8/4-bit parallel interface.",
    difficulty="Intermediate", related=["lvds"])

# =====================================================================
# CATEGORY 2: INDUSTRIAL / FIELDBUS
# =====================================================================
add(id="modbus_rtu", name="Modbus RTU", category="Industrial", topology="Bus (Master-Slave, RS-485)",
    year=1979, inventor="Modicon (Schneider Electric)", place="USA", organization="Modicon",
    description="The oldest and most widely deployed industrial fieldbus protocol, originally created for PLCs, now a universal automation lingua franca.",
    how_it_works="Master polls slaves by numeric address over RS-485 (or RS-232). Data sent as compact binary frames with CRC-16 checksum; function codes define read/write of coils, registers, etc.",
    speed="1200 bps – 115.2 kbps (typical, over RS-485)",
    pins=["A (D+)","B (D-)","GND"],
    frame_fields=[{"name":"Address","bits":8},{"name":"Function Code","bits":8},{"name":"Data","bits":"n×8"},{"name":"CRC","bits":16}],
    use_cases=["PLC-to-sensor communication","SCADA systems","Building automation"],
    advantages=["Extremely simple and well documented","Huge existing device ecosystem","Royalty-free, open standard"],
    limitations=["Slow by modern standards","No native security/encryption","Master-slave only (no peer-to-peer)"],
    real_world_example="A PLC polling a bank of RS-485 temperature/humidity sensors on a factory floor.",
    fun_fact="Modbus was published by Modicon in 1979 and its specification has been royalty-free from the start — a large part of why it is still ubiquitous more than 45 years later. Schneider Electric transferred stewardship to the independent Modbus Organization in 2004.",
    fun_fact_source="Modbus Organization (modbus.org) — Modbus history and the royalty-free licensing terms; Modbus Application Protocol Specification V1.1b3.",
    difficulty="Beginner", related=["modbus_tcp","rs485"])

add(id="modbus_tcp", name="Modbus TCP", category="Industrial", topology="Star (Ethernet)",
    year=1999, inventor="Schneider Electric", place="France", organization="Schneider Electric",
    description="Modbus RTU's message structure carried over standard Ethernet/TCP-IP instead of RS-485, for modern networked automation.",
    how_it_works="Same function codes/data model as Modbus RTU, but wrapped in a TCP/IP packet on port 502 instead of a serial CRC frame.",
    speed="10/100/1000 Mbps (limited by Ethernet, not protocol)",
    pins=["Standard Ethernet (RJ45)"],
    use_cases=["SCADA over plant Ethernet","Remote I/O over LAN/WAN"],
    advantages=["Leverages existing Ethernet infrastructure","Easy to route/bridge with RTU via gateways"],
    limitations=["Not deterministic (no real-time guarantee like EtherCAT)","Needs a gateway to interoperate with legacy RTU devices"],
    real_world_example="A SCADA HMI polling remote terminal units (RTUs) at a water treatment plant over the plant LAN.",
    difficulty="Intermediate", related=["modbus_rtu","ethernet"])

add(id="profibus", name="Profibus", category="Industrial", topology="Bus (Token Passing)",
    year=1989, inventor="German government-funded consortium (BMBF)", place="Germany", organization="PI (Profibus & Profinet International)",
    description="A widely used European fieldbus standard for factory and process automation, predecessor to Profinet.",
    how_it_works="Token-passing among masters, each of which polls its assigned slaves; DP variant for fast I/O, PA variant for intrinsically-safe process instrumentation.",
    speed="9.6 kbps – 12 Mbps",
    pins=["A-Line","B-Line","GND (via 9-pin D-sub, RS-485 electrical layer)"],
    use_cases=["Factory automation (DP)","Process automation with hazardous areas (PA)"],
    advantages=["Deterministic token-passing","Mature, huge installed base in Europe"],
    limitations=["Being phased out in favor of Profinet (Ethernet-based)","Limited node count/segment length"],
    real_world_example="Siemens PLCs controlling distributed I/O racks via Profibus-DP in a bottling plant.",
    difficulty="Intermediate", related=["profinet","rs485"])

add(id="profinet", name="Profinet", category="Industrial", topology="Star/Ring (Ethernet)",
    year=2003, inventor="Siemens / PI consortium", place="Germany", organization="PI (Profibus & Profinet International)",
    description="The Ethernet-based successor to Profibus, providing real-time deterministic communication for modern automation.",
    how_it_works="Runs on standard Ethernet hardware but uses special real-time (RT) and isochronous real-time (IRT) frame prioritization to hit hard real-time deadlines.",
    speed="100 Mbps – 1 Gbps",
    pins=["Standard Ethernet (RJ45)"],
    use_cases=["High-speed motion control","Robotics","Distributed factory I/O"],
    advantages=["Real Ethernet speeds with real-time determinism","Backward-compatible engineering concepts from Profibus"],
    limitations=["Requires Profinet-aware switches for IRT","More complex than plain Modbus TCP"],
    real_world_example="Synchronizing multi-axis servo drives on a packaging line via Profinet IRT.",
    difficulty="Advanced", related=["profibus","ethercat","ethernet"])

add(id="ethercat", name="EtherCAT", category="Industrial", topology="Ring/Daisy-chain (Ethernet)",
    year=2003, inventor="Beckhoff Automation", place="Germany", organization="EtherCAT Technology Group",
    description="An ultra-fast, deterministic Ethernet-based fieldbus where frames are processed 'on the fly' by each slave as they pass through — no store-and-forward delay.",
    how_it_works="A single Ethernet frame travels through every slave device in a daisy chain; each slave reads/writes its assigned data segment within the frame at wire speed (processing-on-the-fly) before forwarding it.",
    speed="100 Mbps (with sub-microsecond jitter)",
    pins=["Standard Ethernet (RJ45)"],
    use_cases=["High-speed motion control","CNC machines","Robotics"],
    advantages=["Extremely low latency/jitter (sub-µs synchronization)","Uses standard, cheap Ethernet cabling/PHYs"],
    limitations=["Requires EtherCAT-specific slave controller ASICs/FPGAs","Master must be a real-time capable PC/PLC"],
    real_world_example="Coordinating dozens of servo axes on a CNC machine with microsecond-level synchronization.",
    fun_fact="EtherCAT's published benchmark is 1000 distributed digital I/O points across 100 nodes updated in 30 microseconds — achieved because each slave reads and writes its slice of the frame on the fly as it passes through, rather than receiving, processing and re-sending it.",
    fun_fact_source="EtherCAT Technology Group, 'EtherCAT — the Ethernet Fieldbus' performance figures (etherCAT.org).",
    difficulty="Advanced", related=["profinet","ethernet"])

add(id="ethernetip", name="EtherNet/IP", category="Industrial", topology="Star (Ethernet)",
    year=2000, inventor="Rockwell Automation / ODVA", place="USA", organization="ODVA",
    description="Ethernet Industrial Protocol — adapts the CIP (Common Industrial Protocol) used in DeviceNet/ControlNet onto standard Ethernet.",
    how_it_works="Wraps CIP messages in standard TCP/UDP/IP packets, allowing explicit (request/response) and implicit (real-time I/O) messaging.",
    speed="10/100/1000 Mbps",
    pins=["Standard Ethernet (RJ45)"],
    use_cases=["Allen-Bradley/Rockwell PLC ecosystems","North American factory automation"],
    advantages=["Common CIP object model shared with DeviceNet/ControlNet","Leverages standard Ethernet infrastructure"],
    limitations=["Less deterministic than EtherCAT/Profinet IRT without CIP Sync/Motion extensions"],
    real_world_example="Allen-Bradley ControlLogix PLC communicating with EtherNet/IP-enabled drives and I/O.",
    difficulty="Intermediate", related=["devicenet","ethernet"])

add(id="devicenet", name="DeviceNet", category="Industrial", topology="Bus (CAN-based)",
    year=1994, inventor="Allen-Bradley (Rockwell Automation)", place="USA", organization="ODVA",
    description="An industrial network built on the CAN physical/data-link layer, adding the CIP application layer for device-level automation.",
    how_it_works="Uses standard CAN bus arbitration/framing, with CIP defining how PLCs and devices (sensors, drives, I/O blocks) exchange structured data.",
    speed="125, 250, or 500 kbps",
    pins=["CAN_H","CAN_L","V+","V-"],
    use_cases=["Device-level factory floor networking (sensors, actuators)"],
    advantages=["Built on proven CAN electrical layer","Power + data on same cable"],
    limitations=["Lower speed than modern Ethernet fieldbuses","Being superseded by EtherNet/IP"],
    real_world_example="A conveyor system's photo-eye sensors and pneumatic valves networked via DeviceNet to a PLC.",
    difficulty="Intermediate", related=["can","ethernetip"])

add(id="canopen", name="CANopen", category="Industrial", topology="Bus (CAN-based)",
    year=1995, inventor="CAN in Automation (CiA) consortium", place="Germany", organization="CiA",
    description="A higher-layer protocol standard built on CAN, defining object dictionaries and communication profiles for industrial/embedded devices.",
    how_it_works="Defines Process Data Objects (PDOs) for real-time cyclic data and Service Data Objects (SDOs) for configuration, all addressed via a standardized Object Dictionary.",
    speed="10 kbps – 1 Mbps (standard CAN)",
    pins=["CAN_H","CAN_L"],
    use_cases=["Medical devices","Elevators","Building automation","Robotics"],
    advantages=["Standardized device profiles across vendors","Mature and well-supported tooling"],
    limitations=["Inherits classic CAN's ~1 Mbps ceiling and 8-byte payload"],
    real_world_example="Motor controllers and encoders in a robotic arm communicating via CANopen PDOs.",
    difficulty="Advanced", related=["can","can_fd"])

add(id="hart", name="HART", category="Industrial", topology="Point-to-Point / Multi-drop",
    year=1986, inventor="Rosemount (now Emerson)", place="USA", organization="FieldComm Group",
    description="Highway Addressable Remote Transducer — overlays a digital signal on top of the classic 4-20 mA analog current loop used in process instrumentation.",
    how_it_works="Uses Frequency Shift Keying (FSK, Bell 202 standard) at ±0.5 mA riding on the 4-20 mA loop, so legacy analog and new digital data coexist on the same two wires.",
    speed="1200 bps (FSK digital overlay)",
    pins=["Loop+","Loop- (2-wire 4-20mA loop)"],
    use_cases=["Process industry field transmitters (pressure, flow, temperature)"],
    advantages=["Backward compatible with existing 4-20mA analog infrastructure","Enables diagnostics/configuration without extra wiring"],
    limitations=["Digital data rate is very slow","Mainly used for configuration/diagnostics, not high-speed control"],
    real_world_example="A HART-enabled pressure transmitter in an oil refinery sending both a 4-20mA reading and digital diagnostics on the same 2 wires.",
    fun_fact="HART superimposes its digital data as a phase-continuous Bell 202 FSK tone whose average current is zero, so it rides on the 4-20 mA loop without shifting the analog reading — which is why a HART transmitter drops straight into an analog-only system that simply never notices the digital traffic.",
    fun_fact_source="FieldComm Group HART specification — 1200/2200 Hz Bell 202 FSK physical layer, phase-continuous zero-average modulation.",
    difficulty="Intermediate", related=["wirelesshart","modbus_rtu"])

add(id="wirelesshart", name="WirelessHART", category="Industrial", topology="Mesh",
    year=2007, inventor="HART Communication Foundation", place="USA", organization="FieldComm Group",
    description="A wireless mesh-networking extension of HART for process plants, based on IEEE 802.15.4 radios.",
    how_it_works="Devices form a self-organizing, self-healing mesh network using time-synchronized channel hopping for reliability in noisy industrial RF environments.",
    speed="250 kbps (802.15.4 PHY)",
    use_cases=["Wireless process monitoring where cabling is impractical"],
    advantages=["No wiring needed","Self-healing mesh improves reliability"],
    limitations=["Battery-powered nodes need power management","More complex network commissioning"],
    real_world_example="Wireless tank-level sensors across a large tank farm reporting via a WirelessHART mesh gateway.",
    difficulty="Advanced", related=["hart","zigbee"])

add(id="opcua", name="OPC UA", category="Industrial", topology="Client-Server (over Ethernet)",
    year=2006, inventor="OPC Foundation", place="USA/International", organization="OPC Foundation",
    description="Open Platform Communications Unified Architecture — a platform-independent, service-oriented standard for secure, semantic industrial data exchange.",
    how_it_works="Defines an information model (objects, types, methods) with built-in security (X.509 certificates, encryption) transported over TCP or HTTPS, independent of any specific fieldbus.",
    speed="Depends on underlying transport (typically Gigabit Ethernet)",
    use_cases=["Industry 4.0 / IIoT data integration","Machine-to-machine and machine-to-cloud data exchange"],
    advantages=["Built-in security and authentication","Platform/vendor independent semantic data model"],
    limitations=["Heavier protocol stack than classic fieldbuses","Not inherently real-time (needs OPC UA TSN extension for hard real time)"],
    real_world_example="A factory MES system pulling structured machine data from PLCs via OPC UA for a cloud analytics dashboard.",
    difficulty="Advanced", related=["mqtt","ethernet"])

add(id="bacnet", name="BACnet", category="Industrial", topology="Bus/Star (multiple physical layers)",
    year=1995, inventor="ASHRAE committee", place="USA", organization="ASHRAE",
    description="A protocol purpose-built for building automation — HVAC, lighting, fire, and access control systems.",
    how_it_works="Defines standardized 'objects' (e.g., Analog Input, Binary Output) that any BACnet device exposes, transportable over MS/TP (RS-485), Ethernet (BACnet/IP), or ARCNET.",
    speed="9.6 kbps–76.8 kbps (MS/TP) or 10/100 Mbps (BACnet/IP)",
    use_cases=["HVAC systems","Building lighting/access control"],
    advantages=["Vendor-neutral standard for building systems","Flexible across multiple physical media"],
    limitations=["Object model can be complex to engineer for large buildings"],
    real_world_example="A building management system controlling rooftop HVAC units via BACnet/IP across the corporate network.",
    difficulty="Intermediate", related=["modbus_tcp"])

add(id="dnp3", name="DNP3", category="Industrial", topology="Point-to-Point / Multi-drop / Ethernet",
    year=1993, inventor="Westronic (later DNP Users Group)", place="Canada/USA",
    description="Distributed Network Protocol 3 — widely used in electric utility SCADA systems, especially in North America.",
    how_it_works="Layered protocol with robust error-checking (CRC per block) and unsolicited event reporting, transportable over serial or TCP/IP (DNP3 over IP).",
    speed="300 bps – 19.2 kbps (serial), or Ethernet speeds over IP",
    use_cases=["Electric utility substations","Water/wastewater SCADA"],
    advantages=["Very robust against noisy long-distance serial links","Time-stamped event reporting built in"],
    limitations=["Steeper learning curve than Modbus","Security add-ons (Secure Authentication) needed for modern cyber requirements"],
    real_world_example="A utility control center polling remote substation RTUs via DNP3 for breaker status and metering data.",
    difficulty="Advanced", related=["modbus_tcp"])

add(id="lonworks", name="LonWorks / LonTalk", category="Industrial", topology="Bus/Star/Free-topology",
    year=1990, inventor="Echelon Corporation", place="USA", organization="Echelon Corporation",
    description="A control networking platform built around the Neuron Chip, widely used in building automation and once in industrial material-handling systems.",
    how_it_works="The LonTalk protocol runs on the Neuron processor and communicates over Free Topology (FT) twisted pair, power line, or fiber, using network variables to share data between devices without central master polling.",
    speed="1.25 Mbps (backbone) / 78 kbps (FT-10, most common twisted-pair mode)",
    pins=["Net A","Net B (twisted pair, polarity-insensitive in FT mode)"],
    use_cases=["Building automation (HVAC, lighting)","Legacy material handling/conveyor control systems"],
    advantages=["Peer-to-peer, no central master required","Free topology wiring — polarity insensitive, flexible layout"],
    limitations=["Neuron Chip is largely obsolete/EOL, driving replacement projects","Lower speed vs modern Ethernet-based fieldbuses"],
    real_world_example="Legacy Vanderlande-style conveyor/sortation control nodes communicating over FT-10 LonWorks, now being replaced with MCU/FPGA-based transceiver solutions.",
    fun_fact="LonTalk was standardised as ANSI/CEA-709.1 in 1999 and later as ISO/IEC 14908-1, making building automation one of the first domains to get a formal open control-networking standard — two decades before comparable IoT standards such as Matter.",
    fun_fact_source="ANSI/CEA-709.1-B; ISO/IEC 14908-1:2012 (Open Data Communication in Building Automation).",
    difficulty="Advanced", related=["can","modbus_rtu"])

add(id="mbus", name="M-Bus (Meter-Bus)", category="Industrial", topology="Bus",
    year=1990, inventor="University of Paderborn / Techem", place="Germany",
    description="A European standard specifically designed for remote reading of utility meters (heat, water, gas, electricity).",
    how_it_works="Master unit powers and polls slave meters over a simple 2-wire bus; a Wireless M-Bus variant also exists using sub-GHz radio.",
    speed="300 bps – 9600 bps (wired)",
    use_cases=["Utility meter reading (heat/water/gas meters)"],
    advantages=["Low-cost, purpose-built for metering","Bus itself can power very low-power slaves"],
    limitations=["Low bandwidth, meter-reading use case only"],
    real_world_example="A building's heat cost allocators being read centrally via wired M-Bus.",
    difficulty="Intermediate", related=["modbus_rtu"])

add(id="foundation_fieldbus", name="Foundation Fieldbus (FF)", category="Industrial", topology="Bus",
    year=1996, inventor="Fieldbus Foundation (merger of ISP and WorldFIP)", place="USA",
    description="A digital fieldbus for process automation providing both device communication and distributed control-in-the-field capability.",
    how_it_works="H1 (31.25 kbps) segment connects field instruments on twisted pair, often intrinsically safe; devices execute function blocks (PID etc.) enabling control loops to run in the field itself.",
    speed="31.25 kbps (H1) / 100 Mbps (HSE — High Speed Ethernet)",
    use_cases=["Oil & gas, chemical, and refining process control"],
    advantages=["Control-in-the-field reduces reliance on central controller","Intrinsically safe options for hazardous areas"],
    limitations=["Complex commissioning/engineering","Being challenged by OPC UA/Ethernet-APL adoption"],
    real_world_example="Refinery pressure and flow transmitters executing PID control blocks directly on the FF H1 segment.",
    difficulty="Advanced", related=["hart","profibus"])

add(id="powerlink", name="Ethernet POWERLINK", category="Industrial", topology="Ring/Daisy-chain (Ethernet)",
    year=2001, inventor="B&R Industrial Automation", place="Austria", organization="Ethernet POWERLINK Standardization Group (EPSG)",
    description="An open, real-time Ethernet protocol using a 'Slot Communication Network Management' (SCNM) mechanism to guarantee determinism on standard Ethernet.",
    how_it_works="A Managing Node polls Controlled Nodes in time-sliced cycles, avoiding Ethernet collisions entirely to guarantee hard real-time delivery.",
    speed="100 Mbps",
    use_cases=["Motion control","Packaging machinery"],
    advantages=["Hard real-time on standard, unmodified Ethernet hardware","Open protocol (royalty free)"],
    limitations=["Smaller install base than EtherCAT/Profinet"],
    real_world_example="Synchronizing servo motors in a printing press using POWERLINK's cyclic real-time frames.",
    difficulty="Advanced", related=["ethercat","profinet"])

add(id="sercos", name="Sercos III", category="Industrial", topology="Ring (Ethernet)",
    year=2005, inventor="Sercos International consortium", place="Germany",
    description="A deterministic real-time Ethernet protocol especially popular for motion control applications requiring extremely tight synchronization.",
    how_it_works="Combines real-time (IP20) cyclic data with standard IP-based communication in the same Ethernet frame, using a ring topology for redundancy.",
    speed="100 Mbps – 1 Gbps",
    use_cases=["High-precision multi-axis motion control"],
    advantages=["Ring redundancy (single cable break tolerant)","Deterministic sub-microsecond jitter"],
    limitations=["Niche compared to EtherCAT/Profinet in general automation"],
    real_world_example="Multi-axis CNC and robotics requiring synchronized servo drive updates every 31.25 µs.",
    difficulty="Advanced", related=["ethercat","profinet"])

# =====================================================================
# CATEGORY 3: AUTOMOTIVE
# =====================================================================
add(id="can", name="CAN (Controller Area Network)", category="Automotive", topology="Bus (Multi-master, differential)",
    year=1983, inventor="Robert Bosch GmbH (Uwe Kiencke lead engineer)", place="Germany", organization="Bosch",
    description="The protocol that revolutionized automotive electronics by letting dozens of ECUs share just 2 wires instead of massive wiring harnesses. Publicly released in 1986.",
    how_it_works="Differential signaling on CAN_H/CAN_L; nodes arbitrate for the bus using non-destructive bitwise arbitration based on message ID priority — lowest ID (dominant bits) wins without collision.",
    speed="125 kbps – 1 Mbps (Classic CAN)",
    pins=["CAN_H","CAN_L"],
    # Standard (11-bit identifier) data frame per Bosch CAN 2.0A, 108 bits total
    # before stuffing. The CRC *field* is 16 bits: a 15-bit sequence plus a
    # 1-bit recessive delimiter, which the previous 15-bit entry omitted.
    frame_fields=[{"name":"SOF","bits":1},{"name":"ID","bits":11},{"name":"RTR","bits":1},
                  {"name":"Control (IDE, r0, DLC)","bits":6},{"name":"Data","bits":"0-64"},
                  {"name":"CRC sequence","bits":15},{"name":"CRC delimiter","bits":1},
                  {"name":"ACK (slot + delimiter)","bits":2},{"name":"EOF","bits":7}],
    frame_note="108 bits total for a standard data frame with a full 8-byte payload, before bit stuffing. The data field is 0-64 bits in 8-bit steps, not a continuous range. A 3-bit intermission and bus-idle period follow EOF but are interframe space, not frame fields.",
    use_cases=["Engine/body/chassis ECU communication","Industrial machine control (via CANopen/DeviceNet)"],
    advantages=["Highly robust against electrical noise (differential)","Priority-based arbitration — no data loss on collision","Mature, decades of tooling"],
    limitations=["Max 8 bytes payload per frame (Classic CAN)","1 Mbps speed ceiling"],
    real_world_example="A car's ABS module broadcasting wheel-speed data at high priority to the engine and stability-control ECUs simultaneously.",
    fun_fact="Bosch created CAN because 1980s luxury cars had wiring harnesses so heavy and complex they were becoming a manufacturing and reliability nightmare.",
    fun_fact_source="Bosch / CAN in Automation (CiA) history of CAN — motivation for the 1983 development project.",
    difficulty="Intermediate", related=["can_fd","lin","canopen"])

add(id="can_fd", name="CAN FD (Flexible Data-rate)", category="Automotive", topology="Bus (differential)",
    year=2012, inventor="Robert Bosch GmbH", place="Germany", organization="Bosch",
    description="An evolution of Classic CAN allowing larger payloads and higher speed for the data phase, addressing bandwidth demands of modern vehicles.",
    how_it_works="Arbitration phase runs at classic CAN speed for compatibility, then the protocol switches to a faster bit rate for the data phase, and payload increases from 8 to up to 64 bytes.",
    speed="Up to 8 Mbps (data phase); 64-byte payload",
    pins=["CAN_H","CAN_L"],
    use_cases=["ADAS sensor data","Modern powertrain ECU networks"],
    advantages=["5-8x higher effective throughput than Classic CAN","Backward compatible arbitration"],
    limitations=["Requires CAN FD-capable transceivers/controllers throughout the bus"],
    real_world_example="Modern EVs using CAN FD to move higher-resolution battery management data between BMS and VCU.",
    difficulty="Intermediate", related=["can"])

add(id="lin", name="LIN (Local Interconnect Network)", category="Automotive", topology="Bus (Single-master, UART-based)",
    year=1998, inventor="LIN Consortium (Volvo, BMW, VW, Audi, Motorola, etc.)", place="Europe",
    description="A low-cost, single-wire complement to CAN for simple, non-critical automotive subsystems.",
    how_it_works="Single master polls slaves round-robin using standard UART framing over one wire, avoiding the cost of a full CAN transceiver for simple devices.",
    speed="Up to 20 kbps",
    pins=["LIN (single wire)","GND"],
    use_cases=["Power windows","Seat control","Mirror adjustment","Climate control actuators"],
    advantages=["Very low cost — single wire, no dedicated CAN transceiver","Simple master-slave scheduling"],
    limitations=["Low speed — not suitable for safety-critical/high-bandwidth data"],
    real_world_example="A car door module using LIN to control the window motor and mirror actuators cheaply.",
    difficulty="Beginner", related=["can","uart"])

add(id="flexray", name="FlexRay", category="Automotive", topology="Bus/Star (dual-channel)",
    year=2000, inventor="FlexRay Consortium (BMW, Daimler, Bosch, Philips, etc.)", place="Germany",
    description="A high-speed, deterministic, fault-tolerant protocol designed for safety-critical, X-by-wire automotive systems.",
    how_it_works="Combines a static time-division segment (guaranteed bandwidth slots) with a dynamic segment (event-driven), often over redundant dual channels for fault tolerance.",
    speed="Up to 10 Mbps per channel",
    use_cases=["Steer-by-wire, brake-by-wire systems","Advanced chassis/suspension control"],
    advantages=["Deterministic timing (TDMA)","Dual-channel redundancy for safety-critical systems"],
    limitations=["Complex, costly compared to CAN","Largely being overtaken by Automotive Ethernet + CAN FD in new designs"],
    real_world_example="Active suspension and steer-by-wire systems in premium vehicles requiring guaranteed timing.",
    difficulty="Advanced", related=["can","automotive_ethernet"])

add(id="most", name="MOST (Media Oriented Systems Transport)", category="Automotive", topology="Ring",
    year=1998, inventor="MOST Cooperation (BMW, Daimler, Harman et al.)", place="Germany",
    description="A ring-topology multimedia network designed to carry audio, video, and data for automotive infotainment systems.",
    how_it_works="Devices are connected in a ring (electrical or optical/fiber) with synchronous, isochronous, and asynchronous channels multiplexed for audio/video streaming plus control data.",
    speed="25/50/150 Mbps (MOST25/50/150)",
    use_cases=["Infotainment head units","Amplifiers, displays, navigation systems in-car"],
    advantages=["Guaranteed bandwidth for real-time audio/video streaming","Optical fiber variant immune to EMI"],
    limitations=["Being displaced by Automotive Ethernet with AVB/TSN"],
    real_world_example="A luxury car's infotainment system streaming synchronized audio to multiple amplifiers over a MOST fiber ring.",
    difficulty="Advanced", related=["automotive_ethernet"])

add(id="automotive_ethernet", name="Automotive Ethernet (BroadR-Reach/100/1000BASE-T1)", category="Automotive", topology="Star/Point-to-point",
    year=2011, inventor="Broadcom (BroadR-Reach), standardized by IEEE", place="USA", organization="IEEE 802.3",
    description="A single-twisted-pair variant of Ethernet engineered to survive the automotive environment (EMI, weight, cost) while delivering high bandwidth.",
    how_it_works="Uses a single unshielded twisted pair (vs 4 pairs in standard Ethernet) with PAM-3 encoding for full-duplex transmission, standardized by IEEE as 100BASE-T1/1000BASE-T1.",
    speed="100 Mbps – 1+ Gbps (multi-Gbps variants emerging)",
    use_cases=["ADAS camera/radar/lidar data backbones","Zonal E/E architectures", "Software-defined vehicles"],
    advantages=["Single twisted pair — lighter, cheaper harness than classic Ethernet","High bandwidth for ADAS/autonomous driving sensor fusion"],
    limitations=["Requires automotive-qualified PHYs (temperature, EMI)"],
    real_world_example="A modern ADAS system streaming camera and lidar point-cloud data over 1000BASE-T1 to a central compute unit.",
    difficulty="Advanced", related=["flexray","ethernet"])

add(id="sent", name="SENT (Single Edge Nibble Transmission)", category="Automotive", topology="Point-to-Point",
    year=2008, inventor="SAE International (J2716)", place="USA", organization="SAE",
    description="A simple unidirectional protocol for transmitting sensor data (like pressure/position) from a sensor directly to an ECU without a full CAN transceiver.",
    how_it_works="Sensor encodes data as a series of pulse-width-modulated 'nibbles' (4-bit values) defined by the time between falling edges — no clock line needed.",
    speed="Effective data rate ~out a few kbps (edge-timed nibbles)",
    pins=["SENT (single wire)","GND","VCC"],
    use_cases=["Automotive pressure/position/angle sensors (e.g., throttle position)"],
    advantages=["Very low pin count, low cost for point sensors","Better noise immunity than plain analog voltage output"],
    limitations=["Unidirectional (sensor to ECU only)","Short-range, point-to-point only"],
    real_world_example="A throttle position sensor reporting angle to the engine ECU via SENT instead of a noisy analog voltage.",
    difficulty="Intermediate", related=["psi5"])

add(id="psi5", name="PSI5", category="Automotive", topology="Point-to-Point / Bus",
    year=2000, inventor="Bosch, Continental and partners", place="Germany",
    description="Peripheral Sensor Interface 5 — a standard for connecting automotive sensors like airbag accelerometers to a central ECU.",
    how_it_works="Current-modulated digital communication over a 2-wire current loop, supporting synchronous (safety-critical, time-triggered) or asynchronous modes.",
    speed="125/189 kbps",
    use_cases=["Airbag/crash sensors","Chassis sensors"],
    advantages=["Deterministic, safety-oriented synchronous mode","Current-loop robust to noise"],
    limitations=["Automotive-specific niche use"],
    real_world_example="Peripheral crash sensors around a car's body reporting to the central airbag control unit via PSI5.",
    difficulty="Advanced", related=["sent","can"])

add(id="kline", name="K-Line (ISO 9141/ISO 14230)", category="Automotive", topology="Point-to-Point / Bus",
    year=1989, inventor="ISO working groups", place="International", organization="ISO",
    description="A single-wire diagnostic communication protocol used in pre-CAN-diagnostic-era vehicles and still present for legacy OBD-II diagnostics.",
    how_it_works="UART-like framing over a single bidirectional wire, with a specific slow-init handshake sequence (5-baud init) to wake up the ECU for diagnostics.",
    speed="10.4 kbps typical",
    pins=["K-line","(optional L-line)"],
    use_cases=["Legacy OBD-II diagnostics"],
    advantages=["Simple single-wire diagnostic access","Still supported for backward compatibility in OBD-II"],
    limitations=["Slow, being replaced entirely by CAN/DoIP for diagnostics"],
    real_world_example="An older (pre-2008) vehicle's OBD-II port using K-Line for scan-tool diagnostics.",
    difficulty="Intermediate", related=["can","uds"])

add(id="uds", name="UDS (Unified Diagnostic Services)", category="Automotive", topology="Point-to-Point (over CAN/Ethernet)",
    year=2006, inventor="ISO (ISO 14229)", place="International", organization="ISO",
    description="A standardized application-layer diagnostic protocol used across virtually all modern vehicle ECUs, riding on top of CAN or DoIP.",
    how_it_works="Defines standardized services (e.g., ReadDataByIdentifier, ECU Reset, Flash Programming) using a request/response model over the underlying transport (CAN-TP or DoIP).",
    speed="Depends on underlying transport (CAN 1Mbps / CAN FD 8Mbps / Ethernet)",
    use_cases=["ECU flashing/reprogramming","Fault code reading (DTCs)","Live sensor data streaming for diagnostics"],
    advantages=["Standardized across OEMs/tools","Rich service set (security access, routine control, flashing)"],
    limitations=["Requires transport-layer segmentation (CAN-TP) for messages >8 bytes"],
    real_world_example="A dealership scan tool reading fault codes and reflashing an ECU using UDS over CAN.",
    difficulty="Advanced", related=["can","doip","kline"])

add(id="doip", name="DoIP (Diagnostics over IP)", category="Automotive", topology="Star (Ethernet)",
    year=2012, inventor="ISO (ISO 13400)", place="International", organization="ISO",
    description="Carries UDS diagnostic messages over Ethernet/IP instead of CAN, enabling much faster ECU flashing in modern vehicles.",
    how_it_works="Wraps UDS diagnostic service messages in a DoIP header/payload over TCP/UDP, using vehicle discovery (vehicle announcement/identification) over the car's Ethernet backbone.",
    speed="100 Mbps – 1 Gbps (Ethernet)",
    use_cases=["Fast ECU reprogramming/flashing in production and service"],
    advantages=["Dramatically faster flashing than CAN-based UDS","Leverages in-vehicle Ethernet backbone"],
    limitations=["Requires Ethernet-equipped ECUs/gateway"],
    real_world_example="A modern EV getting a multi-gigabyte software update flashed in minutes via DoIP instead of hours over CAN.",
    difficulty="Advanced", related=["uds","automotive_ethernet"])

add(id="j1939", name="SAE J1939", category="Automotive", topology="Bus (CAN-based)",
    year=1994, inventor="SAE International", place="USA", organization="SAE",
    description="A CAN-based application-layer protocol standard for heavy-duty vehicles — trucks, buses, agricultural and construction equipment.",
    how_it_works="Uses 29-bit extended CAN IDs structured as Parameter Group Numbers (PGNs) that standardize exactly what each message represents (e.g., engine RPM, coolant temp).",
    speed="250 kbps / 500 kbps (Classic CAN electrical layer)",
    use_cases=["Heavy trucks, buses, tractors, construction equipment networking"],
    advantages=["Standardized PGNs mean cross-vendor interoperability","Robust CAN physical layer"],
    limitations=["Inherits Classic CAN's 8-byte/1Mbps ceiling (unless using J1939-based CAN FD extensions)"],
    real_world_example="A semi-truck's engine, transmission, and brake ECUs sharing standardized J1939 PGNs like engine speed and fuel rate.",
    difficulty="Intermediate", related=["can","obd2"])

add(id="obd2", name="OBD-II", category="Automotive", topology="Bus (multiple physical layers)",
    year=1996, inventor="SAE / EPA mandate", place="USA", organization="SAE",
    description="On-Board Diagnostics II — the legally mandated diagnostic connector/protocol suite for emissions and general diagnostics on all US cars since 1996.",
    how_it_works="Standardizes the physical 16-pin connector and a set of diagnostic modes (Mode 01-0A) for reading live data and fault codes, over any of several underlying protocols (CAN, K-Line, J1850).",
    speed="Depends on underlying protocol (typically CAN 500kbps today)",
    use_cases=["Emissions testing","Aftermarket scan tools/dongles","Fleet telematics"],
    advantages=["Universal, legally mandated connector across all modern vehicles","Simple standardized PIDs for common data (RPM, speed, etc.)"],
    limitations=["Limited to a fixed diagnostic mode set — manufacturer-specific data needs UDS"],
    real_world_example="A consumer Bluetooth OBD-II dongle reading live RPM/speed data into a smartphone app.",
    difficulty="Beginner", related=["j1939","can","kline"])

# =====================================================================
# CATEGORY 4: NETWORKING / ETHERNET / INTERNET STACK
# =====================================================================
add(id="ethernet", name="Ethernet", category="Networking", topology="Star/Bus (switched)",
    year=1973, inventor="Robert Metcalfe & David Boggs", place="USA", organization="Xerox PARC",
    description="The foundational LAN technology, invented at Xerox PARC to network the first personal computers and laser printers.",
    how_it_works="Data is packaged into frames with MAC source/destination addresses; original coax/CSMA-CD has been replaced by switched twisted-pair/fiber with full-duplex operation.",
    speed="10 Mbps – 1 Gbps (up to 10+ Gbps industrial/datacenter)",
    pins=["TX+","TX-","RX+","RX-"],
    # The Start-of-Frame Delimiter is the field that actually marks frame start
    # and was missing; with it the total is 12208 bits per IEEE 802.3, not 12200.
    frame_fields=[{"name":"Preamble","bits":56},{"name":"SFD","bits":8},
                  {"name":"Dest MAC","bits":48},{"name":"Src MAC","bits":48},
                  {"name":"Length/Type","bits":16},{"name":"Payload","bits":"368-12000"},
                  {"name":"FCS","bits":32}],
    frame_note="12208 bits maximum for a standard (non-jumbo) frame. IEEE 802.3 calls the third field Length/Type: values ≤1500 are a length, ≥1536 an EtherType. A 96-bit interpacket gap separates frames but is not part of the frame.",
    use_cases=["LANs","Industrial Ethernet fieldbuses (Profinet, EtherCAT)","Home/office networking"],
    advantages=["Massive ecosystem, cheap hardware","Scalable from 10 Mbps to 100+ Gbps"],
    limitations=["Not inherently deterministic (needs TSN for real-time guarantees)"],
    real_world_example="Literally the network connecting your laptop to your office's internet gateway.",
    fun_fact="Metcalfe's original 1973 memo describing Ethernet used the 'ether' of physics as a metaphor for the shared coaxial cable medium.",
    fun_fact_source="Robert Metcalfe's 22 May 1973 Xerox PARC memo 'Alto Ethernet'; Metcalfe & Boggs, 'Ethernet: Distributed Packet Switching for Local Computer Networks', CACM 19(7), 1976.",
    difficulty="Beginner", related=["tcp","udp","modbus_tcp"])

add(id="tcp", name="TCP (Transmission Control Protocol)", category="Networking", topology="Point-to-Point (logical, over IP)",
    year=1974, inventor="Vint Cerf & Bob Kahn", place="USA", organization="DARPA",
    description="The reliable, connection-oriented transport protocol underlying most of the internet — guarantees ordered, error-checked delivery.",
    how_it_works="Establishes a connection via a 3-way handshake (SYN, SYN-ACK, ACK), then uses sequence numbers, acknowledgments, and retransmission to guarantee reliable, in-order delivery.",
    speed="Limited by underlying network (Ethernet/Wi-Fi/cellular)",
    # Full RFC 9293 header. The previous entry listed only 6 fields totalling
    # 121 bits, which is not even byte-aligned and so cannot exist on the wire;
    # Data Offset, Reserved, Checksum, Urgent Pointer and Options were missing.
    # Flags is 8 bits, not 9 — the 9th bit (the RFC 3540 ECN-nonce) was
    # reclassified as Reserved.
    frame_fields=[{"name":"Src Port","bits":16},{"name":"Dst Port","bits":16},
                  {"name":"Seq Num","bits":32},{"name":"Ack Num","bits":32},
                  {"name":"Data Offset","bits":4},{"name":"Reserved","bits":4},
                  {"name":"Flags","bits":8},{"name":"Window","bits":16},
                  {"name":"Checksum","bits":16},{"name":"Urgent Pointer","bits":16},
                  {"name":"Options + Padding","bits":"0-320"}],
    frame_note="160 bits (20 bytes) minimum, 480 bits (60 bytes) maximum. Data Offset gives the header length in 32-bit words, so the header is always word-aligned.",
    use_cases=["Web browsing (HTTP/HTTPS)","File transfer","Any application needing guaranteed delivery"],
    advantages=["Reliable, ordered, error-checked delivery","Congestion control avoids network collapse"],
    limitations=["Higher latency/overhead than UDP due to handshakes and acknowledgments"],
    real_world_example="Every time your browser loads a webpage, it opens a TCP connection to the server first.",
    difficulty="Intermediate", related=["udp","ethernet","ip"])

add(id="udp", name="UDP (User Datagram Protocol)", category="Networking", topology="Point-to-Point (logical, over IP)",
    year=1980, inventor="David P. Reed", place="USA", organization="Network Working Group (RFC 768, 1980 — predates the IETF, first convened Jan 1986)",
    description="A minimal, connectionless transport protocol that trades reliability for speed and low overhead.",
    how_it_works="Simply sends datagrams with source/destination ports and a checksum — no handshake, no guaranteed delivery or ordering.",
    speed="Limited by underlying network",
    frame_fields=[{"name":"Src Port","bits":16},{"name":"Dst Port","bits":16},
                  {"name":"Length","bits":16},{"name":"Checksum","bits":16}],
    frame_note="64 bits (8 bytes) fixed, per RFC 768. Length counts the header plus data, so its minimum legal value is 8.",
    use_cases=["Live video/audio streaming","Online gaming","DNS queries","MQTT-SN/CoAP IoT messaging"],
    advantages=["Very low latency/overhead","No connection setup needed"],
    limitations=["No guaranteed delivery or ordering — app must handle loss"],
    real_world_example="A video call app using UDP so a dropped frame doesn't stall the whole call waiting for retransmission.",
    difficulty="Beginner", related=["tcp","mqtt","coap"])

add(id="ip", name="IP (Internet Protocol, v4/v6)", category="Networking", topology="Mesh/Global",
    year=1981, inventor="Vint Cerf & Bob Kahn (IPv4, RFC 791)", place="USA", organization="Network Working Group / DARPA (RFC 791, 1981 — predates the IETF)",
    description="The addressing and routing backbone of the entire internet, letting packets find their way across interconnected networks.",
    how_it_works="Each packet carries source/destination IP addresses; routers forward packets hop-by-hop based on routing tables toward the destination network.",
    use_cases=["Literally every internet-connected device"],
    advantages=["Globally scalable addressing and routing","IPv6 vastly expands address space vs IPv4's 4.3 billion limit"],
    limitations=["IPv4 address exhaustion drove the slow, ongoing transition to IPv6"],
    real_world_example="Your phone's IP address routing traffic through your ISP to reach a website's server anywhere in the world.",
    difficulty="Intermediate", related=["tcp","udp","dns"])

add(id="arp", name="ARP (Address Resolution Protocol)", category="Networking", topology="Bus (LAN broadcast)",
    year=1982, inventor="David C. Plummer", place="USA", organization="Network Working Group (RFC 826, 1982 — predates the IETF)",
    description="Resolves an IP address to a physical MAC address on a local network segment.",
    how_it_works="A device broadcasts 'who has IP X?' and the owning device replies with its MAC address, which gets cached in an ARP table.",
    use_cases=["Every Ethernet/Wi-Fi LAN needs it to actually deliver frames"],
    advantages=["Simple, essential glue between IP and Ethernet layers"],
    limitations=["No authentication — vulnerable to ARP spoofing/poisoning attacks"],
    real_world_example="Your laptop broadcasting an ARP request to find your router's MAC address before sending any traffic.",
    difficulty="Intermediate", related=["ethernet","ip"])

add(id="dhcp", name="DHCP", category="Networking", topology="Client-Server",
    year=1993, inventor="Ralph Droms / IETF", place="USA", organization="IETF (RFC 1531, 1993; current spec RFC 2131, 1997)",
    description="Automatically assigns IP addresses and network configuration to devices joining a network.",
    how_it_works="DORA process: client broadcasts Discover, server responds Offer, client sends Request, server confirms with Ack.",
    use_cases=["Automatic IP assignment on home/office/industrial networks"],
    advantages=["No manual IP configuration needed for every device"],
    limitations=["Rogue DHCP servers can hijack network configuration if not secured"],
    real_world_example="Your phone automatically getting an IP address the moment it joins a Wi-Fi network.",
    difficulty="Beginner", related=["ip","ethernet"])

add(id="dns", name="DNS", category="Networking", topology="Client-Server (hierarchical)",
    year=1983, inventor="Paul Mockapetris", place="USA", organization="USC Information Sciences Institute (RFC 882/883, 1983; superseded by RFC 1034/1035, 1987)",
    description="The internet's 'phone book' — translates human-readable domain names into IP addresses.",
    how_it_works="Hierarchical, distributed lookup: root servers → TLD servers → authoritative servers resolve a name to its IP through recursive/iterative queries.",
    use_cases=["Every time you type a website address instead of an IP"],
    advantages=["Human-friendly naming for machine-addressed networks","Distributed and highly scalable"],
    limitations=["Vulnerable to spoofing/cache poisoning without DNSSEC"],
    real_world_example="Typing 'github.com' and DNS resolving it to the actual server IP behind the scenes.",
    difficulty="Beginner", related=["ip","tcp","udp"])

add(id="icmp", name="ICMP", category="Networking", topology="Point-to-point (over IP)",
    year=1981, inventor="Jon Postel", place="USA", organization="Network Working Group / USC ISI (RFC 792, 1981 — predates the IETF)",
    description="Used for network diagnostics and error reporting — the protocol behind the familiar 'ping' command.",
    how_it_works="Routers/hosts send ICMP messages (Echo Request/Reply, Destination Unreachable, Time Exceeded) to report network conditions.",
    use_cases=["Ping/traceroute network diagnostics"],
    advantages=["Simple, essential network troubleshooting tool"],
    limitations=["Often blocked/rate-limited by firewalls for security reasons"],
    real_world_example="Running 'ping google.com' to check if a connection is reachable and measure latency.",
    difficulty="Beginner", related=["ip"])

add(id="http", name="HTTP/HTTPS", category="Networking", topology="Client-Server",
    year=1991, inventor="Tim Berners-Lee", place="Switzerland (CERN)", organization="CERN / IETF / W3C",
    description="The application protocol underlying the World Wide Web, defining how browsers request and servers deliver resources.",
    how_it_works="Request-response text-based (now often binary in HTTP/2/3) protocol over TCP (or QUIC for HTTP/3), with methods GET/POST/PUT/DELETE; HTTPS adds TLS encryption.",
    use_cases=["Web browsing","REST APIs","IoT device cloud communication"],
    advantages=["Universal, simple request-response model","HTTPS provides encryption and authentication"],
    limitations=["More overhead than lightweight IoT protocols like MQTT/CoAP for constrained devices"],
    real_world_example="Your browser sending an HTTPS GET request every time you load a webpage.",
    difficulty="Beginner", related=["tcp","mqtt","coap"])

add(id="ftp", name="FTP / TFTP", category="Networking", topology="Client-Server",
    year=1971, inventor="Abhay Bhushan (FTP)", place="USA", organization="Network Working Group (RFC 114, 1971 — predates the IETF; RFC 959 standardised it in 1985)",
    description="File Transfer Protocol (and its tiny cousin TFTP) move files between systems — TFTP is especially common for embedded firmware transfer.",
    how_it_works="FTP uses TCP with separate control/data connections; TFTP uses simple UDP-based lockstep transfer, ideal for bootloaders with minimal code footprint.",
    use_cases=["Firmware upload to network devices/routers (TFTP)","General file transfer (FTP)"],
    advantages=["TFTP's tiny protocol footprint suits ROM bootloaders","FTP supports authentication and directory browsing"],
    limitations=["Neither is encrypted by default (use FTPS/SFTP for security)"],
    real_world_example="A network switch's bootloader fetching firmware images via TFTP during a recovery boot.",
    difficulty="Beginner", related=["tcp","udp"])

add(id="telnet_ssh", name="Telnet / SSH", category="Networking", topology="Client-Server",
    year=1969, inventor="Telnet: ARPANET team / SSH: Tatu Ylönen (1995)", place="USA/Finland",
    description="Remote terminal access protocols — Telnet is the unencrypted original, SSH is its secure, modern replacement.",
    how_it_works="Both provide a remote shell/console session over TCP; SSH adds public-key authentication and full encryption of the session.",
    use_cases=["Remote CLI access to routers, switches, embedded Linux boards"],
    advantages=["SSH provides secure remote management essential for production systems"],
    limitations=["Telnet sends everything (including passwords) in plaintext — a major security risk"],
    real_world_example="An engineer SSHing into a remote embedded Linux gateway to check logs.",
    difficulty="Beginner", related=["tcp"])

add(id="snmp", name="SNMP", category="Networking", topology="Client-Server (Manager-Agent)",
    year=1988, inventor="IETF working group", place="USA", organization="IETF",
    description="Simple Network Management Protocol — the standard way to monitor and manage network devices (routers, switches, printers, UPS, etc.).",
    how_it_works="A management station polls 'agents' on devices for values in a Management Information Base (MIB) tree, or agents send unsolicited 'traps' on events.",
    use_cases=["Network device monitoring/management dashboards"],
    advantages=["Universally supported on network-attached hardware","Trap mechanism enables real-time alerting"],
    limitations=["SNMPv1/v2c security is weak (plaintext community strings); v3 adds proper security"],
    real_world_example="A network monitoring dashboard polling switch port utilization stats via SNMP.",
    difficulty="Intermediate", related=["udp"])

add(id="mqtt", name="MQTT", category="Networking", topology="Publish-Subscribe (Broker-based)",
    year=1999, inventor="Andy Stanford-Clark (IBM) & Arlen Nipper (Cirrus Link/Eurotech)", place="USA/UK",
    description="A lightweight publish-subscribe messaging protocol invented to monitor oil pipeline sensors over expensive, unreliable satellite links.",
    how_it_works="Clients publish messages to 'topics' on a central broker; other clients subscribe to topics of interest and receive messages automatically, decoupling senders from receivers.",
    speed="Minimal overhead — as low as 2-byte header",
    use_cases=["IoT telemetry to the cloud","Home automation (Home Assistant, Tasmota devices)","Remote sensor monitoring"],
    advantages=["Extremely lightweight — ideal for constrained devices/networks","QoS levels (0/1/2) allow tunable delivery guarantees"],
    limitations=["Needs a broker (single point unless clustered)","Not designed for very large payloads/streaming media"],
    real_world_example="A fleet of IoT temperature sensors publishing readings to an MQTT broker in the cloud for a dashboard app.",
    fun_fact="MQTT was invented in 1999 specifically to monitor oil pipelines via satellite, where every byte of bandwidth was expensive — which is why its fixed header is just two bytes.",
    fun_fact_source="Andy Stanford-Clark & Arlen Nipper's accounts of MQTT's origin; OASIS MQTT 3.1.1/5.0 specification (fixed header size).",
    difficulty="Intermediate", related=["coap","http","tcp"])

add(id="coap", name="CoAP", category="Networking", topology="Client-Server (RESTful, over UDP)",
    year=2014, inventor="IETF CoRE Working Group", place="International", organization="IETF (RFC 7252)",
    description="Constrained Application Protocol — brings a RESTful, HTTP-like model to extremely resource-constrained IoT devices, over UDP.",
    how_it_works="Mimics HTTP's GET/POST/PUT/DELETE methods but with a compact binary header over UDP, and adds optional 'confirmable' messages for reliability when needed.",
    use_cases=["Constrained IoT sensor/actuator nodes","Low-power mesh networks (with 6LoWPAN)"],
    advantages=["Very low overhead, HTTP-like familiarity","Built-in support for multicast and resource discovery"],
    limitations=["Smaller ecosystem/tooling than MQTT/HTTP"],
    real_world_example="A battery-powered smart-building sensor exposing its readings as a CoAP RESTful resource.",
    difficulty="Advanced", related=["mqtt","udp"])

add(id="websocket", name="WebSocket", category="Networking", topology="Client-Server (persistent, over TCP)",
    year=2011, inventor="IETF (Ian Fette, Google)", place="USA", organization="IETF (RFC 6455)",
    description="Provides a persistent, full-duplex communication channel over a single TCP connection, upgrading from an initial HTTP handshake.",
    how_it_works="Starts as an HTTP request with an 'Upgrade' header; once accepted, both sides can send messages freely in either direction without repeated HTTP overhead.",
    use_cases=["Real-time web dashboards","Browser-based IoT device control panels","Live chat/notifications"],
    advantages=["Low-latency, bidirectional communication in the browser","Reuses existing HTTP infrastructure/ports"],
    limitations=["Requires a persistent connection — more server-side resource use than stateless HTTP"],
    real_world_example="A browser-based SCADA dashboard receiving live sensor updates over a WebSocket without polling.",
    difficulty="Intermediate", related=["http","tcp"])

add(id="ntp", name="NTP", category="Networking", topology="Client-Server (hierarchical)",
    year=1985, inventor="David L. Mills", place="USA", organization="University of Delaware / Network Working Group (RFC 958, 1985; current spec RFC 5905, 2010)",
    description="Network Time Protocol — synchronizes clocks across networked devices to within milliseconds of Coordinated Universal Time.",
    how_it_works="Clients query a hierarchy of time servers (stratum 0 atomic/GPS clocks down through stratum levels) and use round-trip delay measurement to correct for network latency.",
    use_cases=["Keeping embedded devices, servers, and networks time-synchronized"],
    advantages=["Millisecond-level accuracy over the internet","Hierarchical design scales globally"],
    limitations=["Not precise enough for hard real-time/motion-control synchronization (PTP is used instead)"],
    real_world_example="An IoT data logger syncing its clock via NTP so sensor timestamps are accurate.",
    difficulty="Beginner", related=["udp"])

add(id="mdns", name="mDNS / Zero-configuration Networking", category="Networking", topology="Multicast (LAN)",
    year=2000, inventor="Stuart Cheshire (Apple)", place="USA", organization="IETF (Zeroconf effort from 2000; mDNS standardised as RFC 6762, 2013)",
    description="Multicast DNS lets devices discover each other and resolve names on a local network without any central DNS server (the basis of Apple's Bonjour).",
    how_it_works="Devices multicast DNS-like queries/responses on the local subnet (224.0.0.251) so any device can announce/discover services (e.g., '_http._tcp.local').",
    use_cases=["Smart home device discovery","Network printer/service discovery"],
    advantages=["No central server needed for local discovery","Plug-and-play device/service finding"],
    limitations=["Limited to the local network segment (not routable by default)"],
    real_world_example="Your printer showing up automatically in your OS's print dialog without manual IP configuration.",
    difficulty="Intermediate", related=["dns","udp"])

# =====================================================================
# CATEGORY 5: WIRELESS
# =====================================================================
add(id="bluetooth_classic", name="Bluetooth Classic", category="Wireless", topology="Piconet (star, up to 7 slaves)",
    year=1994, inventor="Ericsson (Jaap Haartsen)", place="Sweden", organization="Bluetooth SIG",
    description="Named after 10th-century Danish King Harald 'Bluetooth' who united Danish tribes — symbolizing uniting communication protocols.",
    how_it_works="Frequency-hopping spread spectrum (1600 hops/sec) across 79 channels in the 2.4 GHz ISM band, master-slave piconet architecture.",
    speed="1-3 Mbps",
    use_cases=["Wireless audio (headsets, speakers)","Serial data links (HC-05 modules)"],
    advantages=["Mature, ubiquitous support","Good for continuous audio streaming"],
    limitations=["Higher power consumption than BLE","Limited to 7 active slaves per piconet"],
    real_world_example="Wireless headphones streaming music from a phone via Bluetooth Classic (A2DP profile).",
    fun_fact="Bluetooth's logo is actually a bind rune combining the Younger Futhark runes for Harald Bluetooth's initials, H and B.",
    fun_fact_source="Bluetooth SIG, 'Origin of the Bluetooth Name' (bluetooth.com).",
    difficulty="Beginner", related=["ble","wifi"])

add(id="ble", name="Bluetooth Low Energy (BLE)", category="Wireless", topology="Star / Mesh (BLE Mesh)",
    year=2010, inventor="Nokia (Wibree project) → Bluetooth SIG", place="Finland/Global", organization="Bluetooth SIG",
    description="A power-optimized variant of Bluetooth designed for coin-cell-battery devices that send small amounts of data infrequently.",
    how_it_works="Devices advertise on 3 dedicated channels and connect briefly to exchange data via GATT (Generic Attribute Profile) services/characteristics, then sleep to save power.",
    speed="1-2 Mbps (up to higher rates in BLE 5.x Coded/2M PHY modes)",
    use_cases=["Fitness trackers/wearables","Asset tracking tags","Smart locks","BLE beacons"],
    advantages=["Extremely low power — years of coin-cell battery life","Wide smartphone compatibility"],
    limitations=["Lower throughput/range than Wi-Fi","Connection intervals add latency vs continuous streaming"],
    real_world_example="A fitness tracker syncing step data to a phone app via BLE while sipping a coin-cell battery for months.",
    difficulty="Intermediate", related=["bluetooth_classic","zigbee"])

add(id="wifi", name="Wi-Fi (IEEE 802.11)", category="Wireless", topology="Star (Access Point) / Ad-hoc",
    year=1997, inventor="IEEE 802.11 working group (Vic Hayes 'father of Wi-Fi')", place="USA/International", organization="IEEE / Wi-Fi Alliance",
    description="The dominant wireless LAN technology, evolving from 2 Mbps in 1997 to multi-gigabit speeds today (Wi-Fi 6/6E/7).",
    how_it_works="CSMA/CA (collision avoidance) medium access in 2.4/5/6 GHz bands, with increasingly advanced modulation (OFDM, OFDMA, MU-MIMO) for higher throughput.",
    speed="2 Mbps (802.11 original) – 9.6 Gbps+ (Wi-Fi 6E/7)",
    use_cases=["Home/office wireless networking","IoT devices (ESP32, smart home)","Video streaming"],
    advantages=["High throughput and range vs Bluetooth/Zigbee","Direct IP connectivity — no gateway needed"],
    limitations=["Higher power consumption than BLE/Zigbee for battery devices","Congested 2.4GHz band in dense environments"],
    real_world_example="An ESP32 dev board connecting directly to your home router and serving a web dashboard.",
    difficulty="Beginner", related=["ble","ethernet"])

add(id="zigbee", name="Zigbee", category="Wireless", topology="Mesh",
    year=2003, inventor="Zigbee Alliance (now CSA)", place="International", organization="Connectivity Standards Alliance",
    description="A low-power mesh networking standard built on IEEE 802.15.4, designed for large numbers of simple sensor/actuator devices.",
    how_it_works="Devices self-organize into a mesh where messages can hop through multiple nodes to reach the coordinator, extending range beyond direct radio reach.",
    speed="250 kbps",
    use_cases=["Smart home devices (bulbs, sensors, locks)","Smart metering"],
    advantages=["Self-healing mesh extends range and reliability","Very low power for battery/mains-powered sensor nodes"],
    limitations=["Lower throughput than Wi-Fi/BLE","Ecosystem fragmentation across vendors (partly solved by Matter)"],
    real_world_example="A Philips Hue smart bulb network where bulbs relay Zigbee mesh messages to reach distant fixtures.",
    difficulty="Intermediate", related=["thread","wirelesshart","ble"])

add(id="thread", name="Thread", category="Wireless", topology="Mesh (IPv6)",
    year=2014, inventor="Thread Group (Google/Nest, Samsung, ARM et al.)", place="USA", organization="Thread Group",
    description="An IPv6-based, low-power mesh networking protocol built on 802.15.4, designed as a modern foundation for smart home connectivity (used by Matter).",
    how_it_works="Every device gets a routable IPv6 address in a self-healing mesh, eliminating the need for proprietary gateways required by Zigbee.",
    speed="250 kbps (802.15.4 PHY)",
    use_cases=["Modern smart home devices (Matter-based)","Google Nest ecosystem"],
    advantages=["Native IPv6 — directly routable/addressable","No single-vendor proprietary hub required"],
    limitations=["Requires a Thread Border Router to bridge to normal Wi-Fi/internet"],
    real_world_example="A Matter-certified smart plug joining a Thread mesh via a Google Nest Hub acting as border router.",
    difficulty="Advanced", related=["zigbee","matter"])

add(id="matter", name="Matter", category="Wireless", topology="Star/Mesh (over Wi-Fi/Thread)",
    year=2022, inventor="Connectivity Standards Alliance (Amazon, Apple, Google, Samsung et al.)", place="International", organization="CSA",
    description="A unifying application-layer smart home standard designed to make devices from different brands work together regardless of the underlying radio (Wi-Fi, Thread, BLE for commissioning).",
    how_it_works="Defines a common data model and secure commissioning process on top of IP (via Wi-Fi or Thread), so a single device can be controlled by Apple Home, Google Home, or Amazon Alexa interchangeably.",
    use_cases=["Cross-vendor smart home devices (bulbs, locks, thermostats)"],
    advantages=["True cross-ecosystem interoperability","Backed by all major smart home platform vendors"],
    limitations=["Still a young standard — retrofit of legacy Zigbee devices needs bridges"],
    real_world_example="A Matter-certified smart lock that works natively with Apple HomeKit, Google Home, and Alexa without separate apps.",
    difficulty="Advanced", related=["thread","zigbee","wifi"])

add(id="zwave", name="Z-Wave", category="Wireless", topology="Mesh",
    year=2001, inventor="Zensys (Denmark)", place="Denmark", organization="Z-Wave Alliance",
    description="A proprietary low-power mesh protocol for home automation, operating in the sub-1GHz band to avoid Wi-Fi/Bluetooth congestion.",
    how_it_works="Sub-GHz (908/868 MHz depending on region) mesh network with source-routing, giving longer range and less RF interference than 2.4 GHz alternatives.",
    speed="9.6-100 kbps",
    use_cases=["Home security sensors","Smart locks","Home automation hubs (SmartThings, Hubitat)"],
    advantages=["Sub-GHz band avoids 2.4GHz congestion/interference","Mature certification program ensures interoperability"],
    limitations=["Proprietary chipset licensing (historically Sigma Designs/Silicon Labs only)","Lower throughput than Zigbee/Thread"],
    real_world_example="A home security system's door/window sensors meshing back to a Z-Wave hub.",
    difficulty="Intermediate", related=["zigbee"])

add(id="nfc", name="NFC (Near Field Communication)", category="Wireless", topology="Point-to-Point (very short range)",
    year=2004, inventor="NXP Semiconductors & Sony", place="Netherlands/Japan", organization="NFC Forum",
    description="An ultra-short-range (a few cm) wireless technology derived from RFID, enabling simple tap-to-connect interactions.",
    how_it_works="Inductive coupling between two loop antennas at 13.56 MHz; can operate in active (both powered) or passive (reader powers a passive tag) mode.",
    speed="106-424 kbps",
    use_cases=["Contactless payments (tap-to-pay)","Access badges","Pairing (tap-to-pair) for Bluetooth/Wi-Fi setup"],
    advantages=["Extremely simple 'tap' user experience","Passive tags need no battery"],
    limitations=["Very short range (~4 cm) by design (a security feature, not a bug)"],
    real_world_example="Tapping your phone or credit card on a payment terminal to pay contactlessly.",
    difficulty="Beginner", related=["rfid"])

add(id="rfid", name="RFID", category="Wireless", topology="Point-to-Point / Point-to-Multipoint",
    year=1973, inventor="Mario Cardullo (first patented active RFID)", place="USA",
    description="Radio Frequency Identification — the broad technology family behind NFC, warehouse tags, and toll-road transponders.",
    how_it_works="A reader emits RF energy; passive tags backscatter a modulated reply using energy harvested from the reader's field (or active tags use their own battery for longer range).",
    speed="Varies by frequency band (LF/HF/UHF)",
    use_cases=["Warehouse/retail inventory tracking","Toll road transponders (active UHF)","Access control cards"],
    advantages=["Passive tags are extremely cheap and batteryless","Can read many tags simultaneously (anti-collision)"],
    limitations=["Range and read reliability vary a lot with frequency/environment"],
    real_world_example="A retail store scanning an entire rack of clothing inventory instantly using UHF RFID tags.",
    difficulty="Beginner", related=["nfc"])

add(id="uwb", name="UWB (Ultra-Wideband)", category="Wireless", topology="Point-to-Point / Mesh",
    year=1998, inventor="Robert A. Scholtz & academic pioneers (commercialized by various)", place="USA", organization="FiRa Consortium / IEEE 802.15.4z",
    description="A radio technology using very short pulses across a wide spectrum, enabling centimeter-level distance and positioning accuracy.",
    how_it_works="Measures the precise time-of-flight of extremely short RF pulses spread across a wide bandwidth (>500 MHz) to calculate distance with centimeter precision.",
    speed="~27-480 Mbps (data), but primarily used for ranging not bulk data",
    use_cases=["Precise indoor positioning","Secure keyless car entry (relay-attack resistant)","AirTag/SmartTag-style item finding"],
    advantages=["Centimeter-level ranging accuracy","Highly resistant to relay attacks vs BLE-only keyless entry"],
    limitations=["Higher chipset cost than BLE","Shorter practical range than Wi-Fi/BLE for data"],
    real_world_example="Apple's 'Precision Finding' pointing you directly to a lost AirTag using UWB ranging.",
    difficulty="Advanced", related=["ble","rfid"])

add(id="antplus", name="ANT+", category="Wireless", topology="Star/Mesh",
    year=2003, inventor="Dynastream Innovations (Garmin)", place="Canada", organization="ANT+ Alliance",
    description="A low-power wireless protocol optimized for sports and fitness sensors — heart rate straps, cycling power meters, cadence sensors.",
    how_it_works="Similar 2.4GHz low-power design philosophy to BLE, with a well-defined device profile library specifically for fitness/sports data.",
    speed="1 Mbps (low duty cycle)",
    use_cases=["Heart rate monitors","Bike power meters/cadence sensors","Sports watches"],
    advantages=["Extremely long battery life for sensor straps","Mature standardized sports device profiles"],
    limitations=["Narrower ecosystem than BLE (mostly fitness-specific)"],
    real_world_example="A cycling power meter pedal broadcasting wattage data to a bike computer via ANT+.",
    difficulty="Intermediate", related=["ble"])

# =====================================================================
# CATEGORY 6: CELLULAR / LPWAN
# =====================================================================
add(id="gsm", name="GSM / GPRS / EDGE (2G)", category="Cellular", topology="Star (Cellular)",
    year=1991, inventor="ETSI (European Telecommunications Standards Institute)", place="Europe/Finland (first call)",
    description="The original digital cellular standard, later extended with GPRS (2.5G) and EDGE (2.75G) to add packet data capability.",
    how_it_works="TDMA (Time Division Multiple Access) digital voice/data over licensed cellular spectrum; GPRS/EDGE add packet-switched data on top of the same network.",
    speed="9.6 kbps (GSM voice/data) – 384 kbps (EDGE)",
    use_cases=["Legacy M2M/telemetry modules","Basic voice/SMS"],
    advantages=["Still the most globally ubiquitous fallback network in many regions"],
    limitations=["Being sunset (2G shutdown) in many countries in favor of LTE-M/NB-IoT"],
    real_world_example="Older vending machines/ATMs using a 2G GSM modem to report status.",
    difficulty="Beginner", related=["lte","nbiot"])

add(id="lte", name="LTE / 4G", category="Cellular", topology="Star (Cellular)",
    year=2009, inventor="3GPP consortium", place="International (first deployment: Sweden/Norway)", organization="3GPP",
    description="Long-Term Evolution — the 4th generation cellular standard bringing broadband-class mobile data.",
    how_it_works="All-IP packet-switched network using OFDMA (downlink) and SC-FDMA (uplink) for efficient spectrum use at much higher speeds than 3G.",
    speed="Up to 100+ Mbps (theoretical up to 1 Gbps LTE-Advanced)",
    use_cases=["Mobile broadband","4G routers/gateways for industrial connectivity"],
    advantages=["High throughput, low latency vs earlier generations","All-IP architecture simplifies data services"],
    limitations=["Higher power consumption than LPWAN options for simple IoT sensors"],
    real_world_example="A remote industrial site using an LTE router as its primary internet backhaul link.",
    difficulty="Intermediate", related=["gsm","nbiot","5g"])

add(id="ltem", name="LTE-M", category="Cellular", topology="Star (Cellular)",
    year=2016, inventor="3GPP", place="International", organization="3GPP",
    description="A low-power, low-cost variant of LTE specifically designed for IoT devices needing moderate data rates and voice fallback.",
    how_it_works="Reduces LTE bandwidth/complexity requirements while retaining mobility and voice (VoLTE) support, plus deep sleep power-saving modes (PSM, eDRX).",
    speed="~1 Mbps",
    use_cases=["Asset trackers","Wearables","POS terminals needing mobility"],
    advantages=["Supports mobility/handoff between towers (unlike NB-IoT)","Lower cost/power than full LTE"],
    limitations=["Lower throughput than full LTE"],
    real_world_example="A GPS asset tracker on a shipping container using LTE-M to report location as it crosses cell tower boundaries.",
    difficulty="Advanced", related=["nbiot","lte"])

add(id="nbiot", name="NB-IoT", category="Cellular", topology="Star (Cellular)",
    year=2016, inventor="3GPP (Huawei/Vodafone-led)", place="International", organization="3GPP",
    description="Narrowband IoT — an ultra-low-power, ultra-low-bandwidth cellular standard for the simplest, most battery-sensitive IoT sensors.",
    how_it_works="Operates in a very narrow 200 kHz channel (can even reuse GSM guard bands), trading throughput for extreme power savings and deep building penetration.",
    speed="~250 kbps (max), often much lower in practice",
    use_cases=["Smart water/gas meters","Smart parking sensors","Environmental sensors in remote locations"],
    advantages=["Multi-year battery life on small batteries","Excellent signal penetration (basements, underground meters)"],
    limitations=["No mobility/handoff support (stationary devices only)","Very low throughput"],
    real_world_example="A smart water meter reporting consumption once a day for 10 years on a single battery via NB-IoT.",
    difficulty="Advanced", related=["ltem","lora"])

add(id="5g", name="5G", category="Cellular", topology="Star (Cellular)",
    year=2019, inventor="3GPP consortium", place="International (first commercial: South Korea)", organization="3GPP",
    description="The 5th generation cellular standard, targeting massive bandwidth, ultra-low latency, and massive device density for IoT.",
    how_it_works="Uses new radio (5G NR) with sub-6GHz and mmWave spectrum, network slicing, and beamforming to serve eMBB (broadband), URLLC (ultra-reliable low latency), and mMTC (massive IoT) use cases simultaneously.",
    speed="Up to 10+ Gbps (mmWave), 1ms-class latency for URLLC",
    use_cases=["Industrial private 5G networks","AR/VR streaming","Massive IoT sensor deployments","Remote-controlled robotics/vehicles"],
    advantages=["Extremely high throughput and low latency","Network slicing tailors the network to each application's needs"],
    limitations=["mmWave has very short range/poor building penetration","Infrastructure cost/rollout still ongoing in many regions"],
    real_world_example="A factory using a private 5G network (URLLC slice) to remotely control robotic arms in real time.",
    difficulty="Advanced", related=["lte","wifi"])

add(id="lora", name="LoRa", category="Cellular", topology="Star-of-stars",
    year=2009, inventor="Cycleo (acquired by Semtech in 2012)", place="France", organization="Semtech",
    description="A proprietary Chirp Spread Spectrum radio modulation technique enabling very long range (kilometers) at very low power in unlicensed sub-GHz bands.",
    how_it_works="Chirp Spread Spectrum (CSS) modulation trades data rate for range and noise immunity — signals can be decoded even below the noise floor.",
    speed="0.3-50 kbps",
    use_cases=["Agricultural sensors","Smart city sensors","Remote environmental monitoring"],
    advantages=["Multi-kilometer range in unlicensed spectrum (no subscription fees)","Excellent power efficiency for battery-powered nodes"],
    limitations=["Very low data rate","Duty-cycle restrictions in many regions (e.g., EU 868MHz band)"],
    real_world_example="Soil moisture sensors scattered across a large farm reporting back to a single LoRa gateway kilometers away.",
    fun_fact="LoRa's chirp spread-spectrum modulation is the same basic idea as chirp radar — and as the frequency sweeps some bats use for echolocation: sweeping the tone across the band makes the signal recoverable even when it arrives below the noise floor.",
    fun_fact_source="Semtech's published account of LoRa's origins (acquired from Cycleo, 2012) and chirp spread-spectrum literature.",
    difficulty="Intermediate", related=["lorawan","nbiot"])

add(id="lorawan", name="LoRaWAN", category="Cellular", topology="Star-of-stars",
    year=2015, inventor="LoRa Alliance", place="International", organization="LoRa Alliance",
    description="The open MAC-layer networking protocol standard built on top of the LoRa physical radio layer.",
    how_it_works="Defines network server architecture, device classes (A/B/C for different power/latency trade-offs), and adaptive data rate to optimize range vs battery life automatically.",
    speed="0.3-50 kbps (inherits LoRa PHY)",
    use_cases=["Citywide/regional IoT sensor networks","Utility metering","Livestock tracking"],
    advantages=["Open standard on top of LoRa's long range/low power PHY","Device Class A/B/C flexibility for different application needs"],
    limitations=["Regional spectrum regulations limit duty cycle/power"],
    real_world_example="A city-wide LoRaWAN network monitoring parking spot occupancy sensors across an entire downtown.",
    difficulty="Advanced", related=["lora","nbiot"])

add(id="sigfox", name="Sigfox", category="Cellular", topology="Star",
    year=2010, inventor="Ludovic Le Moan & Christophe Fourtet", place="France", organization="Sigfox (now UnaBiz)",
    description="An ultra-narrowband LPWAN network operator/technology sending extremely small messages over very long range.",
    how_it_works="Ultra Narrow Band (UNB) modulation sends tiny messages (up to 12 bytes) that are received by multiple base stations simultaneously for redundancy, with no need for the device to ever 'join' a network like LoRaWAN.",
    speed="100-600 bps",
    use_cases=["Simple asset tracking","Basic status/alarm reporting (extremely infrequent, tiny messages)"],
    advantages=["Ultra-low power, ultra-low cost per message","No SIM card or complex provisioning needed"],
    limitations=["Extremely limited message size/frequency (a few tens of bytes, a few times a day)","Coverage depends on operator network build-out (unlike LoRaWAN's open deployment model)"],
    real_world_example="A simple asset tag sending a 'device X moved' alert once via Sigfox's ultra-narrowband network.",
    difficulty="Advanced", related=["lorawan","nbiot"])

# =====================================================================
# CATEGORY 7: AUDIO / VIDEO / DISPLAY
# =====================================================================
add(id="i2s", name="I²S (Inter-IC Sound)", category="Audio/Video", topology="Point-to-Point",
    year=1986, inventor="Philips Semiconductors", place="Netherlands",
    description="A serial bus standard specifically for connecting digital audio devices like codecs, DACs, and ADCs.",
    how_it_works="3 lines carry bit clock (BCLK/SCK), word/frame select (WS/LRCLK — distinguishes left/right channel), and serial data (SD) synchronously.",
    speed="Typical audio rates: 44.1/48/96/192 kHz sample rate x bit depth",
    pins=["SCK/BCLK","WS/LRCLK","SD"],
    use_cases=["Connecting MCU to audio DAC/ADC codecs","Digital microphones (I2S MEMS mics)"],
    advantages=["Clean, glitch-free synchronous audio transfer","Simple wiring for stereo PCM audio"],
    limitations=["Not typically used for compressed/non-PCM formats without extensions"],
    real_world_example="An ESP32 streaming audio to an external I2S DAC module for a smart speaker project.",
    difficulty="Intermediate", related=["tdm","pcm"])

add(id="tdm", name="TDM (Time Division Multiplexing - Audio)", category="Audio/Video", topology="Point-to-Point (multi-channel)",
    year=1960, inventor="Telecom industry (Bell System)", place="USA",
    description="Interleaves multiple audio channels onto a single serial data line by giving each channel its own time slot within a frame.",
    how_it_works="Multiple audio channels (e.g., 8) are packed sequentially into time slots within each sample period on a shared data line, synchronized by a frame sync signal.",
    use_cases=["Multi-channel audio interfaces","Telecom trunk lines (original use)"],
    advantages=["Carries many audio channels over very few wires"],
    limitations=["Requires precise synchronization across all channels"],
    real_world_example="A multi-channel audio codec chip transmitting 8 microphone channels over a single TDM data line to an MCU.",
    difficulty="Advanced", related=["i2s","pcm"])

add(id="pcm", name="PCM (Pulse Code Modulation)", category="Audio/Video", topology="Point-to-Point",
    year=1937, inventor="Alec Reeves", place="France/UK",
    description="The foundational method of representing analog audio signals digitally by sampling amplitude at regular intervals.",
    how_it_works="Analog signal is sampled at a fixed rate (e.g., 44.1kHz) and each sample is quantized to a fixed bit depth (e.g., 16-bit), forming the basis of WAV/CD audio.",
    use_cases=["Uncompressed digital audio (CDs, WAV files)","Telephony (64 kbps PCM)"],
    advantages=["Simple, lossless representation within quantization limits","Universal — nearly all digital audio starts as PCM"],
    limitations=["Uncompressed — larger file size / bandwidth vs compressed formats"],
    real_world_example="A CD storing music as 44.1kHz/16-bit PCM samples.",
    fun_fact="Alec Reeves conceived PCM in 1937 and filed the French patent in 1938, but the US patent did not issue until 1943 and the electronics to make it practical did not exist for another decade — Bell Labs' SIGSALY (1943) was the first working system.",
    fun_fact_source="Alec Reeves, French patent no. 852,183 (filed 1938); US patent 2,272,070 (1942); ITU historical accounts of PCM.",
    difficulty="Beginner", related=["i2s","tdm"])

add(id="spdif", name="S/PDIF", category="Audio/Video", topology="Point-to-Point",
    year=1990, inventor="Sony & Philips", place="Japan/Netherlands",
    description="Sony/Philips Digital Interface — a consumer digital audio standard for transmitting stereo/compressed surround audio over a single cable (coax or optical/TOSLINK).",
    how_it_works="Biphase-mark encoded serial data carries PCM stereo or compressed (Dolby/DTS) audio over standard coax or optical fiber, self-clocking so no separate clock line is needed.",
    use_cases=["Connecting CD/DVD/Blu-ray players, TVs, and AV receivers"],
    advantages=["Optical (TOSLINK) variant provides electrical isolation and immunity to interference","Simple single-cable consumer audio connection"],
    limitations=["Consumer-grade only (professional gear typically uses AES/EBU)"],
    real_world_example="A TV sending audio to a soundbar via an optical TOSLINK S/PDIF cable.",
    difficulty="Intermediate", related=["i2s","pcm"])

add(id="hdmi", name="HDMI", category="Audio/Video", topology="Point-to-Point",
    year=2002, inventor="HDMI Founders consortium (Sony, Philips, Hitachi, etc.)", place="International", organization="HDMI Forum",
    description="High-Definition Multimedia Interface — the dominant standard for carrying uncompressed digital video and audio between consumer devices.",
    how_it_works="TMDS (Transition-Minimized Differential Signaling) encodes video/audio/control data across multiple differential pairs, plus a separate CEC line for device control.",
    speed="4.95 Gbps (1.0) – 48 Gbps (2.1)",
    use_cases=["Connecting set-top boxes, game consoles, and PCs to TVs/monitors"],
    advantages=["Single cable for video+audio+control (CEC)","Backward compatible across versions"],
    limitations=["Licensing/royalty fees for manufacturers","Cable length limited without active/optical extenders at high resolutions"],
    real_world_example="A gaming console connected to a 4K TV over a single HDMI cable carrying both video and audio.",
    difficulty="Intermediate", related=["displayport","mipi_dsi"])

add(id="mipi_dsi", name="MIPI DSI", category="Audio/Video", topology="Point-to-Point",
    year=2006, inventor="MIPI Alliance", place="USA/International", organization="MIPI Alliance",
    description="Display Serial Interface — the standard high-speed interface connecting an SoC/MCU to a display panel in phones, tablets, and embedded devices.",
    how_it_works="Uses differential D-PHY or C-PHY lanes to send pixel data at high speed with low power/EMI, common in mobile and embedded display modules.",
    speed="Up to several Gbps per lane",
    use_cases=["Smartphone/tablet display panels","Embedded HMI touchscreen modules"],
    advantages=["Very low power and EMI vs parallel RGB interfaces","Scales with multiple lanes for higher resolution"],
    limitations=["Requires MIPI-capable SoC and specialized display panel"],
    real_world_example="A Raspberry Pi's official touchscreen display connected via a MIPI DSI ribbon cable.",
    difficulty="Advanced", related=["mipi_csi","hdmi"])

add(id="mipi_csi", name="MIPI CSI", category="Audio/Video", topology="Point-to-Point",
    year=2005, inventor="MIPI Alliance", place="USA/International", organization="MIPI Alliance",
    description="Camera Serial Interface — the standard high-speed interface connecting an image sensor/camera module to an SoC.",
    how_it_works="Similar D-PHY/C-PHY differential lane technology as DSI, but carrying pixel data from the camera sensor to the processor.",
    speed="Up to several Gbps per lane",
    use_cases=["Smartphone cameras","Raspberry Pi camera module","Machine vision embedded cameras"],
    advantages=["High bandwidth for high-resolution image sensors","Low power/EMI vs parallel camera interfaces"],
    limitations=["Requires MIPI CSI-capable receiver silicon"],
    real_world_example="A Raspberry Pi Camera Module streaming video to the Pi's ISP via MIPI CSI-2.",
    difficulty="Advanced", related=["mipi_dsi"])

add(id="displayport", name="DisplayPort", category="Audio/Video", topology="Point-to-Point",
    year=2006, inventor="VESA (Video Electronics Standards Association)", place="USA", organization="VESA",
    description="A royalty-free digital display standard developed as a modern, open alternative to HDMI/DVI, especially popular for PC monitors.",
    how_it_works="Uses a packetized micro-packet architecture over multiple differential lanes, supporting multi-stream transport (daisy-chaining multiple monitors).",
    speed="17.28 Gbps (1.2) – 80 Gbps (2.1 UHBR20)",
    use_cases=["PC monitors","Laptop docking stations (often via USB-C Alt Mode)"],
    advantages=["Royalty-free standard","Multi-Stream Transport allows daisy-chained monitors from one port"],
    limitations=["Less common than HDMI in consumer TVs/home theater"],
    real_world_example="A laptop driving two external 4K monitors daisy-chained via a single DisplayPort cable.",
    difficulty="Intermediate", related=["hdmi"])

add(id="lvds", name="LVDS", category="Audio/Video", topology="Point-to-Point",
    year=1994, inventor="National Semiconductor", place="USA", organization="IEEE / TIA",
    description="Low-Voltage Differential Signaling — a general-purpose high-speed differential signaling standard used for displays and high-speed data links before MIPI became dominant.",
    how_it_works="Small-swing (~350mV) differential signaling drastically reduces EMI and power vs single-ended signaling at multi-hundred-Mbps to multi-Gbps speeds.",
    speed="~400 Mbps – multi-Gbps per lane",
    use_cases=["Industrial/embedded display panels","Legacy laptop display connections"],
    advantages=["Low EMI, low power, robust at high speeds over moderate distances","Simple, well-understood differential signaling"],
    limitations=["Being displaced by MIPI DSI/eDP in mobile-derived embedded designs"],
    real_world_example="An industrial HMI panel using an LVDS interface to connect its display module.",
    difficulty="Advanced", related=["mipi_dsi","parallel"])

# =====================================================================
# CATEGORY 8: USB FAMILY
# =====================================================================
add(id="usb11", name="USB 1.1", category="USB", topology="Star (Host + Hub)",
    year=1998, inventor="USB-IF consortium (Intel-led: Ajay Bhatt)", place="USA", organization="USB Implementers Forum",
    description="The first widely adopted USB revision, unifying the chaos of serial/parallel/PS2 ports into one plug-and-play connector.",
    how_it_works="Host-centric polled bus; Low Speed (1.5 Mbps) for mice/keyboards, Full Speed (12 Mbps) for most other peripherals.",
    speed="1.5 Mbps (Low Speed) / 12 Mbps (Full Speed)",
    use_cases=["Legacy keyboards, mice, low-speed peripherals"],
    advantages=["Universal plug-and-play, eliminated a mess of legacy connectors"],
    limitations=["Very slow by modern standards"],
    real_world_example="Early 2000s USB keyboards and mice.",
    fun_fact="Ajay Bhatt, one of the Intel engineers behind USB, became a minor celebrity after Intel's 2009 'Sponsors of Tomorrow' commercials featured him — played by an actor, because the real Bhatt declined to appear.",
    fun_fact_source="Intel 'Sponsors of Tomorrow' advertising campaign (2009); Intel newsroom profiles of Ajay Bhatt.",
    difficulty="Beginner", related=["usb20"])

add(id="usb20", name="USB 2.0", category="USB", topology="Star (Host + Hub)",
    year=2000, inventor="USB-IF consortium", place="USA", organization="USB Implementers Forum",
    description="Added 'High Speed' mode, becoming the long-reigning workhorse standard for embedded devices, flash drives, and peripherals.",
    how_it_works="Adds High Speed (480 Mbps) mode while remaining backward compatible with 1.1 Low/Full speed devices via the same connector.",
    speed="480 Mbps (High Speed)",
    use_cases=["Flash drives","MCU debug/programming interfaces","Most embedded USB peripherals"],
    advantages=["Huge speed jump over 1.1 while staying backward compatible","Extremely widespread hardware/driver support"],
    limitations=["Half-duplex effectively due to shared bus arbitration; superseded in throughput by USB 3.x"],
    real_world_example="Nearly every USB flash drive and MCU dev board (e.g., STM32 Nucleo) programming interface.",
    difficulty="Beginner", related=["usb11","usb3x"])

add(id="usb3x", name="USB 3.x (3.0/3.1/3.2)", category="USB", topology="Star (Host + Hub)",
    year=2008, inventor="USB-IF consortium", place="USA", organization="USB Implementers Forum",
    description="Introduced SuperSpeed transfer with dedicated additional differential pairs, massively increasing throughput while staying connector-compatible.",
    how_it_works="Adds a separate SuperSpeed differential pair (full-duplex) alongside the USB 2.0 pair, enabling simultaneous high-speed and legacy operation.",
    speed="5 Gbps (3.0/3.1 Gen1) – 20 Gbps (3.2 Gen2x2)",
    use_cases=["External SSDs","High-speed data acquisition devices","Webcams/capture devices"],
    advantages=["Full-duplex operation, huge throughput gain","Backward compatible connectors (Type-A)"],
    limitations=["Naming scheme became notoriously confusing across revisions"],
    real_world_example="An external USB 3.0 SSD achieving 400+ MB/s transfer speeds.",
    difficulty="Intermediate", related=["usb20","usbc"])

add(id="usbc", name="USB-C / USB PD", category="USB", topology="Star (Host + Hub)",
    year=2014, inventor="USB-IF consortium", place="USA", organization="USB Implementers Forum",
    description="A reversible connector standard that, combined with USB Power Delivery (PD), unified data and power charging into a single universal port.",
    how_it_works="24-pin reversible connector supports USB data, DisplayPort/Thunderbolt Alt Modes, and USB PD negotiates variable voltage/current (up to 240W in PD 3.1 EPR) between devices.",
    speed="Up to 40 Gbps (Thunderbolt 3/4 Alt Mode via USB-C)",
    use_cases=["Modern smartphones/laptops charging and data","USB PD fast charging","Docking stations (video+data+power over one cable)"],
    advantages=["Reversible connector — no more wrong-side-up frustration","Single cable for power, data, and even video"],
    limitations=["Cable/accessory quality varies widely — not all USB-C cables support all features"],
    real_world_example="A laptop charging and driving an external monitor through a single USB-C cable to a dock.",
    difficulty="Intermediate", related=["usb3x"])

add(id="usbcdc", name="USB CDC (Communications Device Class)", category="USB", topology="Point-to-Point (over USB)",
    year=1999, inventor="USB-IF", place="USA",
    description="A standard USB device class that lets an embedded MCU appear as a virtual serial (COM) port to a host PC without custom drivers.",
    how_it_works="MCU firmware implements the CDC-ACM class, and the OS automatically loads a generic serial driver, exposing familiar UART-like read/write over USB.",
    use_cases=["MCU virtual COM port for debug/console/firmware updates"],
    advantages=["No custom driver needed on Windows/Linux/macOS","Familiar serial programming model over USB's connector/speed"],
    limitations=["Adds USB stack complexity/code size to the MCU firmware vs plain UART"],
    real_world_example="An Arduino or STM32 board showing up as 'COM3' when plugged into a PC via USB.",
    difficulty="Intermediate", related=["usb20","uart"])

add(id="usbhid", name="USB HID", category="USB", topology="Point-to-Point (over USB)",
    year=1996, inventor="USB-IF", place="USA",
    description="Human Interface Device class — the standard behind keyboards, mice, and game controllers working without any special drivers.",
    how_it_works="Devices describe their data format via a 'HID report descriptor', letting any compliant OS parse button/axis/key data generically.",
    use_cases=["Keyboards, mice, joysticks/gamepads","Custom embedded devices needing driverless PC control (e.g., macro pads)"],
    advantages=["Zero driver installation needed on virtually any OS","Flexible report descriptor supports many device types"],
    limitations=["Report descriptors can be tricky to design/debug for custom devices"],
    real_world_example="A custom embedded macro keypad appearing instantly as a working keyboard on any PC.",
    difficulty="Intermediate", related=["usb20"])

add(id="usbmsc", name="USB MSC (Mass Storage Class)", category="USB", topology="Point-to-Point (over USB)",
    year=1999, inventor="USB-IF", place="USA",
    description="The standard class that makes flash drives and SD card readers show up as generic disk drives on any OS.",
    how_it_works="Implements the SCSI command set (Bulk-Only Transport) over USB, letting the OS treat the device as a standard block storage device.",
    use_cases=["USB flash drives","MCU exposing its SD card as a drive to a host PC"],
    advantages=["Universal driverless disk access across all major OSes"],
    limitations=["Being partly supplanted by MTP for smartphones (which want richer file semantics)"],
    real_world_example="An MCU-based data logger exposing its onboard SD card as a normal USB drive when plugged into a PC.",
    difficulty="Intermediate", related=["usb20","sdio"])

add(id="usbdfu", name="USB DFU (Device Firmware Upgrade)", category="USB", topology="Point-to-Point (over USB)",
    year=2004, inventor="USB-IF", place="USA",
    description="A standard USB class specifically for safely uploading new firmware images to a device's bootloader.",
    how_it_works="Device enters a special DFU mode exposing simple upload/download commands, letting a host tool flash new firmware without a custom protocol.",
    use_cases=["STM32/embedded MCU firmware updates via USB bootloader"],
    advantages=["Standardized, tool-supported (e.g., dfu-util) firmware flashing over USB","No custom protocol/driver needed"],
    limitations=["Device must implement/enter a dedicated DFU bootloader mode"],
    real_world_example="Flashing new firmware onto an STM32 board's built-in USB DFU bootloader using 'dfu-util'.",
    difficulty="Advanced", related=["usb20"])

# =====================================================================
# CATEGORY 9: FPGA / HIGH-SPEED SERDES
# =====================================================================
add(id="pcie", name="PCIe (PCI Express)", category="High-Speed/FPGA", topology="Point-to-Point (switched fabric)",
    year=2003, inventor="Intel-led PCI-SIG consortium", place="USA", organization="PCI-SIG",
    description="The high-speed serial successor to the parallel PCI bus, now the backbone interconnect inside virtually every PC and many embedded/FPGA systems.",
    how_it_works="Point-to-point serial differential 'lanes' (x1, x4, x8, x16) using 8b/10b or 128b/130b encoding, with a switched fabric replacing the old shared parallel bus.",
    speed="Gen1: 2.5 Gbps/lane; Gen2: 5 Gbps; Gen3: 8 Gbps; Gen4: 16 Gbps; Gen5: 32 Gbps",
    use_cases=["GPUs, SSDs (NVMe)","FPGA accelerator cards","High-speed data acquisition systems"],
    advantages=["Massive scalable bandwidth via lane aggregation","Low latency, point-to-point switched architecture"],
    limitations=["Complex PHY/protocol stack — significant FPGA/ASIC resources needed to implement"],
    real_world_example="An NVMe SSD achieving multi-GB/s speeds over a PCIe Gen4 x4 link.",
    difficulty="Advanced", related=["sgmii","serdes"])

add(id="rapidio", name="RapidIO", category="High-Speed/FPGA", topology="Switched fabric",
    year=1997, inventor="Motorola & Mercury Computer Systems", place="USA", organization="RapidIO Trade Association",
    description="A high-performance, low-latency interconnect designed for embedded systems needing deterministic, packet-switched communication (e.g., telecom, radar).",
    how_it_works="Packet-switched serial fabric supporting both message-passing and memory-mapped transactions with very low, deterministic latency.",
    speed="Up to 10+ Gbps per lane",
    use_cases=["Telecom base stations","Military radar/signal processing systems","Multi-DSP/FPGA systems"],
    advantages=["Deterministic low latency, ideal for real-time DSP clusters","Supports both message and memory-mapped semantics"],
    limitations=["Niche compared to PCIe/Ethernet — smaller ecosystem"],
    real_world_example="Multiple DSPs and FPGAs in a radar signal-processing system exchanging data deterministically over RapidIO.",
    difficulty="Advanced", related=["pcie","aurora"])

add(id="aurora", name="Aurora (Xilinx/AMD Protocol)", category="High-Speed/FPGA", topology="Point-to-Point",
    year=2003, inventor="Xilinx (now AMD)", place="USA", organization="Xilinx/AMD",
    description="A lightweight, open, license-free serial protocol from Xilinx for chip-to-chip or board-to-board links using FPGA transceivers (GTX/GTH/GTY).",
    how_it_works="Simple frame/streaming layer built directly on FPGA high-speed serial transceivers, requiring minimal logic overhead versus PCIe's complex stack.",
    speed="Up to 100+ Gbps aggregate (multi-lane, depends on transceiver generation)",
    use_cases=["FPGA-to-FPGA high-speed links","Custom high-speed data acquisition backplanes"],
    advantages=["Very simple to implement compared to PCIe/Ethernet MAC","Open/free — no licensing fee, Xilinx-provided IP core"],
    limitations=["Primarily Xilinx/AMD FPGA ecosystem-specific"],
    real_world_example="Two FPGA boards in a data-acquisition system exchanging captured ADC samples over an Aurora link.",
    difficulty="Advanced", related=["pcie","serdes"])

add(id="jesd204", name="JESD204B/C", category="High-Speed/FPGA", topology="Point-to-Point",
    year=2006, inventor="JEDEC", place="USA", organization="JEDEC",
    description="A standardized high-speed serial interface specifically for connecting data converters (ADCs/DACs) to FPGAs/ASICs, replacing wide parallel LVDS buses.",
    how_it_works="Serializes ADC/DAC data over 1-8+ high-speed serial lanes with deterministic latency and frame alignment characters, drastically reducing pin count vs parallel interfaces.",
    speed="Up to 32 Gbps per lane (JESD204C)",
    use_cases=["High-speed/high-resolution ADC and DAC interfacing (radar, software-defined radio, instrumentation)"],
    advantages=["Massively reduces pin count vs parallel ADC/DAC interfaces","Deterministic latency important for multi-channel phase-coherent systems"],
    limitations=["Complex link establishment (SYNC/SYSREF) procedures"],
    real_world_example="A software-defined radio's high-speed ADC streaming samples to an FPGA over JESD204B.",
    difficulty="Advanced", related=["pcie","aurora"])

add(id="serdes", name="SERDES (generic)", category="High-Speed/FPGA", topology="Point-to-Point",
    year=1990, inventor="Various (general industry technique)", place="International",
    description="Not a single protocol but the general SERializer/DESerializer technique underlying most modern high-speed serial links (PCIe, SATA, Ethernet, etc.).",
    how_it_works="Parallel data is serialized into a high-speed differential stream (often with 8b/10b or 64b/66b encoding for clock recovery/DC balance), then deserialized at the receiver.",
    speed="Ranges from ~1 Gbps to 100+ Gbps per lane depending on generation",
    use_cases=["Underlying technology for PCIe, SATA, Ethernet (SGMII/XAUI), Aurora, JESD204"],
    advantages=["Drastically reduces pin count for high-bandwidth links","Enables multi-Gbps transmission over ordinary PCB traces/cables"],
    limitations=["Requires careful PHY design (equalization, clock recovery) at high speeds"],
    real_world_example="Every modern high-speed interface (PCIe, SATA, USB3, Ethernet) relies on SERDES at the physical layer.",
    difficulty="Advanced", related=["pcie","sgmii","aurora"])

add(id="sgmii", name="SGMII", category="High-Speed/FPGA", topology="Point-to-Point",
    year=2001, inventor="Cisco Systems", place="USA",
    description="Serial Gigabit Media Independent Interface — a serialized version of the GMII interface connecting a MAC to a PHY chip.",
    how_it_works="Serializes the parallel GMII data/control lines onto a single differential SERDES pair, reducing pin count between the Ethernet MAC (in an FPGA/SoC) and the external PHY.",
    speed="1.25 Gbps (to carry 1000 Mbps Ethernet data + control)",
    use_cases=["FPGA/SoC Ethernet MAC-to-PHY connections"],
    advantages=["Far fewer pins than parallel GMII/RGMII for MAC-PHY connection"],
    limitations=["Requires SERDES-capable FPGA/SoC transceiver"],
    real_world_example="An FPGA's Ethernet MAC connecting to an external Gigabit PHY chip via SGMII to save pins.",
    difficulty="Advanced", related=["rgmii","serdes","ethernet"])

add(id="rgmii", name="RGMII", category="High-Speed/FPGA", topology="Point-to-Point",
    year=2002, inventor="Multiple vendors (Broadcom, Marvell, etc.)", place="USA",
    description="Reduced GMII — a pin-reduced parallel interface between an Ethernet MAC and PHY, using both clock edges to halve pin count vs full GMII.",
    how_it_works="Uses DDR (double data rate) signaling on 4 data lines (vs GMII's 8) by transferring data on both rising and falling clock edges.",
    speed="1000 Mbps (Gigabit Ethernet)",
    use_cases=["Embedded Linux boards' Ethernet MAC-to-PHY connection (common on Raspberry Pi-class SoCs)"],
    advantages=["Fewer pins than GMII while remaining a simple parallel-style interface (no SERDES needed)"],
    limitations=["Still more pins than SGMII; sensitive to trace-length matching for DDR timing"],
    real_world_example="A typical embedded Linux SoC's onboard Ethernet controller talking to an external PHY chip via RGMII.",
    difficulty="Advanced", related=["sgmii","ethernet"])

add(id="xaui", name="XAUI", category="High-Speed/FPGA", topology="Point-to-Point",
    year=2002, inventor="IEEE 802.3ae task force", place="USA", organization="IEEE",
    description="10 Gigabit Attachment Unit Interface — an early standard for extending the physical reach of 10 Gigabit Ethernet MAC-to-PHY connections.",
    how_it_works="Uses 4 lanes of 3.125 Gbps SERDES with 8b/10b encoding to carry 10G Ethernet data between chips on a board or across a short cable.",
    speed="10 Gbps (4 x 3.125 Gbps lanes)",
    use_cases=["10 Gigabit Ethernet chip-to-chip/module interconnects (largely historical, superseded by XFI/SFI)"],
    advantages=["Extended electrical reach vs direct parallel 10G interfaces of its era"],
    limitations=["Largely superseded by simpler single-lane XFI/SFI interfaces in modern designs"],
    real_world_example="Early 10 Gigabit Ethernet switch line cards connecting MAC and PHY chips via XAUI.",
    difficulty="Advanced", related=["sgmii","ethernet"])

# =====================================================================
# CATEGORY 10: SENSOR-SPECIFIC
# =====================================================================
add(id="iolink", name="IO-Link", category="Sensor-Specific", topology="Point-to-Point",
    year=2009, inventor="IO-Link Consortium (Balluff, Festo, Siemens, etc.)", place="Germany", organization="IO-Link Community",
    description="A standardized point-to-point communication protocol that digitizes the connection between simple industrial sensors/actuators and a controller, over the existing 3-wire cable.",
    how_it_works="Overlays digital communication on the standard 3-wire sensor cable (24V, GND, switching signal becomes a digital comms line), enabling parameterization and diagnostics alongside the process data.",
    speed="4.8 / 38.4 / 230.4 kbps (COM1/2/3)",
    use_cases=["Smart industrial sensors/actuators with remote configuration/diagnostics"],
    advantages=["Uses standard, unshielded 3-wire sensor cabling","Enables remote parameterization/diagnostics of simple sensors"],
    limitations=["Point-to-point only (needs an IO-Link master to aggregate multiple sensors)"],
    real_world_example="A proximity sensor on a production line reporting not just on/off but also temperature and duty-cycle diagnostics via IO-Link.",
    difficulty="Intermediate", related=["hart","modbus_rtu"])

add(id="dsi3", name="DSI3", category="Sensor-Specific", topology="Bus (Master-Slave)",
    year=2011, inventor="DSI Consortium (Bosch, Infineon, etc.)", place="Germany",
    description="Distributed System Interface 3 — a current-modulated automotive sensor bus, evolution of DSI/PSI5 for connecting multiple sensors on one bus.",
    how_it_works="Master supplies power and clock via current modulation; multiple slaves can share the same 2-wire bus, responding in synchronized time slots.",
    speed="Up to 200 kbps",
    use_cases=["Automotive pressure/acceleration sensor networks"],
    advantages=["Multiple sensors on a single 2-wire bus (vs point-to-point PSI5)","Robust current-loop signaling"],
    limitations=["Automotive-specific, limited outside that domain"],
    real_world_example="Multiple tire-pressure or suspension sensors sharing a single DSI3 bus back to a central ECU.",
    difficulty="Advanced", related=["psi5","sent"])

# =====================================================================
# CATEGORY 11: SECURITY PROTOCOLS
# =====================================================================
add(id="tls", name="TLS / SSL", category="Security", topology="Point-to-Point (over TCP)",
    year=1995, inventor="Netscape (SSL) → IETF (TLS)", place="USA", organization="Netscape Communications (SSL 2.0, 1995); IETF TLS working group from 1996, TLS 1.0 = RFC 2246 (1999)",
    description="Transport Layer Security (successor to the original Netscape SSL) — the cryptographic protocol securing virtually all HTTPS web traffic.",
    how_it_works="A handshake negotiates cipher suites and exchanges keys (via asymmetric crypto), then symmetric encryption protects the actual data for speed.",
    use_cases=["HTTPS web security","Securing MQTT/IoT cloud connections"],
    advantages=["Provides confidentiality, integrity, and authentication","Continuously updated to counter new cryptographic attacks"],
    limitations=["Adds computational overhead — can be costly for very constrained MCUs (mitigated by TLS-PSK, DTLS)"],
    real_world_example="The padlock icon in your browser indicating your connection to a website is TLS-encrypted.",
    difficulty="Advanced", related=["dtls","http","mqtt"])

add(id="dtls", name="DTLS", category="Security", topology="Point-to-Point (over UDP)",
    year=2006, inventor="IETF", place="International", organization="IETF (RFC 4347/6347)",
    description="Datagram TLS — brings TLS-equivalent security to UDP-based protocols, which don't have TCP's built-in ordering/retransmission.",
    how_it_works="Adapts the TLS handshake and record protocol to tolerate packet loss and reordering inherent to UDP.",
    use_cases=["Securing CoAP IoT traffic","VPN protocols (e.g., OpenVPN, DTLS-based VPNs)"],
    advantages=["Brings TLS-grade security to latency-sensitive/lossy UDP applications"],
    limitations=["More complex to implement correctly than TLS due to UDP's unreliable nature"],
    real_world_example="A constrained IoT sensor securing its CoAP messages using DTLS instead of full TLS/TCP.",
    difficulty="Advanced", related=["tls","coap","udp"])

add(id="ipsec", name="IPSec", category="Security", topology="Point-to-Point / Site-to-Site",
    year=1995, inventor="IETF", place="International", organization="IETF",
    description="A suite of protocols securing IP communications at the network layer, commonly used for VPNs.",
    how_it_works="Authentication Header (AH) and Encapsulating Security Payload (ESP) provide authentication/encryption; IKE negotiates keys between endpoints.",
    use_cases=["Site-to-site VPNs","Securing remote industrial control system links"],
    advantages=["Network-layer security transparent to applications above it","Widely supported in routers/firewalls"],
    limitations=["Complex configuration (especially NAT traversal)"],
    real_world_example="Two factory sites connected via an IPSec VPN tunnel over the public internet for secure SCADA data exchange.",
    difficulty="Advanced", related=["tls"])

add(id="wpa", name="WPA2 / WPA3", category="Security", topology="Point-to-Point (Wi-Fi)",
    year=2004, inventor="Wi-Fi Alliance", place="USA", organization="Wi-Fi Alliance",
    description="The security protocols protecting Wi-Fi networks from eavesdropping and unauthorized access.",
    how_it_works="WPA2 uses AES-CCMP encryption with a 4-way handshake for key exchange; WPA3 adds SAE (Simultaneous Authentication of Equals) to resist offline dictionary attacks.",
    use_cases=["Securing home/office/industrial Wi-Fi networks"],
    advantages=["WPA3's SAE handshake resists the KRACK-style and dictionary attacks that affected WPA2"],
    limitations=["WPA2 has known vulnerabilities (KRACK); legacy device support sometimes forces fallback to weaker WPA2"],
    real_world_example="Your home Wi-Fi router requiring a WPA2/WPA3 password before allowing devices to join.",
    difficulty="Intermediate", related=["wifi","macsec"])

add(id="macsec", name="MACsec", category="Security", topology="Point-to-Point (Ethernet, link layer)",
    year=2006, inventor="IEEE 802.1AE working group", place="USA", organization="IEEE",
    description="Provides encryption and integrity protection at the Ethernet (Layer 2) level, securing traffic between directly connected switches/devices.",
    how_it_works="Encrypts and authenticates Ethernet frames hop-by-hop between MACsec-capable devices, transparent to higher-layer protocols like IP/TCP.",
    use_cases=["Securing links between data center switches","Protecting industrial Ethernet backbones"],
    advantages=["Line-rate encryption transparent to upper layers","Protects against physical-layer eavesdropping/tapping on the wire itself"],
    limitations=["Requires MACsec-capable hardware on both ends of each link"],
    real_world_example="Two data center switches encrypting all Ethernet frames between them using MACsec to prevent physical wiretapping.",
    difficulty="Advanced", related=["ethernet","ipsec"])

# =====================================================================
# CATEGORY 12: AEROSPACE / DEFENSE
# =====================================================================
add(id="arinc429", name="ARINC 429", category="Aerospace", topology="Point-to-Point (broadcast, unidirectional)",
    year=1977, inventor="Aeronautical Radio, Inc. (ARINC)", place="USA", organization="ARINC Industry Activities (the standards body was sold to SAE International in Jan 2014; Collins Aerospace bought the separate ARINC business)",
    description="The most widely used avionics data bus standard, defining how flight computers and instruments exchange data in most commercial aircraft.",
    how_it_works="Unidirectional, single-transmitter/multiple-receiver broadcast on a twisted pair, sending fixed 32-bit words at one of two speeds.",
    speed="12.5 kbps (Low Speed) or 100 kbps (High Speed)",
    frame_fields=[{"name":"Label","bits":8},{"name":"SDI","bits":2},{"name":"Data","bits":19},{"name":"SSM","bits":2},{"name":"Parity","bits":1}],
    use_cases=["Commercial aircraft avionics (flight computers, navigation instruments)"],
    advantages=["Extremely robust and deterministic — decades of proven reliability","Simple unidirectional broadcast simplifies certification/analysis"],
    limitations=["Low bandwidth by modern standards","Unidirectional — needs a separate bus per direction, increasing wiring"],
    real_world_example="A Boeing 737's flight management computer broadcasting airspeed data to multiple cockpit instruments via ARINC 429.",
    difficulty="Advanced", related=["arinc664","mil1553"])

add(id="arinc664", name="ARINC 664 (AFDX)", category="Aerospace", topology="Switched (Ethernet-based)",
    year=2003, inventor="Airbus / ARINC", place="France/USA", organization="ARINC Industry Activities (now under SAE ITC)",
    description="Avionics Full-Duplex Switched Ethernet — brings switched Ethernet's bandwidth to modern aircraft while adding deterministic guarantees ARINC 429 lacked.",
    how_it_works="Standard Ethernet hardware with 'Virtual Links' that guarantee bandwidth and deterministic timing for each data flow through redundant dual switched networks.",
    speed="10/100 Mbps",
    use_cases=["Modern aircraft avionics networks (Airbus A380, A350, Boeing 787)"],
    advantages=["Much higher bandwidth than ARINC 429","Deterministic guarantees despite using standard Ethernet hardware"],
    limitations=["More complex certification/configuration (Virtual Link bandwidth allocation)"],
    real_world_example="The Airbus A380's avionics systems communicating over redundant AFDX switched Ethernet networks.",
    difficulty="Advanced", related=["arinc429","ethernet"])

add(id="mil1553", name="MIL-STD-1553", category="Aerospace", topology="Bus (Bus Controller/Remote Terminal)",
    year=1973, inventor="US Department of Defense / SAE", place="USA", organization="US DoD",
    description="A military standard data bus used extensively in aircraft, spacecraft, and ships for mission-critical, highly deterministic communication.",
    how_it_works="A single Bus Controller polls up to 31 Remote Terminals in a strict command-response protocol over a redundant dual-redundant twisted-shielded pair.",
    speed="1 Mbps",
    use_cases=["Military aircraft avionics","Spacecraft subsystems","Some legacy industrial/defense systems"],
    advantages=["Extremely deterministic, proven reliability in mission-critical systems","Dual-redundant bus for fault tolerance"],
    limitations=["Low bandwidth by modern standards","Costly, specialized transceivers/hardware"],
    real_world_example="An F-16 or similar military aircraft's flight control computer communicating with sensors/actuators via a redundant MIL-STD-1553 bus.",
    fun_fact="MIL-STD-1553 was published in 1973 and is still specified for new military and spacecraft designs — the James Webb Space Telescope, launched in 2021, uses a 1553 bus for command and telemetry.",
    fun_fact_source="MIL-STD-1553B; NASA JWST observatory command & data handling documentation.",
    difficulty="Advanced", related=["spacewire","arinc429"])

add(id="spacewire", name="SpaceWire", category="Aerospace", topology="Point-to-Point (switched network)",
    year=2003, inventor="European Space Agency (ESA)", place="Europe", organization="ESA",
    description="A spacecraft onboard data-handling network standard, combining ideas from IEEE 1355 and Ethernet-like switching for satellites and space probes.",
    how_it_works="Point-to-point full-duplex LVDS links connected through routing switches, supporting both high-speed data and low-latency time-code distribution across a spacecraft.",
    speed="2 Mbps – 400 Mbps",
    use_cases=["Satellite/spacecraft onboard data handling","Space telescope instrument data links (e.g., contributing heritage to JWST-era designs)"],
    advantages=["Designed for the radiation/reliability demands of space","Flexible switched network topology"],
    limitations=["Specialized, space-industry-specific ecosystem"],
    real_world_example="ESA and NASA spacecraft using SpaceWire to connect onboard computers, instruments, and mass memory.",
    difficulty="Advanced", related=["mil1553"])

# Write JSON
out_path = os.path.join(os.path.dirname(__file__), "data", "protocols.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(P, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(P)} protocols to {out_path}")

# sanity: category counts
c = Counter(p["category"] for p in P)
for k, v in sorted(c.items()):
    print(f"  {k}: {v}")
