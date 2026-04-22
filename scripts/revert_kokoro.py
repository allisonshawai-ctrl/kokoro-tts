#!/usr/bin/env python3
"""
revert_kokoro.py — Reverts Kokoro TTS patches from OpenClaw Control UI.

Use this if the page goes blank after patching, or to cleanly undo all changes.

Usage: python revert_kokoro.py [--openclaw-dir DIR]
"""
import sys
import os
import glob
import argparse

DEFAULT_OPENCLAW_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm", "node_modules", "openclaw", "dist")

def find_control_ui_js(dist_dir):
    pattern = os.path.join(dist_dir, "control-ui", "assets", "index-*.js")
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"No Control UI JS found at {pattern}")
    return matches[0]

def find_csp_js(dist_dir):
    pattern = os.path.join(dist_dir, "control-ui-*.js")
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"No CSP JS found at {pattern}")
    return matches[0]

def revert_ui_js(path):
    """Remove _ttsSpeak helper and restore Nb() call."""
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # Remove helper
    helper_start = c.find("function _ttsSpeak(")
    ex_start = c.find("function ex(e){")
    if helper_start >= 0 and helper_start < ex_start:
        c = c[:helper_start] + c[ex_start:]
        print("  Removed _ttsSpeak helper")
    else:
        print("  No _ttsSpeak helper found (already clean)")

    # Restore Nb() call in button if _ttsSpeak(r,n) is present
    old_call = "_ttsSpeak(r,n)"
    original_nb = "Nb(r,{onEnd:()=>{n.isConnected&&(n.classList.remove(`chat-tts-btn--active`),n.title=`Read aloud`)},onError:()=>{n.isConnected&&(n.classList.remove(`chat-tts-btn--active`),n.title=`Read aloud`)}})"
    if old_call in c:
        c = c.replace(old_call, original_nb, 1)
        print("  Restored original Nb() call")
    else:
        print("  Button already uses original Nb() call")

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

def revert_csp_js(path):
    """Restore original connect-src (remove Kokoro additions)."""
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # Remove media-src blob: line
    import re
    # Remove the media-src line added as a separate array entry
    c = re.sub(r',\n\t\t"media-src blob:"', '', c)
    # Restore connect-src to original
    c = re.sub(r'"connect-src \'self\' ws: wss:[^"]*"', '"connect-src \'self\' ws: wss:"', c)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("  Restored original CSP")

def main():
    parser = argparse.ArgumentParser(description="Revert Kokoro TTS patches from OpenClaw")
    parser.add_argument("--openclaw-dir", default=DEFAULT_OPENCLAW_DIR)
    args = parser.parse_args()

    dist_dir = args.openclaw_dir

    print("Reverting Control UI JS...")
    ui_js = find_control_ui_js(dist_dir)
    revert_ui_js(ui_js)

    print("Reverting CSP JS...")
    csp_js = find_csp_js(dist_dir)
    revert_csp_js(csp_js)

    print()
    print("Done. Restart gateway and hard refresh:")
    print("  openclaw gateway restart")
    print("  Ctrl+Shift+R in browser")

if __name__ == "__main__":
    main()
