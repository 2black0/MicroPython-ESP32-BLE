"""
main.py – MicroPython ESP32 BLE UART Demo

This script configures an ESP32 as a BLE (Bluetooth Low Energy) peripheral offering
the Nordic UART Service (NUS). It lets a central device (e.g., smartphone app)
send simple text commands to:
  - Toggle an onboard LED
  - Read temperature and humidity from an HDC1080 sensor

The on-board LED also blinks when disconnected and stays solid when connected.
"""

from machine import Pin, Timer, SoftI2C
from time import sleep_ms
import ubluetooth
# raw_temperature is available but not used in this example; you could use it for direct chip-temp reads
from esp32 import raw_temperature  
from hdc1080 import HDC1080

class BLE:
    """
    BLE UART helper class.

    Handles:
      - BLE initialization & advertising
      - Connection / disconnection callbacks
      - GATT service registration (Nordic UART Service)
      - Reading incoming commands and sending notifications

    Commands supported over BLE:
      - 'red_led'   : Toggle the red LED (GPIO2)
      - 'read_temp' : Read temperature in °C from HDC1080
      - 'read_hum'  : Read relative humidity (%) from HDC1080
    """
    def __init__(self, name):
        """
        Initialize the BLE device.

        Args:
            name (str): The advertised device name (e.g., "ESP32").
        """
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)

        # On-board LED pin (GPIO2 on many ESP32 boards)
        self.led = Pin(2, Pin.OUT)

        # Two timers for blinking the LED when disconnected
        self.timer1 = Timer(0)
        self.timer2 = Timer(1)

        # Start with disconnected blink pattern
        self.disconnected()

        # Register IRQ callback before registering services
        self.ble.irq(self.ble_irq)

        # Setup Nordic UART GATT service
        self.register()

        # Begin advertising
        self.advertiser()

    def connected(self):
        """
        Called when a central device connects.
        Stops the blink timers so the LED can stay solid.
        """
        self.timer1.deinit()
        self.timer2.deinit()

    def disconnected(self):
        """
        Called when no central is connected.
        Starts two timers to blink the LED:
          - Timer1 sets LED on every second
          - Timer2 clears LED every second, offset by 200ms
        """
        self.timer1.init(period=1000, mode=Timer.PERIODIC,
                         callback=lambda t: self.led(1))
        sleep_ms(200)
        self.timer2.init(period=1000, mode=Timer.PERIODIC,
                         callback=lambda t: self.led(0))

    def ble_irq(self, event, data):
        """
        BLE interrupt request handler.

        Args:
            event (int): The BLE event code.
            data: Event-specific data.
        """
        if event == 1:
            # _IRQ_CENTRAL_CONNECT: a central has connected
            self.connected()
            self.led(1)  # solid on to indicate connection

        elif event == 2:
            # _IRQ_CENTRAL_DISCONNECT: central has disconnected
            self.advertiser()    # resume advertising
            self.disconnected()  # restart blink pattern

        elif event == 3:
            # _IRQ_GATTS_WRITE: client has written to RX characteristic
            buffer = self.ble.gatts_read(self.rx)
            message = buffer.decode('utf-8').strip()
            print("Received over BLE:", message)

            # Handle known commands
            if message == 'red_led':
                # toggle the LED and send status back
                red_led.value(not red_led.value())
                print('red_led state:', red_led.value())
                self.send('red_led ' + str(red_led.value()))

            elif message == 'read_temp':
                # read temp in °C (True for fast, raw data)
                temp = sensor.read_temperature(True)
                print('Temperature:', temp)
                self.send(str(temp))

            elif message == 'read_hum':
                # read humidity in %
                hum = sensor.read_humidity()
                print('Humidity:', hum)
                self.send(str(hum))

    def register(self):
        """
        Register the Nordic UART Service (NUS) with two characteristics:
          - TX (notify) for sending data to central
          - RX (write) for receiving data from central
        """
        # NUS base UUID and characteristic UUIDs
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID  = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID  = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX  = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX  = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)

        # Define the service tuple
        BLE_UART  = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES  = (BLE_UART,)

        # Register GATT services and save characteristic handles
        ((self.tx, self.rx,),) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        """
        Send a notification on the TX characteristic.

        Args:
            data (str): The string to send (a newline will be appended).
        """
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        """
        Start BLE advertising with the given device name.
        Uses a simple non-connectable advertisement packet every 100ms.
        """
        name_bytes = bytes(self.name, 'utf-8')
        adv_payload = bytearray('\x02\x01\x02') + bytearray((len(name_bytes) + 1, 0x09)) + name_bytes
        self.ble.gap_advertise(100, adv_payload)


# === Main / Test Code ===

# Initialize I2C for the HDC1080 sensor
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
sensor = HDC1080(i2c)

# On-board LED reused for command toggling
red_led = Pin(2, Pin.OUT)

# Create and start BLE UART device named "ESP32"
ble = BLE("ESP32")
