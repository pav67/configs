#!/usr/bin/env bash
set -euo pipefail

OS="$(uname -s)"
SESSION_NAME="${TMUX_SHARED_SESSION:-shared}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"
SERVICE_FILE="${USER_SYSTEMD_DIR}/tmux-shared.service"
BACKUP_TS="$(date +%Y%m%d-%H%M%S)-$$"
export PATH="$HOME/.local/bin:$PATH"
[[ "$SESSION_NAME" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "Nom de session invalide" >&2; exit 1; }

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
    log "Installation des dépendances : tmux, vim, neovim, zsh et outils shell..."

    if [ "$OS" = Darwin ]; then
        # Both standard prefixes; an existing custom brew in PATH takes priority.
        if ! command -v brew >/dev/null 2>&1; then
            for prefix in /opt/homebrew /usr/local; do
                if [ -x "$prefix/bin/brew" ]; then
                    eval "$("$prefix/bin/brew" shellenv)"
                    break
                fi
            done
        fi
        if ! command -v brew >/dev/null 2>&1; then
            log "Homebrew requis : installe-le depuis https://brew.sh puis relance ./install.sh"
            exit 1
        fi
        eval "$(brew shellenv)"
        brew install tmux vim neovim zsh git curl python fzf fd bat ripgrep eza lf diffutils starship leaf-markdown-viewer
    elif command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y tmux vim neovim zsh git curl python3 procps ca-certificates tar xz-utils unzip less diffutils fzf fd-find bat ripgrep eza lf
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y tmux vim-enhanced neovim zsh git curl python3 procps-ng ca-certificates tar xz unzip less diffutils fzf fd-find bat ripgrep eza lf
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y tmux vim-enhanced neovim zsh git curl python3 procps-ng ca-certificates tar xz unzip less diffutils fzf fd-find bat ripgrep eza lf
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -Syu --needed --noconfirm tmux vim neovim zsh git curl python procps-ng ca-certificates tar xz unzip less diffutils fzf fd bat ripgrep eza lf
    else
        echo "Gestionnaire de paquets non reconnu."
        echo "Installe manuellement : tmux vim neovim zsh git curl python3 procps ca-certificates tar xz-utils unzip less diffutils fzf fd-find bat ripgrep eza lf"
        exit 1
    fi
}

install_packages

DOWNLOAD_DIR="$(mktemp -d)"
trap 'rm -rf "$DOWNLOAD_DIR"' EXIT
mkdir -p "$HOME/.local/bin"
if ! command -v starship >/dev/null 2>&1; then
    log "Installation de Starship"
    curl -fsSL https://starship.rs/install.sh -o "$DOWNLOAD_DIR/starship.sh"
    sh "$DOWNLOAD_DIR/starship.sh" --yes --bin-dir "$HOME/.local/bin"
fi
if ! command -v leaf >/dev/null 2>&1; then
    log "Installation de Leaf (RivoLink/leaf)"
    curl -fsSL https://raw.githubusercontent.com/RivoLink/leaf/main/scripts/install.sh -o "$DOWNLOAD_DIR/leaf.sh"
    sh "$DOWNLOAD_DIR/leaf.sh" "$HOME/.local/bin"
fi

for tool in eza rg fzf lf nvim starship leaf; do
    command -v "$tool" >/dev/null || { log "Dépendance manquante : $tool"; exit 1; }
done

for target in .config/starship.toml .codex/config.toml; do
    mkdir -p "$HOME/$(dirname "$target")"
    backup_file "$HOME/$target"
done
install -m 0644 "$SCRIPT_DIR/starship.toml" "$HOME/.config/starship.toml"
install -m 0600 "$SCRIPT_DIR/codex-config.toml" "$HOME/.codex/config.toml"

log "Installation de l’identité tmux"
mkdir -p "$HOME/.config/tmux"
backup_file "$HOME/.config/tmux/status-identity.sh"
install -m 0755 "$SCRIPT_DIR/tmux/status-identity.sh" "$HOME/.config/tmux/status-identity.sh"

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

log "Installation des plugins Zsh"
for plugin in zsh-vi-mode zsh-autosuggestions; do
    case "$plugin" in
        zsh-vi-mode) repo=jeffreytse/zsh-vi-mode ;;
        zsh-autosuggestions) repo=zsh-users/zsh-autosuggestions ;;
    esac
    destination="$HOME/.oh-my-zsh/custom/plugins/$plugin"
    if [ ! -d "$destination" ]; then
        git clone --depth=1 "https://github.com/$repo.git" "$destination"
    fi
done
# git et history-substring-search sont fournis par Oh My Zsh.

log "Installation de ~/.zshrc"
backup_file "${HOME}/.zshrc"
install -m 0644 "${SCRIPT_DIR}/zshrc" "${HOME}/.zshrc"

