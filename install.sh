#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="${TMUX_SHARED_SESSION:-shared}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"
SERVICE_FILE="${USER_SYSTEMD_DIR}/tmux-shared.service"
BACKUP_TS="$(date +%Y%m%d-%H%M%S)"

log() {
    printf '[shell-kit] %s\n' "$*"
}

backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        cp -a "$file" "${file}.bak.${BACKUP_TS}"
        log "Sauvegarde : ${file}.bak.${BACKUP_TS}"
    fi
}

if [ "$(id -u)" -eq 0 ]; then
    echo "Ne lance pas ce script en root."
    echo "Lance-le avec l'utilisateur qui utilisera tmux/zsh."
    exit 1
fi

install_packages() {
    log "Installation des dépendances : tmux, vim, zsh, git, curl, python3..."

    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y tmux vim zsh git curl python3
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y tmux vim-enhanced zsh git curl python3
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y tmux vim-enhanced zsh git curl python3
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -Sy --noconfirm tmux vim zsh git curl python
    else
        echo "Gestionnaire de paquets non reconnu."
        echo "Installe manuellement : tmux vim zsh git curl python3"
        exit 1
    fi
}

install_packages

log "Installation de ~/.tmux.conf"
backup_file "${HOME}/.tmux.conf"
install -m 0644 "${SCRIPT_DIR}/tmux.conf" "${HOME}/.tmux.conf"

log "Installation de ~/.vimrc"
backup_file "${HOME}/.vimrc"
install -m 0644 "${SCRIPT_DIR}/vimrc" "${HOME}/.vimrc"

log "Installation de Oh My Zsh"
if [ ! -d "${HOME}/.oh-my-zsh/.git" ]; then
    if [ -e "${HOME}/.oh-my-zsh" ]; then
        mv "${HOME}/.oh-my-zsh" "${HOME}/.oh-my-zsh.bak.${BACKUP_TS}"
    fi
    git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git "${HOME}/.oh-my-zsh"
else
    log "Oh My Zsh est déjà installé, conservation de l'installation existante."
fi

log "Installation du thème Headline"
backup_file "${HOME}/headline.zsh-theme"
install -m 0644 "${SCRIPT_DIR}/headline.zsh-theme" "${HOME}/headline.zsh-theme"

log "Installation de ~/.zshrc"
backup_file "${HOME}/.zshrc"
install -m 0644 "${SCRIPT_DIR}/zshrc" "${HOME}/.zshrc"

append_or_replace_block() {
    local target="$1"
    local snippet="$2"

    touch "$target"

    python3 - "$target" "$snippet" <<'PY'
from pathlib import Path
import sys

target = Path(sys.argv[1])
snippet_file = Path(sys.argv[2])

begin = "# >>> tmux-shared auto-attach >>>"
end = "# <<< tmux-shared auto-attach <<<"

text = target.read_text()
snippet = snippet_file.read_text().strip()

if begin in text and end in text:
    before, rest = text.split(begin, 1)
    _, after = rest.split(end, 1)
    text = before.rstrip() + "\n\n" + snippet + "\n" + after.lstrip("\n")
else:
    text = text.rstrip() + "\n\n" + snippet + "\n"

target.write_text(text)
PY
}

# Garde le comportement pour Bash/sh.
log "Configuration de l'auto-attach SSH dans ~/.profile"
append_or_replace_block "${HOME}/.profile" "${SCRIPT_DIR}/profile-snippet.sh"

# Zsh interactif ne lit pas ~/.profile : on ajoute aussi le bloc à ~/.zshrc.
log "Configuration de l'auto-attach SSH dans ~/.zshrc"
append_or_replace_block "${HOME}/.zshrc" "${SCRIPT_DIR}/profile-snippet.sh"

log "Passage de Zsh comme shell par défaut"
ZSH_BIN="$(command -v zsh)"
CURRENT_SHELL="$(getent passwd "$USER" | cut -d: -f7 || true)"
if [ "$CURRENT_SHELL" != "$ZSH_BIN" ]; then
    sudo chsh -s "$ZSH_BIN" "$USER"
else
    log "Zsh est déjà le shell par défaut."
fi

log "Installation du service systemd utilisateur"
mkdir -p "${USER_SYSTEMD_DIR}"
sed "s/Environment=TMUX_SHARED_SESSION=shared/Environment=TMUX_SHARED_SESSION=${SESSION_NAME}/" \
    "${SCRIPT_DIR}/tmux-shared.service" > "${SERVICE_FILE}"

systemctl --user daemon-reload
systemctl --user enable --now tmux-shared.service

log "Activation du démarrage du service utilisateur dès le boot (linger)"
if command -v loginctl >/dev/null 2>&1; then
    sudo loginctl enable-linger "$USER"
else
    log "loginctl absent : le service utilisateur démarrera au login, pas forcément au boot."
fi

log "Vérification de la session tmux"
tmux has-session -t "${SESSION_NAME}" 2>/dev/null || tmux new-session -d -s "${SESSION_NAME}"

cat <<EOF

Installation terminée.

Shell par défaut :
  ${ZSH_BIN}

Session tmux :
  ${SESSION_NAME}

Fichiers installés :
  ~/.tmux.conf
  ~/.vimrc
  ~/.zshrc
  ~/headline.zsh-theme
  ~/.oh-my-zsh/
  ~/.config/systemd/user/tmux-shared.service

Sauvegardes éventuelles :
  *.bak.${BACKUP_TS}

Commandes utiles :
  tmux attach -t ${SESSION_NAME}
  tmux ls
  systemctl --user status tmux-shared.service
  exec zsh

Bindings tmux supplémentaires :
  F2  : nouvelle fenêtre
  F3  : fenêtre précédente
  F4  : fenêtre suivante
  F10 : tuer la fenêtre courante avec confirmation

NOTE :
  Ton .zshrc active le plugin Oh My Zsh "thefuck".
  Le plugin est chargé, mais la commande "thefuck" doit être installée
  séparément sur les machines où tu souhaites l'utiliser.

Déconnecte/reconnecte ta session SSH pour prendre en compte le shell
par défaut et tomber directement dans la session tmux partagée.
EOF
