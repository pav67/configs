from pathlib import Path
import tempfile, os, subprocess, tomllib
repo=Path(__file__).resolve().parents[1]
for name in ['starship.toml','codex-config.toml']:
    tomllib.loads((repo/name).read_text())
with tempfile.TemporaryDirectory(prefix='configs-test-') as tmp:
    root=Path(tmp); home=root/'home'; home.mkdir(); bin=root/'bin'; bin.mkdir()
    # Only mutate a disposable HOME. Replace privileged/network/session operations.
    for name in ['sudo','systemctl','loginctl','tmux','leaf','starship','eza','rg','fzf','lf','nvim']:
        (bin/name).write_text('#!/bin/sh\nexit 0\n')
    (bin/'git').write_text('#!/bin/sh\nfor dest do :; done\nmkdir -p "$dest/.git"\n')
    (bin/'curl').write_text('#!/bin/sh\nwhile [ "$1" != "-o" ]; do shift; done\nprintf "#!/bin/sh\\nexit 0\\n" > "$2"\n')
    for p in bin.iterdir(): p.chmod(0o755)
    env={**os.environ,'HOME':str(home),'PATH':str(bin)+':'+os.environ['PATH'],'TMUX_SHARED_SESSION':'custom-test'}
    (home/'.profile').write_text('# personal profile\n')
    (home/'.codex').mkdir(); (home/'.codex/config.toml').write_text('# existing config\n')
    for _ in range(2):
        subprocess.run(['bash',str(repo/'install.sh')],env=env,check=True,stdout=subprocess.DEVNULL)
    for name in ['.profile','.zshrc']:
        data=(home/name).read_text()
        assert data.count('# >>> tmux-shared auto-attach >>>') == 1
        assert '${TMUX_SHARED_SESSION:-custom-test}' in data
    assert '# personal profile' in (home/'.profile').read_text()
    assert 'Environment=TMUX_SHARED_SESSION=custom-test' in (home/'.config/systemd/user/tmux-shared.service').read_text()
    assert (home/'.codex/config.toml').stat().st_mode & 0o777 == 0o600
    assert any(p.read_text()=='# existing config\n' for p in (home/'.codex').glob('*.bak.*'))
    assert (home/'.config/starship.toml').read_bytes()==(repo/'starship.toml').read_bytes()
    print('OK: TOML, installation isolée répétée, sauvegardes, permissions, session personnalisée, blocs uniques')
