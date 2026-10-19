"""Exercise the real native ps/id implementation in a foreground PTY."""
import errno
import os
from pathlib import Path
import pty
import pwd

script = str(Path(__file__).resolve().parents[1] / 'tmux/status-identity.sh')
pid, fd = pty.fork()
if pid == 0:
    os.execv('/bin/sh', ['sh', '-c', 'exec "$1" "$(tty)"', 'sh', script])
output = b''
try:
    while True:
        try:
            part = os.read(fd, 4096)
        except OSError as exc:
            if exc.errno == errno.EIO:
                break
            raise
        if not part:
            break
        output += part
finally:
    os.close(fd)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0, output
user = pwd.getpwuid(os.getuid()).pw_name
assert f']{user}#[' in output.decode(), output
assert output.decode().count('') == 2, output
print('OK: native foreground identity on', os.uname().sysname)
