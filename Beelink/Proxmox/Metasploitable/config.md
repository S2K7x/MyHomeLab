# Metasploitable 2 Installation on Proxmox VE

This document details the step-by-step process of installing **Metasploitable 2** on a Proxmox VE node, including critical troubleshooting steps regarding storage management and hardware compatibility for legacy Linux kernels.

> [!WARNING]
> **Metasploitable 2 is intentionally vulnerable.** Never expose this VM to the public internet. It should remain within an isolated lab environment or a protected internal bridge.

---

## 1. Initial Image Preparation

Metasploitable is provided as a VMware virtual disk (`.vmdk`). We must convert it to a format Proxmox handles better (`.qcow2`).

Run these commands in the Proxmox Shell:

```bash
# Download and unzip
wget https://sourceforge.net/projects/metasploitable/files/Metasploitable2/metasploitable-linux-2.0.0.zip
unzip metasploitable-linux-2.0.0.zip
cd Metasploitable2-Linux/

# Convert VMDK to QCOW2
qemu-img convert -O qcow2 Metasploitable.vmdk metasploitable.qcow2

```

## 2. Storage Troubleshooting (Critical)

During installation, we encountered a **97% disk usage** on the `local` storage due to a large 176GB sparse disk and snapshots from another VM (ID 100).

**Actions taken to recover space:**

1. **Deleted Snapshots:** Removed old snapshots from VM 100 to break file locks.
2. **Moved Storage:** Used the "Move Storage" feature in the Proxmox GUI to migrate VM 100 disks from `local` to `local-lvm`.
3. **Manual Cleanup:** Verified and removed orphaned `.qcow2` files in `/var/lib/vz/images/100/`.

## 3. VM Creation & Disk Import

1. **Create VM via GUI:**
* **ID:** 101
* **Name:** Metasploitable2
* **CPU:** 1 Core
* **RAM:** 512 MB (Standard for this legacy system)
* **Network:** Default bridge (`vmbr0`)
* **Disk:** Delete the default disk created by the wizard.


2. **Import Disk via Shell:**

```bash
qm importdisk 101 metasploitable.qcow2 local-lvm

```

## 4. Hardware Compatibility Settings

Metasploitable 2 uses an older Linux kernel (Ubuntu 8.04) that does not support modern `VirtIO` drivers by default. The following hardware changes are mandatory to avoid a "Kernel Panic" or "Disk not found" error.

| Hardware Item | Setting | Reason |
| --- | --- | --- |
| **Bus/Device** | **IDE** (instead of SCSI/VirtIO) | Legacy kernel support for disk mounting. |
| **Network Model** | **Intel E1000** | Legacy driver compatibility for networking. |
| **Storage Type** | **local-lvm** | Better performance and snapshot management. |

## 5. Final Configuration

1. **Hardware Tab:** Attach the "Unused Disk 0" as **IDE 0**.
2. **Options Tab -> Boot Order:** Ensure `ide0` is enabled and moved to the **top priority**.
3. **Start VM:** Launch the console.

## 6. Access Credentials

Once the system has booted and displayed the Metasploitable banner:

* **Username:** `msfadmin`
* **Password:** `msfadmin`

**Post-install verification:**
Run `ifconfig` to verify the IP assignment on `eth0`.