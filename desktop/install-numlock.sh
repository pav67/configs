#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
user_name=$(id -un)
[[ "$user_name" =~ ^[a-z_][a-z0-9_-]*$ ]] || { echo 'Nom utilisateur non pris en charge.' >&2; exit 1; }
[ "$(id -u)" != 0 ] || { echo 'Lancer sans sudo devant ce script.' >&2; exit 1; }
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
printf '%s ALL=(root) NOPASSWD: /usr/local/libexec/keychron-numlock on, /usr/local/libexec/keychron-numlock off\n' "$user_name" > "$tmp/sudoers"
printf '[General]\nNumlock=off\n' > "$tmp/sddm.conf"
sudo -v
sudo visudo -cf "$tmp/sudoers"
sudo install -d -o root -g root -m 0755 /usr/local/libexec /etc/sddm.conf.d
sudo install -o root -g root -m 0755 "$ROOT/libexec/keychron-numlock" /usr/local/libexec/keychron-numlock
sudo install -o root -g root -m 0440 "$tmp/sudoers" /etc/sudoers.d/keychron-numlock
sudo install -o root -g root -m 0644 "$tmp/sddm.conf" /etc/sddm.conf.d/20-numlock.conf
sudo install -o root -g root -m 0644 "$ROOT/systemd/keychron-numlock-shutdown.service" /etc/systemd/system/keychron-numlock-shutdown.service
sudo systemctl daemon-reload
sudo systemctl enable --now keychron-numlock-shutdown.service
# Test the actual keyboard without locking or closing the session.
trap 'sudo -n /usr/local/libexec/keychron-numlock on || true; rm -rf -- "$tmp"' EXIT
sudo -n /usr/local/libexec/keychron-numlock off
sudo -n /usr/local/libexec/keychron-numlock on
printf '%s\n' 'Verr Num : installation et test off/on réussis.'
