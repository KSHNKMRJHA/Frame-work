# -*- coding: utf-8 -*-
"""Physical wiring, addressing, and command tables for every protocol.

Three things live here, all keyed by protocol id:

SIGNALS   the actual conductors: name, direction, what it does. This is what
          makes a pinout diagram real ("TXD = transmit data, RS-232 levels")
          rather than just a list of names.
ADDRESSING how a protocol identifies a node (7-bit I2C, 8-bit Modbus slave
          address, 29-bit J1939 PGN, MAC, URL path...). Protocols that are
          connectionless or have no addressing say so explicitly.
COMMANDS  the protocol's own command/opcode vocabulary (Modbus function codes,
          HTTP methods, MQTT control packet types, USB request codes, AT
          commands...). Protocols without a command set get an empty list.

Only well-documented facts are listed. Where a protocol genuinely has no
addressing or command set, the entry is empty and the UI says so rather than
inventing one.
"""
from copy import deepcopy


def s(name, direction, description, extra=None):
    """One conductor: name, direction (A=input/B=bidir/O=output/G=ground/P=power),
    what it carries, and optionally role notes."""
    row = {"name": name, "dir": direction, "description": description}
    if extra:
        row["extra"] = extra
    return row


# ------------------------------------------------------- SIGNALS / WIRING --
# Direction codes: O = output from host, I = input to host, B = bidirectional,
# P = power, G = ground/reference.
SIGNALS = {
    "uart": [s("TXD", "O", "Transmit data", "idle high, start bit low"),
             s("RXD", "I", "Receive data"),
             s("GND", "G", "Signal reference"),
             s("VCC", "P", "Supply for the transceiver, not the cable")],
    "rs232": [s("TXD", "O", "Transmit data (bipolar)"),
              s("RXD", "I", "Receive data"),
              s("GND", "G", "Signal ground (required)"),
              s("DTR", "O", "Data terminal ready"), s("DSR", "I", "Data set ready"),
              s("RTS", "O", "Request to send"), s("CTS", "I", "Clear to send")],
    "rs485": [s("A", "I/O", "Non-inverting differential input"),
              s("B", "I/O", "Inverting differential input"),
              s("GND", "G", "Common reference / shield drain")],
    "spi": [s("SCLK", "O", "Serial clock, master-generated"),
            s("MOSI", "O", "Master-out slave-in data"),
            s("MISO", "I", "Master-in slave-out data"),
            s("CS/SS", "O", "Chip select, one per slave"),
            s("GND", "G", "Common ground")],
    "i2c": [s("SDA", "B", "Serial data, open-drain"),
            s("SCL", "O", "Serial clock, open-drain"),
            s("VCC", "P", "Pull-up supply (open-drain lines rise to this)"),
            s("GND", "G", "Common ground")],
    "can": [s("CAN_H", "B", "Differential high line"),
            s("CAN_L", "B", "Differential low line"),
            s("GND", "G", "Common reference")],
    "lin": [s("LIN", "B", "Single-wire bus (wake-up, sync, data)"),
            s("GND", "G", "Vehicle ground")],
    "ethernet": [s("TX+/-", "O", "Transmit differential pair"),
                 s("RX+/-", "I", "Receive differential pair"),
                 s("LED1/2", "O", "Link/activity indicator pairs"),
                 s("SHIELD", "G", "Connector shield")],
    "usb20": [s("D+", "B", "Differential data plus"),
              s("D-", "B", "Differential data minus"),
              s("VBUS", "P", "5 V bus power"),
              s("GND", "G", "Return path")],
    "rs422": [s("TX+/TX-", "O", "Balanced transmit pair"),
              s("RX+/RX-", "I", "Balanced receive pair"),
              s("GND", "G", "Optional reference")],
    "i2s": [s("BCLK", "O", "Bit clock"),
            s("WS", "O", "Word select / channel select"),
            s("SDATA", "I", "Serial data in"),
            s("MCLK", "O", "Master clock (MCLK/LRCLK)")],
    "lvds": [s("Tx pair", "O", "Low-voltage differential transmit pair"),
             s("Rx pair", "I", "Differential receive pair"),
             s("GND", "G", "Reference")],
    "arinc429": [s("A", "O", "Non-inverting (+6.5 to +10 V)"),
                 s("B", "O", "Inverting (-6.5 to -10 V)"),
                 s("SHIELD", "G", "Shield / reference")],
}
# ------------------------------------------------------------- ADDRESSING --
# How each protocol identifies a node/endpoint. Protocols with no addressing
# concept get "" and an explicit reason, so the UI never implies one exists.
ADDRESSING = {
    "i2c": "7-bit or 10-bit slave address in the first byte after START; 0x00 = "
           "general call, 0x7F = reserved (10-bit uses a 11110xxxx prefix).",
    "i3c": "7-bit device address plus a 4-bit bus-controller/arbitration byte "
           "(S0/S1) in the header; 0x00 = broadcast.",
    "spi": "No address on the wire - the peripheral is selected by its dedicated "
           "CS/SS pin, so addressing is a pinout property, not a frame field.",
    "uart": "No addressing in the frame - a UART is point-to-point; multidrop uses "
            "RTS/CTS or a separate transceiver per device.",
    "rs485": "No address on the wire - nodes share the bus and are separated by the "
             "application protocol's addressing.",
    "can": "11-bit (standard) or 29-bit (extended) identifier in the arbitration "
           "field; the numerically lowest ID wins arbitration.",
    "modbus_rtu": "1-247 slave address (0 = broadcast), carried as the first byte "
                  "of every frame; 248-255 reserved.",
    "modbus_tcp": "Unit ID (1-255) inside the PDU, plus the 32-bit Transaction ID "
                  "that pairs a request with its response.",
    "lin": "Unicast IDs 0x00-0x3F; publisher IDs 0x80-0xFF; 0xFF addresses all nodes.",
    "usb20": "7-bit device address assigned during enumeration (0-127); the "
             "endpoint number is carried in the PID.",
    "ethernet": "48-bit MAC address in the frame header; FF:FF:FF:FF:FF:FF is broadcast.",
    "ip": "32-bit IPv4 address in the header, scoped by subnet mask and gateway.",
    "mqtt": "No address in the frame - a broker fans messages out to topic "
            "subscriptions; the client is identified by its TCP connection.",
    "coap": "The URI path or token identifies the resource; no fixed address field.",
    "http": "URL path plus Host header identify the resource; no address field.",
    "wifi": "48-bit MAC address is the station identifier.",
    "zigbee": "16-bit PAN address plus a 16/64-bit IEEE device address; 0xFFFE is "
              "the coordinator and 0xFFFF is the broadcast address.",
    "arinc429": "8-bit label (LBN/LSS) in the first word identifies the data source; "
                "labels 0-127 are conventional.",
}
# ---------------------------------------------------------------- COMMANDS --
# Protocol-defined command/opcode vocabularies: (code, name, note).
COMMANDS = {
    "modbus_rtu": [
        ("0x01", "Read Coils", "read 1-2000 discrete outputs"),
        ("0x02", "Read Discrete Inputs", "read 1-2000 discrete inputs"),
        ("0x03", "Read Holding Registers", "read 1-125 16-bit registers"),
        ("0x04", "Read Input Registers", "read 1-125 16-bit input registers"),
        ("0x05", "Write Single Coil", "write one coil"),
        ("0x06", "Write Single Register", "write one holding register"),
        ("0x0F", "Write Multiple Coils", "write 1-1968 coils"),
        ("0x10", "Write Multiple Registers", "write 1-123 registers"),
    ],
    "http": [
        ("GET", "GET", "retrieve a resource"),
        ("POST", "POST", "submit data / create"),
        ("PUT", "PUT", "replace a resource"),
        ("DELETE", "DELETE", "remove a resource"),
        ("PATCH", "PATCH", "partial update"),
        ("HEAD", "HEAD", "headers only"),
        ("OPTIONS", "OPTIONS", "query capabilities / CORS"),
    ],
    "mqtt": [
        ("1", "CONNECT", "client -> broker, opens a session"),
        ("2", "CONNACK", "broker -> client, accepts the session"),
        ("3", "PUBLISH", "publish a message"),
        ("4", "PUBACK", "QoS 1 acknowledgement"),
        ("5", "PUBREC / PUBREL", "QoS 2 handshake"),
        ("6", "PUBCOMP", "QoS 2 completion"),
        ("8", "SUBSCRIBE", "subscribe to topics"),
        ("9", "SUBACK", "subscribe acknowledgement"),
        ("10", "UNSUBSCRIBE", "unsubscribe"),
        ("12", "PINGREQ / PINGRESP", "keep-alive"),
        ("14", "DISCONNECT", "graceful close"),
    ],
    "coap": [
        ("0.01", "GET", "retrieve a resource"),
        ("0.02", "POST", "create / submit"),
        ("0.03", "PUT", "update"),
        ("0.04", "DELETE", "remove"),
        ("2.01", "Created", "response to POST"),
        ("2.02", "Deleted", "response to DELETE"),
        ("4.04", "Not Found", "resource does not exist"),
        ("5.00", "Internal Server Error", "server-side failure"),
    ],
    "canopen": [
        ("0x000", "NMT", "network management (start/stop a node)"),
        ("0x080", "SYNC", "synchronise process data objects"),
        ("0x180+ID", "TPDO1", "transmit process data object 1"),
        ("0x480+ID", "RPDO1", "receive process data object 1"),
        ("0x580+ID", "SDO response", "service data object reply"),
        ("0x600+ID", "SDO Rx/Tx", "service data object transfer"),
    ],
    "usb20": [
        ("GET_DESCRIPTOR", "Get Descriptor", "read device configuration"),
        ("SET_ADDRESS", "Set Address", "assign the bus address"),
        ("SET_CONFIGURATION", "Set Configuration", "choose a working configuration"),
        ("GET_STATUS", "Get Status", "device state"),
        ("CLEAR_FEATURE / SET_FEATURE", "Feature control", "halt, remote wakeup"),
    ],
}


