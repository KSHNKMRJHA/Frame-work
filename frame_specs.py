# -*- coding: utf-8 -*-
"""Bit-level frame structures for every protocol record.

Field layouts below follow the published specification for each protocol, not
guesswork. Where a standard defines a variable-length or variable-size field the
entry uses a string (e.g. "0-1500") so the diagram can label it honestly and
`frame_note` records what the bit-level bar chart cannot show.

Two invariants are enforced by build_scripts/check_data.py:
  * every field name within a protocol is unique (frame puzzles grade on names)
  * every field has a non-empty bit count
Protocols with no fixed bit-level frame keep frame_fields == [] and carry a
frame_note explaining why; those are listed in NO_FIXED_FRAME.
"""
from copy import deepcopy


def f(name, bits):
    """One frame field: a name plus an int or "lo-hi"/"lo-hi+" string bit count."""
    return {"name": name, "bits": bits}


# id: (fields, frame_note)
FRAME_SPECS = {
    # ------------------------------------------------------ ON-BOARD --------
    "rs232": (
        [f("Start", 1), f("Data", "5-9"), f("Parity (optional)", "0-1"), f("Stop", "1-2")],
        "RS-232 carries UART framing with inverted bipolar levels. A quiet line sits "
        "negative (mark), so a scope on an idle port reads about -12 V, not 0 V.",
    ),
    "rs485": (
        [f("Start", 1), f("Data", "5-9"), f("Parity (optional)", "0-1"), f("Stop", "1-2")],
        "RS-485 defines no framing of its own — it is a differential carrier, so the "
        "frame belongs to the application protocol (Modbus, PROFIBUS, DMX512) using it.",
    ),
    "spi": (
        [f("CS asserted", "1+"), f("Byte stream (8 bits per frame)", "8*n"), f("CS deasserted", "1+")],
        "SPI has no header, length or checksum: CS brackets a raw bit stream whose width "
        "is defined by the peripheral datasheet, not the SPI specification.",
    ),
    "qspi": (
        [f("Command", "1-4"), f("Address", "24-32"), f("Data lanes IO0-IO3", "8*n"), f("Dummy cycles", "0-32")],
        "The command/address header is device-specific (x4 read, page program, read ID). "
        "Widths shown follow the common W25Q-style memory command set.",
    ),
    "i3c": (
        [f("START (S0)", 1), f("Header byte", 8), f("Repeated START (Sr)", 1), f("Address + R/W", 9), f("Data", "8*n"), f("STOP", 1)],
        "I3C keeps I2C framing but replaces the open-drain START with an in-band S0 header "
        "and adds push-pull clock stretching plus bus ownership (MRS/ACK).",
    ),
    "1wire": (
        [f("Reset pulse (low)", "96-768 us"), f("Presence detect (pull-up)", "0-1"), f("ROM code", 64), f("Data slots (reset + write 1)", 1)],
        "1-Wire is not clocked: timing slots encode each bit. The master drives a low "
        "reset, every device answers with a presence pulse, then a 64-bit ROM code is read "
        "LSB-first (family code, 48-bit serial, parity).",
    ),
    "microwire": (
        [f("CS asserted", 1), f("Clock pulses per bit", "8"), f("Byte stream", "8*n"), f("CS deasserted", 1)],
        "MicroWire/Plus is SPI-like but each bit occupies eight clock pulses; the device "
        "samples the line at the middle pulse. There is no standard frame header.",
    ),
    "smbus": (
        [f("START", 1), f("Address + R/W", "7-10"), f("Command code", 8), f("Data", "8*n"), f("STOP", 1)],
        "SMBus adds a command byte between address and data and defines optional timeouts "
        "(T_TIMEOUT) and a PEC byte. It is deliberately a strict subset of I2C.",
    ),
    "pmbus": (
        [f("START", 1), f("Address + R/W", 9), f("Command byte", 8), f("Write-protect", 1), f("Data", "8*n"), f("PEC", 8), f("STOP", 1)],
        "PMBus (SMBus-PM) adds a mandatory PEC (CRC-8) and a write-protect bit for "
        "read-back protection on configuration writes.",
    ),
    "sdio": (
        [f("Command response index", 6), f("Function", 2), f("Block size", 8), f("Argument", 16), f("Data or response", "8*n"), f("CRC7", 8), f("End bit", 1), f("CRC16", 16)],
        "SDIO Command Response (CMD6) carries an argument/response block; the 17-bit "
        "bicycle is wrapped in CRC7 (command) and CRC16 (data) checks.",
    ),
    # -------------------------------------------------- NETWORKING -----------
    "ip": (
        [f("Version + IHL", 4), f("DSCP + ECN", 6), f("Total length", 16), f("Identification", 16), f("Flags + Fragment offset", 16), f("TTL", 8), f("Protocol", 8), f("Header checksum", 16), f("Source address", 32), f("Destination address", 32), f("Options + payload", "0-320")],
        "IHL (in 32-bit words) tells the receiver how much header is options; the payload "
        "is everything after it, so total length is the only integrity check.",
    ),
    "arp": (
        [f("Hardware type", 16), f("Protocol type", 16), f("Hardware size", 8), f("Protocol size", 8), f("Opcode", 16), f("Sender hardware address", "0+"), f("Sender IP address", 32), f("Target hardware address", "0+"), f("Target IP address", 32)],
        "Address widths follow the HW/PROTO size fields, so one frame shape serves "
        "Ethernet/IPv4 and other combinations. ARP is unauthenticated and cacheable.",
    ),
    "dhcp": (
        [f("Operation", 8), f("Hardware type", 8), f("Hardware length", 8), f("Hops", 8), f("Transaction ID", 32), f("Elapsed time", 16), f("Flags", 16), f("Client IP", 32), f("Your IP", 32), f("Server IP", 32), f("Gateway IP", 32), f("Client hardware address", "0+"), f("Server host name", "0+"), f("Boot file name", "0+"), f("Magic cookie", 32), f("Options", "0-312")],
        "The magic cookie 0x63825363 marks the options field as DHCP-specific; options are "
        "type-length-value triples (RFC 3396 renamed them to free htype values).",
    ),
    "dns": (
        [f("Transaction ID", 16), f("Flags", 16), f("Questions", 16), f("Answer RRs", 16), f("Authority RRs", 16), f("Additional RRs", 16), f("Question name", "0+"), f("Question type + class", 32), f("Answer records", "0+")],
        "Name compression lets a pointer (two high bits set) reuse an earlier name, so a "
        "question name can be much shorter than the string it represents.",
    ),
    "icmp": (
        [f("Type", 8), f("Code", 8), f("Checksum", 16), f("Identifier", 16), f("Sequence number", 16), f("Data", "0+")],
        "Echo (types 8/0) fills identifier and sequence number; error types (3, 11, 12) "
        "reinterpret them as the offending packet header plus its first 8 bytes.",
    ),
    "http": (
        [f("Request/status line", "0+"), f("Headers", "0+"), f("Blank line CRLF", 2), f("Body", "0+")],
        "HTTP/1.1 is text with no fixed length — the body ends at Content-Length or is "
        "chunked. HTTP/2 instead uses fixed 9-byte HEADERS frames with HPACK compression.",
    ),
    "ftp": (
        [f("Command line or reply", "0+"), f("CRLF", 2), f("Response text", "0+"), f("Data channel (separate TCP connection)", "0+")],
        "Control and data use two separate TCP connections; data framing follows the TYPE "
        "(A/I) and PORT/PASV mode rather than the reply itself.",
    ),
    "telnet_ssh": (
        [f("SSH packet length", 32), f("Padding length", 8), f("Payload", "0+"), f("Random padding", "0+"), f("MAC", "0+")],
        "Telnet is a raw 7-bit command stream with IAC option negotiation prefixes. SSH "
        "wraps every packet in the binary packet protocol with an optional MAC.",
    ),
    "snmp": (
        [f("Message version", 8), f("Community or Engine ID", "0+"), f("PDU type", 8), f("Request ID", 32), f("Error status + index", 32), f("Variable bindings", "0+")],
        "SNMPv2c added the 64-bit counter64 and the bulk PDU. SNMPv3 replaced the community "
        "string with an engine ID plus authentication and encryption.",
    ),
    # ---------------------------------------------------- AUTOMOTIVE --------
    "can_fd": (
        [f("SOF", 1), f("Identifier (base)", "11-29"), f("RRS + IDE + FDF", 3), f("FDF", 1), f("EDL / res", 4), f("BRS", 1), f("ESI", 1), f("DLC", 4), f("Data", "0-512"), f("Stuff count", 7), f("CRC (17/21-bit)", "17-21"), f("CRC delimiter", 1), f("ACK", 1), f("ACK delimiter", 1), f("EOF", 7)],
        "CAN FD adds a flexible data-rate switch (BRS), up to 64 data bytes, and a "
        "21-bit CRC. Stuffing still applies in the arbitration phase, and the stuff count "
        "is transmitted in the CRC field.",
    ),
    "lin": (
        [f("Break", "≥13 bits"), f("Delimiter", "0-1"), f("Sync 0x55", 8), f("PID (2 parity bits)", 8), f("Data (up to 8 bytes)", "8*n"), f("Checksum", 8)],
        "The header (break, sync 0x55, PID) is master-sent and defines the response; the "
        "checksum is additive over all header and data bytes including protected PID bits.",
    ),
    "flexray": (
        [f("FTS start segment", 11), f("Frame ID", 6), f("Payload length", "0-512"), f("Header CRC", 16), f("Payload", "8*n"), f("Header CRC + Frame CRC", 32), f("BSS + FTS end", "11+")],
        "FlexRay is TDMA: a static segment (time-triggered, fixed slots) and optional "
        "dynamic segment (event-triggered) repeat every cycle, which is what gives "
        "deterministic latency.",
    ),
    "most": (
        [f("Block type + length", 16), f("Source address", 16), f("Destination address", 16), f("Control + parity", 16), f("Data + CRC", "0+")],
        "MOST is a ring/daisy topology with a central master granting transmission slots; "
        "the block header is followed by a payload protected by CRC.",
    ),
    "automotive_ethernet": (
        [f("Destination MAC", 48), f("Source MAC", 48), f("Ethertype", 16), f("VLAN tag (optional)", 32), f("Payload", "0+"), f("FCS", 32)],
        "Automotive Ethernet (100BASE-T1/1000BASE-T1) adds a MACsec-based link, SPoE or "
        "some/IP payload, and is usually carried over twisted pair with a 100 Ω link.",
    ),
    "sent": (
        [f("Sync pulse (20 ns)", "1+"), f("ID (10 bits)", 10), f("Payload nibbles (4/8/12/16)", "4*n"), f("CRC (5 bits)", 5)],
        "SAE J1939-21 SENT encodes 4-, 8-, 12- or 16-bit messages as nibbles after a sync "
        "pulse, protected by a 5-bit CRC over the ID and data.",
    ),
    "psi5": (
        [f("Sync pulse", "1+"), f("Wake-up pulse", "1+"), f("SOF + sync", 8), f("Sync bits", 8), f("Nibble data (4 bits per slot)", "4*n"), f("Parity/CRC bits", 4)],
        "PSI5 slots one 4-bit nibble per symbol after sync and wake pulses, giving the "
        "half-duplex single-wire bus its low cost and deterministic slot timing.",
    ),
    "kline": (
        [f("Start pattern (Sync)", 8), f("Key byte", 8), f("Type + data", "8*n"), f("Checksum (or 'ff')", 8), f("Stop / end-of-line", 1)],
        "K-Line (ISO 9141/14230) uses a slow, bit-banged 5 V bus with a sync pattern and "
        "checksum; it predates high-speed OBD-II CAN.",
    ),
    "uds": (
        [f("Payload length", 16), f("SID + data ID", 8), f("Data", "0+"), f("Positive response SID", 8), f("Response data", "0+")],
        "UDS is an application protocol layered on ISO-TP and CAN; the SID byte selects "
        "the service (0x10 DiagnosticSessionControl, 0x22 ReadDataByIdentifier, ...).",
    ),
    # ------------------------------------------------------ INDUSTRIAL --------
    "modbus_tcp": (
        [f("Transaction ID", 16), f("Protocol ID", 16), f("Length", 16), f("Unit ID", 8), f("Function code", 8), f("Data", "0-253"), f("CRC", 16)],
        "Modbus TCP replaces the RTU CRC with a TCP checksum, so the MBAP header is a "
        "fixed 7 bytes and the PDU matches Modbus RTU's function code + data.",
    ),
    "profibus": (
        [f("SOF (0x68)", 8), f("DA + SA + FC", 11), f("Data length", 6), f("Data", "0-246"), f("FCS (CRC-16)", 16), f("End byte", 8)],
        "PROFIBUS-DP uses a length byte: SOF 0x68, address/function byte, length, user "
        "data, CRC-16, and end byte 0xD7, with rotating token management implicit.",
    ),
    "profinet": (
        [f("FrameID", 16), f("SendClockID", 16), f("Destination ID", 16), f("Source ID", 16), f("Transport size", 16), f("Frame send offset", 16), f("Priority + VLAN", 32), f("DCP/DATA payload", "0+")],
        "PROFINET RT frames are Layer 2 Ethernet with an RT_COLOUR subtype; real-time "
        "data reserves bandwidth via DCP plus a scheduled cycle, and TCP/IP is used for setup.",
    ),
    "ethercat": (
        [f("EtherCAT header", 11), f("EtherType", 16), f("Data length", 11), f("Index", 16), f("Address", 32), f("Irq", 16), f("Data length bits", 11), f("Reserved", 4), f("Payload", "0+"), f("Working counter", 16)],
        "EtherCAT frames pass through all nodes and return with the working counter "
        "incremented per slave read, so one datagram can address a whole segment.",
    ),
    "ethernetip": (
        [f("Encapsulation command", 16), f("Length", 16), f("Session handle", 32), f("Status", 32), f("Sender context", 64), f("Options", 32), f("CIP message", "0+")],
        "EtherNet/IP wraps CIP messages in a TCP/UDP encapsulation header; explicit and "
        "implicit I/O use different encapsulation types.",
    ),
    "devicenet": (
        [f("SOF", 1), f("Preamble", "12-64"), f("Delimiter", 1), f("MAC ID", 12), f("RTR", 1), f("DNET", 8), f("UNET", 8), f("LEN", 8), f("Data", "8*n"), f("CRC", 5), f("End buffer", "16-32")],
        "DeviceNet (CANopen-based) arbitrates with CAN but places a 5-bit CRC and end "
        "buffer in the CAN data payload; CAN identifiers split into priority/MAC fields.",
    ),
    "opcua": (
        [f("Message type + chunking", 8), f("Message size", 24), f("Secure channel ID", 32), f("Security header", "0+"), f("Sequence number", 32), f("Request ID", 32), f("Timestamp", 64), f("Body", "0+")],
        "OPC UA binary encoding is a stack of node IDs plus extension objects; the secure "
        "channel adds a symmetric header (token ID, sequence number, request ID).",
    ),
    "bacnet": (
        [f("BVLC type + function", 16), f("Length", 16), f("NPDU version", 8), f("Control", 8), f("DNET/DLEN/DSN", 24), f("SNET/SLEN/LSN", 16), f("APDU type + flags + segment", "0+"), f("APDU service choice", 8), f("Service parameters", "0+")],
        "BACnet is a stack: BVLC, NPDU (routing), APDU (segmentation), then a service "
        "choice and parameters. Segmented reads use APDU sequence/segment numbers.",
    ),
    "dnp3": (
        [f("Start bytes 0x0564", 16), f("Length", 8), f("Link control", 8), f("Destination", 16), f("Source", 16), f("CRC (16-bit, rolling)", 16), f("Transport control + header", "0+"), f("Application header", "0+"), f("Fragment data", "0+")],
        "DNP3 concatenates link, transport and application fragments into one frame with "
        "a rolling CRC per 16-byte block, so a whole burst can be validated.",
    ),
    "lonworks": (
        [f("Preamble", "0+"), f("Start bit", 1), f("T1 + T2 alternating bits", "0+"), f("Frame data + checksum", "8*n"), f("End byte", 8)],
        "LONWORKS Manchester-encodes bytes with a delta-encoded checksum; the alternating "
        "channel (TP0/TP1) is measured and adjusted adaptively.",
    ),
    "mbus": (
        [f("Start (16 stop bits + 1)", 1), f("Length", 8), f("Address type", 8), f("Primary address", 8), f("Checksum (2 bytes)", 16), f("Command", 8), f("Data + checksum", "0+")],
        "M-Bus uses the idle line as clock: each bit is a 1/1/1 pattern and the checksum "
        "is an 8-bit running sum sent twice for 16-bit integrity.",
    ),
    "foundation_fieldbus": (
        [f("Preamble", "16-32"), f("Start delimiter 0x68", 8), f("Frame type", 8), f("Length", 8), f("Destination address", 8), f("Source address", 8), f("Sequence number", 8), f("Function code", 8), f("Service ID", 16), f("Data", "0+"), f("Frame check (CRC-16)", 16)],
        "FF (IEC 61850) uses a 16-bit CRC over the whole frame plus a leading preamble, "
        "with services addressed by 16-bit IDs rather than offsets.",
    ),
    "powerlink": (
        [f("SOF 0xAA", 8), f("Len + Type", 8), f("Address 1", 8), f("Address 2", 8), f("Control + sequence", 8), f("Data", "0+"), f("CRC-16", 16), f("EOF 0x55", 8)],
        "POWERLINK byte-stuffs 0xA5/0x5A so escaped 0xAA/0x55 data can never be mistaken "
        "for the frame delimiters, then protects it with CRC-16.",
    ),
    # ------------------------------------------------------- SECURITY --------
    "tls": (
        [f("Content type", 8), f("Legacy record version", 16), f("Length", 16), f("Record payload", "0-16384"), f("AEAD tag", 16), f("Explicit IV (pre-TLS1.3)", "0-64")],
        "Every TLS record carries content type, version and length. TLS 1.3 hides the "
        "content type inside the ciphertext (outer byte reads 'application data') and "
        "protects the header itself as additional authenticated data.",
    ),
    "dtls": (
        [f("Content type", 8), f("Version", 16), f("Epoch", 16), f("Sequence number", 48), f("Length", 16), f("Record payload", "0-16384"), f("AEAD tag", 16)],
        "DTLS adds an explicit epoch, a 48-bit sequence number and per-record replay "
        "protection because UDP can reorder and duplicate datagrams.",
    ),
    "ipsec": (
        [f("Next header", 8), f("Payload length", 8), f("SPI", 32), f("Sequence number", 32), f("IV (CBC/CCM)", "0+"), f("ICV", "0+"), f("Encrypted payload", "0+")],
        "Transport mode leaves the IP header in clear for NAT traversal while ESP "
        "encrypts only the payload; tunnel mode (0x04) wraps the whole original datagram.",
    ),
    "wpa": (
        [f("Frame control", 16), f("Duration", 16), f("Address 1", 48), f("Address 2", 48), f("Address 3", 48), f("Sequence control", 16), f("CCMP/GCM header", "0+"), f("Encrypted payload", "0+"), f("MIC / tag", "0+"), f("FCS", 32)],
        "WPA3 replaces the TKIP MIC with an 8-byte GCM tag; SAE (Simultaneous "
        "Authentication of Equals) resists offline dictionary attacks on the PSK.",
    ),
    "macsec": (
        [f("SecTAG (ES/PN/SCI flags)", 16), f("Version", 8), f("SCID / SCI", "0+"), f("SecControl", 8), f("Payload", "0+"), f("ICV", "0+")],
        "MACsec is a Layer 2 (Ethernet) rather than Layer 3 mechanism, so it protects the "
        "same delivery model as the link and needs no IP-layer key exchange.",
    ),
    # --------------------------------------------------------- WIRELESS --------
    "zigbee": (
        [f("Frame control", 16), f("Sequence number", 8), f("Destination PAN ID", 16), f("Destination address", "16-64"), f("Source PAN ID", 16), f("Source address", "16-64"), f("Security header", "0+"), f("Payload", "0+"), f("FCS (16-bit)", 16)],
        "Zigbee inherits IEEE 802.15.4 framing; APS security adds link and network keys, "
        "and the frame control bits tell the receiver which addressing mode applies.",
    ),
    "thread": (
        [f("802.15.4 frame control", 16), f("Sequence number", 8), f("PAN ID", 16), f("Addressing fields", "0+"), f("Mesh header", 16), f("Payload (6LoWPAN or IPv6)", "0+"), f("FCS", 16)],
        "Thread carries 6LoWPAN-compressed IPv6 inside 802.15.4 frames, with a mesh header "
        "for hop-by-hop routing that never appears in the application packet.",
    ),
    "usb11": (
        [f("PID (device address + endpoint)", 11), f("Data toggle + payload", "0-64"), f("CRC5", 5)],
        "USB 1.x has no SOF framing on the data lines: each packet starts with an 8-bit "
        "PID whose CRC-5 is embedded in it, followed by data and a CRC-16.",
    ),
    "usb20": (
        [f("PID", 8), f("Endpoint + toggle + data", "0-4096"), f("CRC16", 16)],
        "USB 2.0 keeps the PID plus CRC-16 structure but raises bulk packets to 512 bytes "
        "and adds split transactions so large transfers keep the bus responsive.",
    ),
    "usb3x": (
        [f("DCI + SCS", 16), f("CRC (32-bit)", 32), f("DID", 8), f("DPort", 8), f("Sequence number", 8), f("Interlaced RTD", 8), f("Data frames (CRC-16 + payload)", "0+"), f("LFPS / Ordered sets", "0+")],
        "SuperSpeed uses 128b/132b line coding with sequence numbers, 32-bit frame CRCs "
        "and LFPS signalling for low-power states; there are no separate data toggles.",
    ),
    "usbc": (
        [f("Physical Layer Packet (preamble + PHY pattern)", 40), f("Link Layer header (version, type, lanes, CRC)", "0+"), f("Data payload (SS or DF)", "0+"), f("LTSsm", "0+")],
        "USB-C is a connector with a USB Power Delivery state machine layered over it: "
        "the PD contract (voltage, current) is negotiated on CC1/CC2 with BMC packets.",
    ),
    "usbcdc": (
        [f("Setup packet", 64), f("Control transfer stage", 8), f("Notification (port change, suspend)", 8), f("BULK/INTERRUPT data", "0+")],
        "CDC is a device class rather than a wire format; virtual serial ports carry data "
        "as USB bulk transfers, so the framing comes from the USB core.",
    ),
    "usbhid": (
        [f("Report type (Input/Output/Feature)", 8), f("Report ID", 8), f("Data (Input or Output report)", "0+")],
        "HID reports sit on interrupt endpoints: an IN report carries device-to-host state "
        "and an OUT report carries host-to-device data, both with an optional report ID.",
    ),
    "usbmsc": (
        [f("Command Block Wrapper (CBW)", 96), f("Data (bulk IN/OUT)", "0+"), f("Command Status Wrapper (CSW)", 24)],
        "Bot (USB Mass Storage) wraps SCSI over bulk endpoints: the host sends a 31-byte "
        "CBW, the device replies with a 13-byte CSW giving residue and status.",
    ),
    # ------------------------------------------------------- AEROSPACE --------
    "arinc664": (
        [f("Preamble (0x7E)", 8), f("IFG (inter-frame gap)", "0+"), f("Sequence number", 1), f("Destination (48-bit MAC)", 48), f("Source (48-bit MAC)", 48), f("Virtual link identifier + BAG", 16), f("Payload", "0+"), f("FCS", 32)],
        "AFDX frames interleave on one link: the 8-bit preamble plus a minimum IFG lets a "
        "switch detect frame starts without carrier sense, and BAG sets the bandwidth "
        "allocation gap that bounds jitter.",
    ),
    "mil1553": (
        [f("Command word (16 bits: status/address/type/count)", 16), f("Data words (16 bits each)", "16*n"), f("Status word (16 bits)", 16)],
        "MIL-STD-1553B is command/response: the bus controller sends a command word, up to "
        "32 data words, then the RT returns a status word — timing is per word, not per frame.",
    ),
    "spacewire": (
        [f("Start flag", 1), f("Frame type (encoding ID)", 2), f("Frame length", 14), f("Sequence count", 8), f("NSP (network protocol header)", "0+"), f("Data field (path control + payload)", "0+"), f("Frame error flag", 1)],
        "SpaceWire uses SPEME framing with pluggable encoding IDs; the FCT (flow control "
        "token) throttles the source when the receiver link cannot keep up.",
    ),
    "cyphal": (
        [f("Header (24-bit magic + version)", 24), f("Source ID", 7), f("Destination ID", 7), f("Transfer-ID", 4), f("Payload length", 8), f("Payload", "0+"), f("Tail byte (CRC)", 8)],
        "UAVCAN/Cyphal uses a 4-bit Transfer-ID that increments per session so a lost "
        "frame does not desynchronise the next request, plus a 7-bit node ID in the tail.",
    ),
    # ----------------------------------------------------- AUDIO / VIDEO ------
    "i2s": (
        [f("BCLK pulse (per data bit)", 1), f("WS (channel select)", 1), f("Left sample (16/20/24/32 bits)", 32), f("Right sample (32 bits)", 32)],
        "I2S delays the MSB by one BCLK after the WS edge (Philips standard), which lets "
        "the receiver latch data on the rising edge and change WS without a setup conflict.",
    ),
    "tdm": (
        [f("BCLK pulse", 1), f("Frame sync pulse", 1), f("Slot 0 (1-32 bits)", 32), f("Slot 1", 32), f("Slot N", 32)],
        "TDM is time-division multiplexing with a fixed frame-sync and slot rate; unlike "
        "I2S the data position in the frame is fixed by the slot count, not by a WS line.",
    ),
    "pcm": (
        [f("Bit clock pulse", 1), f("Frame sync", 1), f("Channel sample (8/16/24 bits)", 16)],
        "PCM (Pulse Code Modulation, audio) is I2S without the standard's exact framing "
        "rules: a frame-sync pulse marks the start of a fixed-length stereo word.",
    ),
    "hdmi": (
        [f("TMDS character (10 bits, encoded)", 10), f("Guard band (2 bits for control/video periods)", 2), f("Video data stream", "0+"), f("Data island + guard band", "0+")],
        "HDMI 2.x TMDS reduces 8 bits to 10 with 2-bit running disparity and uses a 4-bit "
        "period boundary; DVI/HDMI 1.x used 10-of-20 LVDS signalling.",
    ),
    # --------------------------------------------------- HIGH-SPEED / FPGA ----
    "pcie": (
        [f("Fmt + Type", 5), f("TC + Attr", 3), f("TD (digest)", 1), f("EP", 1), f("AT", 2), f("Length", 10), f("Requester ID", 16), f("Tag", 8), f("Last BE", 1), f("First BE", 1), f("Completer ID", 16), f("Completer ID type", 3), f("PCIe Data Payload", "8*n")],
        "TLP headers are 3 or 4 DW long (12 or 16 bytes), so the fixed overhead is tiny "
        "against a 4 KB maximum payload; 128b/130b encoding and the ECRC field protect the header.",
    ),
    "rapidio": (
        [f("Physical Layer command/status field", 16), f("Transport field", 8), f("Logical layer field", 8), f("Transport Control Command (NACK, Response)", 8), f("Data payload", "0+"), f("ECRC/CRC field", 8)],
        "RapidIO uses 8- or 16-bit symbols on up to four lanes with a three-layer "
        "architecture; disabled, control, and data symbols interleave in the stream.",
    ),
    "jesd204": (
        [f("Line interface characters (multi-lane sync)", "8*n"), f("Block start (4 byte times per lane)", 32), f("Alignment character", 8), f("Payload characters", "0+"), f("Frame character / CRC / parity", "8-16")],
        "JESD204B uses a lane-parallel interface where each lane carries 4-byte characters "
        "with 1/8b/10b encoding; the block start character realigns lanes after elastic buffer.",
    ),
    "nvme": (
        [f("PCIe header (Fmt/Type/TC/Length)", 16), f("DID", 16), f("Requester ID", 16), f("SQE/CQE opcode", 8), f("Flags + command fields", 16), f("Namespace + LBA list", "0+"), f("Data payload", "0+"), f("CQE status field", 16), f("Phase tag (SQ/CQ)", 4)],
        "NVMe queues admin and I/O commands as SQEs and returns CQEs; the 4-bit phase bit "
        "in the completion lets a poller tell new entries without a doorbell read.",
    ),
    "sata": (
        [f("SOF (Start of Frame, 4 bytes: FF F8 F8 FF)", 32), f("DIP (Data/Idle)", "8*n"), f("FIS (Frame Information Structure)", 32), f("CRC (32-bit, per DWORD)", 32)],
        "SATA uses fixed-size frames starting with a COMRESET SOF (FF F8 F8 FF) and a "
        "32-bit CRC per dword, which is what makes hot-plug and error recovery reliable.",
    ),
    # --------------------------------------------------- SENSOR-SPECIFIC -----
    "iolink": (
        [f("Wake-up sequence (9-33 carrier pulses)", "0+"), f("Mode configuration (1-3 bytes)", "8-24"), f("I-Command (1 byte)", 8), f("I-Block data (parameter + data)", "8*n"), f("Checksum (8-bit)", 8), f("Acknowledgement", 8)],
        "IO-Link point-to-point uses a modified UART at 4.8 kbit/s with 24 V wake-up pulses; "
        "the checksum is a simple 8-bit sum protecting the unidirectional command sequence.",
    ),
    "dsi3": (
        [f("Header (2 bytes)", 16), f("Payload (4-16 bytes)", "8*n"), f("CRC8", 8)],
        "DSI3 is a short-range, low-power sensor interconnect (Google/Nest) with a 2-byte "
        "header; CRC-8 protects each packet against capacitive-coupling errors.",
    ),
    "nmea": (
        [f("Talker ID (2 ASCII)", 16), f("Sentence formatter (3 ASCII)", 24), f("Fields (comma-separated)", "0+"), f("Checksum (XOR of chars between $ and *)", 8), f("CR/LF", 16)],
        "NMEA 0183 sentences are ASCII terminated by CRLF with a single XOR checksum, so a "
        "sentence can be parsed by scanning for '$' then '*' without any framing bytes.",
    ),
    # ---------------------------------------------------------- CELLULAR -----
    "lorawan": (
        [f("PHY header (BW/CR coding rate + implicit header)", 16), f("CRC (16-bit)", 16), f("MAC header (FHDR + FPort)", 8), f("FCtrl", 8), f("FPortNS", 8), f("FOpts", "0+"), f("FRMPayload (encrypted)", "0+")],
        "LoRaWAN splits PHY (chirp modulation, spreading factor) from MAC (dev addresses, "
        "FCntUp anti-replay, confirmed downlink). Encryption is end-to-end AES-128.",
    ),
    "mipi_dsi": (
        [f("Data ID", 8), f("Header (WC 16 bits + data ID 8 bits)", 24), f("Packet payload", "0+"), f("CRC16", 16)],
        "MIPI DSI packets are DSI-relative: the display controller needs no knowledge of "
        "the panel's command set, it just forwards packets in order.",
    ),
    "mipi_csi": (
        [f("Packet header", 8), f("Data ID", 8), f("Word count", 16), f("Virtual channel ID", 4), f("Packet payload", "0+"), f("ECC (8 or 24 bit)", "8-24")],
        "MIPI CSI-2 carries camera frames over up to 4 data lanes; the VC field lets one "
        "physical link carry multiple virtual streams, and lane numbers are inferred by order.",
    ),
    "displayport": (
        [f("Main stream header (92 or 80 bits)", "80-92"), f("Secondary channel packet (count, type, payload)", "0+"), f("Audio payload", "0+"), f("Main stream payload", "0+"), f("FEC (forward error correction, DPC)", 0)],
        "DisplayPort main stream headers carry M/N (modulus/remainder) so the receiver can "
        "recover exact pixel timing; FEC corrects the burst errors from unshielded cable.",
    ),
    "midi": (
        [f("Status byte (4-bit type + 4-bit channel)", 8), f("Data bytes (1-2)", "8-16"), f("Real-time message (single status byte)", 8)],
        "MIDI runs on a 31.25 kbit/s current-loop DIN cable; most messages are 2-3 bytes "
        "with the first byte carrying message type and channel number in its nibbles.",
    ),
    "firewire": (
        [f("Header (tag, data length, tcode)", 32), f("Data length", 16), f("Data", "0+"), f("Header CRC (4-bit)", 4), f("Data CRC (16-bit)", 16)],
        "IEEE 1394 (FireWire) uses asynchronous and isochronous packets distinguished by "
        "tcode, on a 100/400/800 Mbit/s daisy-chain with arbitration by node ID.",
    ),
    "usbdfu": (
        [f("DFU state machine / request code", 8), f("Block data (2048 bytes typical)", "0+"), f("CRC32", 32), f("Manifest data", "0+")],
        "DFU downloads firmware as SET_FILE/ WRITE_ blocks, 2048 bytes by convention, "
        "with a manifest and a CRC32 or checksum per block.",
    ),
    "usb4": (
        [f("Header (Quadword)", 32), f("Packet type + length", 16), f("Reserved", 48), f("Digest (CRC32)", 32), f("Payload", "0+"), f("Link layer packet", "0+")],
        "USB4 tunnels PCIe, DisplayPort and USB3 traffic over 20+ Gbit/s using 64-byte "
        "Line Coding Blocks with a per-block CRC32 digest.",
    ),
    "matter": (
        [f("Message flags + type", 16), f("Exchange counter", 32), f("Session ID", 32), f("Message counter", 32), f("Protocol ID", 16), f("Length", 16), f("Payload", "0+")],
        "Matter reuses CHIP's secure-session framing, where the message counter is the "
        "anti-replay value and the exchange counter orders protocol messages.",
    ),
    "nfc": (
        [f("Preamble", "0+"), f("SOF (0x26/0x27/0xAA)", 8), f("Command (RREQ/RSP/REQA/FF)", 8), f("Target select / UID", "0+"), f("Payload (NDEF or anticollision)", "0+"), f("CRC", 16)],
        "NFC couples RF framing with ISO/IEC 14443 or 15693: the ATS/ATQA reply is sent "
        "at 106 kbit/s while the reader field is modulated at 1.6 or 2.6 MHz.",
    ),
    "rfid": (
        [f("Command (inventory, select, read)", 8), f("Version / memory bank", 8), f("Block selector", "0+"), f("Data (EPC, TID, user)", "0+"), f("CRC (16-bit)", 16)],
        "Gen2 (EPCglobal Gen2) is the UHF RFID air interface; commands are inventory "
        "round-based with a CRC-16 CCITT protecting every response.",
    ),
    "sercos": (
        [f("Command phase S|C (0x6B)", 8), f("Address", 16), f("Control + length", 8), f("Data", "0+"), f("Phase 2 telegram", "8*n"), f("Phase 3 ACK", 8)],
        "SERCOS runs three phases per cycle: command (master to all), telegram (cyclic "
        "process data from all) and acknowledgement, giving deterministic scheduling.",
    ),
    "tsn": (
        [f("Destination MAC", 48), f("Source MAC", 48), f("Ethertype 0x22F0", 16), f("Stream ID", 32), f("Frame ID", 16), f("Reserved", 16), f("Payload + padding", "0+"), f("FCS", 32)],
        "802.1 TSN adds stream identity (Stream ID + Frame ID) so each talker/listener "
        "pair gets scheduled gates and reserved bandwidth.",
    ),
    "dds": (
        [f("RTPS header", 40), f("Submessage keys", "0+"), f("Payload", "0+"), f("CDR", "0+"), f("Message receipt / inlineQos", "0+")],
        "DDS-RTPS groups submessages by entity/topic in one multicast PDU, each preceded "
        "by a MessageId so partial delivery can be detected.",
    ),
    "knx": (
        [f("Control field", 4), f("Address + extended frame type", 12), f("Payload length", 4), f("Data (8 or 16 bit)", "0-16"), f("Checksum (parity + FF)", 8)],
        "KNX TP1 uses 8-bit telegrams (4-bit control, 4-bit length, 4-bit payload) or the "
        "extended 16-bit format; the checksum is even parity plus 0xFF padding.",
    ),
    "dali": (
        [f("Forward frame (address + data)", 16), f("Answer byte (status)", 8), f("Data", "8*n")],
        "DALI-2 sends a 16-bit forward frame and receives an 8-bit answer byte back-powering "
        "the line: only 1.2 kbit/s but 64 nodes and no separate return wire.",
    ),
    "canopen": (
        [f("SOF", 1), f("Identifier (11 or 29 bit)", 11), f("RTR", 1), f("Control field", 8), f("Data", "8*n"), f("CRC (15-bit)", 15), f("CRC delim + ACK + delim + EOF", 1)],
        "CANopen puts an 8-bit control field in byte 0: a 4-bit node-ID nibble selects "
        "SDO/PDO/emergency/NMT and the SDO 4-bit command code selects the transfer.",
    ),
    "hart": (
        [f("Preamble bits", "8-32"), f("Start bit", 1), f("Frame bytes", 3), f("Address", 6), f("Function", 3), f("HART CRC (DCC)", 8), f("End-of-frame", 1)],
        "HART is Bell 202 FSK on the 4-20 mA loop with a Bell 202/212 or Manchester "
        "reply; 3-byte frames carry a 6-bit address and the CRC is a DCC sum.",
    ),
    "wirelesshart": (
        [f("Preamble", "8-32"), f("Start bit", 1), f("Network manager / device address", 16), f("Command + response", "8*n"), f("DCC checksum", 8), f("EOF", 1)],
        "WirelessHART is the TDMA version: every slot is scheduled, so the 10 ms network "
        "has fixed slots for the manager, each device, and a discovery slot.",
    ),
    "doip": (
        [f("Protocol version", 8), f("Inverse version", 8), f("Payload type", 16), f("Payload length", 32), f("Data", "0+")],
        "DoIP wraps diagnostics over TCP/13400 with a generic header of version, inverted "
        "version, payload type and 32-bit length.",
    ),
    "j1939": (
        [f("PGN (24 bits)", 24), f("Data", "0+")],
        "J1939-21 uses the 29-bit CAN identifier: priority (3), extended data page (1), "
        "data page (1), PDU format (4), PDU specific (4) and source address (8).",
    ),
    "obd2": (
        [f("Mode/request", 8), f("PID or service + PID", 16), f("Data", "8*n")],
        "OBD-II is a query/response service set (modes 01-0A) carried on CAN, ISO 9141 "
        "K-Line, J1850 PWM/VPW or J1708 depending on vehicle year.",
    ),
    "can_xl": (
        [f("SOF + arbitration", "1-32"), f("Address field (in-frame multiplexing)", "0-20"), f("Data", "0-2048"), f("CRC", 32)],
        "CAN XL uses in-frame multiplexing for addressing up to 1024 nodes and payload "
        "segments up to 2048 bytes, trading classic CAN arbitration for throughput.",
    ),
    "someip": (
        [f("Service ID", 16), f("Method ID", 16), f("Session ID", 32), f("Interface ID", 32), f("Message ID", 32), f("Length", 32), f("Payload", "0+")],
        "SOME/IP is serialized over UDP or TCP and (unlike SOME/IP-ET) can share one "
        "endpoint with several services by using distinct service IDs.",
    ),
    "xcp": (
        [f("Packet length", 16), f("CC (command code)", 8), f("Counter", 8), f("Data", "0+")],
        "XCP (Universal Measurement and Calibration Protocol) is XCP-on-CAN/Ethernet; "
        "the same packet framing supports both transports with a counter for ordering.",
    ),
    "t1s": (
        [f("Sync pulse", 1), f("Header (2 bits)", 2), f("ID + payload", "0+"), f("CRC (5 bits)", 5)],
        "T1S (Automotive Ethernet SerDes) signals on a single balanced pair with an "
        "embedded clock and pulse-width signalling instead of a separate clock lane.",
    ),
    "mqtt": (
        [f("Packet type + flags", "4+n"), f("Remaining length", "0-268435455"), f("Variable header", "0+"), f("Payload", "0+")],
        "Remaining length is a variable-length integer: 7 bits per byte with a continuation "
        "bit, so 4 bytes encode up to 256 MB — far beyond any legal MQTT message size.",
    ),
    "coap": (
        [f("Ver + Type + TKL", 8), f("Code", 8), f("Message ID", 16), f("Token", "0-8"), f("Options (delta + length)", "0+"), f("0xFF payload marker", "0-1"), f("Payload", "0+")],
        "Options use delta encoding against the previous option number and a 4-bit nibble "
        "length (13/14 escape the nibble). CoAP runs over UDP, not TCP.",
    ),
    "websocket": (
        [f("FIN + opcode", 4), f("Mask + payload length", 4), f("Extended payload length", "0-64"), f("Masking key (client to server)", "0-32"), f("Payload", "0+")],
        "RFC 6455 requires client-to-server frames to be masked and server-to-client frames "
        "not to be. Length is 0-125 inline, else a 16- or 64-bit extended field.",
    ),
    "ntp": (
        [f("Leap indicator + Version", 8), f("Mode", 8), f("Stratum", 8), f("Poll", 8), f("Precision", 8), f("Root delay", 32), f("Root dispersion", 32), f("Reference ID", 32), f("Reference/Origin timestamp", 64), f("Receive timestamp", 64), f("Transmit timestamp", 64)],
        "Timestamps are 64-bit seconds since 1900 with a 32-bit fraction (~232 ps resolution). "
        "The 32-bit era counter rolls over in 2036.",
    ),
    "mdns": (
        [f("Transaction ID (zeroed)", 16), f("Flags", 16), f("Questions", 16), f("Answers", 16), f("Authorities", 16), f("Additionals", 16), f("Resource records", "0+")],
        "mDNS reuses the DNS wire format with the ID zeroed, sends to 224.0.0.251 on "
        "UDP/5353, and resolves name clashes by random 1-10 s probing.",
    ),
    "emmc": (
        [f("Command index", 6), f("Argument", 32), f("Response", 16), f("Data block", "8*512B"), f("CMDQ CRC16", 16)],
        "eMMC uses command/index/argument/response registers plus 512-byte data blocks "
        "with a CMDQ CRC16 for reliable multi-block transfers.",
    ),
    "ufs": (
        [f("Type + UFID", 8), f("Flags + Function", 8), f("Task tag", 16), f("Data segment (up to 64 KB)", "8*n"), f("Digest", "8*n")],
        "UFS Transport Protocol (UTP) layers a 12-byte UFS header over each Logical Data "
        "Block; the digest protects data integrity.",
    ),
    "mdio": (
        [f("START", 2), f("OP (write/read)", 2), f("PHY address", 5), f("Register address", 5), f("Data", 16), f("TA (turnaround)", 2)],
        "MDIO Clause 22 is a bit-banged management bus: PRE(00)/IDLE(01)/TERM(10)/TA(11) "
        "form the frame and each register access is 32 bits.",
    ),
}


