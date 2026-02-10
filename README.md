<img src="./Images/Wallpaper.jpeg" style="width:100%;" />

# 🏠 My Home Lab & Command Center

Welcome to my Home Lab repository. This environment is a high-performance hybrid of **offensive security labs**, **self-hosted services**, **SIEM monitoring**, and **hardware hardening**.

> [!IMPORTANT]
> **Work in Progress**: This lab is constantly evolving. I’m frequently breaking, fixing, and optimizing things, so expect frequent updates!

---

## 🛠 Hardware Architecture

| Device | Role | Platform | Specs Highlights |
| --- | --- | --- | --- |
| **🚀 PLAYER 7** | **Primary Command Center** | Windows 11 / WSL2 | **Ultra 5 245K \| RTX 5070 \| 32GB DDR5** |
| **💻 Beelink** | Virtualization & SIEM | Proxmox | Wazuh, Metasploitable Labs |
| **🥧 Raspberry Pi 5** | Core Services | Debian / Docker | Nextcloud, Pi-hole, n8n |
| **⌨️ Pi 500+** | Dev Environment | Linux Arm | Custom Aliases & CTF Tools |
| **📱 Pixel 9a** | Hardened Mobile | GrapheneOS | Maya Golan Persona |
| **🐬 Flipper Zero** | RF & HID Tools | Unleashed FW | Sub-GHz & BadUSB Payloads |

---

## 📂 Repository Organization

### ⚡ Primary Workstation (PLAYER 7)
* **[`/config.md`](./config.md)**: Full hardware specifications and system architecture.
* **[`/cyber.md`](./cyber.md)**: WSL2 Kali Linux setup, Oh-My-Zsh customization, and CUDA-accelerated cracking.
* **[`/gaming.md`](./gaming.md)**: High-refresh rate optimizations (180Hz), DLSS 3.5, and monitoring stack.

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

* **Command & Control**: The **PLAYER 7** acts as the central node for managing the Proxmox cluster and RPi services.
* **SIEM Pipeline**: Wazuh Manager (Beelink) → `custom_n8n.py` (RPi 5) → Discord Alerts.
* **Vault Sync**: Real-time encrypted sync between **Pixel 9a**, **PLAYER 7**, and **RPi 5** via Syncthing.
* **Identity Management**: Isolated OpSec protocols for the **Maya Golan** persona.
* **GPU Cracking**: Offloading heavy cryptographic tasks from the lab to the **RTX 5070** via WSL2 CUDA passthrough.

---

> [!TIP]
> **Always optimize, never compromise.** Have fun breaking things.