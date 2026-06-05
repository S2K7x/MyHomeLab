# Sécurité — UbuntuServer

Security posture, hardening configuration, and alert pipeline for `ubuntuserver`.

---

## Security Stack Overview

| Component | Status | Notes |
|---|---|---|
| **Wazuh SIEM** | ✅ Active | Manager + Indexer + Dashboard (v4.14.2) |
| **Fail2ban** | ✅ Active | SSH jail, Discord ban/unban alerts |
| **Tailscale VPN** | ✅ Active | Mesh VPN, IP: `100.123.91.70` |
| **SSH Key Auth** | ✅ Active | 3 authorized keys configured |
| **UFW Firewall** | ⏳ Configured | Apply with `sudo /home/admini/apply-security-hardening.sh` |
| **SSH Hardening** | ⏳ Configured | PasswordAuthentication no, MaxAuthTries 3 |

---

## Applying Security Hardening

All hardening steps are pre-configured and ready to apply:

```bash
sudo /home/admini/apply-security-hardening.sh
```

This runs 4 steps in sequence:
1. Fail2ban Discord notifications + SSH jail
2. SSH hardening drop-in
3. Logrotate for monitoring logs
4. UFW firewall

> **Important:** Open a second SSH terminal and test key-based login before closing your current session after applying SSH hardening.

---

## Fail2ban

### SSH Jail Configuration

Config file (after apply): `/etc/fail2ban/jail.d/homelab.local`

```ini
[sshd]
enabled   = true
maxretry  = 3
findtime  = 10m
bantime   = 2h
ignoreip  = 127.0.0.1/8 ::1 10.100.102.0/24 100.64.0.0/10
```

- **LAN and Tailscale IPs are never banned** (`ignoreip` covers both)
- Bans are 2h by default; repeat offenders can be banned permanently via `fail2ban-client`

### Discord Notifications

Action file (after apply): `/etc/fail2ban/action.d/discord-notify.conf`

```ini
actionban   = discord_alert.sh "🚫 IP Bannie [<name>]" "IP <ip> bannie — <failures> tentatives" 16711680
actionunban = discord_alert.sh "✅ IP Débannie [<name>]" "IP <ip> débannie du jail <name>" 65280
```

### Useful Commands

```bash
# View current bans
sudo fail2ban-client status sshd

# Manually ban an IP
sudo fail2ban-client set sshd banip <IP>

# Unban an IP
sudo fail2ban-client set sshd unbanip <IP>

# View recent ban events
sudo journalctl -u fail2ban --since "24h ago" | grep -E "Ban|Unban"
```

---

## SSH Hardening

Drop-in config (after apply): `/etc/ssh/sshd_config.d/99-homelab-hardening.conf`

```
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
MaxAuthTries 3
MaxSessions 5
LoginGraceTime 30
X11Forwarding no
AllowTcpForwarding yes
ClientAliveInterval 300
ClientAliveCountMax 2
```

**Note:** `AllowTcpForwarding yes` is intentionally kept for Tailscale tunnel compatibility.

---

## UFW Firewall

Rules applied by `apply-security-hardening.sh`:

| Port/Interface | Service | Policy |
|---|---|---|
| 22/tcp | SSH | Allow (all) |
| 80/tcp | HTTP (NPM) | Allow (all) |
| 443/tcp | HTTPS (NPM) | Allow (all) |
| 139, 445/tcp | Samba | Allow from `10.100.102.0/24` only |
| 1514/tcp | Wazuh agents | Allow from `10.100.102.0/24` only |
| 41641/udp | Tailscale | Allow (all) |
| `tailscale0` | Tailscale interface | Allow (all) |
| `172.16.0.0/12` | Docker networks | Allow (prevents Docker breakage) |

**Docker compatibility:** UFW uses `default allow forward` and Docker manages its own iptables chains — container networking is unaffected.

```bash
# Check UFW status
sudo ufw status verbose

# Temporarily disable (emergency)
sudo ufw disable
```

---

## Wazuh SIEM

Single-node deployment (manager + indexer + dashboard).

| Component | Port | URL |
|---|---|---|
| Manager (agent comms) | 1514/1515 | — |
| REST API | 55000 | `https://10.100.102.101:55000` |
| Dashboard | 8443 | `https://10.100.102.101:8443` |
| Indexer (OpenSearch) | 9200 | Internal only |

### Agent Registration

To register a new Wazuh agent on another host:
```bash
# On the agent host (Linux)
curl -so wazuh-agent.deb https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.14.2-1_amd64.deb
sudo WAZUH_MANAGER='10.100.102.101' dpkg -i ./wazuh-agent.deb
sudo systemctl enable --now wazuh-agent
```

---

## Tailscale VPN

```bash
# Check status
tailscale status

# Add a new device
tailscale up --authkey <key>

# View IP
tailscale ip -4
```

Server IP on tailnet: `100.123.91.70`

Remote access to all web services is available via Tailscale without exposing ports publicly.

---

## Security Monitoring

### SSH Brute-Force Monitoring

The `quick_audit.sh` script tracks SSH failures over 24h:
```bash
bash ~/.hermes/skills/devops/host-audit-full/scripts/quick_audit.sh
```

Alert thresholds:
- > 10 failures → warning
- > 50 failures → critical (Discord alert)

### Auth Log Analysis

```bash
# Failed SSH attempts (last 24h)
journalctl -u ssh --since "24h ago" | grep "Failed password" | wc -l

# Top attacker IPs
journalctl -u ssh --since "24h ago" | grep "Failed password" \
  | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | sort | uniq -c | sort -rn | head -10

# Successful logins
journalctl -u ssh --since "24h ago" | grep "Accepted"
```

### Security Audit Skill

The `devops/security-posture-check` Hermes skill runs a full security audit and sends a scored report (/100) to Discord:

```bash
# Run via Hermes
hermes run devops/security-posture-check
```

---

## Hardening Checklist

- [x] Fail2ban active (SSH jail)
- [x] Tailscale VPN active
- [x] Wazuh SIEM deployed
- [x] SSH key auth configured (3 keys)
- [x] Discord alerts for bans/unbans
- [ ] UFW firewall enabled ← `sudo /home/admini/apply-security-hardening.sh`
- [ ] SSH password auth disabled ← included in above script
- [ ] Logrotate for monitoring logs ← included in above script

---

*Last updated: 2026-06-05*
