# SPDX-FileCopyrightText: 2024 Mike Causer <https://github.com/mcauser>
# SPDX-License-Identifier: MIT

"""
MicroPython HDC1080 Temperature & Humidity Sensor
https://github.com/mcauser/micropython-hdc1080
"""

__version__ = "1.0.1"

from micropython import const
from time import sleep_ms

# registers
_TEMPERATURE = const(0x00)
_HUMIDITY = const(0x01)
_CONFIG = const(0x02)
_SERIAL_ID0 = const(0xFB)
_SERIAL_ID1 = const(0xFC)
_SERIAL_ID2 = const(0xFD)
_MANUFACTURER_ID = const(0xFE)
_DEVICE_ID = const(0xFF)


class HDC1080:
    def __init__(self, i2c):
        self._i2c = i2c
        self._address = 0x40  # fixed I2C address
        self._buf1 = bytearray(1)
        self._buf2 = bytearray(2)
        self._config = 0x10

    def _read16(self, reg):
        self._buf1[0] = reg
        self._i2c.writeto(self._address, self._buf1)
        sleep_ms(20)
        self._i2c.readfrom_into(self._address, self._buf2)
        return (self._buf2[0] << 8) | self._buf2[1]

    def _write_config(self):
        self._buf2[0] = _CONFIG
        self._buf2[1] = self._config
        self._i2c.writeto(self._address, self._buf2)

    def _read_config(self):
        # shift out the first 8 reserved bits
        self._config = self._read16(_CONFIG) >> 8

    def check(self):
        if self._i2c.scan().count(self._address) == 0:
            raise OSError(f"HDC1080 not found at I2C address {self._address:#x}")
        return True

    def config(
        self, config=None, humid_res=None, temp_res=None, mode=None, heater=None
    ):
        if config is not None:
            self._config = config
            self._write_config()
        else:
            self._read_config()
            if humid_res is not None:
                # 00 = 14-bit, 01 = 11-bit, 10 = 8-bit
                if humid_res == 8:
                    self._config |= 2
                    self._config &= ~1
                elif humid_res == 11:
                    self._config &= ~2
                    self._config |= 1
                elif humid_res == 14:
                    self._config &= ~3
                else:
                    raise ValueError("humid_res must be 8, 11 or 14")
            if temp_res is not None:
                # 0 = 14-bit, 1 = 11-bit
                if temp_res == 11:
                    self._config |= 4
                elif temp_res == 14:
                    self._config &= ~4
                else:
                    raise ValueError("temp_res must be 11 or 14")
            if mode is not None:
                # mode 0 = temp or humid acquired
                # mode 1 = temp and humid acquired in sequence, temp first
                self._config &= ~16
                self._config |= (mode & 1) << 4
            if heater is not None:
                self._config &= ~32
                self._config |= (heater & 1) << 5
            self._write_config()

    def reset(self):
        self._config = 128
        self._write_config()
        # sw reset bit self clears
        self._read_config()

    def battery_status(self):
        # returns 0 if Vcc > 2.8V
        # returns 1 if Vcc < 2.8V
        self._read_config()
        return (self._config >> 3) & 1

    def temperature(self):
        # temperature in celsius
        return (self._read16(_TEMPERATURE) / 65536) * 165 - 40

    def humidity(self):
        # relative humidity percentage
        return (self._read16(_HUMIDITY) / 65536) * 100

    def serial_number(self):
        # unique per device
        return (
            (self._read16(_SERIAL_ID0) << 24)
            | (self._read16(_SERIAL_ID1) << 8)
            | (self._read16(_SERIAL_ID2) >> 8)
        )

    def manufacturer_id(self):
        # fixed 21577 == 0x5449 == b'\x54\x49' == b'TI'
        return self._read16(_MANUFACTURER_ID)

    def device_id(self):
        # fixed 4176 == 0x1050 == b'\x10\x50' == b'\x10P'
        return self._read16(_DEVICE_ID)
