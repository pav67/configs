"""Drive the real Bash terminal wizard through a PTY; no installation occurs."""
import errno
import fcntl
import os
from pathlib import Path
import pty
import select
import struct
import subprocess
import tempfile
import termios
import time

repo = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    for keys, expected in [(b'q', None), (b'n \n\n', 'zsh tools'), (b'njj \nrn jj \n\n', 'starship')]:
        # Last scenario uses j/j to navigate, returns from summary, then reselects.
        if expected == 'starship':
            keys = b'njj \nrn \n\n'
        output_file = root / 'selection'
        output_file.unlink(missing_ok=True)
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack('HHHH', 24, 80, 0, 0))
        script = '''set -Eeuo pipefail
source "$1/lib/components.sh"
source "$1/lib/wizard.sh"
source "$1/lib/install-ui.sh"
OS=Linux
ui_init
REQUESTED="${COMPONENT_IDS[*]}"
wizard
printf '%s' "$COMPONENTS" > "$2"
step "Test sans installation"
'''
        proc = subprocess.Popen(['bash', '-c', script, 'test', str(repo), str(output_file)],
                                stdin=slave, stdout=slave, stderr=slave,
                                env={**os.environ, 'HOME': str(root), 'XDG_STATE_HOME': str(root / 'state'), 'TERM': 'xterm-256color'})
        os.close(slave)
        output = b''
        sent = False
        deadline = time.monotonic() + 10
        try:
            while True:
                assert time.monotonic() < deadline, output.decode(errors='replace')
                if not sent and b'Q : quitter' in output:
                    os.write(master, keys)
                    sent = True
                ready, _, _ = select.select([master], [], [], 0.1)
                if not ready:
                    continue
                try:
                    chunk = os.read(master, 65536)
                except OSError as exc:
                    if exc.errno == errno.EIO:
                        break
                    raise
                if not chunk:
                    break
                output += chunk
        finally:
            os.close(master)
            if proc.poll() is None:
                proc.wait(timeout=2)
        assert proc.returncode == 0, output.decode(errors='replace')
        assert b'\x1b[?1049h' in output and b'\x1b[?1049l' in output
        if expected is None:
            assert not output_file.exists()
            assert b'annulee' in output
        else:
            assert output_file.read_text().split() == expected.split(), output_file.read_text()
            assert b'RECAPITULATIF' in output
    rejected = subprocess.run(['bash', str(repo / 'install.sh')], capture_output=True)
    assert rejected.returncode == 2 and b'--all' in rejected.stderr
    invalid = subprocess.run(['bash', str(repo / 'install.sh'), '--components', 'unknown'], capture_output=True)
    assert invalid.returncode == 2
print('OK: wizard selection, automatic dependencies, back, cancel, terminal restoration and CLI validation')
