#!/usr/bin/env python3
"""Clipboard contents, persistent pins and automatic paste."""
from pathlib import Path
import json
import os
import subprocess
import hashlib
import base64
import tempfile
import time


def run(args, **kwargs):
    return subprocess.run(args, stdout=subprocess.PIPE, check=True, **kwargs)


def active_window():
    try:
        return json.loads(run(['hyprctl', 'activewindow', '-j'], timeout=2).stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        return {}


def paste_to_window(window):
    address = window.get('address')
    if not address:
        return
    # Closing the overlay may restore another window under the pointer.
    # Restore the original target, then wait for the compositor to confirm it.
    subprocess.run(['hyprctl', 'dispatch', 'focuswindow', f'address:{address}'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
    for _ in range(20):
        time.sleep(0.05)
        if active_window().get('address') == address:
            break
    else:
        return
    modifiers = 'CTRL SHIFT' if window.get('class', '').lower() == 'kitty' else 'CTRL'
    subprocess.run(['hyprctl', 'dispatch', 'sendshortcut',
                    f'{modifiers},v,address:{address}'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)


def active_monitor(window):
    try:
        monitors = json.loads(run(['hyprctl', 'monitors', '-j'], timeout=2).stdout)
        return next((m for m in monitors if m['id'] == window.get('monitor')),
                    next((m for m in monitors if m.get('focused')), None))
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def mime_type(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    return 'text/plain;charset=utf-8'


def pin_directory():
    return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'clipboard-pins'


def content_id(data):
    return hashlib.sha256(data).hexdigest()


def set_pin(data, pinned):
    directory = pin_directory()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / (content_id(data) + '.json')
    if not pinned:
        path.unlink(missing_ok=True)
        return
    # Persist the contents, not a cliphist ID that can expire.
    fd, temporary = tempfile.mkstemp(dir=directory, prefix='.pin-')
    try:
        with os.fdopen(fd, 'w') as output:
            json.dump({'data': base64.b64encode(data).decode('ascii')}, output)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_pins():
    pins = []
    for path in sorted(pin_directory().glob('*.json')):
        try:
            data = base64.b64decode(json.loads(path.read_text())['data'], validate=True)
            if path.stem == content_id(data):
                pins.append(data)
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return pins


def copy_content(data):
    # Do not pipe stdout/stderr: the background wl-copy owner inherits them.
    args = ['wl-copy']
    kind = mime_type(data)
    if kind.startswith('image/'):
        args += ['--type', kind]
    subprocess.run(args, input=data, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=True)


def main():
    from clipboard_picker import choose
    window = active_window()
    entries = run(['cliphist', 'list']).stdout.splitlines()
    data = choose(entries, read_pins(), window)
    if data is not None:
        copy_content(data)
        paste_to_window(window)


if __name__ == '__main__':
    main()
