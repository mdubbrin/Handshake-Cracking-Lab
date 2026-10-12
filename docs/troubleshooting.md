# Troubleshooting

Most problems are one of the first three.

---

## Monitor mode won't enable

Check the driver actually supports it:

```bash
iw phy | grep -A10 "Supported interface modes"
```

No `* monitor` in the list means no command will fix it — you need a
different adapter.

**`Operation not possible due to RF-kill`:**

```bash
sudo rfkill unblock wifi
```

---

## `airodump-ng` shows no networks

Almost always NetworkManager still scanning on the card and stealing the
channel:

```bash
sudo nmcli device set wlan1 managed no
```

Still nothing? The heavier option — note this drops *all* your network
connections:

```bash
sudo airmon-ng check kill
```

**Only seeing 5 GHz networks?** Force the band:

```bash
sudo airodump-ng --band bg wlan1mon
```

A 2.4-only adapter can't see a 5 GHz hotspot at all — set your phone's
hotspot to 2.4 GHz.

---

## The hotspot doesn't show up

- **Is it still on?** Phones time out idle hotspots. Keep a device connected.
- **iPhone:** keep the Personal Hotspot screen open, phone unlocked.
- **Move closer.** `PWR` should be above -60 at a metre.
- It shows **WPA3 / SAE** — working as intended, this attack doesn't apply.
  Go back to Step 1 and look for a WPA2 option.

---

## No STATION rows under the AP

You need a connected device that's actually transmitting. Connect your second
device and load a webpage on it.

---

## Deauth doesn't work

**Test injection first:**

```bash
sudo aireplay-ng --test wlan1mon
```

If it fails and you're on an Intel card (AX200/AX201/AX210, most modern
laptops), that's expected — those drivers don't do injection. **Use Path B in
Step 5.** Nothing you configure will change it.

**Hangs on "Waiting for beacon frame":** it can't hear the AP. Keep
`airodump-ng` running in another terminal to hold the channel, or set it
manually:

```bash
sudo iw dev wlan1mon set channel 6
```

**`fixed channel wlan1mon: -1`:** something's channel-hopping behind your
back. Release the card with `nmcli` and kill any stray `airodump-ng`.

**It sends but the client stays connected:**

- **802.11w is on.** Common in WPA2/WPA3 mixed mode. Set the hotspot to WPA2
  only. If you can't, you've just demonstrated a working countermeasure.
- **Wrong client MAC.** Copy it exactly from the STATION column — phones use
  randomised MACs, so it won't match what the device shows in its settings.
- **Too far from the client.** Your frames have to reach *it*, not just the AP.

---

## No handshake appears

1. **Did you use `-c` to lock the channel?** Most common cause by far.
2. **Is the device actually reconnecting?** Watch it drop and rejoin.
3. **Try again.** It's four frames in a few milliseconds; missing them is
   normal. Two or three attempts is unremarkable.
4. **Get closer** — you need to hear both the AP and the client.
5. **Check the right file.** Each run makes a new one: `ls -t capture-*.cap | head -1`

**Handshake split across several files?**

```bash
mergecap -w merged.cap capture-0*.cap
```

---

## `aircrack-ng` says "no valid handshakes"

Name the target explicitly:

```bash
aircrack-ng -w wordlist.txt -b DE:AD:BE:EF:1A:2B -e "LabAP_test" capture-01.cap
```

Still failing? Check what you actually captured:

```bash
tshark -r capture-01.cap -Y eapol
```

You need **messages 1 and 2 from the same exchange**. One alone won't crack.

---

## It runs the whole list and finds nothing

The password isn't in the list. Against a decent passphrase that's the normal
outcome — see `defenses.md`.

For the lab, check it's really there:

```bash
grep -cx 'sunflower22' wordlist.txt
```

If you built the file on Windows, strip the line endings:

```bash
sed -i 's/\r$//' wordlist.txt
```

---

## No Wi-Fi after the lab

```bash
sudo airmon-ng stop wlan1mon
sudo nmcli device set wlan1 managed yes
sudo systemctl restart NetworkManager
```

A reboot fixes anything this leaves behind.
