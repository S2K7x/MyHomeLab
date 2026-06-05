# UbuntuServer — Beelink Mini S13 VM

> **Role:** Primary self-hosted services node, monitoring hub, and SIEM platform.
> Runs as a KVM/QEMU virtual machine on the Beelink Mini S13 (Proxmox host).

---

## Hardware & System Specs

| Property | Value |
|---|---|
| **Hostname** | `ubuntuserver` |
| **OS** | Ubuntu 24.04.3 LTS (Noble Numbat) |
| **Hypervisor** | KVM / QEMU (Proxmox host) |
| **vCPUs** | 4 |
| **RAM** | 11 GB |
| **Root Volume** | 61 GB (LVM — `ubuntu-vg/ubuntu-lv`) |
| **Unallocated** | `lv-0` — 62 GB LVM volume (unmounted, available for root extension) |
| **LAN IP** | `10.100.102.101` |
| **Tailscale IP** | `100.123.91.70` |
| **VPN** | Tailscale (mesh VPN) |

> [!NOTE]
> `lv-0` (62 GB) is currently unmounted and can be used to extend the root filesystem when needed.
> Use the `devops/disk-forensics` Hermes skill to investigate and extend LVM.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│               Beelink Mini S13 (Proxmox)                │
│  ┌───────────────────────────────────────────────────┐  │
│  │          UbuntuServer VM (Ubuntu 24.04)           │  │
│  │  10.100.102.101  │  Tailscale: 100.123.91.70      │  │
│  │                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │  Monitoring  │  │   Security   │               │  │
│  │  │  Prometheus  │  │  Wazuh SIEM  │               │  │
│  │  │  Grafana     │  │  Fail2ban    │               │  │
│  │  │  cAdvisor    │  │  Tailscale   │               │  │
│  │  │  NodeExp     │  └──────────────┘               │  │
│  │  │  Glances     │  ┌──────────────┐               │  │
│  │  │  Dozzle      │  │  Management  │               │  │
│  │  │  Speedtest   │  │  Portainer   │               │  │
│  │  └──────────────┘  │  NPM (proxy) │               │  │
│  │  ┌──────────────┐  │  Dashy       │               │  │
│  │  │     Apps     │  │  Filebrowser │               │  │
│  │  │  Vaultwarden │  └──────────────┘               │  │
│  │  │  Samba       │                                 │  │
│  │  │  IT-Tools    │  ┌──────────────┐               │  │
│  │  │  Watchtower  │  │  Automation  │               │  │
│  │  │  MyLittleQ   │  │  Hermes      │               │  │
│  │  └──────────────┘  │  Cron jobs   │               │  │
│  │                     └──────────────┘               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │
         ├── Discord (alerts & daily reports)
         ├── Tailscale (remote access from any device)
         └── Nginx Proxy Manager (reverse proxy → HTTPS)