# Carrier chains: a logical protocol has no conductors of its own - its wiring
# is whatever carries it. Following the chain down to a physical protocol is the
# honest way to answer "what do I actually plug in?".
CARRIERS = {
    "http": "tcp", "ftp": "tcp", "telnet_ssh": "tcp", "ntp": "udp", "mdns": "udp",
    "snmp": "udp", "dhcp": "udp", "dns": "udp", "coap": "udp",
    "tcp": "ip", "udp": "ip", "arp": "ethernet", "icmp": "ip", "ip": "ethernet",
    "websocket": "tcp", "mqtt": "tcp",
    "tls": "tcp", "dtls": "udp", "ipsec": "ip", "wpa": "wifi", "macsec": "ethernet",
    "modbus_tcp": "tcp", "profinet": "ethernet", "ethercat": "ethernet",
    "ethernetip": "tcp", "opcua": "tcp", "bacnet": "ethernet", "dnp3": "tcp",
    "someip": "ethernet", "doip": "tcp", "foundation_fieldbus": "ethernet",
    "powerlink": "ethernet", "sercos": "ethernet", "tsn": "ethernet", "dds": "udp",
    "hart": "rs485", "wirelesshart": "sub_ghz_radio", "knx": "twisted_pair_knx",
    "mbus": "rs485", "lonworks": "twisted_pair_knx", "dmx512": "rs485",
    "dali": "dali_pair",
    "ble": "ble_radio", "bluetooth_classic": "ble_radio", "antplus": "ble_radio",
    "zigbee": "ieee802154", "thread": "ieee802154", "zwave": "sub_ghz_radio",
    "uwb": "uwb_radio", "nfc": "nfc_radio", "rfid": "rf_radio",
    "sigfox": "sub_ghz_radio", "lorawan": "lora_radio", "lora": "lora_radio",
    "gsm": "cellular_radio", "lte": "cellular_radio", "ltem": "cellular_radio",
    "nbiot": "cellular_radio", "5g": "cellular_radio", "wifi": "wifi_radio",
    "matter": "thread_802154", "6lowpan": "ieee802154",
    "uds": "isotp", "isotp": "can", "j1939": "can", "obd2": "can",
    "xcp": "can", "canopen": "can", "devicenet": "can", "can_xl": "can",
    "automotive_ethernet": "ethernet", "flexray": "flexray", "most": "most",
    "sent": "sent", "psi5": "psi5", "t1s": "automotive_ethernet", "kline": "kline",
    "mavlink": "uart", "cyphal": "uart", "nmea": "uart",
    "nvme": "pcie", "sata": "sata_phy", "ufs": "pcie",
    "jtag": "jtag", "swd": "swd", "mipi_dsi": "mipi_dsi", "mipi_csi": "mipi_csi",
    "hdmi": "hdmi", "displayport": "dp", "tdm": "i2s", "pcm": "i2s",
    "spdif": "spdif", "firewire": "firewire", "midi": "midi",
    "iolink": "iolink", "dsi3": "dsi3", "rs232": "rs232", "1wire": "one_wire",
    "i3c": "i2c", "smbus": "i2c", "pmbus": "i2c", "qspi": "spi", "microwire": "spi",
    "modbus_rtu": "rs485", "profibus": "rs485", "lin": "lin", "can_fd": "can",
    "usb3x": "usb20", "usbc": "usb20", "usb11": "usb20", "usbhid": "usb20",
    "usbmsc": "usb20", "usbdfu": "usb20", "usbcdc": "usb20",
"pcie": "pcie", "sgmii": "ethernet", "rgmii": "ethernet", "xaui": "ethernet",
    "aurora": "serdes", "rapidio": "rapidio", "jesd204": "jesd204", "serdes": "serdes",
    "spacewire": "spacewire", "mil1553": "mil1553", "arinc664": "arinc664",
    "sdio": "sdio", "emmc": "emmc", "mdio": "mdio", "parallel": "parallel_bus",
    "usb4": "usb4",
}


