#!/usr/bin/env python3
"""
sample_voices.py — Interactive Kokoro voice sampler.

Lists all voices from a running Kokoro container, lets you preview each one,
and returns the selected voice ID. Used by patch_kokoro.py --interactive.

Usage (standalone):  python sample_voices.py [--port 8199] [--phrase "Custom sample text"]
Usage (from script): from sample_voices import choose_voice; voice = choose_voice(port=8199)
"""
import sys
import os
import json
import tempfile
import subprocess
import platform
import urllib.request
import urllib.error
import argparse


DEFAULT_PORT   = 8199
DEFAULT_PHRASE = "Hello! I'm the voice you selected. How do I sound?"

# Grouped for readability in the menu
VOICE_GROUPS = {
    "British Female": ["bf_alice", "bf_emma", "bf_lily", "bf_v0emma", "bf_v0isabella"],
    "British Male":   ["bm_daniel", "bm_fable", "bm_george", "bm_lewis", "bm_v0george", "bm_v0lewis"],
    "American Female":["af_alloy", "af_aoede", "af_bella", "af_heart", "af_jadzia", "af_jessica",
                       "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky"],
    "American Male":  ["am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael",
                       "am_onyx", "am_puck"],
    "Other":          [],  # filled dynamically from API
}


def get_voices(port):
    """Fetch voice list from Kokoro API, fall back to hardcoded list."""
    try:
        url = f"http://127.0.0.1:{port}/v1/voices"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            # API may return list of strings or list of objects
            if isinstance(data, list):
                if data and isinstance(data[0], str):
                    return data
                if data and isinstance(data[0], dict):
                    return [v.get("id") or v.get("voice_id") or v.get("name") for v in data]
    except Exception:
        pass

    # Fall back: probe /v1/audio/speech with a bad voice to get the error listing
    try:
        url = f"http://127.0.0.1:{port}/v1/audio/speech"
        body = json.dumps({"model": "kokoro", "input": "x", "voice": "__probe__", "response_format": "mp3"}).encode()
        req = urllib.request.Request(url, data=body, headers={"content-type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=5)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            # Parse "Available voices: voice1, voice2, ..." from error message
            if "Available voices:" in msg:
                after = msg.split("Available voices:")[1]
                voices_raw = after.split('"')[0].strip().rstrip("}")
                voices = [v.strip() for v in voices_raw.split(",") if v.strip()]
                if voices:
                    return voices
    except Exception:
        pass

    # Last resort: return known-good subset
    return [
        "bf_v0isabella", "bf_alice", "bf_emma", "bf_lily",
        "bm_george", "bm_daniel",
        "af_heart", "af_nova", "af_sky", "af_bella",
        "am_echo", "am_michael",
    ]


def play_audio(wav_path):
    """Play a WAV file using platform-native tools (no pip required)."""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"$p=(New-Object System.Media.SoundPlayer '{wav_path}');$p.PlaySync()"],
                check=True, timeout=30
            )
        elif system == "Darwin":
            subprocess.run(["afplay", wav_path], check=True, timeout=30)
        else:
            # Linux: try aplay, then paplay
            for player in ["aplay", "paplay"]:
                try:
                    subprocess.run([player, wav_path], check=True, timeout=30)
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
    except subprocess.TimeoutExpired:
        print("  (playback timed out)")
    except Exception as e:
        print(f"  (could not play audio: {e})")
        print(f"  Audio saved to: {wav_path}")


