#!/usr/bin/env python3
"""
watch_kokoro.py — Auto-healer for Kokoro TTS patches.

Checks whether the Kokoro patch is still applied. If OpenClaw updated and
overwrote the patched files, re-applies the patch and restarts the gateway.

Designed to run as a Windows Scheduled Task (at startup + hourly).

Usage: python watch_kokoro.py [--voice VOICE] [--port PORT] [--openclaw-dir DIR] [--dry-run]
"""
import sys
import os
import glob
import subprocess
import argparse
import datetime

DEFAULT_VOICE        = "bf_v0isabella"
DEFAULT_PORT         = 8199
DEFAULT_OPENCLAW_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm", "node_modules", "openclaw", "dist")
LOG_FILE             = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "kokoro-watch.log")

PATCH_MARKER         = "function _ttsSpeak("
CSP_MARKER           = "media-src blob:"


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def find_file(pattern):
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def is_ui_patched(dist_dir):
    path = find_file(os.path.join(dist_dir, "control-ui", "assets", "index-*.js"))
    if not path:
        return False, "UI JS not found"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if PATCH_MARKER in content:
        return True, os.path.basename(path)
    return False, os.path.basename(path)


def is_csp_patched(dist_dir):
    # Find the file with connect-src
    for path in glob.glob(os.path.join(dist_dir, "control-ui-*.js")):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "connect-src" in content:
            return CSP_MARKER in content, os.path.basename(path)
    return False, "CSP JS not found"


def resolve_openclaw_cmd():
    """Find openclaw executable."""
    candidates = [
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm", "openclaw.cmd"),
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm", "openclaw"),
        "openclaw",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return "openclaw"


def apply_patch(dist_dir, voice, port, dry_run):
    patch_script = os.path.join(os.path.dirname(__file__), "patch_kokoro.py")
    if not os.path.isfile(patch_script):
        log(f"ERROR: patch_kokoro.py not found at {patch_script}")
        return False

    cmd = [sys.executable, patch_script,
           "--voice", voice,
           "--port", str(port),
           "--openclaw-dir", dist_dir,
           "--no-interactive"]

    if dry_run:
        log(f"DRY RUN: would run: {' '.join(cmd)}")
        return True

    log("Applying Kokoro TTS patch...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.stdout:
            for line in result.stdout.strip().splitlines():
                log(f"  {line}")
        if result.returncode != 0:
            log(f"  patch_kokoro.py exited with code {result.returncode}")
            if result.stderr:
                log(f"  stderr: {result.stderr[:200]}")
            return False
        return True
    except Exception as e:
        log(f"ERROR running patch: {e}")
        return False


def restart_gateway(dry_run):
    openclaw = resolve_openclaw_cmd()
    cmd = [openclaw, "gateway", "restart"]
    if dry_run:
        log(f"DRY RUN: would run: {' '.join(cmd)}")
        return
    log("Restarting OpenClaw gateway...")
    try:
        subprocess.run(cmd, timeout=15, capture_output=True)
        log("Gateway restart signal sent.")
    except Exception as e:
        log(f"WARNING: could not restart gateway: {e}")


def main():
    parser = argparse.ArgumentParser(description="Auto-healer for Kokoro TTS patches")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--openclaw-dir", default=DEFAULT_OPENCLAW_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Check only, don't patch")
    args = parser.parse_args()

    dist_dir = args.openclaw_dir

    if not os.path.isdir(dist_dir):
        log(f"openclaw dist not found: {dist_dir} — skipping")
        sys.exit(0)

    ui_ok, ui_file   = is_ui_patched(dist_dir)
    csp_ok, csp_file = is_csp_patched(dist_dir)

    if ui_ok and csp_ok:
        log(f"Patch OK ({ui_file}, {csp_file}) — nothing to do.")
        sys.exit(0)

    if not ui_ok:
        log(f"UI patch missing in {ui_file} — OpenClaw may have updated.")
    if not csp_ok:
        log(f"CSP patch missing in {csp_file}.")

    patched = apply_patch(dist_dir, args.voice, args.port, args.dry_run)
    if patched and not args.dry_run:
        restart_gateway(args.dry_run)
        log("Re-patch complete.")
    elif args.dry_run:
        log("Dry run complete — no changes made.")
    else:
        log("Re-patch failed — manual intervention needed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
