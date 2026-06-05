# Automation — UbuntuServer

All scheduled tasks, alert pipelines, and AI-driven audit skills running on `ubuntuserver`.

---

## Cron Jobs

Defined in `crontab -e` for user `admini`:

| Schedule | Command | Log File | Description |
|---|---|---|---|
| `0 * * * *` | `syscheck.sh` | `last_run_cron.log` | Hourly system health check + conditional Discord alerts |
| `0 0 * * *` | `syscheck.sh --daily-report` | `last_daily_report.log` | Midnight daily summary report sent to Discord |
| `0 2 * * *` | `backup_volumes.sh` | `last_backup.log` | Daily Docker volume backup (2am) |
| `0 3 * * 0` | `docker_cleanup.sh` | `last_cleanup.log` | Weekly Docker cleanup (Sunday 3am) |
| `0 20 * * *` | `update_bounty.sh` | `update_bounty.log` | Daily bug bounty update script |

All scripts reside in `~/.hermes/monitoring/`.

---

## Discord Alert System

**Script:** `~/.hermes/monitoring/discord_alert.sh`

Sends rich embed notifications to Discord via webhook. Called by all automation scripts.

```
Usage: discord_alert.sh "Title" "Message" [color_decimal]

Color codes:
  16711680  = Red    (critical alerts)
  16744272  = Orange (warning alerts)
  65280     = Green  (success/recovery)
  3447003   = Blue   (informational)
```

**Alert Triggers:**

| Trigger | Threshold | Color | Source |
|---|---|---|---|
| Disk usage high | > 85% | Red | `syscheck.sh` + Grafana |
| RAM usage high | > 85% | Orange | `syscheck.sh` + Grafana |
| CPU usage high | > 90% | Orange | Grafana alert rule |
| Container crash | Any restarting | Red | `syscheck.sh` |
| Fail2ban ban | Any IP banned | Red | `discord-notify.conf` |
| Fail2ban unban | IP released | Green | `discord-notify.conf` |
| Daily report | Midnight | Blue | `syscheck.sh --daily-report` |
| Docker cleanup done | Sunday 3am | Blue | `docker_cleanup.sh` |
| Watchtower update | Sunday 4am | Blue | Watchtower container |
| Volume backup done | Daily 2am | Green/Red | `backup_volumes.sh` |

---

## Grafana Alerting (via Provisioning)

Grafana is configured to send alerts to Discord using provisioned contact points.
All configuration survives container recreates — stored in `/home/admini/.hermes/monitoring/grafana-provisioning/`.

**Contact point:** `~/.hermes/monitoring/grafana-provisioning/alerting/homelab_alerts.yml`

**Alert rules (3):**

| Rule | Condition | For | Severity |
|---|---|---|---|
| High Disk Usage | Root filesystem available < 15% | 5 min | Warning |
| High CPU Usage | CPU idle < 10% (>90% busy) | 5 min | Warning |
| High Memory Usage | Available memory < 10% | 5 min | Warning |

**Notification policy:** Group by `alertname`, wait 30s, repeat every 4h.

---

## Prometheus Alertmanager

**Container:** `alertmanager-alertmanager-1`
**Port:** `:9093`
**Config:** `/home/admini/alertmanager/alertmanager.yml`

Routes Prometheus-generated alerts to Discord. Provides:
- Alert grouping (reduces noise)
- Deduplication
- Inhibition rules (critical silences warning for same alert)
- Resolve notifications when alert clears

Alertmanager is scraped by Prometheus as a target (`alertmanager` job).

---

## Hourly Syscheck (`syscheck.sh`)

**Script:** `~/.hermes/monitoring/syscheck.sh`
**Cron:** Every hour — `0 * * * *`
**Log directory:** `~/.hermes/monitoring/logs/syscheck-<timestamp>.log`

**What it checks:**
1. System info (`uname`, `uptime`)
2. Disk usage on `/` — alerts if > 85%
3. Memory usage — alerts if > 85%
4. Top CPU and memory processes (`ps`)
5. Listening ports (`ss -tuln`)
6. Running Docker containers
7. Systemd journal errors (last 200 lines)
8. dmesg tail (last 80 lines)

**Daily report mode** (`--daily-report` flag, runs at midnight):
- Sends a comprehensive Discord embed with all metrics
- Includes disk %, RAM %, container count, and system uptime

---

## Daily Docker Volume Backup (`backup_volumes.sh`)

**Script:** `~/.hermes/monitoring/backup_volumes.sh`
**Schedule:** Daily at 2am — `0 2 * * *`
**Retention:** 7 days
**Destination:** `/home/admini/backups/`

Backs up critical Docker volumes to prevent data loss from container updates or crashes.

