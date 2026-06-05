# Automation — UbuntuServer

All scheduled tasks, alert pipelines, and AI-driven audit skills running on `ubuntuserver`.

---

## Cron Jobs

Defined in `crontab -e` for user `admini`:

| Schedule | Command | Log File | Description |
|---|---|---|---|
| `0 * * * *` | `syscheck.sh` | `last_run_cron.log` | Hourly system health check + conditional Discord alerts |
| `0 0 * * *` | `syscheck.sh --daily-report` | `last_daily_report.log` | Midnight daily summary report sent to Discord |
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

| Trigger | Threshold | Color | Description |
|---|---|---|---|
| Disk usage high | > 85% | Red | Root filesystem approaching capacity |
| RAM usage high | > 85% | Orange | Memory pressure detected |
| Container crash | Any | Red | Docker container exited unexpectedly |
| Daily report | Midnight | Blue | Scheduled summary of system health |
| Docker cleanup done | Sunday 3am | Blue | Reports MB freed after weekly prune |

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

**Output files:**
- Full log: `~/.hermes/monitoring/logs/syscheck-<UTC-timestamp>.log`
- Summary JSON: `~/.hermes/monitoring/last_summary.json`

---

## Daily Docker Volume Backup (`backup_volumes.sh`)

**Script:** `~/.hermes/monitoring/backup_volumes.sh`
**Schedule:** Daily at 2am — `0 2 * * *`

Backs up critical Docker volumes to prevent data loss from container updates or crashes.
Wazuh, Vaultwarden, and other stateful service data is preserved.

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

Monitors Docker Hub for new image versions of all running containers.
When an update is detected:
1. Pulls the new image
2. Stops and removes the old container
3. Starts a new container with the same configuration
4. Reports updates to Discord

---

## Hermes AI Skills

Claude Code (Hermes) skills deployed for on-demand DevOps auditing.
Invoked via Claude Code CLI: `claude "run devops/host-audit-full"`

### `devops/host-audit-full`
**Full server audit + Discord report**

Performs a comprehensive health check:
- System resources (CPU, RAM, disk, load)
- All Docker containers status
- Systemd service health
- Network connectivity
- Recent error logs
- Sends formatted report to Discord

### `devops/docker-audit`
**Deep Docker health check**

Inspects all containers in detail:
- Container health status and restart counts
- Image versions and update availability
- Volume mounts and network configuration
- Resource usage per container
- Unhealthy containers with root cause hints

### `devops/security-posture-check`
**Security configuration audit**

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
| Prometheus config | `~/.hermes/monitoring/prometheus.yml` | Scrape targets and global settings |
| Alert rules | `~/.hermes/monitoring/alert_rules.yml` | Prometheus alerting rules |
| Monitoring compose | `~/.hermes/monitoring/docker-monitoring-compose.yml` | Prometheus + Grafana + cAdvisor + Node Exporter stack |

---

## Log Retention

Syscheck logs accumulate in `~/.hermes/monitoring/logs/` and `~/.hermes/monitoring/` (flat `.log.gz` files from the Hermes skill runs). These are gzip-compressed after rotation.

To view a recent log:
```bash
# Last syscheck log
cat ~/.hermes/monitoring/logs/$(ls -t ~/.hermes/monitoring/logs/ | head -1)

# Last daily summary JSON
cat ~/.hermes/monitoring/last_summary.json | python3 -m json.tool
```

---

*Last updated: 2026-06-05*
