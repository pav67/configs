"""Drive the installed Zsh/plugin stack through a PTY; never execute pasted text.

Requires the workstation's installed Oh My Zsh and zsh-vi-mode.
Usage: python3 tests/check_zsh_keys.py [path/to/zshrc]
"""
import os
from pathlib import Path
import pty
import select
import signal
import sys
import tempfile
import time

rc = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'zshrc').resolve()
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    log = root / 'state'
    (root / '.zshrc').write_text('''source "$TEST_ZSHRC"
PROMPT='KEY_TEST_READY> '
_key_test_state() { print -r -- "$ZVM_MODE|$BUFFER" > "$TEST_STATE"; }
autoload -Uz add-zle-hook-widget
add-zle-hook-widget line-pre-redraw _key_test_state
''')
    pid, fd = pty.fork()
    if pid == 0:
        os.environ.update(ZDOTDIR=tmp, TEST_STATE=str(log), TEST_ZSHRC=str(rc),
                          TERM='xterm-256color', TMUX_AUTO_ATTACH='0')
        os.execvp('zsh', ['zsh', '-d', '-i'])

    def drain(seconds):
        output = b''
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if select.select([fd], [], [], .02)[0]:
                output += os.read(fd, 65536)
        return output

    def check(label, keys, expected):
        os.write(fd, keys)
        drain(.3)
        actual = log.read_text().rstrip('\n')
        assert actual == expected, f'{label}: expected {expected!r}, got {actual!r}'
        print(f'OK: {label}')

    try:
        output = b''
        deadline = time.monotonic() + 15
        while b'KEY_TEST_READY> ' not in output and time.monotonic() < deadline:
            output += drain(.2)
        assert b'KEY_TEST_READY> ' in output, 'Zsh did not reach its prompt'
        drain(.3)
        check('insert text', b'hello', 'i|hello')
        check('Escape enters normal mode', b'\x1b', 'n|hello')
        check('a returns to insertion', b'a', 'i|hello')
        check('Insert preserves text and insertion mode', b'\x1b[2~', 'i|hello')
        check('Shift-Insert sequence is inert', b'\x1b[2;2~', 'i|hello')
        # An extra character completes ZLE paste highlighting and triggers redraw.
        check('bracketed paste preserves case and mode',
              b'\x1b[200~ world\x1b[201~!', 'i|hello world!')
        check('Escape still works after paste', b'\x1b', 'n|hello world!')
        check('append after paste', b'a?', 'i|hello world!?')
        check('unbracketed terminal paste', b' plain', 'i|hello world!? plain')
    finally:
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
        os.close(fd)
