# -*- coding: utf-8 -*-
"""Minimal, copy-pasteable bring-up snippets per flagship protocol.

Each snippet is the smallest program that proves the bus is alive
(echo a byte, scan for a device, read an ID register). Kept short on
purpose — this is a field reference, not a driver manual.
"""

SNIPPETS = {
    "uart": [
        {
            "platform": "Arduino (C++)",
            "language": "cpp",
            "title": "115200 8N1 echo — proves TX+RX wiring",
            "code": (
                "void setup() {\n"
                "  Serial.begin(115200);\n"
                "  while (!Serial) { ; }  // wait on native-USB boards\n"
                "}\n"
                "void loop() {\n"
                "  if (Serial.available()) {\n"
                "    Serial.write(Serial.read());  // echo back\n"
                "  }\n"
                "}\n"
            ),
        },
        {
            "platform": "MicroPython",
            "language": "python",
            "title": "UART write + readline",
            "code": (
                "from machine import UART\n"
                "uart = UART(1, baudrate=115200, tx=17, rx=16)\n"
                "uart.write(b'hello\\r\\n')\n"
                "print(uart.readline())\n"
            ),
        },
    ],
    "i2c": [
        {
            "platform": "Arduino (C++)",
            "language": "cpp",
            "title": "Bus scanner — finds every ACKing address",
            "code": (
                "#include <Wire.h>\n"
                "void setup() {\n"
                "  Serial.begin(115200);\n"
                "  Wire.begin();\n"
                "  for (uint8_t addr = 1; addr < 127; addr++) {\n"
                "    Wire.beginTransmission(addr);\n"
                "    if (Wire.endTransmission() == 0) {\n"
                '      Serial.print("Found: 0x"); Serial.println(addr, HEX);\n'
                "    }\n"
                "  }\n"
                "}\n"
                "void loop() {}\n"
            ),
        },
        {
            "platform": "STM32 HAL (C)",
            "language": "c",
            "title": "Read WHO_AM_I register (e.g. MPU-6050)",
            "code": (
                "uint8_t reg = 0x75, id = 0;\n"
                "HAL_I2C_Mem_Read(&hi2c1, 0x68 << 1, reg,\n"
                "                 I2C_MEMADD_SIZE_8BIT, &id, 1, 100);\n"
            ),
        },
    ],
    "spi": [
        {
            "platform": "Arduino (C++)",
            "language": "cpp",
            "title": "Flash JEDEC ID — proves SCLK/MOSI/MISO/CS",
            "code": (
                "#include <SPI.h>\n"
                "const int CS = 10;\n"
                "void setup() {\n"
                "  Serial.begin(115200);\n"
                "  pinMode(CS, OUTPUT); digitalWrite(CS, HIGH);\n"
                "  SPI.begin();\n"
                "  digitalWrite(CS, LOW);\n"
                "  SPI.transfer(0x9F);  // JEDEC ID command\n"
                "  uint8_t mfr = SPI.transfer(0x00);\n"
                "  uint8_t mem = SPI.transfer(0x00);\n"
                "  uint8_t cap = SPI.transfer(0x00);\n"
                "  digitalWrite(CS, HIGH);\n"
                '  Serial.printf("%02X %02X %02X\\n", mfr, mem, cap);\n'
                "}\n"
                "void loop() {}\n"
            ),
        },
        {
            "platform": "Linux / Raspberry Pi (Python)",
            "language": "python",
            "title": "Same JEDEC ID via spidev, mode 0",
            "code": (
                "import spidev\n"
                "spi = spidev.SpiDev(0, 0)\n"
                "spi.max_speed_hz = 10_000_000\n"
                "spi.mode = 0  # CPOL=0, CPHA=0\n"
                "resp = spi.xfer2([0x9F, 0x00, 0x00, 0x00])\n"
                "print([hex(b) for b in resp[1:]])  # expect e.g. EF 40 18\n"
            ),
        },
    ],
    "can": [
        {
            "platform": "Arduino + MCP2515 (C++)",
            "language": "cpp",
            "title": "Send one 8-byte frame at 500 kbps",
            "code": (
                "#include <mcp_can.h>\n"
                "#include <SPI.h>\n"
                "MCP_CAN CAN(10);  // CS pin\n"
                "void setup() {\n"
                "  Serial.begin(115200);\n"
                "  while (CAN_OK != CAN.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ)) delay(100);\n"
                "  CAN.setMode(MCP_NORMAL);\n"
                "  uint8_t data[8] = {0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88};\n"
                "  CAN.sendMsgBuf(0x123, 0, 8, data);\n"
                "}\n"
                "void loop() {}\n"
            ),
        },
        {
            "platform": "Linux SocketCAN (Python)",
            "language": "python",
            "title": "Receive and print one frame",
            "code": (
                "import can\n"
                "bus = can.interface.Bus(channel='can0', interface='socketcan')\n"
                "msg = bus.recv(timeout=1.0)\n"
                "if msg is not None:\n"
                "    print(f'{msg.arbitration_id:#x} [{msg.dlc}]', msg.data.hex(' '))\n"
            ),
        },
    ],
    "modbus_rtu": [
        {
            "platform": "Python (pymodbus)",
            "language": "python",
            "title": "Read 4 holding registers from slave 1",
            "code": (
                "from pymodbus.client import ModbusSerialClient\n"
                "mb = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=9600,\n"
                "                        parity='E', timeout=1)\n"
                "mb.connect()\n"
                "rr = mb.read_holding_registers(address=0, count=4, device_id=1)\n"
                "print(rr.registers)\n"
                "mb.close()\n"
            ),
        },
    ],
    "mqtt": [
        {
            "platform": "Python (paho-mqtt)",
            "language": "python",
            "title": "Publish one retained reading, QoS 1",
            "code": (
                "import paho.mqtt.client as mqtt\n"
                "c = mqtt.Client()\n"
                "c.connect('broker.local', 1883, keepalive=60)\n"
                "c.publish('plant/line1/temp', '23.4', qos=1)\n"
                "c.disconnect()\n"
            ),
        },
        {
            "platform": "MicroPython (umqtt)",
            "language": "python",
            "title": "Publish from a constrained device",
            "code": (
                "from umqtt.simple import MQTTClient\n"
                "c = MQTTClient('pico-01', 'broker.local')\n"
                "c.connect()\n"
                "c.publish(b'plant/line1/temp', b'23.4')\n"
                "c.disconnect()\n"
            ),
        },
    ],
}


def get_snippets(pid):
    """Return the snippet list for a protocol id, or []."""
    return SNIPPETS.get(pid, [])


def has_snippets(pid):
    """Whether bring-up snippets exist for this protocol id."""
    return pid in SNIPPETS
