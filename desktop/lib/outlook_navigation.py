#!/usr/bin/env python3
"""Open the adjacent Outlook message through its parent list, keeping a pop-out."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from outlook_floating import is_outlook_popout


def clients():
    return json.loads(subprocess.check_output(['hyprctl', 'clients', '-j'], text=True, timeout=5))


def dispatch(action, args):
    result = subprocess.run(['hyprctl', 'dispatch', action, args], capture_output=True, text=True, timeout=5)
    if result.returncode or result.stdout.strip() != 'ok':
        raise RuntimeError(result.stderr or result.stdout)


def parent_window(current, windows):
    candidates = [w for w in windows if w.get('class') == 'google-chrome'
                  and w.get('initialTitle') != 'about:blank - Google Chrome'
                  and w.get('title', '').endswith('Outlook - Google Chrome')]
    # Prefer the account identified in the message's title, then its screen.
    parts = current.get('title', '').rsplit(' – ', 2)
    if len(parts) == 3:
        same_account = [w for w in candidates if ' – ' + parts[1] + ' – Outlook' in w.get('initialTitle', '')]
        if same_account:
            candidates = same_account
    if len(candidates) > 1:
        local = [w for w in candidates if w.get('monitor') == current.get('monitor')]
        if local:
            candidates = local
    if len(candidates) != 1:
        raise RuntimeError('Laisse une seule fenêtre principale Outlook ouverte sur la liste des messages.')
    return candidates[0]


def navigate(direction):
    current = json.loads(subprocess.check_output(['hyprctl', 'activewindow', '-j'], text=True, timeout=5))
    if not current.get('address'):
        return
    if not is_outlook_popout(current):
        # Preserve the real Ctrl+< / Ctrl+> in terminals and other applications.
        code = '194' if direction == 'next' else '193'
        dispatch('sendshortcut', 'CTRL,code:' + code + ',address:' + current['address'])
        return
    windows = clients()
    parent = parent_window(current, windows)
    previous = {w['address'] for w in windows}
    selector = 'address:' + parent['address']
    dispatch('sendshortcut', ',' + ('Down' if direction == 'next' else 'Up') + ',' + selector)
    time.sleep(0.25)
    dispatch('sendshortcut', 'SHIFT,Return,' + selector)
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        new = [w for w in clients() if w['address'] not in previous and is_outlook_popout(w)]
        if len(new) == 1:
            replacement = new[0]
            break
        if len(new) > 1:
            raise RuntimeError('Plusieurs fenêtres ont été ouvertes ; le message initial est conservé.')
        time.sleep(0.15)
    else:
        dispatch('focuswindow', 'address:' + current['address'])
        raise RuntimeError('Aucun nouveau message ouvert. Vérifie que la fenêtre principale est sur la liste des emails.')
    # Let the floating-window watcher handle the new title, then retain geometry.
    time.sleep(0.3)
    selector = 'address:' + replacement['address']
    dispatch('setfloating', selector)
    if current.get('floating'):
        width, height = current['size']
        x, y = current['at']
        dispatch('resizewindowpixel', f'exact {width} {height},' + selector)
        dispatch('movewindowpixel', f'exact {x} {y},' + selector)
    dispatch('focuswindow', selector)
    if any(w['address'] == current['address'] for w in clients()):
        dispatch('closewindow', 'address:' + current['address'])
    print('Navigation Outlook terminée.', flush=True)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('next', 'previous'):
        raise RuntimeError('Usage : outlook-navigation next|previous')
    runtime = Path(os.environ['XDG_RUNTIME_DIR'])
    with (runtime / 'outlook-navigation.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        navigate(sys.argv[1])


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        subprocess.run(['notify-send', 'Navigation Outlook', str(exc)], check=False)
        print(str(exc), file=sys.stderr)
        sys.exit(1)
