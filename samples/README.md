# Practice capture

`practice-handshake-01.cap` — a WPA2 capture with a complete 4-way handshake,
so you can do Steps 6–8 without any wireless hardware.

```
ESSID       PixelHotspot_Lab
BSSID       de:ad:be:ef:1a:2b
client      aa:bb:cc:11:22:33
passphrase  sunflower22
```

Use it:

```bash
cp samples/practice-handshake-01.cap capture-01.cap
aircrack-ng capture-01.cap                     # (1 handshake)
printf '%s\n' password hunter2 sunflower22 > wordlist.txt
aircrack-ng -w wordlist.txt capture-01.cap     # KEY FOUND! [ sunflower22 ]
```

It's also a good way to check your tools work before blaming your capture.

**This was generated, not captured off the air** — the MACs and network name
are invented, and no real device or person is involved. The handshake itself
is cryptographically genuine though: the signatures are real, derived from
`sunflower22` exactly as a real device would, which is why `aircrack-ng`
cracks it normally.
