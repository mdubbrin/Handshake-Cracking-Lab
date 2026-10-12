# Defenses

What actually stops the attack you just ran, in order of how much it helps.

---

## 1. A long passphrase

**This is the one that matters.**

Every other step can go perfectly — good capture, working injection, fast GPU
— and it all amounts to nothing if the password isn't guessable. You didn't
break WPA2 in Step 8, you broke `sunflower22`.

At a generous 1,000,000 guesses/sec (a serious GPU rig, far beyond a laptop):

| passphrase | time to crack |
|---|---|
| `password1` | instant — it's in every wordlist |
| `sunflower22` | seconds |
| `Summer2024!` | minutes — rule-based lists expect this pattern |
| 8 random lowercase | ~2.5 days |
| 10 random lowercase | ~4 years |
| 4 random words | ~115 years |
| 20 random characters | forever |

**Length beats complexity.** `correct-horse-battery-staple` is far stronger
than `P@ssw0rd!` and much easier to type into a smart TV. Punctuation adds a
few bits; each extra word adds about thirteen.

The thing to internalise: **an offline attack has no rate limit and no
lockout.** Once someone has your handshake, your passphrase is doing all the
work, alone — and they can retry it in five years on better hardware.

Use four or five random words, or 16+ random characters from a password
manager.

---

## 2. WPA3

**Removes the offline attack entirely.** A captured WPA3 exchange can't be
used to test password guesses, so there's nothing to crack — an attacker is
forced to guess online, one try at a time, against something that can log and
rate-limit them.

It also brings forward secrecy, and makes the deauth fail.

Two caveats: **mixed `WPA2/WPA3` mode is as weak as WPA2** for anything that
negotiates down to it, and a weak password is still weak, just harder to
attack at scale.

---

## 3. 802.11w (Protected Management Frames)

**Stops the deauth. Doesn't protect the password.**

Forged deauth frames get ignored, so Step 5 Path A stops working. But you can
still wait for a device to reconnect on its own — people's phones join
networks all day — and it does nothing about a handshake already captured.

Optional in WPA2 (usually off), mandatory in WPA3. Turn it on if your router
offers it. Its real value is blocking **evil twin** attacks, where deauth is
used to herd devices onto a fake AP.

---

## 4. WPA2/WPA3-Enterprise

**No shared password at all.** Everyone authenticates individually against a
RADIUS server, so there's nothing for this attack to target. This is why
`eduroam` works the way it does.

Needs a RADIUS server and certificates — right for an organisation, overkill
for a house. If you do run it, make sure clients **validate the server
certificate**; otherwise a fake RADIUS server harvests credentials, and that
misconfiguration is very common.

---

## What doesn't work

| | |
|---|---|
| **Hiding the SSID** | It's in every connection attempt. Visible the moment anyone connects, and it breaks roaming. |
| **MAC filtering** | MACs are plaintext in your capture. Copy one, `macchanger`, done — about 30 seconds. |
| **Lowering transmit power** | A directional antenna hears you from much further than you'd think. |
| **Changing the password often** | A 13-minute crack doesn't care about 30-day rotation, and rotation pressure makes people pick weaker, more patterned passwords. |

**Turn WPS off.** Not part of this lab, but the WPS PIN is checked in two
halves — about 11,000 attempts — and Pixie Dust often breaks it instantly. It
bypasses a strong passphrase completely. It's the worst default on consumer
routers.

---

## Can you detect it?

Not the cracking — that's offline, on someone else's computer, with no
network traffic at all. A device sitting in monitor mode is essentially
undetectable.

The deauth is loud, though. In Wireshark: `wlan.fc.type_subtype == 12`. The
user-visible symptom is devices dropping and reconnecting for no reason.

---

## Short version

1. **Use a long random passphrase.** This is the one that matters.
2. **Enable WPA3** if all your devices support it — avoid mixed mode.
3. **Enable PMF** to stop deauth.
4. **Turn off WPS.**

The lab you just ran is defeated by step 1 alone.
