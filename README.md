![Wallpaper](Images/Wallpaper.jpeg)

# 🏠 My Home Lab | Secure Infrastructure & Pentesting

Welcome to my Home Lab repository. This environment is a hybrid of **self-hosted production services**, **cybersecurity monitoring (SIEM)**, and **mobile/hardware hardening**.

> [!WARNING]
> **Experimental Environment**: This repository contains penetration testing tools (Flipper Zero, Metasploitable, Wazuh) and hardened mobile configurations. Use responsibly.

---

## 🛠 Hardware Architecture

| Device | Role | OS / Platform |
| :--- | :--- | :--- |
| **Beelink** | Virtualization & Security | Proxmox VE (Wazuh, Bitwarden, n8n) |
| **Raspberry Pi 5** | Core Home Services | Raspberry Pi OS (Nextcloud, Pi-hole) |
| **Pi 500+** | Dev & Tools | Raspberry Pi OS (CTF Aliases & Tools) |
| **Pixel 9a** | Hardened Mobile | GrapheneOS (Maya Golan Persona) |
| **Flipper Zero** | Hardware Pentesting | Unleashed Firmware |

---

## 📂 Repository Roadmap

### 🛡️ Security & SIEM (`/Beelink`, `/Pixel 9a`)
- **Wazuh**: Full SIEM setup with custom n8n integration, Discord alerts, and automated reporting.
- **Metasploitable**: Dedicated VM for internal pentesting and CTF practice.
- **Bitwarden**: Self-hosted password management for the entire lab.
- **Sock Puppet**: Identity management protocol for the **Maya Golan** persona.

### 🤖 Automation & Monitoring (`/Raspberry pi 5`)
- **n8n**: Workflow automation (local on Pi 5 & cloud-ready on Beelink).
- **Custom Scripts**: 
  - `Cryptalyst.py`: Crypto-analysis/monitoring.
  - `Rasbstats`: Real-time hardware telemetry.
  - `Forge`, `Nexus`, `Miru`, `Joker`: Custom Python automation suite.
- **Crontabs**: Scheduled maintenance and backup scripts.

### 📡 Field Tools (`/Flipper-Zero`)
- **BadUSB**: Automated payloads (RickRoll, Stealth Info Grab, Emergency Lock).
- **Unleashed Config**: Frequency de-restriction and extended protocol dictionaries.

### 🏠 Home Services (`/Raspberry pi 5`, `/Beelink`)
- **Nextcloud**: Personal cloud storage linked to mobile profiles.
- **Pi-hole**: Network-wide DNS sinkhole and ad-blocking.
- **Stremio**: Self-hosted media streaming via Docker.
- **MesSignets**: Local bookmark management system.

---

## 🚀 Key Workflows

1. **The Vault Sync**: All documentation from the **Pixel 9a** is synced via Syncthing to the **RPi 5**, then backed up to the **Beelink** storage.
2. **Security Alerts**: **Wazuh Manager** monitors log events → Triggers **custom_n8n.py** → Sends formatted reports to **Discord**.
3. **Mobile Isolation**: Using GrapheneOS profiles to separate "Owner" (Lab Admin) from "Maya Golan" (Sock Puppet).

---

## 📝 Maintenance & Logs

- **System Tools**: See `/Raspberry pi 500+/Config_Tools` for environment setup.
- **CTF Ready**: Use `ctf_aliases` on the Pi 500+ for a streamlined terminal experience.
- **Shopping List**: Planned upgrades for the Proxmox nodes and RF antennas.