# How it works

Read this after you've done the lab.

---

## The handshake isn't leaking your password

When a device joins a WPA2 network, both sides need a shared encryption key.
The passphrase never crosses the air — that part genuinely works, and this
attack doesn't break it.

You didn't *extract* the password from those frames. You **guessed** it, and
used the frames to check each guess. That distinction is the whole lesson.

---

## Where the key comes from

**Step 1 — passphrase to PMK:**

```
PMK = PBKDF2-HMAC-SHA1(passphrase, SSID, 4096 rounds)
```

Two things matter here.

**The SSID is the salt.** So the same password on two differently-named
networks gives completely different results — you can't build one universal
lookup table. But a default name like `linksys` or `attwifi` is shared by
millions of networks, so precomputed tables for common SSIDs are real and
cheap. A unique network name genuinely helps.

**4096 rounds is deliberate slowness.** It's why you got a few thousand
guesses a second instead of billions. This is the main thing standing between
a weak Wi-Fi password and instant compromise.

**Step 2 — PMK to session key.** The PMK is long-term, so each session
derives a fresh key from it plus both MAC addresses and two random numbers
(nonces). Exchanging those nonces is the entire point of the 4-way handshake:

| | | |
|---|---|---|
| **M1** | AP → device | here's my random number |
| **M2** | device → AP | here's mine, plus proof I know the password |
| **M3** | AP → device | verified, install the key |
| **M4** | device → AP | done |

---

## The part that gives it away

That "proof" in M2 is a **MIC** — a signature computed with a key derived
from the password.

Its purpose is legitimate: it proves the device knows the passphrase. But
look at what it's made of, from an eavesdropper's seat:

| ingredient | where you got it |
|---|---|
| SSID | broadcast constantly in beacons |
| both MAC addresses | plaintext in every frame header |
| both random numbers | M1 and M2, plaintext |
| the MIC itself | M2, plaintext |
| the passphrase | ...the one unknown |

So the handshake hands you a complete **password-checking machine**. One
unknown, and a published formula that tells you when a guess is right.

That's why you could have turned the hotspot off and still cracked it. You
weren't attacking the network — you were attacking a maths problem you'd
written down.

### Seeing it in your own output

When `aircrack-ng` found the key it printed a `Master Key`. That's the PMK —
the output of step 1 above, for the correct password. Everything it did was:
guess → derive PMK → derive session key → compute MIC → compare → discard.
A few thousand times a second.

---

## Why the deauth worked

802.11 management frames — including deauthentication — are sent **in the
clear and unauthenticated** in WPA2. A deauth frame is just a source MAC, a
destination MAC, and a reason code. Nothing signs it.

So you put the AP's address in the "from" field and sent it. The device had
no way to disagree.

This isn't an implementation bug, it's the 1997 protocol working as
specified. The fix arrived in 2009: **802.11w (Management Frame
Protection)**, which signs management frames. With it on, forged deauths are
ignored.

PMF is optional in WPA2 and usually off — which is why this lab works. It's
mandatory in WPA3.

---

## Why WPA3 stops all of this

WPA3 replaces the handshake with **SAE**, and the critical property is that
a passive listener **can't test guesses offline**. Nothing in a captured SAE
exchange is a checkable function of the password. The password-checking
machine in the table above simply doesn't exist.

An attacker is forced back to guessing *online*, one try at a time, against a
device that can rate-limit and log them.

WPA3 also gives **forward secrecy**: capture traffic today, learn the
password next year, and you still can't decrypt it. Under WPA2, learning the
password lets you decrypt anything you recorded whose handshake you caught.

So the honest summary:

> Every step of this attack follows from 1990s design decisions that have all
> since been fixed — and the fixes ship switched off on most routers.

---

## Related: the PMKID attack

In 2018 it turned out many APs include a **PMKID** in M1 — another value
derived from the password, with everything else public. Same weakness as the
MIC.

But it's in **M1**, which the AP sends when *you* ask to associate. So: no
client needed, no deauth, no waiting. Walk up, ask, get a crackable hash.

Most phone hotspots aren't vulnerable, but it's why "my network has no
clients on it" isn't a defense.

---

## Further reading

- [The PMKID attack](https://hashcat.net/forum/thread-7717.html) — original writeup
- Vanhoef & Piessens, *KRACK* (2017) — attacking the handshake's logic rather than the password
- Vanhoef, *Dragonblood* (2019) — attacks on WPA3's SAE; it isn't magic either
