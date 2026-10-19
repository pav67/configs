"""Check interactive-only attachment on Linux/macOS, without a real tmux server."""
from pathlib import Path
import os
import pty
import subprocess
import tempfile

snippet = Path(__file__).resolve().parents[1] / 'profile-snippet.sh'
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    log = root / 'calls'
    for name, body in {
        'uname': 'echo "$TEST_OS"',
        'tmux': 'echo "$*" >> "$TEST_LOG"',
    }.items():
        path = root / name
        path.write_text('#!/bin/sh\n' + body + '\n')
        path.chmod(0o755)
    for platform, ssh, nested, enabled, interactive, tty, expected in [
        ('Darwin', '', '', '1', True, True, True),
        ('Linux', '', '', '1', True, True, False),
        ('Linux', '/dev/pts/1', '', '1', True, True, True),
        ('Darwin', '', 'already', '1', True, True, False),
        ('Darwin', '', '', '0', True, True, False),
        ('Darwin', '/dev/ttys001', '', '1', False, True, False),
        ('Darwin', '', '', '1', True, False, False),
    ]:
        log.write_text('')
        env = {**os.environ, 'PATH': str(root) + ':' + os.environ['PATH'],
               'TEST_OS': platform, 'TEST_LOG': str(log), 'TMUX': nested,
               'SSH_TTY': ssh, 'TMUX_AUTO_ATTACH': enabled, 'TMUX_SHARED_SESSION': 'test-session'}
        master, slave = pty.openpty()
        try:
            subprocess.run(['zsh', '-dfi' if interactive else '-df', '-c', 'source "$1"', 'test', str(snippet)],
                           env=env, stdin=slave if tty else subprocess.DEVNULL,
                           stdout=slave if tty else subprocess.DEVNULL,
                           stderr=subprocess.PIPE, check=True, timeout=10)
        finally:
            os.close(slave)
            os.close(master)
        assert bool(log.read_text()) == expected, (platform, ssh, nested, enabled, interactive, tty)
        if expected:
            assert log.read_text().strip() == 'new-session -A -s test-session'
print('OK: local macOS, Linux SSH, nested session, opt-out and noninteractive exclusions')
