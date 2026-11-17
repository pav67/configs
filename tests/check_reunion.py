#!/usr/bin/env python3
"""Capture synthetic sources, stop gracefully, verify WAVs and offline output."""
import array
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import wave

SCRIPT = Path(__file__).resolve().parents[1] / 'desktop/lib/reunion_audio.py'
with tempfile.TemporaryDirectory(prefix='reunion-test-') as tmp:
    home = Path(tmp)
    tools = home / 'tools'
    tools.mkdir()
    def executable(name, text):
        p = tools / name
        p.write_text('#!' + sys.executable + '\n' + text)
        p.chmod(0o755)
    executable('notify-send', 'pass\n')
    executable('fuzzel', 'import sys; sys.exit(1)\n')
    executable('pactl', '''import sys,json
if 'get-default-source' in sys.argv: print('micro')
elif 'get-default-sink' in sys.argv: print('casque')
else: print(json.dumps([{'name':'casque.monitor'}]))
''')
    executable('parec', '''import sys,time,struct
value = 1000 if '--device=micro' in sys.argv else 2000
while True:
 sys.stdout.buffer.write(struct.pack('<h',value)*1600)
 sys.stdout.buffer.flush()
 time.sleep(.1)
''')
    env = dict(os.environ, HOME=tmp, PATH=str(tools)+os.pathsep+os.environ['PATH'])
    proc = subprocess.Popen([sys.executable, str(SCRIPT), 'record'], env=env)
    try:
        for _ in range(100):
            if (home/'.local/state/reunion-audio/recording.json').exists(): break
            if proc.poll() is not None: raise AssertionError('Recorder exited early')
            time.sleep(.05)
        else: raise AssertionError('No recording state')
        time.sleep(.5)
        proc.send_signal(signal.SIGINT)
        assert proc.wait(timeout=15) == 0
    finally:
        if proc.poll() is None: proc.kill(); proc.wait()
    last=json.loads((home/'.local/state/reunion-audio/last.json').read_text())
    directory=Path(last['directory'])
    assert not (home/'.local/state/reunion-audio/recording.json').exists()
    assert directory.stat().st_mode & 0o077 == 0
    for filename, expected in [('micro.wav',1000),('interlocuteurs.wav',2000),('reunion.wav',1500)]:
        with wave.open(str(directory/filename)) as audio:
            assert audio.getframerate()==16000 and audio.getnchannels()==1
            assert audio.getnframes()>1000
            data=array.array('h',audio.readframes(1000))
            if sys.byteorder!='little': data.byteswap()
            assert all(v==expected for v in data),filename
    # Exercise transcript/export handling without downloading a model in CI.
    binary=home/'.local/opt/whisper.cpp/build/bin/whisper-cli'
    binary.parent.mkdir(parents=True)
    binary.write_text('#!'+sys.executable+'''\nimport sys,pathlib
p=pathlib.Path(sys.argv[sys.argv.index('-of')+1])
p.with_suffix('.txt').write_text('Bonjour, réunion de test.\\n')
p.with_suffix('.srt').write_text('1\\n00:00:00,000 --> 00:00:01,000\\nBonjour\\n')
''')
    binary.chmod(0o755)
    subprocess.run([sys.executable,str(SCRIPT),'transcribe',str(directory)],env=env,check=True)
    assert 'Bonjour' in (directory/'transcription.md').read_text()
    assert not (home/'.local/state/reunion-audio/transcription.json').exists()
print('Synthetic two-source capture, clean stop, WAV mixing and transcript exports: OK')
