#!/usr/bin/env python3
"""
patch_kokoro.py — Patches OpenClaw Control UI to use Kokoro TTS instead of browser Web Speech API.

Usage: python patch_kokoro.py [--voice VOICE] [--port PORT] [--openclaw-dir DIR]

Idempotent: safe to run multiple times. Detects and replaces any prior patch version.
"""
import sys
import os
import glob
import argparse

# ── Config ──────────────────────────────────────────────────────────────────
DEFAULT_VOICE = "bf_v0isabella"
DEFAULT_PORT  = 8199
DEFAULT_OPENCLAW_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm", "node_modules", "openclaw", "dist")
# ────────────────────────────────────────────────────────────────────────────

def find_control_ui_js(dist_dir):
    """Find the main Control UI JS bundle (index-*.js)."""
    pattern = os.path.join(dist_dir, "control-ui", "assets", "index-*.js")
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"No Control UI JS found at {pattern}")
    if len(matches) > 1:
        print(f"  Warning: multiple matches, using first: {matches}")
    return matches[0]

def find_csp_js(dist_dir):
    """Find the CSP/gateway JS file — the one that contains buildControlUiCspHeader."""
    pattern = os.path.join(dist_dir, "control-ui-*.js")
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"No CSP JS found at {pattern}")
    # Pick the file that actually contains connect-src (the CSP builder)
    for m in matches:
        with open(m, "r", encoding="utf-8") as f:
            content = f.read()
        if "connect-src" in content:
            return m
    # Fall back to first match
    return matches[0]

