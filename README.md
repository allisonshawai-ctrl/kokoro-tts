# kokoro-tts — OpenClaw Skill

Replaces the robotic browser TTS voice in the [OpenClaw](https://openclaw.ai) Control UI with **Kokoro** — a high-quality local neural TTS engine. Works fully offline after setup.

**Default voice:** `bf_v0isabella` (British female, natural-sounding)

## What it does

The OpenClaw Control UI speaker button uses the browser's Web Speech API by default (robotic Windows/system voice). This skill patches the compiled Control UI to call a local [Kokoro FastAPI](https://github.com/remsky/Kokoro-FastAPI) Docker container instead, producing natural speech without any cloud API calls.

## Requirements

- OpenClaw installed
- Docker Desktop running
- Python 3.8+ (for the patch script)

## Quick Start

**1. Start Kokoro container**
```bash
docker run -d --name kokoro-tts --restart always -p 8199:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

**2. Run the patch**
```bash
python scripts/patch_kokoro.py
```

**3. Restart OpenClaw gateway**
```bash
openclaw gateway restart
```

**4. Hard refresh the Control UI**
`Ctrl+Shift+R` in browser — done.

## Options

```
python scripts/patch_kokoro.py --voice bf_alice --port 8199
```

Available voices: `bf_v0isabella`, `bf_alice`, `bf_emma`, `bf_lily`, `bm_george`, `bm_daniel`, `af_heart`, `af_nova`, `af_sky` and [many more](https://github.com/remsky/Kokoro-FastAPI).

## After OpenClaw updates

Re-run the patch script after any OpenClaw update (the compiled JS files get overwritten):
```bash
python scripts/patch_kokoro.py && openclaw gateway restart
```

## Revert

```bash
python scripts/revert_kokoro.py && openclaw gateway restart
```

## Install as OpenClaw Skill

Download `kokoro-tts.skill` from [Releases](../../releases) and install:
```bash
openclaw skills install kokoro-tts.skill
```

Then trigger it by asking the OpenClaw agent:
> "Set up Kokoro TTS for the Control UI"

## How it works

- Injects a `_ttsSpeak()` fetch function into the compiled Control UI JS bundle
- Replaces the speaker button's `Nb()` (Web Speech API) call with `_ttsSpeak()`
- Patches the gateway Content Security Policy to allow `connect-src http://127.0.0.1:8199` and `media-src blob:`
- Falls back to browser TTS if Kokoro is unreachable

## License

MIT
