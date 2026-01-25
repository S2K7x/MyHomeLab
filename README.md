# 🏠 My Home Lab

Welcome to my Home Lab repository. This environment is a hybrid of **self-hosted services**, **SIEM monitoring**, and **mobile/hardware hardening**.

> [!IMPORTANT]
> **Work in Progress**: This lab is constantly evolving. I’m frequently breaking, fixing, and optimizing things, so expect frequent updates!

---

## 🛠 Hardware Architecture

| Device | Role | Platform |
| --- | --- | --- |
| **💻 Beelink** | Virtualization & SIEM | Proxmox (Wazuh, Metasploitable) |
| **🥧 Raspberry Pi 5** | Core Services | Nextcloud, Pi-hole, n8n |
| **⌨️ Pi 500+** | Dev Environment | Custom Aliases & CTF Tools |
| **📱 Pixel 9a** | Hardened Mobile | GrapheneOS (Maya Golan Persona) |
| **🐬 Flipper Zero** | RF & HID Tools | Unleashed Firmware |

---

## 📂 Repository Organization

### 🛡️ Security & Pentesting

* **`/Beelink`**: Wazuh SIEM (Discord alerts), Metasploitable lab, and Bitwarden.
* **`/Pixel 9a`**: GrapheneOS config & **Maya Golan** Sock Puppet documentation.
* **`/Flipper-Zero`**: Unleashed firmware config and **BadUSB** payloads.

### 🤖 Automation & Monitoring

* **`/Raspberry pi 5`**:
* **Services**: n8n, Pi-hole, Nextcloud, MesSignets.
* **Script Suite**: `Cryptalyst` (Crypto), `Rasbstats` (Telemetry), `Forge`, `Joker`.


* **`/Raspberry pi 500+`**: Shell optimization and `ctf_aliases`.

---

## 🚀 Key Workflows

* **SIEM Pipeline**: Wazuh Manager → `custom_n8n.py` → Discord Alerts.
* **Vault Sync**: Real-time sync between **Pixel 9a** and **RPi 5** via Syncthing.
* **Identity Management**: Isolated OpSec protocols for the **Maya Golan** persona.
* **HID Automation**: Flipper Zero payloads for rapid system maintenance.

---

> [!TIP]
> **Have fun**