| Service | Method | Typical Size |
|---|---|---|
| Vaultwarden | `tar` of `/home/admini/bitwarden/vw-data` | ~474 KB |
| Portainer | Named volume `portainer_data` | ~52 KB |
| Prometheus | Named volume `prometheus_data` | ~6.7 MB |
| Grafana | `docker cp grafana.db` + gzip | ~163 KB |

Sends Discord notification with backup results (success/failure per item).

---

## Weekly Docker Cleanup (`docker_cleanup.sh`)

**Script:** `~/.hermes/monitoring/docker_cleanup.sh`
**Cron:** Sunday at 3am — `0 3 * * 0`
**Log:** `/tmp/docker_cleanup.log`

**What it prunes:**
- Unused Docker images (`docker image prune -f`)
- Stopped containers (`docker container prune -f`)
- Unused networks (`docker network prune -f`)
- Dangling volumes (`docker volume prune -f`)

**Post-cleanup:** Sends a Discord embed reporting MB of disk space freed.

---

## Watchtower Auto-Updates

**Container:** `watchtower-watchtower-1`
**Image:** `containrrr/watchtower:latest`
**Schedule:** Sunday at 4am
**Mode:** Auto-update (pulls + restarts)

Monitors Docker Hub for new image versions of all running containers.
When an update is detected:
1. Pulls the new image
2. Stops and removes the old container
3. Starts a new container with the same configuration
4. Reports updates to Discord

---

## Security Hardening Script

**Script:** `/home/admini/apply-security-hardening.sh`
**Requires:** `sudo`

One-shot script that applies all security hardening steps:

```bash
sudo /home/admini/apply-security-hardening.sh
```

Steps applied:
1. **Fail2ban** — SSH jail + Discord ban/unban action
2. **SSH** — drop-in `/etc/ssh/sshd_config.d/99-homelab-hardening.conf`
3. **Logrotate** — 14-day rotation for Hermes monitoring logs
4. **UFW** — Docker-compatible firewall rules

See [`security.md`](./security.md) for full details.

---

## Hermes AI Skills

Claude Code (Hermes) skills deployed for on-demand DevOps auditing.
Skills are located under `~/.hermes/skills/devops/`.

### `devops/host-audit-full`
**Full server audit + Discord report**

Performs a comprehensive health check and sends a scored report (/100) to Discord:
- System resources (CPU, RAM, disk, load)
- All Docker containers status
- Systemd service health
- SSH brute-force attempts (24h)
- Fail2ban and Tailscale status

Script: `~/.hermes/skills/devops/host-audit-full/scripts/quick_audit.sh [--discord] [--json]`

### `devops/docker-audit`
**Deep Docker health check**

Inspects all containers in detail:
- Container health status and restart counts
- Resource usage per container
- Unhealthy containers with root cause hints

### `devops/security-posture-check`
**Security configuration audit + score /100 to Discord**

Reviews:
- Fail2ban status and recent bans
- Open ports and firewall rules
- Wazuh agent connectivity
- SSH configuration hardening
- Tailscale VPN status
- Recent auth failures in logs

### `devops/disk-forensics`
**Disk investigation + LVM extension guide**

Investigates disk usage:
- Finds large files and directories
- Identifies log bloat and Docker layer waste
- Guides LVM extension using the available `lv-0` (62 GB) volume
- Provides step-by-step `lvextend` + `resize2fs` commands

---

## Monitoring Configuration Files

| File | Path | Description |
|---|---|---|
| Prometheus config | `~/.hermes/monitoring/prometheus.yml` | Scrape targets, alertmanager endpoint, global settings |
| Alert rules | `~/.hermes/monitoring/alert_rules.yml` | 8 Prometheus alerting rules |
| Monitoring compose | `~/.hermes/monitoring/docker-monitoring-compose.yml` | Prometheus + Grafana + cAdvisor + Node Exporter |
| Grafana dashboards | `~/.hermes/monitoring/grafana-dashboards/` | Exported JSON (Node Exporter Full, Docker Monitoring) |
| Grafana datasources | `~/.hermes/monitoring/grafana-datasources/prometheus.yml` | Prometheus datasource provisioning |
| Grafana alerting | `~/.hermes/monitoring/grafana-provisioning/alerting/` | Discord contact point + alert rules (provisioned) |

---

## Log Retention

Syscheck logs accumulate in `~/.hermes/monitoring/logs/`.
Logrotate (once applied via `apply-security-hardening.sh`) rotates all monitoring logs daily with 14-day retention.

To view a recent log:
```bash
# Last syscheck log
cat ~/.hermes/monitoring/logs/$(ls -t ~/.hermes/monitoring/logs/ | head -1)

# Quick audit (text output)
bash ~/.hermes/skills/devops/host-audit-full/scripts/quick_audit.sh

# Quick audit to Discord
bash ~/.hermes/skills/devops/host-audit-full/scripts/quick_audit.sh --discord
```

---

*Last updated: 2026-06-05*
