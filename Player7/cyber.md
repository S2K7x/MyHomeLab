# ⚡ Cyber Operations & Lab Environment

This document details the professional setup of the offensive security environment on the **PLAYER 7** workstation. The focus is on a high-performance **WSL2** integration for seamless transition between Windows host and Linux toolsets.

---

## 🐧 WSL2 & Kali Linux Integration
The primary penetration testing environment is built on **WSL2 (Windows Subsystem for Linux)** for native x86 performance and kernel-level integration.

### Core Setup
* **Distribution:** Kali Linux (Rolling Release)
* **Kernel:** Microsoft Standard WSL2 Kernel
* **Installation:** ```powershell
  wsl --install -d kali-linux
  kex --esm --ip # For GUI sessions if needed

```

### Package Management

The environment is initialized with the `kali-linux-default` metapackage to ensure a balance between tool availability and disk footprint:

* **Tooling:** Nmap, Metasploit Framework, Burp Suite, SQLmap, John the Ripper, etc.
* **Architecture:** Full x86_64 support for native binary execution.

---

## 🐚 Shell Customization (ZSH)

To maximize terminal productivity and aesthetics, the default shell has been upgraded with **Oh My Zsh**.

### Configuration Details

* **Framework:** [Oh My Zsh](https://ohmyz.sh/)
* **Theme:** `robbyrussell` or `agnoster` (Powerline enabled for git status).
* **Essential Plugins:**
* `git`: Contextual aliases for repo management.
* `zsh-autosuggestions`: Asynchronous command suggestions based on history.
* `zsh-syntax-highlighting`: Real-time visual feedback for command validity.
* `sudo`: Double-press `ESC` to prepend `sudo` to the previous command.



### `.zshrc` Performance Tweaks

The following optimizations are applied to the ZSH profile:

* **History:** Increased limit (10,000 entries) with timestamps for audit trails.
* **Aliases:** Custom aliases for automated recon sequences and WSL-Windows path interop.
* **Autocorrections:** Disabled to prevent interference with complex CLI tool syntax.

---

## 🧪 Virtualization Strategy (x86 Native)

Unlike previous ARM-based environments (Mac), this setup utilizes the **Intel Ultra 5 245K** core count for intensive virtualization via **VMware Workstation Pro**:

| Environment | Purpose | Network Mode |
| --- | --- | --- |
| **Active Directory Lab** | GOAD / Pentest training | NAT / Host-Only |
| **Metasploitable** | Vulnerability research | Isolated |
| **Windows Sandbox** | Malware analysis & Detonation | Disposable |

---

## 🛠 Hardware Acceleration (CUDA)

* **Driver:** NVIDIA CUDA WSL Driver.
* **Use Case:** Direct passthrough of the **RTX 5070** to WSL2 for high-speed password cracking.
* **Test Command:** `hashcat -I` (Confirmed recognition of the 12GB VRAM device).