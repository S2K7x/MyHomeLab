# 📊 **Uptime Kuma Monitoring Setup**

This section documents the deployment and configuration of **Uptime Kuma** as the primary monitoring solution for the homelab, integrated with **Tailscale** for secure access and **n8n** for advanced alerting.

---

## 🚀 **Deployment**

The service is deployed using **Docker Compose** to ensure data persistence and easy updates.

```yaml
version: '3.3'

services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    volumes:
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock # Allows monitoring of local Docker containers
    ports:
      - 3001:3001
    restart: always
```

---

## 🛠️ **Configuration Highlights**

### **1. DNS Monitoring (Pi-hole)**
To properly monitor **Pi-hole**, the DNS probe must be configured to distinguish between the domain being queried and the resolver itself:
- **Hostname**: A public domain (e.g., `google.com`).
- **Resolver Server**: The internal IP of the Pi-hole (e.g., `10.100.102.15`).
- **Why**: This confirms the Pi-hole is actually resolving queries, not just that its web interface is up.

### **2. Security & Access**
- **Networking**: Isolated within a **Tailscale** mesh. No ports are exposed to the public internet.
- **Authentication**: **2FA (Two-Factor Authentication)** is enabled for the admin account.
- **SSL**: Accessed via Tailscale's encrypted overlay (HTTPS via `tailscale cert` recommended for production-grade security).

### **3. Advanced Alerting (n8n Integration)**
Alerts are not sent directly to messaging apps. Instead, they trigger a **Webhook in n8n**:
- **Workflow**: Uptime Kuma → n8n Webhook → Logic/Filtering → Final Notification.
- **Auto-Remediation**: The n8n workflow is designed to attempt a service restart (via SSH or Docker API) before escalating the alert to the administrator.

---

## 💡 **Best Practices Implemented**
- **Grouping**: Monitors are organized by category (Infrastructure, Home Automation, Services).
- **Retry Logic**: "Retries" are set to **3-5** to prevent "alert fatigue" from minor network blips.
- **Database**: Uses the default **SQLite** (`kuma.db`) for simplicity and performance.
- **Maintenance Windows**: Scheduled downtime is used during server updates to prevent notification storms.

---

## 💾 **Backup Strategy**
Since all configurations and history are stored in the `./data` directory:
- Regular backups of the `kuma.db` file are automated.
- The entire `./data` folder is included in the standard homelab backup rotation.