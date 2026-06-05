# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **personal homelab documentation and configuration repository** — not a traditional software project. It contains infrastructure-as-code (Docker Compose), configuration documentation (Markdown), and Python automation scripts for a multi-device homelab setup spanning 6 physical devices. There is no build system, test runner, or CI/CD pipeline.

## Devices and Their Roles

| Device | Role | Key IPs |
|---|---|---|
| **Player7** | Primary workstation (Intel Ultra 5 245K, RTX 5070, 32GB DDR5) | Local |
| **Beelink** | Proxmox hypervisor hosting Ubuntu Server Docker stack | 10.100.102.15 |
| **Raspberry Pi 5** | Core self-hosted services + automation scripts | 100.121.5.36 (Tailscale) |
| **Raspberry Pi 500+** | Dev environment, CTF tooling | — |
| **Flipper Zero** | RF/HID/NFC security testing (Unleashed firmware) | — |
| **Pixel 9a** | GrapheneOS hardened mobile | — |

## Architecture: How Services Connect

```
Player7 (WSL2/Kali, VMware labs, CUDA cracking)
  └─ Beelink (Proxmox @ 10.100.102.15)
      ├─ VM 101: Metasploitable 2  (intentionally vulnerable lab target)
      ├─ VM 102: Kali Linux        (offensive VM)
      ├─ LXC: Tailscale subnet router (advertises 10.100.102.0/24)
      └─ Ubuntu Server Docker stack:
          ├─ Wazuh Manager/Indexer/Dashboard (SIEM, ports 1514/1515/55000/8443/9200)
          ├─ Vaultwarden (password manager, TLS via /certs/)
          ├─ n8n main + worker (workflow automation, port 5678)
          ├─ Dashy (service dashboard, port 8080)
          └─ Stremio + Gluetun VPN (PIA, Israel region)

Raspberry Pi 5 (100.121.5.36)
  ├─ Nextcloud     (DAVx5 sync from Pixel 9a, data on label=NEXTCLOUD_DATA SSD)
  ├─ n8n           (webhook relay for Wazuh → Discord alerts)
  ├─ Pi-hole       (DNS on port 53, monitored by Wazuh as SIEM input)
  ├─ Uptime Kuma   (service monitoring, port 3001)
  ├─ Syncthing     (vault sync: RPi5 ↔ Pixel 9a)
  └─ Cron scripts  (6 Python automation scripts, see below)
```

**Alert pipeline:** Wazuh agents → Wazuh Manager → `custom_n8n.py` (Python bridge) → RPi5 n8n webhook → Discord

## Docker Compose Services

All services use `restart: always` and named volumes. No health checks are defined — rely on Uptime Kuma for monitoring.

- **Wazuh** (`Beelink/Proxmox/Ubuntu-Server/Wazuh/docker-compose.yaml`): v4.14.2, three containers (manager, indexer, dashboard). Env vars: `INDEXER_PASSWORD`, `API_PASSWORD`, `DASHBOARD_PASSWORD`.
- **n8n** (`Beelink/Proxmox/Ubuntu-Server/n8n/docker-compose.yaml`): Main + worker pattern, PostgreSQL 16 + Redis 7 backend, Cloudflare Tunnel for external access. Env vars: `DB_POSTGRESDB_*`, `N8N_ENCRYPTION_KEY`.
- **Vaultwarden** (`Beelink/Proxmox/Ubuntu-Server/bitwarden/docker-compose.yaml`): TLS certs mounted from `/certs/cert.crt` and `/cert.key`, accessible via Tailscale DNS.
- **Stremio** (`Beelink/Proxmox/Ubuntu-Server/Streamio/docker-compose.yaml`): Routes through Gluetun VPN container (PIA, OpenVPN, Israel region).
- **RPi5 n8n** (`Rasberry pi 5/n8n/docker-compose.yaml`): Single instance using `naskio/n8n-python:latest-debian` (Python-capable image).

## Python Automation Scripts (RPi5 Crontab)

All scripts live in `/home/pi/Scripts/` on the RPi5 and share these patterns:
- `load_dotenv()` from a `.env` file for secrets (`DISCORD_WEBHOOK_URL`, `GEMINI_API_KEY`)
- Google Gemini API (`genai` library) for AI-generated content
- Discord webhooks for output delivery
- JSON files for local persistence (weights, cache, stats)
- SQLite for structured local storage

| Script | Schedule | Purpose |
|---|---|---|
| `Cryptalyst/Cryptalyst.py` | Daily 19:00 | Crypto market analysis via Gemini → Discord |
| `Joker/joker.py` | Every 2h | Randomized content generator (weighted source selection) |
| `Joker/jokerxxx.py` | Every 4h | NSFW-aware content variant |
| `Forge/forge.py` | Daily 12:00 | Cybersecurity/IT/coding challenge generator → Discord |
| `Nexus/nexus.py` | Daily 11:00 | (See script for current purpose) |
| `Scripties/scripties.py` | Daily 00:00 | (See script for current purpose) |

To run a script manually on the RPi5:
```bash
cd /home/pi/Scripts/<ScriptName> && python3 <script>.py
# For Forge specifically (uses its own venv):
cd /home/pi/Scripts/Forge && /home/pi/Scripts/env/bin/python3 forge.py
```

## Key Conventions

**Secrets management:** `.env` files are gitignored (`.gitignore` excludes `.env`, `*.pem`, `*.key`, `.terraform/`, `*.tfstate`). Never commit secrets. All docker-compose files reference env vars that must exist in a local `.env` alongside the compose file.

**Filesystem labels for portability:** The Nextcloud SSD is mounted via `LABEL=NEXTCLOUD_DATA` in `/etc/fstab`, not by UUID or device path. This allows zero-reconfiguration SSD swaps.

**Tailscale mesh (no public ports):** Services are accessed via Tailscale IPs or DNS, not exposed to the internet. Cloudflare Tunnel handles the one exception (n8n external webhooks).

**Versioned Docker images:** Pin exact versions (e.g., `wazuh-manager:4.14.2`, `postgres:16-alpine`). Do not use `latest` tags except for the RPi5 n8n image.

**Documentation style:** Use GitHub-flavored Markdown with callout blocks (`> [!WARNING]`, `> [!IMPORTANT]`, `> [!TIP]`), hardware spec tables, and troubleshooting sections. Each device has its own directory with config and operational docs.

## Network Topology Reference

- **Tailscale subnet router** (LXC on Beelink): Advertises `10.100.102.0/24` to the Tailscale mesh. IP forwarding must be enabled on the host (`net.ipv4.ip_forward=1`).
- **Beelink LAN IP:** `10.100.102.15`
- **RPi5 Tailscale IP:** `100.121.5.36`
- **Proxmox Web UI:** `https://10.100.102.15:8006`
- **Wazuh Dashboard:** `https://<beelink-ip>:8443`
- **TLS certificates:** Obtained via `tailscale cert` for `.ts.net` hostnames.

## Proxmox VM Notes

- **VM 101 (Metasploitable 2):** Uses IDE disk controller and Intel E1000 NIC — required for the legacy OS. 512MB RAM.
- **VM 102 (Kali):** QEMU Guest Agent installed, SSH on port 22. 2 cores, 4GB RAM.
- If importing a `.vmdk` for Metasploitable: convert first with `qemu-img convert -f vmdk -O qcow2 source.vmdk dest.qcow2`, then import with `qm importdisk`.
- Reset SSH host keys after cloning VMs: `sudo rm /etc/ssh/ssh_host_* && sudo dpkg-reconfigure openssh-server`.
