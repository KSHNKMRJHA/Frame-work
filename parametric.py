# -*- coding: utf-8 -*-
"""Machine-readable parametric specs for every protocol record.

The original `speed` field is free prose ("up to ~7-12.5 Mbps on some modern
MCUs") — great for humans, useless for sorting, filtering, charting, or a
selection wizard. This module attaches a numeric envelope to each protocol:

  data_rate_min_bps / data_rate_max_bps — representative usable range
  distance_max_m                        — longest specified/practical segment
  nodes_max                             — most devices on one segment
  lifecycle                             — emerging | active | mature | legacy
  osi_layer                             — which stack layers the entry covers
  standard_doc                          — the defining document (numbered!)

Semantics (read before quoting a number back at an engineer):

* Numbers are *representative maxima*, not guaranteed combinations. RS-485
  does 10 Mbps at 12 m OR 100 kbps at 1200 m — never both at once. The
  Encyclopedia and Selector pages say this next to every table.
* None means "not defined at this layer" (it inherits a carrier). TCP has no
  data rate of its own; SERDES is a technique, not a standard. Filters treat
  None as "this dimension does not exclude the protocol".
* Values are order-of-magnitude selection guidance, sourced from the
  specification or textbook figure named in standard_doc — not datasheet
  replacements. The device datasheet always wins.

Same pattern as technical_profiles.py: category defaults keep all 140+
protocols covered, per-protocol overrides pin the flagships precisely.
"""

from copy import deepcopy

SPEC_FIELDS = (
    "data_rate_min_bps",
    "data_rate_max_bps",
    "distance_max_m",
    "nodes_max",
    "lifecycle",
    "osi_layer",
    "standard_doc",
)

LIFECYCLES = ("emerging", "active", "mature", "legacy")

_CAT_DEFAULTS = {
    "On-Board": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 10_000_000,
        "distance_max_m": 1,
        "nodes_max": 4,
        "lifecycle": "mature",
        "osi_layer": "L1+L2 (board link)",
        "standard_doc": "Vendor / device datasheets",
    },
    "Industrial": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 100_000_000,
        "distance_max_m": 1200,
        "nodes_max": 32,
        "lifecycle": "mature",
        "osi_layer": "L1-L7 (fieldbus profile)",
        "standard_doc": "Fieldbus organization specification",
    },
    "Automotive": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 1_000_000,
        "distance_max_m": 100,
        "nodes_max": 16,
        "lifecycle": "mature",
        "osi_layer": "L1+L2 (vehicle network)",
        "standard_doc": "OEM / standards-body specification",
    },
    "Networking": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": None,
        "distance_max_m": None,
        "nodes_max": None,
        "lifecycle": "active",
        "osi_layer": "L3+ (stack layer)",
        "standard_doc": "IETF RFC",
    },
    "Wireless": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 250_000,
        "distance_max_m": 100,
        "nodes_max": 16,
        "lifecycle": "active",
        "osi_layer": "L1+L2 (radio link)",
        "standard_doc": "IEEE / alliance specification",
    },
    "Cellular": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 1_000_000,
        "distance_max_m": 10_000,
        "nodes_max": None,
        "lifecycle": "active",
        "osi_layer": "L1-L7 (cellular stack)",
        "standard_doc": "3GPP specification",
    },
    "Audio/Video": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 10_000_000,
        "distance_max_m": 5,
        "nodes_max": 2,
        "lifecycle": "mature",
        "osi_layer": "L1+L2 (media link)",
        "standard_doc": "Interface specification",
    },
    "USB": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 480_000_000,
        "distance_max_m": 5,
        "nodes_max": 127,
        "lifecycle": "mature",
        "osi_layer": "L1-L7 (USB stack)",
        "standard_doc": "USB-IF specification",
    },
    "High-Speed/FPGA": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 10_000_000_000,
        "distance_max_m": 1,
        "nodes_max": None,
        "lifecycle": "active",
        "osi_layer": "L1 (serial link)",
        "standard_doc": "Standards-body / vendor specification",
    },
    "Sensor-Specific": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 250_000,
        "distance_max_m": 20,
        "nodes_max": 8,
        "lifecycle": "active",
        "osi_layer": "L1+L2 (sensor bus)",
        "standard_doc": "Sensor consortium specification",
    },
    "Security": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": None,
        "distance_max_m": None,
        "nodes_max": None,
        "lifecycle": "active",
        "osi_layer": "Security layer (see description)",
        "standard_doc": "IETF / IEEE standard",
    },
    "Aerospace": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 100_000_000,
        "distance_max_m": 100,
        "nodes_max": None,
        "lifecycle": "mature",
        "osi_layer": "L1+L2 (avionics bus)",
        "standard_doc": "ARINC / MIL specification",
    },
    "Debug & Trace": {
        "data_rate_min_bps": None,
        "data_rate_max_bps": 100_000_000,
        "distance_max_m": 0.5,
        "nodes_max": 8,
        "lifecycle": "active",
        "osi_layer": "L1 (debug link)",
        "standard_doc": "ARM / IEEE debug specification",
    },
}

