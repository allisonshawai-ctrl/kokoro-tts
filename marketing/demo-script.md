# Demo Video Script — Kokoro TTS for OpenClaw

**Format:** Screen-record, 45–60 seconds, no voice-over needed (can add caption text)
**Hook:** Open with sound ON so they hear the difference immediately

---

## Scene 1 — The Problem (0:00–0:10)

**On screen:** OpenClaw Control UI, click the speaker button on a chat message.

**Audio:** Default robotic Windows/system voice reading the message.

**Text overlay:** "Your OpenClaw UI sounds like this."

---

## Scene 2 — The Fix (0:10–0:25)

**On screen:** Terminal window running:
```
docker run -d --name kokoro-tts --restart always -p 8199:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
python scripts/patch_kokoro.py
```
Show the interactive voice picker — scroll through the list, pick `bf_v0isabella`.

**Text overlay:** "One command. One install."

---

## Scene 3 — The Result (0:25–0:40)

**On screen:** Back to OpenClaw Control UI, click the speaker button.

**Audio:** Kokoro British female voice reading the message clearly and naturally.

**Text overlay:** "Now it sounds like THIS."

---

## Scene 4 — The Cause (0:40–0:55)

**On screen:** The patch files shown briefly — the injected `_ttsSpeak()` function, the CSP patch.

**Text overlay:** "Fully local. 60+ voices. Auto-heals after updates. Free."

---

## Scene 5 — CTA (0:55–end)

**On screen:** GitHub release page + CashApp + SSG link.

**Text overlay:** "Free download. Donate to SSG to support the cause. $cashyslashy on CashApp."

---

# Alternative: Voice-Over Version

**Duration:** 60–90 seconds
**Tone:** Calm, confident, not salesy

---

**[0:00–0:08]** Show OpenClaw UI speaker button. Hear robotic voice.

**[0:08]** "The OpenClaw Control UI has a speaker button built in. But by default, it uses your browser's built-in TTS — and it sounds robotic."

**[0:20]** Show terminal: Docker run + patch script running interactively.

"Installing Kokoro takes about 30 seconds. You get an interactive voice picker — preview any of 60+ voices — and pick the one you like. Then it patches OpenClaw and you're done."

**[0:38]** Show speaker button pressed, Kokoro voice plays.

"Once it's set up, every message reads aloud in a natural British female voice — fully offline, no cloud, no API key."

**[0:52]**

"The patch auto-reapplies after OpenClaw updates, so it never breaks permanently."

**[1:00]** Show GitHub + CashApp + SSG links.

"It's free to download. If it adds value to your workflow, consider donating to SSG Charity — 100% of contributions go to a good cause. That's $cashyslashy on CashApp, or ssg-charity.com."
