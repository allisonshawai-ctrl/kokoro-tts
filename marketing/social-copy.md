# Social Copy — Kokoro TTS for OpenClaw

---

## Twitter/X — Main Launch Thread

```
🧵 The OpenClaw Control UI has a "read aloud" button.

By default, it sounds like this:
[SAMPLE: robotic Windows voice]

After Kokoro TTS, it sounds like this:
[SAMPLE: Kokoro natural voice]

Here's how it works — free and fully local. 🧵
```

```
1/ The speaker button in OpenClaw uses the browser's built-in Web Speech API.
Robotic. Flat. No personality.

I patched it to use Kokoro — a local neural TTS engine that runs on YOUR machine.
No cloud. No API key. No data leaves your network.
```

```
2/ Setup takes about 2 minutes.

One Docker command:
docker run -d --name kokoro-tts --restart always -p 8199:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest

One Python command:
python scripts/patch_kokoro.py

Done. Restart OpenClaw. Hard refresh.
```

```
3/ The patch script is interactive.

Before committing, you hear actual audio samples from all 60+ Kokoro voices.
British male, American female, you name it.
Pick the one you want, then it patches OpenClaw.

No guessing. No misclicks.
```

```
4/ It auto-heals after OpenClaw updates.

OpenClaw overwrites the patched files when it updates.
There's a background watcher that detects this and re-applies the patch automatically.
You never have to think about it again.
```

```
5/ It's free to download.

If it adds value to your workflow — consider throwing a dollar to SSG Charity.
Every contribution supports a real cause.
$cashyslashy on CashApp | ssg-charity.com

GitHub: https://github.com/allisonshawai-ctrl/kokoro-tts
```

---

## Twitter/X — Short Hook

```
Made the OpenClaw Control UI sound like a real person.

60+ neural voices. Fully offline. One install command.

Free: https://github.com/allisonshawai-ctrl/kokoro-tts
Support SSG: $cashyslashy on CashApp → ssg-charity.com
```

---

## Discord (OpenClaw Server / AI Community)

```
📢 New Tool: Kokoro TTS for OpenClaw

Replaces the robotic browser TTS in the Control UI with a natural-sounding local voice.
60+ voices (British/American male/female). One-command install. Auto-repairs after OpenClaw updates.

🎧 Live voice preview included — pick your voice before committing.

💰 Pay what you want — all donations go to SSG Charity.
CashApp: $cashyslashy | ssg-charity.com

📦 GitHub: https://github.com/allisonshawai-ctrl/kokoro-tts
```

---

## Reddit — r/OpenClaw / r/selfhosted

```
Title: I built a free tool that replaces OpenClaw's robotic TTS with Kokoro (60+ neural voices, fully offline)

Body:

The OpenClaw Control UI has a "read aloud" button that uses the browser's built-in Web Speech API.
It sounds robotic. I fixed it.

**What it does:**
- Replaces the speaker button call with a fetch to a local Kokoro FastAPI Docker container
- Patches OpenClaw's CSP to allow the local connection
- Includes an interactive voice sampler — preview 60+ voices before installing
- Auto-reapplies the patch after OpenClaw updates (via a Scheduled Task watcher)

**Install:**
```bash
docker run -d --name kokoro-tts --restart always -p 8199:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
python scripts/patch_kokoro.py
openclaw gateway restart
```

**Free.** If it adds value, consider donating to SSG Charity ($cashyslashy on CashApp | ssg-charity.com).

GitHub: https://github.com/allisonshawai-ctrl/kokoro-tts
```

---

## ClawhHub Listing Copy

```
Name: Kokoro TTS for OpenClaw
Tagline: Replace browser TTS with local Kokoro neural voices in the OpenClaw Control UI.

Description:
The OpenClaw Control UI speaker button sounds robotic by default. This skill patches the compiled
Control UI to call a local Kokoro Docker container instead, producing natural, high-quality speech.

What it does:
- Injects a _ttsSpeak() helper into the OpenClaw Control UI JS that calls Kokoro directly
- Patches the gateway CSP to allow localhost connections and blob media sources
- Ships with an interactive voice sampler (sample_voices.py) — preview 60+ voices before installing
- Auto-heals after OpenClaw updates via a Windows Scheduled Task watcher

Requirements: Docker, Python 3.8+
Supports: Windows (primary), Mac/Linux via scripts

Donations: SSG Charity (ssg-charity.com) | CashApp: $cashyslashy
GitHub: github.com/allisonshawai-ctrl/kokoro-tts

Pay what you want — free to download.
```

---

## Email / Newsletter Blurb

```
Subject: Replace your OpenClaw speaker button voice — free tool

If you use OpenClaw, you've seen the "read aloud" button. It uses the browser's built-in
voice — flat, robotic, unmistakable.

I built a free tool that replaces it with Kokoro — a local neural TTS engine.
60+ voices. Fully offline. Installs in 2 minutes.

Free to download. Pay what you want — all donations go to SSG Charity.

Download: github.com/allisonshawai-ctrl/kokoro-tts
Support: $cashyslashy on CashApp | ssg-charity.com
```

---

## Short Form Video (TikTok/Reels/Shorts) — Caption Script

```
THE HACK EVERY OPENCLAW USER NEEDS 💀

The built-in speaker button sounds ROBOTIC.

Here's how to make it sound like a real person — free, fully local, 60+ voices.

🔧 Docker one-liner
🐍 Python patch script
🔊 Pick your voice, preview it FIRST

Link in bio.

#openclaw #aiflow #localai #tts #productivityhack
```

---

## CTA Copy — everywhere

```
Free to download. No API key needed.

If this saves you time or sounds better — chip in for SSG Charity.
Every dollar goes to a real cause.

💚 CashApp: $cashyslashy
🌐 ssg-charity.com
🔗 github.com/allisonshawai-ctrl/kokoro-tts
```
