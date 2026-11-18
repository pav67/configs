#!/usr/bin/env python3
"""Verify streamed Whisper percentages and legacy timestamp estimation."""
from pathlib import Path
import runpy
import tempfile
import wave
import sys

module=runpy.run_path(str(Path(__file__).resolve().parents[1]/'desktop/lib/reunion_audio.py'))
g=module['transcribe'].__globals__
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);state=root/'state';state.mkdir()
    meeting=root/'meeting';meeting.mkdir()
    binary=root/'whisper'
    binary.write_text('#!'+sys.executable+'''\nimport sys,pathlib
assert '-pp' in sys.argv
for percent in (10, 42, 40, 100):
 print(f'whisper_print_progress_callback: progress = {percent:3d}%',file=sys.stderr,flush=True)
p=pathlib.Path(sys.argv[sys.argv.index('-of')+1])
p.with_suffix('.txt').write_text('Test terminé.')
''')
    binary.chmod(0o755)
    g.update(STATE=state,WHISPER=binary,notify=lambda *_:None)
    updates=[];original_save=g['save']
    def save(name,data):
        original_save(name,data)
        if name=='transcription.json':
            updates.append(data['progress'])
            assert g['transcription_progress']()[0]==f'✎ {data["progress"]} %'
    g['save']=save
    g['transcribe'](meeting)
    assert updates==[0,10,42,42,99,100],updates
    assert not (state/'transcription.json').exists()
    with wave.open(str(meeting/'reunion.wav'),'wb') as w:
        w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(b'\0\0'*16000*10)
    original_save('transcription.json',{'directory':str(meeting)})
    (meeting/'whisper.log').write_text('[00:00:00.000 --> 00:00:04.200] Test\n')
    assert g['transcription_progress']()[0]=='✎ ≈ 42 %'
    (meeting/'whisper.log').write_text('Chargement du modèle\n')
    assert g['transcription_progress']()[0]=='✎ Transcription'
print('Streaming progress, monotonic percentages, completion cleanup and legacy estimation: OK')
