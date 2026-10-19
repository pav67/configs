"""Exercise Linux/macOS installs without modifying the real HOME or services."""
from pathlib import Path
import os
import plistlib
import subprocess
import tempfile
import tomllib

repo = Path(__file__).resolve().parents[1]
for name in ['starship.toml', 'codex-config.toml']:
    tomllib.loads((repo / name).read_text())

for platform, gui in [('Linux', True), ('Darwin', True), ('Darwin', False)]:
    with tempfile.TemporaryDirectory(prefix='configs-test-') as tmp:
        root = Path(tmp)
        home = root / 'home with spaces & accents é'
        home.mkdir()
        bin_dir = root / 'bin'
        bin_dir.mkdir()
        log = root / 'commands'
        commands = {name: 'exit 0' for name in [
            'apt-get', 'sudo', 'systemctl', 'loginctl', 'tmux', 'leaf', 'starship',
            'eza', 'rg', 'fzf', 'lf', 'nvim', 'chsh',
        ]}
        commands['sudo'] = '[ "${TEST_FAIL:-}" != "$*" ] || { echo PACKAGE_FAILED >&2; exit 42; }'
        commands.update({
            'uname': 'echo "$TEST_OS"',
            'id': 'echo 1000',
            'dscl': 'echo "UserShell: /bin/zsh"',
            'getent': 'echo "tester:x:1000:1000::/tmp:/bin/zsh"',
            'brew': '[ "$1" != shellenv ] || echo "export HOMEBREW_PREFIX=/test/homebrew"',
            'launchctl': '[ "$TEST_GUI" = yes ]',
            'git': 'echo CLONE_DETAIL; echo CLONE_STDERR >&2; for dest do :; done\nmkdir -p "$dest/.git"',
            'curl': 'echo "Unexpected download" >&2; exit 1',
        })
        for name, body in commands.items():
            path = bin_dir / name
            path.write_text('#!/bin/sh\nprintf "%s %s\\n" "${0##*/}" "$*" >> "$TEST_LOG"\n' + body + '\n')
            path.chmod(0o755)
        env = {**os.environ, 'HOME': str(home), 'PATH': str(bin_dir) + ':' + os.environ['PATH'],
               'TMUX_SHARED_SESSION': 'custom-test', 'TEST_OS': platform,
               'TEST_GUI': 'yes' if gui else 'no', 'TEST_LOG': str(log), 'XDG_STATE_HOME': str(home / '.local/state')}
        (home / '.profile').write_text('# personal profile\n')
        (home / '.codex').mkdir()
        (home / '.codex/config.toml').write_text('# existing config\n')
        for _ in range(2):
            result = subprocess.run(['bash', str(repo / 'install.sh')], env=env, capture_output=True, text=True)
            assert result.returncode == 0, result.stdout + result.stderr
        assert 'CLONE_DETAIL' not in result.stdout + result.stderr
        assert 'Journal complet :' in result.stdout
        assert '\x1b' not in result.stdout  # redirected output never animates
        logs = list((home / '.local/state/shell-kit').glob('install-*'))
        assert len(logs) == 2
        assert all(path.stat().st_mode & 0o777 == 0o600 for path in logs)
        assert any('CLONE_DETAIL' in path.read_text() and 'CLONE_STDERR' in path.read_text() for path in logs)
        for name in ['.profile', '.zshrc']:
            data = (home / name).read_text()
            assert data.count('# >>> tmux-shared auto-attach >>>') == 1
            assert '${TMUX_SHARED_SESSION:-custom-test}' in data
        assert '# personal profile' in (home / '.profile').read_text()
        assert (home / '.codex/config.toml').stat().st_mode & 0o777 == 0o600
        assert any(p.read_text() == '# existing config\n' for p in (home / '.codex').glob('*.bak.*'))
        assert (home / '.config/tmux/status-identity.sh').stat().st_mode & 0o777 == 0o755
        assert (home / '.config/starship.toml').read_bytes() == (repo / 'starship.toml').read_bytes()
        calls = log.read_text()
        if platform == 'Linux':
            assert 'Environment=TMUX_SHARED_SESSION=custom-test' in (home / '.config/systemd/user/tmux-shared.service').read_text()
            assert 'systemctl --user enable --now' in calls
            assert 'brew ' not in calls and 'launchctl ' not in calls
        else:
            plist = home / 'Library/LaunchAgents/net.pav67.tmux-shared.plist'
            config = plistlib.loads(plist.read_bytes())
            assert config['ProgramArguments'] == ['/bin/sh', str(home / '.config/tmux/start-shared.sh'), str(bin_dir / 'tmux'), 'custom-test']
            assert config['RunAtLoad'] and config['AbandonProcessGroup']
            assert config['EnvironmentVariables']['HOME'] == str(home)
            assert config['EnvironmentVariables']['SHELL'] == '/bin/zsh'
            assert not config.get('KeepAlive')
            assert 'brew install tmux' in calls and 'leaf-markdown-viewer' in calls
            assert 'systemctl ' not in calls and 'loginctl ' not in calls and 'getent ' not in calls
            assert ('launchctl bootstrap gui/1000' in calls) == gui
            assert ('launchctl bootout gui/1000/net.pav67.tmux-shared' in calls) == gui
        if platform == 'Linux':
            failed = subprocess.run(['bash', str(repo / 'install.sh')],
                                    env={**env, 'TEST_FAIL': '-n apt-get update'},
                                    capture_output=True, text=True)
            assert failed.returncode == 42, failed.stdout + failed.stderr
            assert 'Installation des dépendances' in failed.stderr
            assert 'PACKAGE_FAILED' not in failed.stdout + failed.stderr
            assert 'Installation terminée' not in failed.stdout
            assert 'Configuration de Starship et Codex' not in failed.stdout
        print(f'OK: {platform}, GUI={gui}, repeated install, backups, service, paths with spaces')
