"""Clipboard persistence and paste behavior; no desktop or real clipboard needed."""
import importlib.util
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import subprocess
import tempfile
import os
import stat

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('history', root / 'desktop/lib/clipboard_history.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
png = b'\x89PNG\r\n\x1a\nTEST'
text = 'Texte\navec accents : été'.encode()

with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'XDG_DATA_HOME': directory}):
    m.set_pin(png, True)
    m.set_pin(text, True)
    m.set_pin(png, True)
    assert set(m.read_pins()) == {png, text}
    assert len(list(m.pin_directory().glob('*.json'))) == 2
    for path in m.pin_directory().glob('*.json'):
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
    # Contents survive independently of cliphist, including binary images.
    (m.pin_directory() / 'broken.json').write_text('{broken')
    assert set(m.read_pins()) == {png, text}
    m.set_pin(png, False)
    assert m.read_pins() == [text]
    m.set_pin(png, False)

with patch.object(m.subprocess, 'run') as copy:
    m.copy_content(png)
    assert copy.call_args.args[0] == ['wl-copy', '--type', 'image/png']
    assert copy.call_args.kwargs['input'] == png
    assert copy.call_args.kwargs['stdout'] == subprocess.DEVNULL

window = {'address': '0x123', 'class': 'google-chrome'}
for selected in (png, None):
    chooser = SimpleNamespace(choose=lambda *_: selected)
    with patch.dict('sys.modules', {'clipboard_picker': chooser}), \
         patch.object(m, 'active_window', return_value=window), \
         patch.object(m, 'read_pins', return_value=[png]), \
         patch.object(m, 'run', return_value=SimpleNamespace(stdout=b'')), \
         patch.object(m, 'copy_content') as copy, \
         patch.object(m, 'paste_to_window') as paste:
        m.main()
        if selected is None:
            copy.assert_not_called()
            paste.assert_not_called()
        else:
            copy.assert_called_once_with(png)
            paste.assert_called_once_with(window)

with patch.object(m, 'active_window', return_value={'address': '0x456'}), patch.object(m.subprocess, 'run') as dispatch:
    m.paste_to_window(window)
    dispatch.assert_not_called()
for app, modifiers in [('kitty', 'CTRL SHIFT'), ('google-chrome', 'CTRL')]:
    with patch.object(m, 'active_window', return_value=window), patch.object(m.subprocess, 'run') as dispatch:
        m.paste_to_window({**window, 'class': app})
        assert dispatch.call_args.args[0][-1] == modifiers + ',v,address:0x123'

# A failed clipboard copy must preserve the successful capture on disk.
with tempfile.TemporaryDirectory() as directory:
    temp_home = Path(directory)
    binary = temp_home / 'bin'
    binary.mkdir()
    for name, body in {'grim': 'printf png > "$1"', 'wl-copy': 'exit 1', 'notify-send': 'exit 0'}.items():
        path = binary / name
        path.write_text('#!/bin/sh\n' + body + '\n')
        path.chmod(0o755)
    subprocess.run([str(root / 'desktop/bin/capture-ecran')],
                   env={**os.environ, 'HOME': directory, 'PATH': str(binary) + ':' + os.environ['PATH']}, check=True)
    assert list((temp_home / 'Images/Captures').glob('*.png'))
print('Persistent pins, binary copy, cancellation, targeted paste, capture preservation: OK')
