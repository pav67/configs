"""Check identity colors, foreground/root selection and safe tmux output."""
from pathlib import Path
import os
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="tmux-theme-") as temp:
    bin_dir = Path(temp)
    commands = {
        "hostname": '#!/bin/sh\nprintf "%s\\n" "$TEST_HOST"\n',
        "ps": '#!/bin/sh\nprintf "%s\\n" "$TEST_PROCESSES"\n',
    }
    for name, content in commands.items():
        path = bin_dir / name
        path.write_text(content)
        path.chmod(0o755)

    def render(host, processes):
        env = {
            **os.environ,
            "PATH": str(bin_dir) + ":" + os.environ["PATH"],
            "TEST_HOST": host,
            "TEST_PROCESSES": processes,
        }
        return subprocess.check_output(
            [str(repo / "tmux/status-identity.sh"), "/dev/pts/42"],
            env=env, text=True,
        )

    colors = {
        "klcentral": "#89b4fa", "codexops": "#a6e3a1",
        "ainode": "#cba6f7", "debian-containers": "#89dceb",
        "kl-ca": "#f9e2af", "infra-core": "#fab387",
        "kl-clients01": "#f5c2e7", "other": "#a6adc8",
    }
    for host, color in colors.items():
        output = render(host, "alice 100 100\nroot 200 100")
        assert f"fg={color},bold]{host}" in output
        assert " alice" in output and " root" not in output
    assert "fg=#f38ba8,bg=default,bold] root" in render(
        "codexops", "alice 100 200\nroot 200 200"
    )
    assert " ?" in render("codexops", "")
    assert "#[bg=red]" not in render("bad#[bg=red]", "alice 100 100")
print("OK: host palette, foreground user, root, missing pane, style escaping")
