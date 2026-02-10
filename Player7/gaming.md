# 🎮 Gaming Environment Setup & Optimization

This document outlines the software stack and optimization steps configured on the **PLAYER 7** workstation to leverage the **NVIDIA RTX 5070** and the **Xiaomi G27Qi 180Hz** display.

---

## 🚀 Primary Game Launchers
To maintain system performance, only essential launchers are installed with "Start on Boot" disabled.

| Launcher | Installation Method | Purpose |
| :--- | :--- | :--- |
| **Steam** | Manual Download | Primary library for AAA and Indie titles. |
| **Epic Games Store** | Manual Download | Exclusive titles and weekly free assets. |
| **Xbox Game Pass** | Windows Store | High-value subscription service for PC titles. |
| **Ninite** | [Ninite.com](https://ninite.com) | Bulk installation of Discord, VLC, and Spotify to avoid bloatware. |

---

## 🛠️ Performance & Monitoring Tools
Strategic tools used to monitor hardware thermals and optimize frame delivery.

* **NVIDIA App:** Replaces GeForce Experience. Used for Game Ready Drivers and managing **DLSS 3.5 / Ray Reconstruction** profiles.
* **MSI Afterburner + RivaTuner:** Configured for On-Screen Display (OSD) to monitor **Intel Ultra 5 245K** temperatures and GPU clock speeds during stress tests.
* **Lossless Scaling:** Acquired via Steam. Used to apply **Frame Generation** on titles that do not natively support DLSS 3.
* **HWiNFO64:** Used for deep-dive sensor logging to ensure the 800W PSU and cooling solution maintain optimal thermal headroom.

---

## ⚙️ Critical System Optimizations
Specific tweaks applied to Windows 11 to eliminate latency and maximize the 180Hz experience.

### 1. Display & GPU Settings
* **Refresh Rate:** Set to **180Hz** in *Windows Advanced Display Settings* (default is often 60Hz).
* **NVIDIA Control Panel:**
    * *Low Latency Mode:* Set to **Ultra**.
    * *Power Management:* Set to **Prefer Maximum Performance**.
    * *Vertical Sync:* Forced **OFF** in-driver (managed via G-Sync/Freesync).

### 2. Input Latency Reduction
* **Enhance Pointer Precision:** **Disabled** in Mouse Settings to ensure a 1:1 raw input ratio (essential for muscle memory).
* **Game Mode:** **Enabled** to allow Windows to prioritize CPU/GPU cycles for the active game process.

---

## 📺 Visual Profile (Xiaomi G27Qi)
* **Resolution:** 2560 x 1440 (Native QHD).
* **HDR:** Enabled for supported cinematic titles (toggled via `Win + Alt + B`).
* **Blue Light Filter:** Managed via **f.lux** or Windows Night Light for late-night documentation/gaming sessions to reduce eye strain.

---

## 📝 Maintenance Routine
1. **Weekly:** Check for NVIDIA Game Ready Driver updates.
2. **Monthly:** Clear DirectX Shader Cache to prevent stuttering in long-term installs.
3. **Quarterly:** Physical dust inspection of the Antec CX300 filters.