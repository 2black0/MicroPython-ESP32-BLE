# MicroPython ESP32 BLE

This is Demo of BLE on ESP32 used for Communication with Android
You need install Serial Bluetooth Terminal (from PS) or you can make your own apps :)

Device:
- Wemos ESP32 D1 Mini
- HDC1080 Sensor

MicroPython Firmware: esp32-idf4-20210202-v1.14.bin (download here https://micropython.org/download/esp32/)

How to use:
1. Copy main.py into your device
2. Restart your device
3. Connect the Android with Bluetooth of ESP32 in Serial Bluetooth Terminal apps
4. send 'red_led' in Serial Bluetooth Terminal for turn on / off the led in ESP32
5. send 'read_temp' and 'read_hum' for read temperature and humidity from HDC1080