# Per-protocol overrides: only the fields that differ from the category
# default are listed. Short keys map to SPEC_FIELDS in apply_parametric_specs.
# rate = data_rate_max_bps, dist = distance_max_m, nodes = nodes_max,
# life = lifecycle, osi = osi_layer, doc = standard_doc.
_OVERRIDES = {
    # ------------------------------- On-Board -------------------------------
    "uart": {"rate": 1_000_000, "dist": 3, "nodes": 2, "osi": "L1+L2 (async serial)", "doc": "MCU reference manual"},
    "rs232": {"rate": 115_200, "dist": 15, "nodes": 2, "doc": "TIA-232-F"},
    "rs485": {"rate": 10_000_000, "dist": 1200, "nodes": 32, "doc": "TIA-485-A"},
    "spi": {"rate": 50_000_000, "dist": 0.3, "nodes": 8, "doc": "Motorola AN991; peripheral datasheet"},
    "qspi": {
        "rate": 400_000_000,
        "dist": 0.1,
        "nodes": 2,
        "life": "active",
        "doc": "JEDEC JESD251 (xSPI); vendor datasheets",
    },
    "i2c": {"rate": 3_400_000, "dist": 1, "nodes": 112, "life": "active", "doc": "NXP UM10204"},
    "i3c": {"rate": 12_500_000, "dist": 1, "nodes": 16, "life": "emerging", "doc": "MIPI I3C v1.1"},
    "1wire": {"rate": 142_000, "dist": 100, "nodes": 32, "doc": "Maxim DS18B20 / 1-Wire design guide"},
    "microwire": {
        "rate": 2_000_000,
        "dist": 1,
        "nodes": 2,
        "life": "legacy",
        "doc": "National Semiconductor datasheets",
    },
    "smbus": {"rate": 100_000, "dist": 1, "nodes": 32, "doc": "SMBus 3.2"},
    "pmbus": {"rate": 400_000, "dist": 1, "nodes": 32, "doc": "PMBus 1.4"},
    "mdio": {"rate": 2_500_000, "dist": 1, "nodes": 32, "doc": "IEEE 802.3 Clause 22/45"},
    "sdio": {
        "rate": 2_500_000_000,
        "dist": 0.1,
        "nodes": 1,
        "life": "active",
        "doc": "SD Association Physical Layer Simplified Spec",
    },
    "emmc": {"rate": 3_200_000_000, "dist": 0.1, "nodes": 1, "doc": "JEDEC JESD84 (eMMC 5.1)"},
    "parallel": {"rate": 800_000_000, "dist": 0.5, "nodes": 2, "doc": "Device datasheets"},
    # ------------------------------ Industrial ------------------------------
    "modbus_rtu": {"rate": 115_200, "dist": 1200, "nodes": 247, "doc": "Modbus over Serial Line V1.02"},
    "modbus_tcp": {"rate": 1_000_000_000, "dist": 100, "nodes": None, "doc": "Modbus Messaging on TCP/IP (port 502)"},
    "profibus": {"rate": 12_000_000, "dist": 1200, "nodes": 126, "doc": "IEC 61158 / PI PROFIBUS spec"},
    "profinet": {
        "rate": 1_000_000_000,
        "dist": 100,
        "nodes": None,
        "life": "active",
        "doc": "IEC 61158 / PI PROFINET spec",
    },
    "ethercat": {"rate": 100_000_000, "dist": 100, "nodes": 65535, "life": "active", "doc": "IEC 61158; ETG.1000"},
    "ethernetip": {"rate": 1_000_000_000, "dist": 100, "nodes": None, "doc": "ODVA CIP / EtherNet/IP spec"},
    "devicenet": {"rate": 500_000, "dist": 500, "nodes": 64, "life": "legacy", "doc": "ODVA DeviceNet spec"},
    "canopen": {"rate": 1_000_000, "dist": 1000, "nodes": 127, "doc": "CiA 301"},
    "hart": {"rate": 1_200, "dist": 1500, "nodes": 15, "doc": "FieldComm HART spec (Bell 202 FSK)"},
    "wirelesshart": {"rate": 250_000, "dist": 200, "nodes": 100, "doc": "FieldComm WirelessHART (IEC 62591)"},
    "opcua": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "life": "active",
        "osi": "L5-L7 + information model",
        "doc": "IEC 62541 (OPC UA)",
    },
    "bacnet": {"rate": 1_000_000_000, "dist": 100, "nodes": None, "doc": "ASHRAE 135 (BACnet)"},
    "dnp3": {"rate": 100_000_000, "dist": 100, "nodes": None, "doc": "IEEE 1815 (DNP3)"},
    "lonworks": {"rate": 1_250_000, "dist": 500, "nodes": 64, "life": "legacy", "doc": "ISO/IEC 14908 (LonTalk)"},
    "mbus": {"rate": 9_600, "dist": 1000, "nodes": 250, "doc": "EN 13757 (M-Bus)"},
    "foundation_fieldbus": {"rate": 100_000_000, "dist": 1900, "nodes": 32, "doc": "IEC 61158 (FF H1/HSE)"},
    "powerlink": {"rate": 100_000_000, "dist": 100, "nodes": 240, "doc": "EPSG Ethernet POWERLINK spec"},
    "sercos": {"rate": 1_000_000_000, "dist": 100, "nodes": 511, "doc": "IEC 61158 / Sercos International"},
    # ------------------------------ Automotive ------------------------------
    "can": {"rate": 1_000_000, "dist": 1000, "nodes": 30, "doc": "Bosch CAN 2.0; ISO 11898-1/2"},
    "can_fd": {"rate": 8_000_000, "dist": 1000, "nodes": 16, "life": "active", "doc": "Bosch CAN FD; ISO 11898-1:2015"},
    "lin": {"rate": 20_000, "dist": 40, "nodes": 17, "doc": "LIN 2.2A"},
    "flexray": {"rate": 10_000_000, "dist": 50, "nodes": 22, "doc": "FlexRay V3.0 (ISO 10681)"},
    "most": {"rate": 150_000_000, "dist": 50, "nodes": 64, "life": "legacy", "doc": "MOST Cooperation (MOST150)"},
    "automotive_ethernet": {
        "rate": 1_000_000_000,
        "dist": 15,
        "nodes": None,
        "life": "active",
        "doc": "IEEE 100BASE-T1/1000BASE-T1",
    },
    "sent": {"rate": 30_000, "dist": 5, "nodes": 2, "life": "active", "doc": "SAE J2716 (SENT)"},
    "psi5": {"rate": 189_000, "dist": 12, "nodes": 4, "life": "active", "doc": "PSI5 V2.2"},
    "kline": {"rate": 10_400, "dist": 5, "nodes": 2, "life": "legacy", "doc": "ISO 9141 / ISO 14230 (KWP2000)"},
    "uds": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "life": "active",
        "osi": "L7 (diagnostic application)",
        "doc": "ISO 14229 (UDS)",
    },
    "doip": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "life": "active",
        "osi": "L5-L7 (diagnostics over IP)",
        "doc": "ISO 13400 (DoIP)",
    },
    "j1939": {"rate": 500_000, "dist": 40, "nodes": 30, "doc": "SAE J1939"},
    "obd2": {
        "rate": 500_000,
        "dist": 5,
        "nodes": 16,
        "life": "active",
        "osi": "L1-L7 (diagnostic connector + protocols)",
        "doc": "SAE J1962 / ISO 15031",
    },
    # ------------------------------ Networking ------------------------------
    "ethernet": {"rate": 400_000_000_000, "dist": 100, "nodes": None, "osi": "L1+L2", "doc": "IEEE 802.3-2022"},
    "tcp": {"osi": "L4 (transport)", "doc": "RFC 9293 (TCP)"},
    "udp": {"osi": "L4 (transport)", "doc": "RFC 768 (UDP)"},
    "ip": {"osi": "L3 (network)", "doc": "RFC 791 (IPv4) / RFC 8200 (IPv6)"},
    "arp": {"osi": "L2/L3 (link mapping)", "doc": "RFC 826 (ARP)"},
    "dhcp": {"osi": "L7 (configuration)", "doc": "RFC 2131 (DHCP)"},
    "dns": {"osi": "L7 (naming)", "doc": "RFC 1035 (DNS)"},
    "icmp": {"osi": "L3 (control)", "doc": "RFC 792 (ICMP)"},
    "http": {"osi": "L7 (application)", "doc": "RFC 9110 (HTTP Semantics)"},
    "ftp": {"osi": "L7 (application)", "life": "mature", "doc": "RFC 959 (FTP)"},
    "telnet_ssh": {"osi": "L7 (remote shell)", "doc": "RFC 4251 (SSH)"},
    "snmp": {"osi": "L7 (management)", "doc": "RFC 3411 (SNMP)"},
    "mqtt": {"osi": "L7 (pub/sub messaging)", "doc": "ISO/IEC 20922 (MQTT)"},
    "coap": {"osi": "L7 (constrained REST)", "doc": "RFC 7252 (CoAP)"},
    "websocket": {"osi": "L7 (full-duplex channel)", "doc": "RFC 6455 (WebSocket)"},
    "ntp": {"osi": "L7 (time sync)", "doc": "RFC 5905 (NTP)"},
    "mdns": {"osi": "L7 + L3 multicast (zero-conf)", "doc": "RFC 6762 (mDNS)"},
    # ------------------------------- Wireless -------------------------------
    "bluetooth_classic": {
        "rate": 3_000_000,
        "dist": 100,
        "nodes": 8,
        "life": "mature",
        "doc": "Bluetooth Core Spec (BR/EDR)",
    },
    "ble": {"rate": 2_000_000, "dist": 200, "nodes": None, "life": "active", "doc": "Bluetooth Core Spec v5.x (LE)"},
    "wifi": {"rate": 9_600_000_000, "dist": 100, "nodes": 2007, "life": "active", "doc": "IEEE 802.11ax-2021"},
    "zigbee": {"rate": 250_000, "dist": 100, "nodes": 500, "doc": "Zigbee PRO (IEEE 802.15.4)"},
    "thread": {"rate": 250_000, "dist": 100, "nodes": 250, "life": "active", "doc": "Thread 1.3 (IEEE 802.15.4)"},
    "matter": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "life": "emerging",
        "osi": "L5-L7 (application layer)",
        "doc": "Matter 1.x (CSA)",
    },
    "zwave": {"rate": 100_000, "dist": 100, "nodes": 232, "doc": "Z-Wave Plus v2 (ITU-T G.9959)"},
    "nfc": {"rate": 848_000, "dist": 0.1, "nodes": 2, "doc": "ISO/IEC 14443 / NFC Forum"},
    "rfid": {"rate": 640_000, "dist": 12, "nodes": None, "doc": "ISO/IEC 18000 (RAIN RFID / EPC Gen2)"},
    "uwb": {"rate": 27_000_000, "dist": 50, "nodes": 8, "life": "active", "doc": "IEEE 802.15.4z (UWB)"},
    "antplus": {"rate": 60_000, "dist": 30, "nodes": 8, "doc": "ANT+ / ANT-FS (Garmin)"},
    # ------------------------------- Cellular -------------------------------
    "gsm": {"rate": 384_000, "dist": 35000, "nodes": None, "life": "legacy", "doc": "3GPP GSM/EDGE"},
    "lte": {"rate": 1_000_000_000, "dist": 10000, "nodes": None, "doc": "3GPP LTE-Advanced"},
    "ltem": {"rate": 1_000_000, "dist": 10000, "nodes": None, "life": "active", "doc": "3GPP LTE-M (Cat-M1)"},
    "nbiot": {"rate": 250_000, "dist": 10000, "nodes": None, "life": "active", "doc": "3GPP NB-IoT (Cat-NB1/NB2)"},
    "5g": {"rate": 10_000_000_000, "dist": 10000, "nodes": None, "life": "active", "doc": "3GPP 5G NR (Rel. 15+)"},
    "lora": {
        "rate": 50_000,
        "dist": 15000,
        "nodes": None,
        "life": "active",
        "osi": "L1 (chirp spread spectrum)",
        "doc": "Semtech LoRa PHY",
    },
    "lorawan": {
        "rate": 22_000,
        "dist": 15000,
        "nodes": None,
        "life": "active",
        "osi": "L2+L3 (MAC + network)",
        "doc": "LoRaWAN L2 1.0.4 (LoRa Alliance)",
    },
    "sigfox": {"rate": 600, "dist": 40000, "nodes": None, "doc": "Sigfox UNB (ETSI TS 103 357)"},
    # ------------------------------ Audio/Video -----------------------------
    "i2s": {"rate": 25_000_000, "dist": 0.5, "nodes": 8, "doc": "Philips I2S bus specification"},
    "tdm": {"rate": 25_000_000, "dist": 0.5, "nodes": 16, "doc": "Codec datasheets (TDM slots)"},
    "pcm": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "osi": "Coding (samples, not a link)",
        "doc": "ITU-T G.711 (PCM)",
    },
    "spdif": {"rate": 3_100_000, "dist": 10, "nodes": 2, "doc": "IEC 60958 (S/PDIF)"},
    "hdmi": {"rate": 48_000_000_000, "dist": 5, "nodes": 2, "life": "active", "doc": "HDMI 2.1 (48G FRL)"},
    "mipi_dsi": {"rate": 6_000_000_000, "dist": 0.3, "nodes": 2, "life": "active", "doc": "MIPI DSI-2"},
    "mipi_csi": {"rate": 10_000_000_000, "dist": 0.3, "nodes": 4, "life": "active", "doc": "MIPI CSI-2"},
    "displayport": {
        "rate": 80_000_000_000,
        "dist": 3,
        "nodes": 4,
        "life": "active",
        "doc": "VESA DisplayPort 2.1 (UHBR20)",
    },
    "lvds": {"rate": 3_000_000_000, "dist": 10, "nodes": 2, "doc": "TIA/EIA-644 (LVDS)"},
    # --------------------------------- USB ----------------------------------
    "usb11": {"rate": 12_000_000, "dist": 5, "nodes": 127, "doc": "USB 1.1 (USB-IF)"},
    "usb20": {"rate": 480_000_000, "dist": 5, "nodes": 127, "doc": "USB 2.0 (USB-IF)"},
    "usb3x": {"rate": 20_000_000_000, "dist": 2, "nodes": 127, "life": "active", "doc": "USB 3.2 Gen 2x2 (USB-IF)"},
    "usbc": {
        "rate": None,
        "dist": 2,
        "nodes": 2,
        "life": "active",
        "osi": "L1 (connector + PD contract)",
        "doc": "USB Type-C R2.4; USB PD R3.2",
    },
    "usbcdc": {"rate": None, "dist": None, "nodes": None, "doc": "USB CDC-ACM (USB-IF class)"},
    "usbhid": {"rate": None, "dist": None, "nodes": None, "doc": "USB HID 1.11 (USB-IF class)"},
    "usbmsc": {"rate": None, "dist": None, "nodes": None, "doc": "USB MSC BOT (USB-IF class)"},
    "usbdfu": {"rate": None, "dist": None, "nodes": None, "doc": "USB DFU 1.1 (USB-IF class)"},
    # ---------------------------- High-Speed/FPGA ---------------------------
    "pcie": {
        "rate": 256_000_000_000,
        "dist": 0.5,
        "nodes": None,
        "life": "active",
        "doc": "PCI-SIG PCIe 4.0 x16 (64 GB/s dir)",
    },
    "rapidio": {"rate": 40_000_000_000, "dist": 1, "nodes": 1024, "doc": "RapidIO Gen3 (40G Serial RapidIO)"},
    "aurora": {"rate": 100_000_000_000, "dist": 10, "nodes": 2, "life": "active", "doc": "AMD Aurora 64B/66B"},
    "jesd204": {
        "rate": 32_000_000_000,
        "dist": 0.5,
        "nodes": 2,
        "life": "active",
        "doc": "JEDEC JESD204C (32 Gbps/lane)",
    },
    "serdes": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "osi": "Technique (serializer/deserializer)",
        "doc": "Vendor transceiver user guides",
    },
    "sgmii": {"rate": 1_250_000_000, "dist": 1, "nodes": 2, "life": "active", "doc": "Cisco SGMII (ENG-46158)"},
    "rgmii": {"rate": 1_000_000_000, "dist": 1, "nodes": 2, "life": "active", "doc": "HP RGMII v2.0"},
    "xaui": {"rate": 10_000_000_000, "dist": 1, "nodes": 2, "life": "legacy", "doc": "IEEE 802.3 Clause 47 (XAUI)"},
    # ---------------------------- Sensor-Specific ---------------------------
    "iolink": {"rate": 230_400, "dist": 20, "nodes": 8, "life": "active", "doc": "IEC 61131-9 (IO-Link)"},
    "dsi3": {"rate": 100_000, "dist": 5, "nodes": 16, "life": "active", "doc": "DSI3 Consortium (2nd gen)"},
    # -------------------------------- Security ------------------------------
    "tls": {"osi": "L5-L7 (session security)", "doc": "RFC 8446 (TLS 1.3)"},
    "dtls": {"osi": "L4 security (datagram TLS)", "doc": "RFC 9147 (DTLS 1.3)"},
    "ipsec": {"osi": "L3 (network security)", "doc": "RFC 4301 (IPsec)"},
    "wpa": {"osi": "L2 (Wi-Fi security)", "doc": "IEEE 802.11i; WPA3 (Wi-Fi Alliance)"},
    "macsec": {"osi": "L2 (Ethernet security)", "doc": "IEEE 802.1AE (MACsec)"},
    # ------------------------------- Aerospace ------------------------------
    "arinc429": {"rate": 100_000, "dist": 60, "nodes": 21, "doc": "ARINC 429P1/P2/P3"},
    "arinc664": {"rate": 1_000_000_000, "dist": 100, "nodes": None, "life": "active", "doc": "ARINC 664P7 (AFDX)"},
    "mil1553": {"rate": 1_000_000, "dist": 100, "nodes": 31, "doc": "MIL-STD-1553B"},
    "spacewire": {
        "rate": 400_000_000,
        "dist": 10,
        "nodes": None,
        "life": "active",
        "doc": "ECSS-E-ST-50-12C (SpaceWire)",
    },
    # ---------------------------- Debug & Trace -----------------------------
    "jtag": {"rate": 100_000_000, "dist": 0.5, "nodes": 8, "osi": "L1 (test/debug access)", "doc": "IEEE 1149.1-2013"},
    "swd": {
        "rate": 50_000_000,
        "dist": 0.5,
        "nodes": 2,
        "life": "active",
        "osi": "L1+L2 (debug access port)",
        "doc": "ARM CoreSight (ADIv5/v6)",
    },
    # ------------------------- Automotive extensions ------------------------
    "can_xl": {"rate": 20_000_000, "dist": 1000, "nodes": 16, "life": "emerging", "doc": "CiA 610-1 (CAN XL)"},
    "isotp": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "osi": "L4-ish (transport segmentation)",
        "doc": "ISO 15765-2",
    },
    "someip": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "life": "active",
        "osi": "L5-L7 (service middleware)",
        "doc": "AUTOSAR SOME/IP",
    },
    "xcp": {"rate": None, "dist": None, "nodes": None, "osi": "L7 (calibration application)", "doc": "ASAM MCD-1 XCP"},
    "t1s": {"rate": 10_000_000, "dist": 25, "nodes": 8, "life": "emerging", "doc": "IEEE 802.3cg (10BASE-T1S)"},
    # ------------------------- Storage / high-speed -------------------------
    "ufs": {"rate": 46_400_000_000, "dist": 0.1, "nodes": 1, "life": "active", "doc": "JEDEC JESD220 (UFS 4.0)"},
    "nvme": {"rate": 112_000_000_000, "dist": 0.5, "nodes": None, "life": "active", "doc": "NVM Express 2.0 (Gen5 x4)"},
    "sata": {"rate": 6_000_000_000, "dist": 1, "nodes": 1, "doc": "SATA-IO SATA 3.x (6 Gbps)"},
    # --------------------------- Drone / robotics ---------------------------
    "mavlink": {
        "rate": 115_200,
        "dist": None,
        "nodes": None,
        "life": "active",
        "osi": "L5-L7 (message dialect)",
        "doc": "MAVLink v2 (mavlink.io)",
    },
    "cyphal": {
        "rate": 8_000_000,
        "dist": 100,
        "nodes": 128,
        "life": "emerging",
        "osi": "L5-L7 (pub/sub + RPC)",
        "doc": "OpenCyphal v1.0",
    },
    # ------------------------ Industrial extensions -------------------------
    "tsn": {
        "rate": None,
        "dist": 100,
        "nodes": None,
        "life": "emerging",
        "osi": "L2 (scheduled bridging)",
        "doc": "IEEE 802.1Qbv/Qbu/AS (TSN)",
    },
    "dds": {
        "rate": None,
        "dist": None,
        "nodes": None,
        "life": "active",
        "osi": "L7 (pub/sub middleware)",
        "doc": "OMG DDS 1.4 / RTPS 2.5",
    },
    "dmx512": {"rate": 250_000, "dist": 300, "nodes": 32, "doc": "ANSI E1.11 (DMX512-A)"},
    "knx": {"rate": 9_600, "dist": 1000, "nodes": 57600, "doc": "ISO/IEC 14543 (KNX)"},
    "dali": {"rate": 1_200, "dist": 300, "nodes": 64, "doc": "IEC 62386 (DALI-2)"},
    # ------------------------------ USB / A-V -------------------------------
    "usb4": {"rate": 80_000_000_000, "dist": 2, "nodes": 127, "life": "active", "doc": "USB4 v2.0 (USB-IF)"},
    "midi": {"rate": 31_250, "dist": 15, "nodes": 4, "doc": "MMA MIDI 1.0; MIDI 2.0 (M2-104)"},
    "firewire": {
        "rate": 3_200_000_000,
        "dist": 100,
        "nodes": 63,
        "life": "legacy",
        "doc": "IEEE 1394-1995 / 1394b-2002",
    },
    # --------------------------- Wireless / sensor --------------------------
    "6lowpan": {
        "rate": 250_000,
        "dist": 100,
        "nodes": None,
        "life": "active",
        "osi": "L2.5-L3 (adaption + RPL)",
        "doc": "RFC 4944 / RFC 6282",
    },
    "nmea": {"rate": 250_000, "dist": 200, "nodes": 50, "doc": "NMEA 0183 v4.11; NMEA 2000"},
}