# Physical media that are not wired pin pairs: RF ports and special media.
MEDIA_SIGNALS = {
    "cellular_radio": [s("ANT", "B", "Antenna port (RF)", "50 Ohm, matched to the radio"),
                       s("GND", "G", "Chassis/board ground")],
    "wifi_radio": [s("ANT / RF", "B", "Antenna or u.FL/IPEX connector"),
                   s("GND", "G", "Board ground")],
    "ble_radio": [s("ANT", "B", "Antenna (2.4 GHz)"), s("GND", "G", "Board ground")],
    "ieee802154": [s("ANT", "B", "Antenna (2.4 GHz)"), s("GND", "G", "Board ground")],
    "thread_802154": [s("ANT", "B", "2.4 GHz antenna"), s("GND", "G", "Board ground")],
    "sub_ghz_radio": [s("ANT", "B", "Sub-GHz antenna"), s("GND", "G", "Board ground")],
    "lora_radio": [s("ANT", "B", "Antenna (LoRa)"), s("GND", "G", "Board ground")],
    "nfc_radio": [s("LOOP", "B", "13.56 MHz coil/antenna"), s("GND", "G", "Board ground")],
    "rf_radio": [s("ANT", "B", "UHF antenna"), s("GND", "G", "Board ground")],
    "uwb_radio": [s("ANT", "B", "UWB antenna"), s("GND", "G", "Board ground")],
    "twisted_pair_knx": [s("TP", "B", "Twisted pair (KNX TP1)"), s("GND", "G", "Reference")],
    "dali_pair": [s("D+", "B", "Data+ pair"), s("D-", "B", "Data- pair"), s("GND", "G", "Return")],
    "sata_phy": [s("TX pair", "O", "SATA transmit pair"), s("RX pair", "I", "SATA receive pair")],
    "jtag": [s("TCK", "O", "Test clock"), s("TMS", "O", "Test mode select"),
             s("TDI", "O", "Data in"), s("TDO", "I", "Data out"), s("GND", "G", "Ground")],
    "swd": [s("SWCLK", "O", "Debug clock"), s("SWDIO", "B", "Debug data"),
            s("GND", "G", "Ground"), s("3V3", "P", "Target reference voltage")],
    "mipi_dsi": [s("CLK+", "O", "Clock lane pair"), s("CLK-", "O", "Clock lane return"),
                 s("D0+/D0- .. D3+/D3-", "O", "Four data lane pairs"), s("GND", "G", "Ground")],
    "mipi_csi": [s("CLK+", "O", "Clock lane pair"), s("D0+/D0- .. D3+/D3-", "O", "Data lanes")],
    "hdmi": [s("TMDS pairs x3", "B", "Differential TMDS lanes"), s("HPD", "I", "Hot plug detect")],
    "dp": [s("Main lanes x4", "B", "Differential main link"), s("AUX", "B", "Auxiliary channel")],
    "spdif": [s("COAX", "B", "Coaxial or TOSLINK optical")],
    "firewire": [s("TPA/TPB", "B", "Differential data pairs"), s("GND", "G", "Ground")],
    "midi": [s("MIDI IN/OUT", "B", "5-pin DIN current loop"), s("GND", "G", "Shield")],
    "one_wire": [s("DQ", "B", "1-Wire data (bidirectional, open-drain)"), s("GND", "G", "Ground")],
    "iolink": [s("C/Q", "B", "Single-wire IOLink data"), s("L+", "P", "24 V supply"),
               s("L-", "G", "0 V supply"), s("GND", "G", "Ground")],
    "dsi3": [s("CLK", "O", "Clock"), s("DATA", "B", "Bidirectional data"), s("GND", "G", "Ground")],
    "kline": [s("K", "B", "Single-wire ISO 9141 K-line"), s("L", "B", "L-line (optional)"),
              s("B+", "P", "Battery +12 V"), s("B-", "G", "Battery ground")],
    "spacewire": [s("TX", "O", "Transmit data"), s("RX", "I", "Receive data"),
                  s("HSK", "B", "Handshake"), s("GND", "G", "Return")],
    "mil1553": [s("A", "B", "Data bus high"), s("B", "B", "Data bus low"), s("GND", "G", "Ground")],
    "arinc664": [s("TX+/TX-", "O", "Differential transmit pair"),
                 s("RX+/RX-", "I", "Differential receive pair"), s("GND", "G", "Ground")],
    "flexray": [s("BP", "O", "Bus positive"), s("BN", "O", "Bus negative"), s("GND", "G", "Ground")],
    "most": [s("MST", "B", "Single data line"), s("MCLR", "B", "Control line"), s("GND", "G", "Ground")],
    "sent": [s("SENT", "B", "Single-wire pulse-width signalling"), s("GND", "G", "Ground")],
    "psi5": [s("PSI5", "B", "Single-wire nibble signalling"), s("GND", "G", "Ground")],
    "pcie": [s("TX lanes", "O", "High-speed differential transmit lanes"),
             s("RX lanes", "I", "High-speed differential receive lanes"), s("GND", "G", "Ground")],
    "rapidio": [s("Data lanes", "B", "Symbol lanes"), s("GND", "G", "Ground")],
    "jesd204": [s("LANE+ / LANE-", "B", "High-speed differential lanes"),
                s("REFCLK", "I", "Reference clock")],
    "serdes": [s("TX", "O", "Differential transmit pair"), s("RX", "I", "Differential receive pair")],
    "isotp": [s("(no conductors)", "-", "ISO-TP is carried inside a CAN frame"),
              s("GND", "G", "Ground")],
    # Storage / management buses that are onboard rather than cabled
    "sdio": [s("CLK", "O", "SD clock up to 50 MHz"), s("CMD", "B", "Command/response"),
             s("D0-D3", "B", "Data lines 0-3"), s("VDD", "P", "Card/IO supply"),
             s("GND", "G", "Ground")],
    "emmc": [s("CLK", "O", "SD clock"), s("CMD", "B", "Command/response"),
             s("DAT[0-7]", "B", "1-8 bit data bus"), s("VDD", "P", "Core supply"),
             s("GND", "G", "Ground")],
    "mdio": [s("MDC", "O", "Management clock"), s("MDIO", "B", "Management data"),
             s("GND", "G", "Ground")],
    "parallel_bus": [s("D0-Dn", "B", "Parallel data bus (8/16/32-bit)"),
                     s("A0-An", "O", "Address bus"), s("/CS", "O", "Chip select"),
                     s("/RD, /WR", "O", "Read/write strobes"), s("GND", "G", "Ground")],
    "usb4": [s("TX lanes", "B", "SuperSpeed differential lanes (up to 20 Gbit/s)"),
             s("RX lanes", "B", "Receive lanes"), s("CC1/CC2", "B", "Configuration channel"),
             s("VBUS", "P", "Bus power"), s("GND", "G", "Ground")],
}