append_or_replace_block() {
    local target="$1"
    local snippet="$2"

    touch "$target"

    TMUX_SHARED_SESSION="$SESSION_NAME" python3 - "$target" "$snippet" <<'PY'
from pathlib import Path
import sys

target = Path(sys.argv[1])
snippet_file = Path(sys.argv[2])

begin = "# >>> tmux-shared auto-attach >>>"
end = "# <<< tmux-shared auto-attach <<<"

text = target.read_text()
snippet = snippet_file.read_text().strip()
import os
snippet = snippet.replace("${TMUX_SHARED_SESSION:-shared}", "${TMUX_SHARED_SESSION:-" + os.environ["TMUX_SHARED_SESSION"] + "}")

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
backup_file "${HOME}/.profile"
append_or_replace_block "${HOME}/.profile" "${SCRIPT_DIR}/profile-snippet.sh"

# Zsh interactif ne lit pas ~/.profile : on ajoute aussi le bloc à ~/.zshrc.
log "Configuration de l'auto-attach SSH dans ~/.zshrc"
append_or_replace_block "${HOME}/.zshrc" "${SCRIPT_DIR}/profile-snippet.sh"

log "Passage de Zsh comme shell par défaut"
ZSH_BIN="$(command -v zsh)"
if [ "$OS" = Darwin ]; then
    # /bin/zsh is already in /etc/shells; no system allowlist changes required.
    ZSH_BIN=/bin/zsh
    CURRENT_SHELL="$(dscl . -read "/Users/$USER" UserShell | awk '{print $2}')"
    if [ "$CURRENT_SHELL" != "$ZSH_BIN" ]; then
        chsh -s "$ZSH_BIN"
    fi

    log "Installation du LaunchAgent tmux (ouverture de session macOS)"
    SERVICE_FILE="$HOME/Library/LaunchAgents/net.pav67.tmux-shared.plist"
    mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
    backup_file "$SERVICE_FILE"
    backup_file "$HOME/.config/tmux/start-shared.sh"
    install -m 0755 "$SCRIPT_DIR/tmux/start-shared.sh" "$HOME/.config/tmux/start-shared.sh"
    python3 - "$SERVICE_FILE" "$(command -v tmux)" "$SESSION_NAME" "$PATH" <<'PLIST'
import plistlib, sys
from pathlib import Path
home = Path.home()
config = {
    "Label": "net.pav67.tmux-shared",
    "ProgramArguments": ["/bin/sh", str(home / ".config/tmux/start-shared.sh"), sys.argv[2], sys.argv[3]],
    "EnvironmentVariables": {"PATH": sys.argv[4], "HOME": str(home), "SHELL": "/bin/zsh"},
    "WorkingDirectory": str(home),
    "RunAtLoad": True,
    # tmux forks its server. Let it survive the short-lived launcher.
    "AbandonProcessGroup": True,
    "StandardOutPath": str(home / "Library/Logs/tmux-shared.log"),
    "StandardErrorPath": str(home / "Library/Logs/tmux-shared.log"),
}
with open(sys.argv[1], "wb") as target:
    plistlib.dump(config, target)
PLIST
    DOMAIN="gui/$(id -u)"
    if launchctl print "$DOMAIN" >/dev/null 2>&1; then
        if launchctl print "$DOMAIN/net.pav67.tmux-shared" >/dev/null 2>&1; then
            launchctl bootout "$DOMAIN/net.pav67.tmux-shared"
        fi
        launchctl bootstrap "$DOMAIN" "$SERVICE_FILE"
    else
        log "Pas de session graphique : LaunchAgent activé à la prochaine connexion graphique."
    fi
    SERVICE_STATUS="launchctl print $DOMAIN/net.pav67.tmux-shared"
else
    CURRENT_SHELL="$(getent passwd "$USER" | cut -d: -f7 || true)"
    if [ "$CURRENT_SHELL" != "$ZSH_BIN" ]; then
        sudo chsh -s "$ZSH_BIN" "$USER"
    fi
    log "Installation du service systemd utilisateur"
    mkdir -p "${USER_SYSTEMD_DIR}"
    backup_file "$SERVICE_FILE"
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

    SERVICE_STATUS="systemctl --user status tmux-shared.service"
fi

log "Vérification de la session tmux"
tmux has-session -t "=${SESSION_NAME}" 2>/dev/null || \
    tmux new-session -d -s "${SESSION_NAME}" || tmux has-session -t "=${SESSION_NAME}"

cat <<EOF

Installation terminée.

Shell par défaut :
  ${ZSH_BIN}

Session tmux :
  ${SESSION_NAME}

Fichiers installés :
  ~/.tmux.conf
  ~/.config/tmux/status-identity.sh
  ~/.vimrc
  ~/.zshrc
  ~/.config/starship.toml
  ~/.codex/config.toml
  ~/.oh-my-zsh/
  ${SERVICE_FILE}

Sauvegardes éventuelles :
  *.bak.${BACKUP_TS}

Commandes utiles :
  tmux attach -t ${SESSION_NAME}
  tmux ls
  ${SERVICE_STATUS}
  exec zsh

Bindings tmux supplémentaires :
  F2  : nouvelle fenêtre
  F3  : fenêtre précédente
  F4  : fenêtre suivante
  F10 : tuer la fenêtre courante avec confirmation

Starship et Leaf déjà présents sont conservés.
Codex CLI et OpenCode : installation/authentification séparées.
Sélectionne une Nerd Font dans ton terminal pour afficher les icônes.

Déconnecte/reconnecte ta session SSH pour prendre en compte le shell
par défaut et tomber directement dans la session tmux partagée.
EOF
