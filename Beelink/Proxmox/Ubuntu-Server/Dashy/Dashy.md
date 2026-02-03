## Dashy - Home Lab Dashboard

This repository contains the configuration and deployment files for **Dashy**, a self-hosted, highly customizable dashboard used to centralize all my Home Lab services (Wazuh, Proxmox, Pi-hole, etc.).

### 🚀 Features

* **Service Monitoring:** Centralized access to all local and Tailscale-hosted services.
* **Status Indicators:** Real-time uptime monitoring for critical infrastructure.
* **Tailscale Integration:** Accessible securely from anywhere via my Tailscale mesh network.

### 🛠 Deployment

The dashboard is deployed as a Docker container on an Ubuntu 22.04 VM (Proxmox).

**Prerequisites:**

* Docker and Docker Compose installed.
* `conf.yml` file initialized in the same directory.

**Docker Compose Configuration:**

```yaml
services:
  dashy:
    image: lissy93/dashy:latest
    container_name: dashy
    volumes:
      - ./conf.yml:/app/user-data/conf.yml
    ports:
      - 8080:8080
    restart: always
    environment:
      - NODE_ENV=production

```

*Note: We use `/app/user-data/conf.yml` as the internal path for persistence.*

### ⚙️ Configuration

My `conf.yml` is structured into several sections:

1. **Infrastructure:** Proxmox VE, Tailscale Gateway (LXC 103).
2. **Security:** Wazuh Dashboard, Vaultwarden.
3. **Network:** Pi-hole, Router admin.

**How to update the config:**

1. Open Dashy in your browser (`http://<server-ip>:8080`).
2. Click the **Edit** icon in the bottom right corner.
3. Add/Modify items.
4. Click **"Save to Disk"** to permanently write changes to `conf.yml`.

### 🌐 Network Access

| Network | Access URL |
| --- | --- |
| **Local LAN** | `http://10.100.102.15:8080` |
| **Tailscale** | `http://100.123.91.70:8080` |

---

### 📝 Maintenance

**View Logs:**

```bash
docker logs -f dashy

```

**Validate Config:**

```bash
docker exec -it dashy yarn validate-config

```