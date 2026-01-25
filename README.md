![Wallpaper](Images/Wallpaper.jpeg)

# 🏠 My Home Lab

Welcome to my Home Lab repository! This is a comprehensive collection of configurations, security protocols, and documentation for my local server and mobile pentesting environment.

> [!IMPORTANT]
> **Work in Progress**: This lab is constantly evolving. I’m frequently breaking, fixing, and optimizing things—especially regarding mobile hardening and OPSEC.

---

## 🛠 Hardware & Setup

Currently, my lab runs on the following hardware:

### 🖥️ Servers & Compute
- **Beelink**: Running **Proxmox** for virtualization and heavy lifting.
- **Raspberry Pi 5**: Primary node for core services (Nextcloud, n8n, Syncthing).
- **Raspberry Pi 500+**: Dedicated to custom shell tools and aliases.

### 📱 Mobile & Pentesting
- **Pixel 9a**: Running **GrapheneOS**. Hardened mobile device with multiple isolated profiles.
- **Flipper Zero**: Running **Unleashed Firmware**. Used for Sub-GHz, NFC, and BadUSB automation.

---

## 📂 Repository Structure

| Folder             | Description                                                                 |
| ------------------ | --------------------------------------------------------------------------- |
| `/Beelink`         | Proxmox configurations and VM setups.                                       |
| `/Raspberry pi 5`  | Pi-hole, Nextcloud, n8n, and Syncthing automation.                          |
| `/Pixel 9a`        | GrapheneOS hardening, system config, and **Sock Puppet** strategies.        |
| `/Flipper-Zero`    | Unleashed firmware config, databases, and custom **BadUSB** payloads.       |
| `/Shopping-List`   | Planned upgrades and hardware tracking.                                     |
| `/Images`          | Resources, wallpapers, and diagrams.                                        |

---

## 🚀 Key Services & Security

### 🌐 Core Services
- **Network**: Pi-hole (DNS Ad-blocking) & PIA VPN.
- **Automation**: n8n, Syncthing (RPi 5 ↔ Pixel 9a sync), and Crontabs.
- **Cloud**: Self-hosted Nextcloud instance.

### 🔐 Security & OPSEC
- **Mobile Hardening**: GrapheneOS with sandboxed Google Play and restricted Gboard.
- **Identity Management**: **"Maya Golan"** persona documentation for isolated testing.
- **Hardware Tools**: Flipper Zero for physical security audits and HID automation.
- **Emergency Protocols**: Integrated **Burn Scripts** and checklists for data sanitization.

---

## 📝 Maintenance

Since this is a personal "playground," documentation might lag behind the actual configuration. 