# Protocols whose standard genuinely defines no fixed bit-level frame. These keep
# an empty frame_fields list so the UI shows an explanatory banner instead of
# inventing a layout that does not exist.
NO_FIXED_FRAME = {
    "gsm", "lte", "ltem", "nbiot", "5g", "sigfox", "zwave", "uwb", "antplus",
    "lora", "jtag", "swd", "mdio", "parallel", "spdif", "lvds", "serdes",
    "sgmii", "rgmii", "xaui", "aurora", "wifi", "bluetooth_classic", "ble",
    "6lowpan", "fapl",
}


# Protocols whose rate is set entirely by the carrier below them. They have no
# speed of their own, so the UI says so explicitly instead of leaving `speed`
# absent (which reads as "missing data" rather than "carrier-defined").
CARRIER_DEPENDENT_SPEED = (
    "Carrier-dependent — the rate is set by the physical/link layer below "
    "(Ethernet, Wi-Fi, cellular, USB, or the specific bearer)."
)


def apply_frame_specs(protocols):
    """Fill in frame_fields/frame_note for every protocol that lacks them.

    Protocols that already declare frame_fields in build_data.py (the curated
    ones: uart, i2c, can, tcp, ...) are left untouched so their hand-written notes
    survive. Protocols with genuinely no fixed bit-level frame get an empty list
    plus a frame_note explaining why, so the UI shows an honest banner instead of
    a fabricated layout.

    Returns (protocols, filled_count, explained_count).
    """
    filled = 0
    explained = 0
    for protocol in protocols:
        pid = protocol["id"]
        # A missing speed means "carrier-dependent" for logical/RF layers, but
        # stating it is clearer than an absent field.
        if not protocol.get("speed"):
            protocol["speed"] = CARRIER_DEPENDENT_SPEED
        if protocol.get("frame_fields"):
            continue
        if pid in FRAME_SPECS:
            fields, note = FRAME_SPECS[pid]
            protocol["frame_fields"] = deepcopy(fields)
            protocol["frame_note"] = note
            filled += 1
        else:
            protocol["frame_note"] = (
                protocol.get("frame_note")
                or "This protocol has no fixed bit-level frame of its own: its data is "
                "carried by the physical/link layer below it, or it is a method inside "
                "a higher-layer message format. See the Electrical & Hardware Profile "
                "for the carrier that frames it."
            )
            explained += 1
    return protocols, filled, explained


def coverage_report(protocols):
    """Return (with_frame, without_frame, unexplained) for verification/reporting."""
    with_frame = [p["id"] for p in protocols if p.get("frame_fields")]
    without = [p["id"] for p in protocols if not p.get("frame_fields")]
    return with_frame, without, sorted(set(without) - set(NO_FIXED_FRAME))
