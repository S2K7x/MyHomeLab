# Flipper Zero - Unleashed Configuration

Detailed documentation of the Flipper Zero setup, firmware hardening, and integration within the **MyHomeLab** ecosystem.

## 💾 1. Firmware Specification

The device has been flashed from Official Firmware (OFW) to **Unleashed**, a power-user fork that unlocks restricted frequencies and adds advanced pentesting tools.

* **Firmware:** [Unleashed Firmware](https://github.com/DarkFlippers/unleashed-firmware)
* **Installation Method:** Web Installer (via `web.unleashedflip.com`)
* **Key Capabilities Unlocked:**
* **Sub-GHz:** Removed regional TX (Transmission) restrictions (Extended Range).
* **Extra Protocols:** Added support for BFT Mitto, Somfy Telis, Nice Flor S, and more.
* **BadKB:** HID (Human Interface Device) emulation over Bluetooth.



---

## 🛠️ 2. System Hardening & UI

Customized settings to improve accuracy, security, and battery management.

* **Security (PIN Code):**
* **Status:** Enabled.
* **Lock Shortcut:** Hold **UP** on the desktop to lock the device instantly.
* **Function:** Protects Sub-GHz logs, NFC dumps, and BadUSB scripts from unauthorized physical access.


* **Display Settings:**
* **Battery View:** Set to `Percentage` for precise monitoring.
* **Clock:** Enabled in the Status Bar (useful for timestamping signal captures).
* **Status Bar:** Set to `On` to monitor active Bluetooth/SD Card status.


* **Sub-GHz HAL:**
* **Extend TX Range:** Enabled for laboratory testing.
* **Frequency Hopping:** Configured in Frequency Analyzer for rapid signal detection.



---

## 📁 3. Storage & Databases (SD Card)

The Flipper Zero is equipped with a high-speed MicroSD card containing the **UberGuidoZ Playground** databases.

### SD Card Structure

* `/subghz`: Contains raw signal dumps and protocol-specific remotes for HomeLab testing.
* `/nfc`: Enhanced with `nfc_dict.txt` for Mifare Classic brute-forcing.
* `/infrared`: Universal remote library for Projectors, ACs, and Audio systems.
* `/badusb`: Automated scripts for system maintenance and payload testing.

### Input Layout (AZERTY)

To ensure compatibility with French keyboards (MacBook/PC), the French layout is configured:

* **Path:** `/ext/badusb/assets/fr.json`
* **Usage:** Selected in the BadUSB/BadKB app settings before running payloads.

---

## 📱 4. GrapheneOS & Mobile Integration

The Flipper Zero is paired with the **Pixel 9a** for mobile management.

* **App:** Flipper Mobile App (Installed via Aurora Store).
* **Connectivity:** Bluetooth Low Energy (BLE).
* **Workflow:**
1. Capture signal/tag in the field.
2. Sync to Pixel 9a via Bluetooth.
3. Upload to **Nextcloud (RPi 5)** via the Pixel for long-term storage and analysis.
4. Remote trigger: Trigger Sub-GHz or IR signals from the Pixel while the Flipper is hidden.



---

## 📡 5. HomeLab Use Cases

Current active testing scenarios for this device:

1. **Physical Access Audit:** Cloning and emulating 125kHz RFID and NFC tags used in the lab environment.
2. **Smart Home Analysis:** Intercepting 433.92MHz signals from smart plugs to map command structures.
3. **HID Maintenance:** Using BadUSB scripts to automate repetitive CLI tasks on the Raspberry Pi 5 or Proxmox nodes.

---

## ⚠️ Safety & Compliance

* **Educational Use Only:** All Sub-GHz transmissions are conducted within a controlled laboratory environment.
* **TX Responsibility:** Extended frequency range is used strictly in accordance with local regulations or within RF-shielded environments.

