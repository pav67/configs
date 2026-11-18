#!/usr/bin/env python3
"""Remote tmux bell queue. Emits identifiers only; never captures pane output."""
import json
import os
from pathlib import Path
import sqlite3
import sys
import time


def connect():
    os.umask(0o077)
    root = Path.home() / '.local/state/tmux-sounds'
    root.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(root / 'events.sqlite', timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, window TEXT, created REAL)')
    return db


def window_key(pid, window):
    if not pid.isdigit() or not window.startswith('@') or not window[1:].isdigit():
        raise ValueError('Invalid tmux window')
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    started = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]
    return f'{boot}:{pid}:{started}:{window}'


def main():
    db = connect()
    if sys.argv[1] == 'emit':
        key = window_key(*sys.argv[2:4])
        with db:
            db.execute('INSERT INTO events(window,created) VALUES (?,?)', (key, time.time()))
            db.execute('DELETE FROM events WHERE id <= (SELECT MAX(id)-1000 FROM events)')
    elif sys.argv[1] == 'follow':
        last = db.execute('SELECT COALESCE(MAX(id),0) FROM events').fetchone()[0]
        print(json.dumps({'ready': True}), flush=True)
        while True:
            for number, key, created in db.execute('SELECT id,window,created FROM events WHERE id>? ORDER BY id', (last,)).fetchall():
                print(json.dumps({'window': key, 'created': created}), flush=True)
                last = number
            time.sleep(.2)
    else:
        raise ValueError('Expected emit or follow')


if __name__ == '__main__':
    main()