```

---

## Running Services (22 Containers)

### Monitoring Stack

| Service | Port | Image | Description |
|---|---|---|---|
| **Prometheus** | `:9090` | `prom/prometheus` | Metrics collection and alerting engine |
| **Grafana** | `:3001` | `grafana/grafana` | Dashboards — Discord alerts provisioned (disk/cpu/ram) |
| **Alertmanager** | `:9093` | `prom/alertmanager` | Prometheus alert routing → Discord with deduplication |
| **cAdvisor** | `:8081` | `gcr.io/cadvisor/cadvisor` | Docker container resource metrics |
| **Node Exporter** | `:9100` | `quay.io/prometheus/node-exporter` | Host-level OS metrics |
| **Glances** | `:61208` | `nicolargo/glances:latest-full` | Real-time system resource overview |
| **Dozzle** | `:9999` | `amir20/dozzle` | Live Docker log viewer (web UI) |
| **Speedtest Tracker** | `:8765` | `lscr.io/linuxserver/speedtest-tracker` | Scheduled ISP speed tests with history |

### Security Stack

| Service | Port(s) | Image | Description |
|---|---|---|---|
| **Wazuh Manager** | `:1514/:1515/:55000` | `wazuh/wazuh-manager:4.14.2` | SIEM agent manager and rule engine |
| **Wazuh Indexer** | `:9200` | `wazuh/wazuh-indexer:4.14.2` | OpenSearch-based log indexer |
| **Wazuh Dashboard** | `:8443` | `wazuh/wazuh-dashboard:4.14.2` | Web UI for SIEM alerts and compliance |
| **Fail2ban** | — | (host service) | Bans IPs on repeated auth failures |
| **Tailscale** | — | (host service) | Zero-config mesh VPN (Tailscale IP: `100.123.91.70`) |

### Management Stack

| Service | Port(s) | Image | Description |
|---|---|---|---|
| **Portainer** | `:9443` | `portainer/portainer-ce` | Docker management web UI (HTTPS) |
| **Nginx Proxy Manager** | `:80/:443/:81` | `jc21/nginx-proxy-manager` | Reverse proxy with Let's Encrypt SSL |
| **Homepage** | `:3005` | `ghcr.io/gethomepage/homepage` | Auto-discovering dashboard with live system widgets |
| **Dashy** | `:8080` | `lissy93/dashy` | Legacy homepage dashboard |
| **Filebrowser** | `:8585` | `filebrowser/filebrowser` | Web-based file manager |

### Application Stack

| Service | Port | Image | Description |
|---|---|---|---|
| **Vaultwarden** | (via NPM) | `vaultwarden/server` | Self-hosted Bitwarden-compatible password manager |
| **Samba** | `:139/:445` | `dperson/samba` | LAN file sharing (SMB protocol) |
| **IT-Tools** | `:8888` | `corentinth/it-tools` | Developer utility toolbox (web UI) |
| **Ntfy** | `:7777` | `binwiederhier/ntfy` | Self-hosted push notifications (mobile app support) |
| **Watchtower** | — | `containrrr/watchtower` | Automatic Docker image updates (Sunday 4am) |
| **MyLittleQuest** | `:3000` | `local-app` | Custom local application |

---

## Quick Access URLs

> Access via LAN (`10.100.102.101`) or Tailscale (`100.123.91.70`).
> SSL-terminated services are proxied through Nginx Proxy Manager.

| Service | Local URL | Notes |
|---|---|---|
| Homepage | `http://10.100.102.101:3005` | Start here (auto-discovering) |
| Dashy | `http://10.100.102.101:8080` | Legacy dashboard |
| Grafana | `http://10.100.102.101:3001` | Monitoring dashboards |
| Prometheus | `http://10.100.102.101:9090` | Metrics + alerts |
| Alertmanager | `http://10.100.102.101:9093` | Alert routing status |
| Wazuh Dashboard | `https://10.100.102.101:8443` | SIEM alerts |
| Portainer | `https://10.100.102.101:9443` | Docker management |
| Nginx Proxy Mgr | `http://10.100.102.101:81` | Proxy admin panel |
| Dozzle | `http://10.100.102.101:9999` | Live Docker logs |
| Glances | `http://10.100.102.101:61208` | System resources |
| Vaultwarden | via NPM proxy | Password manager |
| Filebrowser | `http://10.100.102.101:8585` | File management |
| IT-Tools | `http://10.100.102.101:8888` | Dev tools |
| Ntfy | `http://10.100.102.101:7777` | Push notifications |
| Speedtest | `http://10.100.102.101:8765` | Speed history |
| cAdvisor | `http://10.100.102.101:8081` | Container metrics |
| MyLittleQuest | `http://10.100.102.101:3000` | Custom app |

---

## Automation

See [`automation.md`](./automation.md) for full details on:
- Hourly syscheck with Discord alerting
- Daily midnight report
- Daily 2am Docker volume backup (Vaultwarden, Portainer, Prometheus, Grafana)
- Weekly Docker cleanup (Sunday 3am)
- Watchtower auto-update (Sunday 4am)
- Grafana Discord alert rules (disk/CPU/RAM — provisioned, survives recreates)
- Prometheus → Alertmanager → Discord pipeline

---

## Security

See [`security.md`](./security.md) for full details on:
- Fail2ban SSH jail + Discord ban/unban alerts
- UFW firewall rules (Docker-compatible)
- SSH hardening drop-in config
- Wazuh SIEM agent registration
- Tailscale remote access

To apply all pending hardening:
```bash
sudo /home/admini/apply-security-hardening.sh
```

---

## Hermes Skills

Claude Code AI skills deployed on this server for automated DevOps auditing:

| Skill | Trigger | Description |
|---|---|---|
| `devops/host-audit-full` | On-demand | Full server audit + Discord report |
| `devops/docker-audit` | On-demand | Deep Docker health check |
| `devops/security-posture-check` | On-demand | Security configuration audit |
| `devops/disk-forensics` | On-demand | Disk investigation + LVM extension guide |

Skills are located under `~/.hermes/` and invoked via Claude Code.

---

## Monitoring Configuration

- **Prometheus alert rules**: `~/.hermes/monitoring/alert_rules.yml`
- **Prometheus config**: `~/.hermes/monitoring/prometheus.yml`
- **Docker Compose (monitoring)**: `~/.hermes/monitoring/docker-monitoring-compose.yml`
- **Grafana dashboards**: Node Exporter Full + Docker container metrics

Alert thresholds configured in `syscheck.sh`:
- Disk usage > **85%** → Discord alert (red)
- RAM usage > **85%** → Discord alert (orange)
- Container crash → Discord alert (red)

---

## Setup Notes

- The VM was provisioned on Proxmox (KVM/QEMU) from the Beelink Mini S13 host
- Docker services are managed via Compose files (multiple stacks)
- Watchtower runs weekly on Sunday at 4am and posts update reports to Discord
- Vaultwarden is proxied through NPM for HTTPS access; no direct port exposed
- Wazuh runs as a single-node deployment (manager + indexer + dashboard)
- Samba shares are accessible on the LAN at `\\10.100.102.101`
- Tailscale allows secure remote access from any device on the tailnet

---

*Last updated: 2026-06-05 — 22 containers, Alertmanager + Homepage + Ntfy added, Grafana Discord alerting provisioned*
