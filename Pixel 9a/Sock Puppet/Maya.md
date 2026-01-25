# Sock Puppet Profile: Maya Golan

This document details the configuration and operational security (OpSec) protocols for the secondary "Maya Golan" persona hosted on the **Pixel 9a (GrapheneOS)**.
All the identity of Maya has been AI generated. 

## 🎭 1. The Persona (Identity Specs)

The goal of this identity is to maintain a high-trust, localized Israeli presence without any link to the primary owner.

* **Name:** Maya Golan (מאיה גולן)
* **Age:** 22-24 (Student Persona)
* **Location:** Tel Aviv-Yafo, Israel
* **Occupation:** Psychology Student @ TAU / Freelance Graphic Designer
* **Visual Identity:** AI-generated "Candid Style" portrait (Early 20s, dark wavy hair, Tel Aviv urban background).
* *Storage:* Image stored exclusively within this encrypted profile.


* **Backstory:** Interests include Bauhaus architecture, urban photography, and the TLV coffee scene.

---

## ⚙️ 2. System Configuration (GrapheneOS)

The persona operates within a fully isolated secondary user profile on GrapheneOS.

* **Profile Isolation:** * Separate encryption keys (Data-at-Rest protection).
* **Scrambled PIN:** Enabled for profile entry.
* **End Session:** Profile session is terminated manually after use to clear cache and keys from RAM.


* **Input & Language:**
* **System Language:** English (US) / Hebrew (Secondary).
* **Keyboard:** Gboard with **Network Access Revoked**. English and Hebrew layouts enabled.


* **Security Settings:**
* **USB Halting:** Enabled (Blocks data transfer when locked).
* **Sensors:** Disabled for the browser to prevent hardware fingerprinting.



---

## 🌐 3. Network & Connectivity

Network traffic is strictly controlled to maintain the Tel Aviv geolocation.

* **VPN Protocol:**
* **Provider:** PIA VPN (or equivalent).
* **Exit Node:** Israel (Tel Aviv).
* **Hardening:** "Always-on VPN" + "Block connections without VPN" (System-level Kill Switch).


* **DNS:** Encrypted DNS (AdGuard/NextDNS) to prevent ISP-level leaking of the puppet's activity.
* **MAC Randomization:** Per-network randomization enabled.

---

## 📱 4. Communications & App Stack

Apps are managed via **Aurora Store** (Anonymous Mode) to avoid Google Account linkage.

* **Phone Number:** Virtual +972 (Israeli) number obtained via SMSPool/5sim (Paid with XMR).
* **Telegram:** Hardened configuration.
* Phone number visibility: **Nobody**.
* Discovery by number: **My Contacts**.
* 2FA: Enabled (Stored in a dedicated Sock Puppet Bitwarden vault).


* **Browsing:** Vanadium (Hardened) with "Clear on exit" enabled.
* **Tools:**
* **ExifEraser:** Used to strip all metadata from photos before any upload.
* **Obtainium:** Updates messaging apps directly from source.



---

## 🏠 5. HomeLab Integration (RPi 5)

Integration with the Raspberry Pi 5 is handled through a one-way, air-gapped logic.

* **Syncthing Vault:**
* **Sync Folder:** `/Maya_Vault`
* **Mapping:** Syncs directly to the RPi 5 at `MyHomeLab/SockPuppets/Maya/Data`.
* **Isolation:** This Syncthing instance is unique to Maya's profile and does not see the "Owner" profile's folders.


* **Backup:** Weekly backup of Maya's configuration via Syncthing to an encrypted partition on the RPi 5.

---

## 🛡️ 6. Operational Security (OpSec) Rules

To prevent "Identity Bleed," the following rules must be strictly followed:

1. **Stylometry:** Use Hebrew-English slang, specific emojis, and a different typing rhythm than the owner.
2. **Financial Isolation:** No credit cards. All digital purchases or number rentals are done via **Monero (XMR)** or prepaid gift cards bought with crypto.
3. **Media Chain:** Never upload a photo taken in the "Owner" profile to the "Maya" profile. All media must be re-captured (screenshot) or metadata-scrubbed via **ExifEraser**.
4. **No Cross-Logins:** Never log into any personal account (Owner Gmail, Bank, etc.) while the Maya VPN is active.