#!/usr/bin/env python3
"""Float Outlook pop-outs after Chrome replaces their initial about:blank title."""
import fcntl
import json
import os
from pathlib import Path
import socket
import subprocess
import time


def is_outlook_popout(window):
    return (window.get('initialClass') == 'google-chrome'
            and window.get('initialTitle') == 'about:blank - Google Chrome'
            and window.get('title', '').endswith(' – Outlook - Google Chrome'))


def dispatch(action, args):
    result = subprocess.run(['hyprctl', 'dispatch', action, args],
                            capture_output=True, text=True, timeout=5)
    if result.returncode or result.stdout.strip() != 'ok':
        raise RuntimeError(result.stderr or result.stdout)


def update(seen):
    windows = json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], text=True, timeout=5))
    seen.intersection_update(w['address'] for w in windows)
    for window in windows:
        address = window['address']
        if address in seen or not is_outlook_popout(window):
            continue
        # Respect subsequent manual resizing/tiling by handling each window once.
        if not window['floating']:
            selector = 'address:' + address
            dispatch('setfloating', selector)
            dispatch('resizewindowpixel', 'exact 1100 900,' + selector)
            monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j'], text=True, timeout=5))
            monitor = next((m for m in monitors if m['id'] == window['monitor']), None)
            if monitor:
                width = min(1100, int(monitor['width'] / monitor['scale']) - 80)
                height = min(900, int(monitor['height'] / monitor['scale']) - 100)
                x = monitor['x'] + (int(monitor['width'] / monitor['scale']) - width) // 2
                y = monitor['y'] + (int(monitor['height'] / monitor['scale']) - height) // 2
                dispatch('resizewindowpixel', f'exact {width} {height},' + selector)
                dispatch('movewindowpixel', f'exact {x} {y},' + selector)
        seen.add(address)


def main():
    runtime = Path(os.environ['XDG_RUNTIME_DIR'])
    signature = os.environ['HYPRLAND_INSTANCE_SIGNATURE']
    with (runtime / ('outlook-floating-' + signature + '.lock')).open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        path = runtime / 'hypr' / signature / '.socket2.sock'
        seen = set()
        while path.exists():
            try:
                with socket.socket(socket.AF_UNIX) as connection:
                    connection.connect(str(path))
                    update(seen)
                    with connection.makefile('r') as events:
                        for event in events:
                            if event.startswith(('openwindow>>', 'windowtitle>>', 'windowtitlev2>>', 'closewindow>>')):
                                update(seen)
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
                print(str(exc), flush=True)
                time.sleep(1)


if __name__ == '__main__':
    main()
