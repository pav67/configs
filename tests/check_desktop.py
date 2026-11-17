#!/usr/bin/env python3
"""Exercise deployment and reinstallation without packages or a graphical session."""
import configparser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='desktop-') as tmp:
    home = Path(tmp)
    env = dict(os.environ, HOME=tmp)
    def install(monitors='0'):
        subprocess.run(['python3', str(root / 'desktop/install-configs.py'), monitors], env=env, check=True)
    install()
    if sys.platform.startswith('linux'):
        subprocess.run(['bash', str(root / 'desktop/install.sh'), '--configure-only'], env=env, check=True)
    hypr = home / '.config/hypr'
    config = (hypr / 'hyprland.conf').read_text()
    assert 'kb_file' not in config and 'swap_alt' not in config
    assert 'kb_layout = fr' in config and 'kb_options =' in config
    assert 'monitor = , preferred, auto, auto' in (hypr / 'monitors.conf').read_text()
    assert str(home) in config and '/home/paul' not in config
    waybar = json.loads((home / '.config/waybar/config.jsonc').read_text())
    assert waybar['modules-left'] == ['wlr/taskbar']
    assert waybar['wlr/taskbar']['all-outputs'] is False
    assert 'custom/reunion' in waybar['modules-right']
    assert (home / '.local/lib/reunion_audio.py').exists()
    assert (home / '.config/systemd/user/reunion-audio.service').exists()
    ET.parse(home / '.config/waybar/session-menu.xml')
    for name in ('capture-ecran', 'ouvrir-navigateur', 'lanceur-applications', 'clipboard-store', 'historique-presse-papiers', 'reunion-audio', 'installer-whisper-reunion'):
        assert (home / '.local/bin' / name).stat().st_mode & 0o111
    fuzzel = configparser.ConfigParser(interpolation=None)
    fuzzel.read(home / '.config/fuzzel/fuzzel.ini')
    assert fuzzel.getint('main', 'horizontal-pad') >= 20
    assert fuzzel.getint('main', 'vertical-pad') >= 20
    assert (home / '.config/systemd/user/clipboard-history.service').exists()
    assert 'bind = $mainMod SHIFT, V, togglefloating,' in config
    assert 'bind = $mainMod, V, exec,' in config
    assert 'hyprlauncher' not in config
    assert (home / '.local/share/backgrounds/voie-lactee.png').read_bytes().startswith(b'\x89PNG')
    (hypr / 'monitors.conf').write_text('local monitor rules\n')
    install()
    assert (hypr / 'monitors.conf').read_text() == 'local monitor rules\n'
    assert list(hypr.glob('hyprland.conf.bak.*'))
    install('1')
    monitors = (hypr / 'monitors.conf').read_text()
    assert monitors.index('DP-7') < monitors.index('DP-4') < monitors.index('DP-6')
    for p in home.rglob('*'):
        if p.is_file():
            assert b'@HOME@' not in p.read_bytes(), p
print('Desktop deployment, backups and monitor selection: OK')
