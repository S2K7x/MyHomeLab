# Kali Linux Installation on Proxmox VE

This guide documents the deployment of a Kali Linux Guest VM within a Proxmox VE environment, including initial configuration and SSH setup.

## 1. Prerequisites

* **Hypervisor:** Proxmox VE
* **ISO Image:** Kali Linux 2025.4 Installer (x86_64)
* **Resources Allocated:**
* **CPU:** 2 Cores
* **RAM:** 4096 MB (4 GB)
* **Storage:** 60 GB (VirtIO Block)
* **Network:** VirtIO (bridged)



## 2. VM Creation & OS Installation

1. **ISO Upload:** Uploaded the Kali Linux ISO to the Proxmox `local` storage.
2. **VM Configuration:** Created a new VM (ID 102) with the resources specified above.
3. **Installation:** Performed a **Graphical Install**.
* Configured localization (Language/Keyboard).
* Partitioned the 60 GB disk using the default "Guided - use entire disk" option.


4. **Bootloader:** Installed the **GRUB boot loader** to the primary drive (`/dev/sda`) to ensure the system boots correctly.

## 3. Post-Installation Configuration

### QEMU Guest Agent

To allow Proxmox to manage the VM gracefully (clean shutdowns, IP reporting), the Guest Agent was installed:

```bash
sudo apt update
sudo apt install qemu-guest-agent -y
sudo systemctl enable --now qemu-guest-agent

```

### SSH Server Setup

To enable remote management from a physical workstation:

1. **Install OpenSSH Server:**
```bash
sudo apt install openssh-server -y
sudo systemctl enable ssh --now

```


2. **Identify IP Address:**
```bash
ip a

```



## 4. Troubleshooting: Remote Host Identification

When connecting via SSH from a macOS/Linux client, you may encounter a `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!`. This happens if the IP was previously assigned to a different machine.

**Fix:**
Remove the old host key on the client machine:

```bash
ssh-keygen -R <VM_IP_ADDRESS>

```

## 5. Default Credentials

* **User:** `kali` (or custom user created during install)
* **Password:** `kali` (or custom password created during install)