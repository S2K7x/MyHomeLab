# 🛠️ System Configuration: Raspberry Pi 5

> **Role:** Core self-hosted services, media server, DNS, and automation hub.

### 💿 Software Stack

* **OS:** Raspberry Pi OS Lite (64-bit)
* **Docker:** 29.1.4

---

### 🌐 Access (via Pi-hole DNS — all devices using Pi as DNS resolver)

All services accessible by hostname once your device uses Pi-hole (`10.100.102.100:53`) as DNS.

| URL | Service | Direct Port |
|---|---|---|
| `http://pihole.home` | Pi-hole admin | :8053 |
| `http://nextcloud.home` | Nextcloud | :8080 |
| `http://n8n.home` | n8n automation | :5678 |
| `http://portainer.home` | Portainer Docker UI | :9000 |
| `http://uptime.home` | Uptime Kuma | :3001 |
| `http://jellyfin.home` | Jellyfin media server | :8096 |
| `http://mealie.home` | Mealie recipe manager | :9925 |
| `http://scrutiny.home` | SSD S.M.A.R.T. health | :8082 |

> Caddy reverse proxy on port 80 routes all `.home` domains.
> Traffic is secure — all access is through Tailscale (E2E encrypted) or LAN.

---

### 🐳 Docker Services

| Container | Port | Image | Role |
|---|---|---|---|
| **caddy** | 80 | `caddy:2-alpine` | Reverse proxy — routes all `.home` domains |
| **nextcloud_app** | 8080 | `nextcloud:stable` | Personal cloud storage & productivity |
| **nextcloud_db** | — | `mariadb:10.11` | Nextcloud database |
| **nextcloud_redis** | — | `redis:7-alpine` | Nextcloud cache |
| **n8n_main** | 5678 | `n8nio/n8n:latest` | Workflow automation (Cloudflare Tunnel for webhooks) |
| **n8n_worker** | — | `n8nio/n8n:latest` | n8n worker process |
| **n8n_postgres** | — | `postgres:16-alpine` | n8n database |
| **n8n_redis** | — | `redis:7-alpine` | n8n queue |
| **n8n_cloudflared** | — | `cloudflared:latest` | Cloudflare Tunnel for external webhook access |
| **uptime-kuma** | 3001 | `louislam/uptime-kuma:2` | Service monitoring dashboard |
| **portainer** | 9000/9443 | `portainer/portainer-ce` | Docker management UI |
| **watchtower** | — | `containrrr/watchtower:1.7.1` | Auto-update opt-in containers (Sunday 03:00) |
| **jellyfin** | 8096 | `jellyfin/jellyfin:latest` | Media server — content on `/mnt/nextcloud_data/media/` |
| **mealie** | 9925 | `ghcr.io/mealie-recipes/mealie` | Recipe & meal plan manager |
| **scrutiny** | 8082 | `analogj/scrutiny:master-omnibus` | S.M.A.R.T. health monitoring (SSD + SD card) |
| **node-exporter** | 9100 (host) | `prometheus/node-exporter` | Exposes Pi metrics to Beelink's Prometheus |

> Watchtower label: `com.centurylinklabs.watchtower.enable=true`
> Currently auto-updated: caddy, n8n_main, n8n_worker, n8n_cloudflared, nextcloud_app, portainer, jellyfin, mealie, scrutiny, node-exporter

> [!IMPORTANT]
> **Beelink Prometheus integration:** To see RPi5 metrics in Grafana, add this scrape job to `~/.hermes/monitoring/prometheus.yml` on the Beelink:
> ```yaml
> - job_name: 'rpi5'
>   static_configs:
>     - targets: ['100.121.5.36:9100']
>       labels:
>         instance: 'rpi5'
> ```

---

### 🔄 Crontab — Automation Scripts

All scripts in `/home/pi/Scripts/` with shared venv at `/home/pi/Scripts/env/`.

| Script | Schedule | Purpose |
|---|---|---|
| `Forge/forge.py` | Daily 12:00 | Cybersecurity challenge → Discord |
| `Joker/joker.py` | Every 2h | Random content → Discord |
| `Joker/jokerxxx.py` | Every 4h | NSFW content variant → Discord |
| `Miru/miru.py` | Every 2h +5min | Media/anime tracker → Discord |
| `Nexus/nexus.py` | Daily 11:00 | Interview prep → Discord |
| `Scripties/scripties.py` | Daily 00:00 | Dev snippets → Discord |
| `BackupRepo/backuprepo.py` | Daily 00:05 | GitHub repo → Nextcloud WebDAV |
| `container_watchdog.sh` | Every 5min | Restart unhealthy containers → Discord alert |
| Nextcloud cron | Every 5min | `php cron.php` background jobs |
| `disk_watchdog.sh` | Daily 08:00 | Alert if partition > 80% |
| `docker_cleanup.sh` | Saturday 03:00 | Prune unused Docker resources |
| `docker_backup.sh` | Sunday 02:00 | Backup volumes → SSD (7 copies) |
| `Rasbstats/rasbstat.sh` | Monday 09:00 | Weekly system health report → Discord |

> Discord webhook: `/home/pi/Scripts/system.env`
> Rasbstats config: `/home/pi/Scripts/Rasbstats/rasbstats.conf`

---

### 🛡️ Security & Resilience

| Feature | Config |
|---|---|
| **Pi-hole** | DNS on port 53 — ad blocking + local DNS resolution |
| **Wazuh agent** | Running, reporting to Beelink (`100.123.91.70:1514`) |
| **fail2ban** | SSH: 3 failures → 24h ban |
| **unattended-upgrades** | Security patches auto-applied daily |
| **Hardware watchdog** | BCM2835 — systemd reboots if kernel hangs (15s timeout) |
| **logrotate** | All homelab logs — weekly rotation, 4 weeks, compressed |

### ⚙️ System Tuning

| Parameter | Value |
|---|---|
| `vm.swappiness` | 10 |
| `vm.vfs_cache_pressure` | 50 |

---

### 🗄️ Storage

| Mount | Device | Size | Use |
|---|---|---|---|
| `/` | `/dev/mmcblk0p2` | 29GB SD card | OS + Docker layers |
| `/mnt/nextcloud_data` | `/dev/sda1` | 1.8TB NVMe SSD | Nextcloud data + media + backups |

**SSD structure:**
```
/mnt/nextcloud_data/
├── nextcloud/          ← Nextcloud files
├── db/                 ← MariaDB data
├── media/
│   ├── movies/
│   ├── shows/
│   ├── anime/
│   └── music/
├── docker_backups/     ← Weekly volume backups
└── scrutiny/           ← S.M.A.R.T. database
```

---

### 🔌 Hardware Specifications

| Component | Details |
|---|---|
| **CPU** | Broadcom BCM2712 (2.4GHz quad-core Arm Cortex-A76) |
| **RAM** | 8GB LPDDR4X-4267 SDRAM |
| **Network** | Gigabit Ethernet, Dual-band Wi-Fi, BT 5.0 |
| **LAN IP** | `10.100.102.100` |
| **Tailscale IP** | `100.121.5.36` |
