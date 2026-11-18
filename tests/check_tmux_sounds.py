import importlib.util
from pathlib import Path
import tempfile
import wave
import hashlib
import json

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sounds', root / 'desktop/lib/tmux_sounds.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    m.generate_sounds(directory)
    paths = list(directory.glob('*.wav'))
    assert len(paths) == 20
    assert len({hashlib.sha256(p.read_bytes()).digest() for p in paths}) == 20
    for path in paths:
        with wave.open(str(path)) as audio:
            assert audio.getnchannels() == 1
            assert .2 < audio.getnframes() / audio.getframerate() < 1
    mapping = {}
    for i in range(20):
        number = m.assign_sound(mapping, str(i))
        assert number == m.assign_sound(mapping, str(i))
    assert len(set(mapping.values())) == 20
    assert 1 <= m.assign_sound(mapping, '21') <= 20
    target = directory / 'state/assignments.json'
    m.save_mapping(target, mapping)
    loaded = json.loads(target.read_text())
    assert loaded == mapping
    assert m.assign_sound(loaded, '0') == mapping['0']
print('20 distinct short WAVs, stable random assignments, persistence and pool exhaustion: OK')
