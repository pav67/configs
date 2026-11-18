"""Manual Wayland integration check: python3 tests/check_clipboard_ui.py.

Requires GTK bindings and gtk-layer-shell; opens synthetic content for 1 second.
Never reads or writes the user's clipboard or history.
"""
from pathlib import Path
import os
import json
import subprocess
import struct
import sys
import tempfile
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'desktop/lib'))
from clipboard_picker import Picker, GLib, Gtk


def chunk(kind, data):
    return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))


png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', struct.pack('!IIBBBBB', 500, 240, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress((b'\0' + b'\x89\xb4\xfa' * 500) * 240))
       + chunk(b'IEND', b''))
failures = []
with tempfile.TemporaryDirectory() as directory:
    os.environ['XDG_DATA_HOME'] = directory
    picker = Picker([], [b'Texte court', b'Ligne 1\nLigne 2\nLigne 3', png])

    def check():
        try:
            monitors = json.loads(subprocess.check_output(['hyprctl', 'monitors', '-j']))
            focused = next(m['name'] for m in monitors if m['focused'])
            layers = json.loads(subprocess.check_output(['hyprctl', 'layers', '-j']))
            assert any(layer.get('namespace') == 'clipboard-history'
                       for group in layers[focused]['levels'].values() for layer in group)
            rows = picker.list.get_children()
            heights = [r.get_allocated_height() for r in rows]
            viewport = picker.list.get_parent().get_allocation().height
            assert heights[0] < heights[1] < heights[2], heights
            assert viewport >= sum(heights), (viewport, heights)
            image = rows[2].get_child().get_children()[0].get_children()[0]
            assert image.get_pixbuf() is not None
            assert image.get_allocated_height() >= 150
            print(f'Window {picker.window.get_size()}, viewport {viewport}, row heights {heights}: OK')
        except Exception as error:
            failures.append(error)
        finally:
            picker.window.destroy()
        return False

    GLib.timeout_add(1000, check)
    Gtk.main()
if failures:
    raise failures[0]
