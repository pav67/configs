#!/usr/bin/env python3
"""Play a stable randomly assigned cue per remote tmux window."""
import argparse
import array
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time
import wave

SOUND_COUNT = 20


def generate_sounds(directory):
    directory.mkdir(parents=True, exist_ok=True)
    rate = 24000
    patterns = [(0,), (0, 7), (7, 0), (0, 4, 7), (12, 7, 0)]
    for number in range(SOUND_COUNT):
        target = directory / f'{number + 1:02d}.wav'
        if target.exists():
            continue
        group, pattern = divmod(number, 5)
        samples = array.array('h')
        for note in patterns[pattern]:
            frequency = (392, 523.25, 659.25, 880)[group] * 2 ** (note / 12)
            duration = .15 if len(patterns[pattern]) > 1 else .32
            for index in range(int(rate * duration)):
                t = index / rate
                envelope = min(1, t / .008) * math.exp(-t * 10) * min(1, (duration - t) / .02)
                value = math.sin(2 * math.pi * frequency * t)
                value += .18 * math.sin(2 * math.pi * frequency * (2 + group * .5) * t)
                samples.append(int(5500 * envelope * value))
            samples.extend([0] * int(rate * .045))
        if sys.byteorder != 'little':
            samples.byteswap()
        with wave.open(str(target), 'wb') as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(rate)
            output.writeframes(samples.tobytes())


def assign_sound(mapping, key):
    if key not in mapping:
        available = sorted(set(range(1, SOUND_COUNT + 1)) - set(mapping.values()))
        mapping[key] = random.SystemRandom().choice(available or list(range(1, SOUND_COUNT + 1)))
    return mapping[key]


def save_mapping(path, mapping):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.sounds-')
    try:
        with os.fdopen(fd, 'w') as output:
            json.dump(mapping, output, indent=2)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='codexops@192.168.80.120')
    parser.add_argument('--preview', type=int, choices=range(1, SOUND_COUNT + 1))
    args = parser.parse_args()
    sounds = Path.home() / '.local/share/tmux-sounds'
    generate_sounds(sounds)
    if args.preview:
        subprocess.run(['paplay', str(sounds / f'{args.preview:02d}.wav')], check=True)
        return
    path = Path.home() / '.local/state/tmux-sounds/assignments.json'
    mapping = json.loads(path.read_text()) if path.exists() else {}
    last_played = {}
    command = ['ssh', '-F', '/dev/null', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
               '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=2', args.host,
               'python3 .local/lib/tmux-sound-events.py follow']
    with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as connection:
        try:
            for line in connection.stdout:
                event = json.loads(line)
                if event.get('ready'):
                    print('Sound relay connected', flush=True)
                    continue
                key = args.host + '/' + event['window']
                # Coalesce duplicate alerts from windows linked to several sessions.
                now = time.monotonic()
                if now - last_played.get(key, -10) < .5 or time.time() - event['created'] > 10:
                    continue
                last_played[key] = now
                number = assign_sound(mapping, key)
                save_mapping(path, mapping)
                subprocess.run(['paplay', str(sounds / f'{number:02d}.wav')], timeout=5, check=True)
                print(f"Window {event['window'].rsplit(':', 1)[-1]}: sound {number:02d}", flush=True)
        finally:
            connection.terminate()
            connection.wait(timeout=5)
    raise SystemExit(1)  # systemd reconnects after an SSH disconnect.


if __name__ == '__main__':
    main()
