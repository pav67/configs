"""Check logging, error propagation, interactive prompts and animation cleanup."""
import errno
import os
from pathlib import Path
import pty
import select
import signal
import subprocess
import tempfile
import time

repo = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    env = {**os.environ, 'HOME': str(root), 'XDG_STATE_HOME': str(root / 'state'), 'TERM': 'xterm-256color'}
    prelude = 'set -Eeuo pipefail\nsource "$1/lib/install-ui.sh"\nui_init\n'

    def run(script):
        return subprocess.run(['bash', '-c', prelude + script, 'test', str(repo)],
                              env=env, capture_output=True, text=True, timeout=10)

    result = run('step "Téléchargement"\necho private-detail\necho private-error >&2\nfalse\necho UNREACHABLE\n')
    assert result.returncode == 1, result
    assert '✗ Téléchargement' in result.stderr and 'Installation terminée' not in result.stdout
    assert 'private-' not in result.stdout + result.stderr
    logs = list((root / 'state/shell-kit').glob('install-*'))
    content = logs[0].read_text()
    assert 'private-detail' in content and 'private-error' in content
    assert 'UNREACHABLE' not in content and 'Erreur (code 1)' in content

    result = run('step "Installation"\n( exit 42 )\necho UNREACHABLE')
    assert result.returncode == 42 and 'code 42' in result.stderr
    result = run('step "Préparation"\nUI_HINT="Homebrew absent"\nexit 7')
    assert result.returncode == 7 and 'Homebrew absent' in result.stderr
    result = run('step "Configuration"\ninteractive "Authentification" printf "PROMPT_VISIBLE\\n"\necho HIDDEN\n')
    assert result.returncode == 0 and 'PROMPT_VISIBLE' in result.stdout
    assert 'HIDDEN' not in result.stdout and 'Installation terminée' in result.stdout

    # Exercise terminal mode and interruption in an independent session.
    for interrupt in [False, True]:
        master, slave = pty.openpty()
        script = prelude + 'step "Animation"\necho LOG_ONLY\nsleep 0.6\n'
        process = subprocess.Popen(['bash', '-c', script, 'test', str(repo)], env=env,
                                   stdin=slave, stdout=slave, stderr=slave, start_new_session=True)
        os.close(slave)
        output = b''
        started = time.monotonic()
        sent = False
        while True:
            assert time.monotonic() - started < 10, 'Animation did not stop'
            if interrupt and not sent and time.monotonic() - started > 0.25:
                os.killpg(process.pid, signal.SIGTERM)
                sent = True
            ready, _, _ = select.select([master], [], [], 0.1)
            if ready:
                try:
                    part = os.read(master, 4096)
                except OSError as exc:
                    if exc.errno != errno.EIO:
                        raise
                    break
                if not part:
                    break
                output += part
        os.close(master)
        status = process.wait(timeout=5)
        text = output.decode()
        assert '\x1b[K' in text and 'LOG_ONLY' not in text
        assert status == (143 if interrupt else 0), (status, text)
        assert ('Installation terminée' in text) != interrupt
        assert 'Journal complet :' in text
print('OK: logs, exit status, failure hints, visible authentication, TTY animation and interruption')