def resolve_carrier(pid, _seen=None):
    """Follow CARRIERS until a physical protocol with signals is reached.

    Returns (signals, path) where path is the full chain including both ends,
    so HTTP resolves to ["http", "tcp", "ip", "ethernet"] and the UI can say
    exactly which wires it rides on rather than vaguely "carried over Ethernet".
    """
    seen = _seen if _seen is not None else set()
    if pid in seen:                      # defensive: never loop forever
        return [], []
    seen.add(pid)
    if pid in SIGNALS:
        return deepcopy(SIGNALS[pid]), [pid]
    if pid in MEDIA_SIGNALS:
        return deepcopy(MEDIA_SIGNALS[pid]), [pid]
    nxt = CARRIERS.get(pid)
    if not nxt:
        return [], []
    sigs, chain = resolve_carrier(nxt, seen)
    if not sigs:
        return [], []
    return sigs, [pid] + chain
# ------------------------------------------------------------------ applier --
def apply_physical_io(protocols):
    """Attach signals / addressing / commands to every record.

    A protocol with no conductors of its own inherits them from its carrier
    chain (HTTP -> TCP -> Ethernet -> TX+/RX+) and records that inheritance in
    `signal_source`, so the UI can be explicit about what is real wiring versus
    what is inherited.

    Returns (protocols, with_signals, with_commands, with_addressing) counts.
    """
    n_sig = n_cmd = n_addr = 0
    for p in protocols:
        pid = p["id"]
        sigs, chain = resolve_carrier(pid)
        p["signals"] = sigs
        if sigs:
            n_sig += 1
        # chain is [pid, ...intermediates..., terminal]; the last entry is the
        # protocol that actually supplies the conductors.
        p["signal_source"] = chain[-1] if chain else ""
        p["signal_path"] = " → ".join(chain)
        cmds = COMMANDS.get(pid)
        p["commands"] = [{"code": c, "name": n, "note": d} for c, n, d in cmds] if cmds else []
        if p["commands"]:
            n_cmd += 1
        p["addressing"] = ADDRESSING.get(pid, "")
        if p["addressing"]:
            n_addr += 1
    return protocols, n_sig, n_cmd, n_addr
