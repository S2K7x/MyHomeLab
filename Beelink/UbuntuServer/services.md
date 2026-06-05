# Services — UbuntuServer

Complete inventory of all 19 Docker containers running on `ubuntuserver` (`10.100.102.101`).

> Compose files are located in their respective project directories under `/home/admini/`.
> The monitoring stack uses `~/.hermes/monitoring/docker-monitoring-compose.yml`.

---

## Monitoring Stack

| Name | Port(s) | Docker Image | Compose Stack | Description |
|---|---|---|---|---|
| `monitoring-prometheus-1` | `9090→9090` | `prom/prometheus:latest` | `monitoring` | Scrapes metrics from all exporters; evaluates alert rules; stores time-series data |
| `monitoring-grafana-1` | `3001→3000` | `grafana/grafana:latest` | `monitoring` | Visualization dashboards — ships with Node Exporter Full and Docker dashboards |
| `monitoring-cadvisor-1` | `8081→8080` | `gcr.io/cadvisor/cadvisor:latest` | `monitoring` | Exposes per-container CPU, memory, network, and I/O metrics to Prometheus |
| `monitoring-node-exporter-1` | `9100` (host net) | `quay.io/prometheus/node-exporter:latest` | `monitoring` | Host-level OS metrics (CPU, mem, disk, net) for Prometheus |
| `glances-glances-1` | `61208` | `nicolargo/glances:latest-full` | `glances` | Real-time system overview with web UI; monitors CPU, memory, disk, containers |
| `dozzle-dozzle-1` | `9999→8080` | `amir20/dozzle:latest` | `dozzle` | Streams live Docker logs from all containers via a clean web interface |
| `speedtest-speedtest-tracker-1` | `8765→80` | `lscr.io/linuxserver/speedtest-tracker:latest` | `speedtest` | Runs scheduled internet speed tests and stores historical results |

---

## Security Stack

| Name | Port(s) | Docker Image | Compose Stack | Description |
|---|---|---|---|---|
| `single-node-wazuh.manager-1` | `1514-1515→1514-1515`, `514/udp→514`, `55000→55000`, `1516` | `wazuh/wazuh-manager:4.14.2` | `wazuh` (single-node) | SIEM manager; ingests agent events, applies rules, generates alerts |
| `single-node-wazuh.indexer-1` | `9200→9200` | `wazuh/wazuh-indexer:4.14.2` | `wazuh` (single-node) | OpenSearch-based indexer; stores and indexes all SIEM events |
| `single-node-wazuh.dashboard-1` | `8443→5601` | `wazuh/wazuh-dashboard:4.14.2` | `wazuh` (single-node) | Web UI for browsing SIEM alerts, compliance reports, and agent status |

> Wazuh version: **4.14.2** (single-node deployment)
> Agent communication port: `1514` (TCP/UDP)
> REST API port: `55000`
> Dashboard: `https://10.100.102.101:8443`

**Host-level security services (not containers):**
- **Fail2ban** — monitors auth logs; bans IPs on repeated failures (SSH, NPM, etc.)
- **Tailscale** — mesh VPN daemon; provides `100.123.91.70` for remote access

---

## Management Stack

| Name | Port(s) | Docker Image | Compose Stack | Description |
|---|---|---|---|---|
| `portainer` | `9443→9443`, `8000`, `9000` | `portainer/portainer-ce:latest` | standalone | Docker management UI — manage all stacks, containers, volumes, and networks |
| `nginx-proxy-manager` | `80→80`, `81→81`, `443→443` | `jc21/nginx-proxy-manager:latest` | standalone | Reverse proxy with Let's Encrypt SSL — routes domains to backend services |
| `dashy` | `8080→8080` | `lissy93/dashy:latest` | standalone | Homepage dashboard with links to all self-hosted services |
| `filebrowser-filebrowser-1` | `8585→80` | `filebrowser/filebrowser:latest` | `filebrowser` | Web-based file manager with user accounts; browse and manage server files |

---

## Application Stack

| Name | Port(s) | Docker Image | Compose Stack | Description |
|---|---|---|---|---|
| `vaultwarden` | (via NPM proxy) | `vaultwarden/server:latest` | standalone | Self-hosted Bitwarden-compatible password manager; accessed via HTTPS through NPM |
| `samba` | `139`, `445` (host net) | `dperson/samba:latest` | standalone | SMB file sharing — accessible as `\\10.100.102.101` on LAN |
| `it-tools-it-tools-1` | `8888→80` | `corentinth/it-tools:latest` | `it-tools` | Collection of developer/sysadmin utility tools (hashing, encoding, networking, etc.) |
| `watchtower-watchtower-1` | `8080` (internal) | `containrrr/watchtower:latest` | `watchtower` | Monitors Docker Hub for image updates; pulls and restarts updated containers automatically |
| `local-app-1` | `3000→3000` | `local-app` | `local` | MyLittleQuest — custom local application (built from local Dockerfile) |

---

## Port Reference Summary

| Port | Service | Protocol |
|---|---|---|
| 80 | Nginx Proxy Manager (HTTP) | TCP |
| 81 | Nginx Proxy Manager (Admin UI) | TCP |
| 139 | Samba (NetBIOS) | TCP |
| 443 | Nginx Proxy Manager (HTTPS) | TCP |
| 445 | Samba (SMB) | TCP |
| 514 | Wazuh Syslog | UDP |
| 1514 | Wazuh Agent Manager | TCP |
| 1515 | Wazuh Agent Registration | TCP |
| 3000 | MyLittleQuest | TCP |
| 3001 | Grafana | TCP |
| 8080 | Dashy | TCP |
| 8081 | cAdvisor | TCP |
| 8443 | Wazuh Dashboard (HTTPS) | TCP |
| 8585 | Filebrowser | TCP |
| 8765 | Speedtest Tracker | TCP |
| 8888 | IT-Tools | TCP |
| 9090 | Prometheus | TCP |
| 9100 | Node Exporter | TCP |
| 9200 | Wazuh Indexer (OpenSearch) | TCP |
| 9443 | Portainer (HTTPS) | TCP |
| 9999 | Dozzle | TCP |
| 55000 | Wazuh REST API | TCP |
| 61208 | Glances | TCP |

---

*Last updated: 2026-06-05*
