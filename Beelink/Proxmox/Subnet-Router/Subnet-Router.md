# Setting up Tailscale as a Subnet Router on Proxmox (LXC)

This guide explains how to install Tailscale inside an unprivileged LXC container on Proxmox VE to act as a **Subnet Router**. This allows remote access to the Proxmox Web UI and all other VMs/containers without installing Tailscale on every single machine.

## Prerequisites

* Proxmox VE installed and running.
* A Tailscale account.
* An Ubuntu or Debian LXC template downloaded.

---

## Step 1: Create the LXC Container

1. **Create CT**: Click "Create CT" in the Proxmox UI.
2. **General**: Set Hostname (e.g., `tailscale-gateway`) and a secure password. Uncheck "Privileged container" for better security.
3. **Template**: Select a standard Ubuntu or Debian template (e.g., `ubuntu-22.04-standard`).
4. **Resources**:
* **Disk**: 4GB to 8GB.
* **CPU**: 1 core.
* **Memory**: 512MB RAM.


5. **Network**: Assign a static IPv4 address (e.g., `10.100.102.50/24`) and set your Gateway (e.g., `10.100.102.1`).
6. **Confirm**: Do **NOT** check "Start after created".

---

## Step 2: Enable TUN Device Support

Since the container is unprivileged, you must manually grant access to the TUN device on the Proxmox Host.

1. Open the Proxmox Host Shell.
2. Edit the container configuration file (replace `ID` with your actual CT ID):
```bash
nano /etc/pve/lxc/ID.conf

```


3. Append the following lines to the end of the file:
```text
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file

```


4. Save and Exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## Step 3: Install Tailscale

1. Start the LXC container and open the **Console**.
2. Update the system and install curl:
```bash
apt update && apt upgrade -y
apt install curl -y

```


3. Run the Tailscale installation script:
```bash
curl -fsSL https://tailscale.com/install.sh | sh

```


4. Authenticate the machine:
```bash
tailscale up

```


5. Follow the URL provided in the console to log in to your Tailscale account.

---

## Step 4: Configure Subnet Routing

To access your entire local network via this gateway:

1. **Enable IP Forwarding** inside the LXC container:
```bash
echo 'net.ipv4.ip_forward = 1' | tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding = 1' | tee -a /etc/sysctl.conf
sysctl -p /etc/sysctl.conf

```


2. **Advertise the routes** (replace with your actual local subnet):
```bash
tailscale up --advertise-routes=10.100.102.0/24

```


3. **Approve Routes in Admin Console**:
* Go to the [Tailscale Admin Console](https://login.tailscale.com/admin/machines).
* Find your container, click **Edit route settings**.
* Enable the advertised subnet.
