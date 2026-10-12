# Handshake Cracking Lab

Capture a WPA2 handshake off the air, force a device to reconnect with a
deauth attack, and crack the password offline.

**The target is a hotspot you create on your own phone.** You own it, you set
its password, you turn it off when you're done.

---

## Before you start

**Only attack your own hotspot/network.**

Deauth frames are real transmissions that knock real devices offline. In the
US, deauthing networks you don't control is **illegal**. Doing it to your own
hotspot is fine. The lab always targets one specific device so you don't hit
anyone else.

---

## What you need

- **A Linux machine.** Kali/Parrot have the tools preinstalled. Any distro
  works. A VM only works with a USB adapter passed through.
- **A Wi-Fi adapter with monitor mode.** Injection too, ideally, but Step 5
  has a path that works without it.
- **A phone**: this is the target AP. Any device that hosts a network that **you own** (eg home network, ESP32) will also work. You can find the ESP32 code in the repo.
- **A second device** to connect to the hotspot. A hotspot with nothing
  connected to it never produces a handshake.

```bash
# Debian / Ubuntu / Kali
sudo apt install aircrack-ng tshark

# Fedora
sudo dnf install aircrack-ng wireshark-cli

# Arch
sudo pacman -S aircrack-ng wireshark-cli
```

Check your adapter supports monitor mode:

```bash
iw phy | grep -A10 "Supported interface modes"   # look for "* monitor"
```

Some built-in cards do monitor mode but not packet injection, so use Path B in step 5 if needed. Most built-in Broadcom/Realtek cards do neither; you'll want a cheap USB adapter (anything `ath9k_htc`, e.g. Alfa AWUS036NHA).

---

## The files

| | |
|---|---|
| **[`LAB.md`](LAB.md)** | **The lab. Start here.** |
| [`docs/how-it-works.md`](docs/how-it-works.md) | Why this attack is possible. Read after you finish. |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | When it breaks. It will. |
| [`docs/defenses.md`](docs/defenses.md) | What actually stops it. |
| `samples/` | A practice capture, if you have no adapter. |

**No compatible adapter?** Skip to Step 6 and use the capture in `samples/`.