def patch_ui_js(path, voice, port):
    """Inject _ttsSpeak helper and replace Nb() call in speaker button."""
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # Remove any existing _ttsSpeak injection first (idempotent)
    helper_start = c.find("function _ttsSpeak(")
    ex_start = c.find("function ex(e){")
    if helper_start >= 0 and helper_start < ex_start:
        print("  Removing existing _ttsSpeak helper...")
        c = c[:helper_start] + c[ex_start:]
        ex_start = c.find("function ex(e){")

    if ex_start < 0:
        raise RuntimeError("Could not find 'function ex(e){' anchor in Control UI JS. File may have changed in this OpenClaw version.")

    # Build helper — uses only double-quoted strings (backtick keys are invalid JS in object literals)
    helper = (
        f'function _ttsSpeak(r,n){{'
        f'fetch("http://127.0.0.1:{port}/v1/audio/speech",'
        f'{{method:"POST",'
        f'headers:{{"content-type":"application/json","authorization":"Bearer local"}},'
        f'body:JSON.stringify({{model:"kokoro",input:r,voice:"{voice}",response_format:"mp3"}})}}'
        f').then(function(res){{if(!res.ok)throw new Error("kokoro "+res.status);return res.blob()}})'
        f'.then(function(blob){{'
        f'var url=URL.createObjectURL(blob),a=new Audio(url);'
        f'a.onended=function(){{URL.revokeObjectURL(url);if(n.isConnected){{n.classList.remove("chat-tts-btn--active");n.title="Read aloud"}}}};'
        f'a.onerror=function(){{URL.revokeObjectURL(url);if(n.isConnected){{n.classList.remove("chat-tts-btn--active");n.title="Read aloud"}}}};'
        f'a.play()'
        f'}}).catch(function(err){{'
        f'console.error("[tts]",err);'
        f'if(n.isConnected){{n.classList.remove("chat-tts-btn--active");n.title="Read aloud"}}'
        f'Nb(r,{{onEnd:function(){{if(n.isConnected){{n.classList.remove("chat-tts-btn--active");n.title="Read aloud"}}}},onError:function(){{if(n.isConnected){{n.classList.remove("chat-tts-btn--active");n.title="Read aloud"}}}}}})}})}}\n'
    )

    c = c[:ex_start] + helper + c[ex_start:]

    # Replace the Nb() call in the speaker button with _ttsSpeak(r,n)
    # The button Nb call uses arrow functions with backtick strings
    old_nb = "Nb(r,{onEnd:()=>{n.isConnected&&(n.classList.remove(`chat-tts-btn--active`),n.title=`Read aloud`)},onError:()=>{n.isConnected&&(n.classList.remove(`chat-tts-btn--active`),n.title=`Read aloud`)}})"
    occurrences = []
    idx = 0
    while True:
        idx = c.find(old_nb, idx)
        if idx < 0:
            break
        occurrences.append(idx)
        idx += 1

    if occurrences:
        # Replace the last occurrence (the button call site, not inside the helper)
        last = occurrences[-1]
        c = c[:last] + "_ttsSpeak(r,n)" + c[last + len(old_nb):]
        print(f"  Replaced Nb() call at byte {last}")
    else:
        # May already be replaced from a prior run
        if "_ttsSpeak(r,n)" in c:
            print("  Nb() already replaced with _ttsSpeak(r,n) — skipping")
        else:
            print("  WARNING: Could not find Nb() call in button. Button may not be patched.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

    print(f"  Helper injected: {'_ttsSpeak' in c}")
    print(f"  Voice: {voice}")
    print(f"  No backtick keys: {'`content-type`' not in c[c.find('function _ttsSpeak'):c.find('function ex(e){')] if 'function _ttsSpeak' in c else 'N/A'}")

def patch_csp_js(path, port):
    """Add connect-src and media-src blob: to CSP header builder."""
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    connect_target = f"http://127.0.0.1:{port}"

    # Check if already patched
    if connect_target in c and "media-src blob:" in c:
        print(f"  CSP already patched with {connect_target} and media-src blob:")
        return

    # Replace original connect-src line
    old_connect = '"connect-src \'self\' ws: wss:"'
    new_connect = f'"connect-src \'self\' ws: wss: {connect_target}",\n\t\t"media-src blob:"'

    # Also handle if previously patched with just connect-src but missing media-src
    old_connect_partial = f'"connect-src \'self\' ws: wss: {connect_target}"'
    new_connect_partial = f'"connect-src \'self\' ws: wss: {connect_target}",\n\t\t"media-src blob:"'

    if old_connect in c:
        c = c.replace(old_connect, new_connect, 1)
        print(f"  Added connect-src {connect_target} and media-src blob: to CSP")
    elif old_connect_partial in c and "media-src blob:" not in c:
        c = c.replace(old_connect_partial, new_connect_partial, 1)
        print(f"  Added media-src blob: to CSP (connect-src already present)")
    else:
        print("  WARNING: Could not find connect-src line in CSP JS. CSP may not be patched.")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

def main():
    parser = argparse.ArgumentParser(description="Patch OpenClaw Control UI for Kokoro TTS")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Kokoro voice ID (default: {DEFAULT_VOICE})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Kokoro server port (default: {DEFAULT_PORT})")
    parser.add_argument("--openclaw-dir", default=DEFAULT_OPENCLAW_DIR, help="Path to openclaw/dist directory")
    args = parser.parse_args()

    dist_dir = args.openclaw_dir
    if not os.path.isdir(dist_dir):
        print(f"ERROR: openclaw dist directory not found: {dist_dir}")
        print("Pass --openclaw-dir to specify the correct path.")
        sys.exit(1)

    print(f"OpenClaw dist: {dist_dir}")
    print(f"Voice: {args.voice}  Port: {args.port}")
    print()

    # Patch Control UI JS
    try:
        ui_js = find_control_ui_js(dist_dir)
        print(f"Patching Control UI JS: {os.path.basename(ui_js)}")
        patch_ui_js(ui_js, args.voice, args.port)
        print()
    except Exception as e:
        print(f"ERROR patching Control UI JS: {e}")
        sys.exit(1)

    # Patch CSP JS
    try:
        csp_js = find_csp_js(dist_dir)
        print(f"Patching CSP JS: {os.path.basename(csp_js)}")
        patch_csp_js(csp_js, args.port)
        print()
    except Exception as e:
        print(f"ERROR patching CSP JS: {e}")
        sys.exit(1)

    print("Done. Restart the gateway and hard refresh the Control UI:")
    print("  openclaw gateway restart")
    print("  Ctrl+Shift+R in browser")

if __name__ == "__main__":
    main()
