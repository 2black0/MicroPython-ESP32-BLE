# MicroPython ESP32 BLE Demo

A lightweight MicroPython demo showing how to:

- Expose a Nordic UART Service (NUS) over BLE  
- Control the onboard LED  
- Read temperature & humidity from an HDC1080 sensor  

Ideal for prototyping sensor-to-mobile IoT applications.

---

## 📋 Prerequisites

- **Hardware**  
  - Wemos ESP32 D1 Mini (or any ESP32 board)  
  - HDC1080 temperature & humidity sensor  
  - Optional: external red LED on GPIO 2  

- **Software**  
  - MicroPython Firmware: `esp32-idf4-20210202-v1.14.bin`  
  - Tool to upload files: [ampy](https://github.com/scientifichackers/ampy) or the built-in WebREPL  
  - Android: [Serial Bluetooth Terminal](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal)

---

## ⚙️ Installation

1. Flash MicroPython firmware onto your ESP32:  
   ```bash
   esptool.py --port /dev/ttyUSB0 erase_flash
   esptool.py --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-idf4-20210202-v1.14.bin
   ```

2. Copy files to the board:

   ```bash
   ampy --port /dev/ttyUSB0 put main.py
   ampy --port /dev/ttyUSB0 put hdc1080.py
   ```

3. Reset the ESP32. It will start advertising as **ESP32**.

---

## 🚀 Usage

1. Open your BLE terminal app and connect to **ESP32**.

2. Send one of these commands:

   | Command     | Action                                     |
   | ----------- | ------------------------------------------ |
   | `red_led`   | Toggle the red LED (GPIO 2)                |
   | `read_temp` | Read temperature (°C) & get a notification |
   | `read_hum`  | Read humidity (%) & get a notification     |

3. You’ll receive responses ending with `\n`.

4. Watch the onboard LED blink when disconnected, solid when connected.

---

## 🔍 Wiring

```
ESP32 D1 Mini        HDC1080 Module
---------------       ----------------
GPIO 21 (SDA)   ───>   SDA
GPIO 22 (SCL)   ───>   SCL
GND             ───>   GND
3V3             ───>   VCC

GPIO 2 (optional) ──(LED)─> GND
```

## 📄 License

This project is licensed under the MIT License.
