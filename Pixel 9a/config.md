# Pixel 9a - GrapheneOS Configuration

Documentation of the setup and hardening process for the Pixel 9a, integrated into the **MyHomeLab** ecosystem.

## 1. Installation Phase

The installation was performed using the **GrapheneOS WebUSB-based installer**, the recommended approach for verified boot integrity.

* **Device:** Google Pixel 9a
* **Method:** Web Installer (Chromium-based)
* **Key Steps:**
* Enabled **OEM Unlocking** via Developer Options.
* Flashed factory images via Fastboot mode.
* **Verified Boot:** Bootloader re-locked post-installation to ensure hardware-based attestation.
* **Verified Boot Hash:** `0508de44ee00bfb49ece32c418af1896391abde0f05b64f41bc9a2dfb589445b`



---

## 2. Security Hardening & System Settings

Specific GrapheneOS features enabled to maximize device security:

* **Scrambled PIN:** Randomizes the PIN layout on every boot to prevent shoulder surfing.
* **Auto-Reboot:** Set to **4 hours**. Forces the device into "Before First Unlock" (BFU) state, encrypting data at rest if the device is inactive.
* **USB Halting:** Configured to disable new USB connections when the device is locked to prevent BFU exploits (e.g., Cellebrite/GrayKey).
* **Network Sandboxing:** * **Gboard:** Network permission revoked. Used as a local-only keyboard to prevent keystroke logging to Google servers.
* **Sensors:** Restricted for browser-based apps to mitigate fingerprinting.



---

## 3. Profiles Strategy

A "Hybrid" approach was chosen for a balance between extreme privacy and daily usability:

* **Owner Profile (Main):** Restricted to Open Source (FOSS) apps only. No Google Play Services.
* **Private Space (Android 15):** Sandboxed environment for "untrusted" or proprietary apps.
* **Sandboxed Google Play:** Installed here for apps requiring GSF (Banking, Signal notifications, etc.).
* **Isolation:** The space is locked/hidden when not in use, killing all background processes of the apps within.



---

## 4. App Stack & Package Management

Apps are sourced from trusted repositories, avoiding the standard Play Store.

### Package Managers

* **Neo Store:** Modern F-Droid client for FOSS apps.
* **Aurora Store:** Anonymous interface for the Play Store (for proprietary apps).
* **Obtainium:** Updates apps directly from GitHub releases (e.g., Signal).

### Core Applications

| Category | App | Note |
| --- | --- | --- |
| **VPN** | PIA VPN | System-wide encryption. |
| **Passwords** | Bitwarden | Connected to self-hosted RPi 5 vault. |
| **2FA** | Aegis | Local, encrypted, open-source authenticator. |
| **Browser** | Vanadium | Hardened Chromium (GrapheneOS default). |
| **Mail** | Thunderbird | Connected to personal mail servers. |
| **Maps** | Organic Maps | Offline, privacy-friendly GPS. |
| **Media** | NewPipe / Aves | YouTube frontend (no ads) / Local Gallery. |

---

## 5. HomeLab Integration (RPi 5)

The Pixel 9a acts as a mobile node for the **MyHomeLab** infrastructure.

* **Syncthing:**
* Bidirectional sync between `Pixel 9a/DCIM` and `RPi 5/Storage`.
* Battery optimization set to "Unrestricted" for background sync.


* **Nextcloud (via DAVx5):**
* Synchronizes Contacts and Calendars with the Nextcloud instance running on the Raspberry Pi 5.
* Ensures zero-knowledge sync without Google Contacts.


* **App Manager:** Used to audit trackers in proprietary apps and manage system components.

---

## 6. Privacy Features Applied

* **Storage Scopes:** Enabled for all social media/messaging apps. Apps only see specific files/folders instead of the entire storage.
* **Contact Scopes:** Used to provide "Empty" or "Filtered" contact lists to apps like WhatsApp or Telegram.

---

**Last Updated:** January 25, 2026