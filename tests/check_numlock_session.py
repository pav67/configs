#!/usr/bin/env python3
"""Verify session hooks using mock commands; never lock, reboot, or touch hardware."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp);tools=base/'bin';tools.mkdir();log=base/'events'
    for name in ['sudo','hyprlock','systemctl','hyprctl','flock']:
        p=tools/name
        p.write_text('#!/bin/sh\nprintf "%s\\n" "'+name+' $*" >> "$TEST_LOG"\n'+('exit "${TEST_LOCK_EXIT:-0}"\n' if name=='hyprlock' else 'exit 0\n'))
        p.chmod(0o755)
    env=dict(os.environ,PATH=str(tools)+os.pathsep+os.environ['PATH'],XDG_RUNTIME_DIR=tmp,TEST_LOG=str(log))
    subprocess.run(['bash',str(root/'desktop/bin/verrouiller-session')],env=env,check=True)
    events=log.read_text().splitlines()
    assert events[1:]==['sudo -n /usr/local/libexec/keychron-numlock off','hyprlock ','sudo -n /usr/local/libexec/keychron-numlock on'],events
    log.write_text('')
    r=subprocess.run(['bash',str(root/'desktop/bin/verrouiller-session')],env=dict(env,TEST_LOCK_EXIT='1'))
    assert r.returncode==1 and 'keychron-numlock on' not in log.read_text()
    for action,target in [('logout','hyprctl dispatch exit'),('reboot','systemctl reboot'),('shutdown','systemctl poweroff')]:
        log.write_text('')
        subprocess.run(['bash',str(root/'desktop/bin/session-action'),action],env=env,check=True)
        assert log.read_text().splitlines()==['sudo -n /usr/local/libexec/keychron-numlock off',target]
print('Num Lock ordering for lock/unlock/logout/reboot/shutdown and failed lock: OK')