_SHORT_TO_FIELD = {
    "rate": "data_rate_max_bps",
    "dist": "distance_max_m",
    "nodes": "nodes_max",
    "life": "lifecycle",
    "osi": "osi_layer",
    "doc": "standard_doc",
}


def apply_parametric_specs(protocols):
    """Attach machine-readable numeric envelope + lifecycle + standard refs."""
    for protocol in protocols:
        base = deepcopy(_CAT_DEFAULTS.get(protocol["category"], _CAT_DEFAULTS["On-Board"]))
        for short, value in _OVERRIDES.get(protocol["id"], {}).items():
            base[_SHORT_TO_FIELD[short]] = value
        for field in SPEC_FIELDS:
            protocol[field] = base.get(field)
    return protocols


def format_bps(bps):
    """Human-readable data rate: 9600 -> '9.6 kbps', None -> 'carrier-defined'."""
    if bps is None:
        return "carrier-defined"
    if bps >= 1_000_000_000:
        return f"{bps / 1_000_000_000:g} Gbps"
    if bps >= 1_000_000:
        return f"{bps / 1_000_000:g} Mbps"
    if bps >= 1_000:
        return f"{bps / 1_000:g} kbps"
    return f"{bps:g} bps"


def format_m(m):
    """Human-readable distance: 0.3 -> '30 cm', None -> 'carrier-defined'."""
    if m is None:
        return "carrier-defined"
    if m < 1:
        return f"{m * 100:g} cm"
    if m >= 1000:
        return f"{m / 1000:g} km"
    return f"{m:g} m"
