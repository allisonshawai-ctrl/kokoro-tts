---
name: kokoro-tts
description: >
  Installs and configures Kokoro TTS (high-quality local British/American neural voice) as the
  speak-aloud voice for the OpenClaw Control UI. Use when the user wants to replace the robotic
  Windows TTS voice with a natural-sounding Kokoro voice in the OpenClaw web UI speaker button,
  or when setting up local TTS for OpenClaw from scratch. Also handles re-applying patches after
  OpenClaw updates.
---

# Kokoro TTS for OpenClaw Control UI

Replaces the default browser TTS in the OpenClaw Control UI with Kokoro (neural voice, British
female `bf_v0isabella` by default) served via Docker.

## How it works

The Control UI's speaker button calls an internal `Nb()` function (browser Web Speech API).
This skill patches the compiled Control UI JS to instead call Kokoro's OpenAI-compatible HTTP
API at `http://127.0.0.1:8199`, and patches the gateway CSP to allow the connection.

## Install

### 1. Start the Kokoro Docker container

```bash
docker run -d --name kokoro-tts --restart always -p 8199:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

Verify: `curl -s http://127.0.0.1:8199/v1/audio/speech -X POST -H "content-type: application/json" -d '{"model":"kokoro","input":"hello","voice":"bf_v0isabella","response_format":"mp3"}' -o /dev/null -w "%{http_code}"`
Expected: `200`

### 2. Update OpenClaw config voice

Patch `messages.tts.providers.openai.voice` to `bf_v0isabella` (the Docker image uses `bf_v0isabella`,
not `bf_isabella`):

```bash
openclaw config set messages.tts.providers.openai.voice bf_v0isabella
```

Or use `gateway config.patch`:
```json
{"messages":{"tts":{"providers":{"openai":{"voice":"bf_v0isabella"}}}}}
```

### 3. Run the patch script

```bash
python scripts/patch_kokoro.py
```

This script:
- Injects a `_ttsSpeak()` helper function before `function ex(e)` in the Control UI JS
- Replaces the `Nb(r,{...})` call in the speaker button with `_ttsSpeak(r,n)`
- Patches `control-ui-B9gYJHuG.js` to add `connect-src http://127.0.0.1:8199` and `media-src blob:` to CSP

### 4. Restart the gateway

```bash
openclaw gateway restart
```

### 5. Hard refresh the Control UI

`Ctrl+Shift+R` in the browser.

## Re-applying after OpenClaw updates

OpenClaw updates overwrite the compiled JS files. Re-run the patch script and restart the gateway:

```bash
python scripts/patch_kokoro.py && openclaw gateway restart
```

Consider setting up a file watcher or post-update hook to auto-apply.

## Voice options

Popular voices in the Docker image:
- `bf_v0isabella` — British female (default, recommended)
- `bf_alice`, `bf_emma`, `bf_lily` — Other British female
- `bm_george`, `bm_daniel` — British male
- `af_heart`, `af_nova`, `af_sky` — American female

Change voice: edit the `voice` field in `scripts/patch_kokoro.py` and re-run.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Black page after refresh | Syntax error in patch | Run `scripts/revert_kokoro.py` to restore original |
| `[tts] Error: kokoro 400` | Wrong voice name | Verify voice exists: `curl http://127.0.0.1:8199/v1/audio/speech -d '{"voice":"bf_v0isabella",...}'` |
| `[tts] Failed to fetch` + CSP error | CSP patch missing | Re-run patch script, restart gateway |
| `[tts] GatewayRequestError: talk.speak unavailable` | Old patch version | Re-run patch script |
| Robotic voice, no console error | Cached old JS | Hard refresh `Ctrl+Shift+R` |
| Kokoro container down | Docker not running | `docker start kokoro-tts` |

## Files modified by this skill

- `<openclaw>/dist/control-ui/assets/index-Bsj0vinf.js` — JS patch (function injection + button replacement)
- `<openclaw>/dist/control-ui-B9gYJHuG.js` — CSP header patch

Note: The JS filename (`index-Bsj0vinf.js`) may change between OpenClaw versions. The patch
script auto-detects the correct file.
