#!/usr/bin/env python3
"""Install user configs with HOME expansion and backups; never read credentials."""
from datetime import datetime
from pathlib import Path
import json
import os
import shutil
import sys

root = Path(__file__).resolve().parent
home = Path.home()
backup = datetime.now().strftime('%Y%m%d-%H%M%S') + f'-{os.getpid()}'


def copy(source, target, *, executable=False, preserve=False, binary=False):
    destination = home / target
    if preserve and destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.copy2(destination, str(destination) + '.bak.' + backup)
    if binary:
        shutil.copyfile(root / source, destination)
    else:
        text = (root / source).read_text()
        # Waybar is JSON: HOME may contain a quote or backslash.
        value = json.dumps(str(home), ensure_ascii=False)[1:-1] if source.endswith('.jsonc') else str(home)
        destination.write_text(text.replace('@HOME@', value))
    destination.chmod(0o755 if executable else 0o644)


for name in ('hyprland.conf', 'hyprlock.conf', 'hypridle.conf', 'hyprtoolkit.conf'):
    copy('hypr/' + name, '.config/hypr/' + name)
use_paul_monitors = len(sys.argv) > 1 and sys.argv[1] == '1'
copy('hypr/monitors-paul.conf' if use_paul_monitors else 'hypr/monitors.conf',
     '.config/hypr/monitors.conf', preserve=not use_paul_monitors)
for name in ('config.jsonc', 'style.css', 'session-menu.xml'):
    copy('waybar/' + name, '.config/waybar/' + name)
copy('fuzzel/fuzzel.ini', '.config/fuzzel/fuzzel.ini')
for name in ('capture-ecran', 'ouvrir-navigateur', 'lanceur-applications', 'clipboard-store', 'historique-presse-papiers', 'reunion-audio', 'installer-whisper-reunion'):
    copy('bin/' + name, '.local/bin/' + name, executable=True)
copy('backgrounds/voie-lactee.png', '.local/share/backgrounds/voie-lactee.png', binary=True)
(home / 'Images/Captures').mkdir(parents=True, exist_ok=True)

copy('systemd/clipboard-history.service', '.config/systemd/user/clipboard-history.service')

copy('systemd/reunion-audio.service', '.config/systemd/user/reunion-audio.service')
copy('lib/reunion_audio.py', '.local/lib/reunion_audio.py', executable=True)
copy('reunion-audio/ai.json', '.config/reunion-audio/ai.json', preserve=True)
copy('bin/outlook-flottant', '.local/bin/outlook-flottant', executable=True)
copy('lib/outlook_floating.py', '.local/lib/outlook_floating.py')
copy('applications/thunar.desktop', '.local/share/applications/thunar.desktop')
copy('dbus-1/services/org.xfce.Thunar.service', '.local/share/dbus-1/services/org.xfce.Thunar.service')
copy('dbus-1/services/org.xfce.FileManager.service', '.local/share/dbus-1/services/org.xfce.FileManager.service')
copy('systemd/thunar.service.d/theme.conf', '.config/systemd/user/thunar.service.d/theme.conf')