def synthesize(port, voice, phrase):
    """Request WAV audio from Kokoro for the given voice and phrase."""
    url = f"http://127.0.0.1:{port}/v1/audio/speech"
    body = json.dumps({
        "model": "kokoro",
        "input": phrase,
        "voice": voice,
        "response_format": "wav"
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Kokoro returned {e.code}: {e.read().decode()[:200]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Could not reach Kokoro at port {port}: {e.reason}")


def group_voices(all_voices):
    """Sort voices into display groups."""
    grouped = {k: [] for k in VOICE_GROUPS}
    assigned = set()
    for group, known in VOICE_GROUPS.items():
        if group == "Other":
            continue
        for v in all_voices:
            if v in known:
                grouped[group].append(v)
                assigned.add(v)
    for v in all_voices:
        if v not in assigned:
            grouped["Other"].append(v)
    return {k: v for k, v in grouped.items() if v}


def choose_voice(port=DEFAULT_PORT, phrase=DEFAULT_PHRASE):
    """
    Interactive voice chooser. Returns selected voice ID string.
    Raises SystemExit if user cancels.
    """
    print()
    print("Checking Kokoro server...")
    try:
        all_voices = get_voices(port)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if not all_voices:
        print("No voices found. Is the Kokoro container running?")
        print(f"  docker run -d --name kokoro-tts --restart always -p {port}:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest")
        sys.exit(1)

    grouped = group_voices(all_voices)
    flat = []  # ordered list of all voices for indexing
    for voices in grouped.values():
        flat.extend(voices)

    # Display menu
    print(f"\nFound {len(flat)} voices:\n")
    idx = 1
    for group, voices in grouped.items():
        print(f"  {group}")
        for v in voices:
            marker = " *" if v == "bf_v0isabella" else "  "
            print(f"  {idx:>3}.{marker}{v}")
            idx += 1
    print()
    print("  (* = recommended default)")
    print()

    selected = None
    while True:
        print(f'Sample phrase: "{phrase}"')
        print()
        prompt = "Enter number to preview, voice name directly, or press Enter to use default (bf_v0isabella): "
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(0)

        # Empty = use default
        if raw == "":
            selected = "bf_v0isabella" if "bf_v0isabella" in flat else flat[0]
            print(f"\nUsing default: {selected}")
            break

        # Number selection
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(flat):
                voice = flat[n - 1]
            else:
                print(f"  Invalid number. Enter 1–{len(flat)}.")
                continue
        elif raw in flat:
            voice = raw
        else:
            print(f"  Voice '{raw}' not found. Enter a number or exact voice name.")
            continue

        # Preview
        print(f"\n  Synthesizing '{voice}'...")
        try:
            audio = synthesize(port, voice, phrase)
        except RuntimeError as e:
            print(f"  Error: {e}")
            continue

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio)
            tmp_path = tmp.name

        play_audio(tmp_path)
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        print()
        try:
            confirm = input(f"  Use '{voice}'? [Y/n/number to try another]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(0)

        if confirm in ("", "y", "yes"):
            selected = voice
            break
        elif confirm.isdigit():
            n = int(confirm)
            if 1 <= n <= len(flat):
                voice = flat[n - 1]
                print(f"\n  Synthesizing '{voice}'...")
                try:
                    audio = synthesize(port, voice, phrase)
                except RuntimeError as e:
                    print(f"  Error: {e}")
                    continue
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio)
                    tmp_path = tmp.name
                play_audio(tmp_path)
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
                try:
                    confirm2 = input(f"  Use '{voice}'? [Y/n]: ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
                    sys.exit(0)
                if confirm2 in ("", "y", "yes"):
                    selected = voice
                    break
            else:
                print(f"  Invalid number.")
        # else: loop again

    print(f"\nSelected voice: {selected}\n")
    return selected


def main():
    parser = argparse.ArgumentParser(description="Preview Kokoro TTS voices interactively")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Kokoro server port (default: {DEFAULT_PORT})")
    parser.add_argument("--phrase", default=DEFAULT_PHRASE, help="Sample phrase to synthesize")
    args = parser.parse_args()

    voice = choose_voice(port=args.port, phrase=args.phrase)
    print(f"Voice ID: {voice}")
    print()
    print("To patch OpenClaw with this voice:")
    print(f"  python patch_kokoro.py --voice {voice}")


if __name__ == "__main__":
    main()
