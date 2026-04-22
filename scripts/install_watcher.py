#!/usr/bin/env python3
"""
install_watcher.py — Registers watch_kokoro.py as a Windows Scheduled Task.

Runs at:
  - System startup (with 60s delay to let OpenClaw start first)
  - Every hour (to catch silent auto-updates)

Usage: python install_watcher.py [--voice VOICE] [--port PORT] [--uninstall]
Run as Administrator if you want the task to run even when not logged in.
"""
import sys
import os
import subprocess
import argparse

TASK_NAME  = "KokoroTTSWatcher"
DEFAULT_VOICE = "bf_v0isabella"
DEFAULT_PORT  = 8199


def get_python():
    return sys.executable


def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def install(voice, port):
    python  = get_python()
    watcher = os.path.join(get_script_dir(), "watch_kokoro.py")
    args    = f'--voice {voice} --port {port}'

    # XML task definition — two triggers: startup (delay 1min) + hourly
    xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Re-applies Kokoro TTS patches to OpenClaw after updates.</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Delay>PT60S</Delay>
    </BootTrigger>
    <TimeTrigger>
      <Repetition>
        <Interval>PT1H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2024-01-01T00:00:00</StartBoundary>
    </TimeTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT5M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>{python}</Command>
      <Arguments>"{watcher}" {args}</Arguments>
      <WorkingDirectory>{get_script_dir()}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    xml_path = os.path.join(os.environ.get("TEMP", "."), f"{TASK_NAME}.xml")
    with open(xml_path, "w", encoding="utf-16") as f:
        f.write(xml)

    # Uninstall existing first (ignore errors)
    subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True
    )

    result = subprocess.run(
        ["schtasks", "/Create", "/TN", TASK_NAME, "/XML", xml_path, "/F"],
        capture_output=True, text=True
    )

    try:
        os.unlink(xml_path)
    except Exception:
        pass

    if result.returncode == 0:
        print(f"Scheduled Task '{TASK_NAME}' installed successfully.")
        print(f"  Runs at: startup (60s delay) + every hour")
        print(f"  Voice: {voice}  Port: {port}")
        print(f"  Log: {os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'kokoro-watch.log')}")
        print()
        print("Run now to verify:")
        print(f"  schtasks /Run /TN {TASK_NAME}")
    else:
        print(f"ERROR installing task: {result.stderr or result.stdout}")
        print("Try running as Administrator.")
        sys.exit(1)


def uninstall():
    result = subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"Scheduled Task '{TASK_NAME}' removed.")
    else:
        print(f"Could not remove task (may not exist): {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Install/uninstall Kokoro TTS auto-watcher")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()

    if args.uninstall:
        uninstall()
    else:
        install(args.voice, args.port)


if __name__ == "__main__":
    main()
