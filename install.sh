#!/usr/bin/env bash
set -Eeuo pipefail

OS="$(uname -s)"
SESSION_NAME="${TMUX_SHARED_SESSION:-shared}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"
SERVICE_FILE="${USER_SYSTEMD_DIR}/tmux-shared.service"
BACKUP_TS="$(date +%Y%m%d-%H%M%S)-$$"
export PATH="$HOME/.local/bin:$PATH"
# shellcheck source=lib/components.sh
source "$SCRIPT_DIR/lib/components.sh"
# shellcheck source=lib/wizard.sh
source "$SCRIPT_DIR/lib/wizard.sh"
# shellcheck source=lib/install-ui.sh
source "$SCRIPT_DIR/lib/install-ui.sh"
MODE=wizard
while [ "$#" -gt 0 ]; do
    case "$1" in
        --all) MODE="batch"; REQUESTED="${COMPONENT_IDS[*]}"; shift;;
        --components)
            [ "$#" -ge 2 ] || { echo "--components attend une liste separee par des virgules" >&2; exit 2; }
            parse_components "$2"; MODE="batch"; shift 2;;
        --list) printf '%s\n' "${COMPONENT_IDS[@]}"; exit 0;;
        --help|-h)
            printf '%s\n' './install.sh : wizard plein ecran' './install.sh --all : tout installer sans wizard' './install.sh --components zsh,starship,tmux : selection explicite' './install.sh --list : identifiants disponibles'
            exit 0;;
        *) echo "Option inconnue : $1" >&2; exit 2;;
    esac
done
if [ "$MODE" = wizard ] && { [ ! -t 0 ] || [ ! -t 1 ] || [ "${TERM:-dumb}" = dumb ]; }; then
    echo "Un terminal interactif est requis. Utilise --all ou --components pour automatiser." >&2
    exit 2
fi
ui_init
[[ "$SESSION_NAME" =~ ^[a-zA-Z0-9_-]+$ ]] || { UI_HINT="Nom de session invalide"; exit 1; }
if [ "$(id -u)" -eq 0 ]; then
    UI_HINT="Utilise le compte qui utilisera le kit, pas root."; exit 1
fi
if [ "$MODE" = wizard ]; then
    REQUESTED="${COMPONENT_IDS[*]}"
    wizard
fi
resolve_components
log "Composants explicites : $REQUESTED ; plan effectif : $COMPONENTS"

backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        cp -a "$file" "${file}.bak.${BACKUP_TS}"
        log "Sauvegarde : ${file}.bak.${BACKUP_TS}"
    fi
}

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

install_packages() {
    local manager prefix
    if [ "$OS" = Darwin ]; then
        if ! command -v brew >/dev/null 2>&1; then
            for prefix in /opt/homebrew /usr/local; do
                if [ -x "$prefix/bin/brew" ]; then eval "$("$prefix/bin/brew" shellenv)"; break; fi
            done
        fi
        if ! command -v brew >/dev/null 2>&1; then
            UI_HINT="Installe Homebrew depuis https://brew.sh puis relance le kit."; exit 1
        fi
        eval "$(brew shellenv)"
        manager=brew; packages=(python)
    elif command -v apt-get >/dev/null 2>&1; then
        manager=apt; packages=(python3)
    elif command -v dnf >/dev/null 2>&1; then
        manager=dnf; packages=(python3)
    elif command -v yum >/dev/null 2>&1; then
        manager=yum; packages=(python3)
    elif command -v pacman >/dev/null 2>&1; then
        manager=pacman; packages=(python)
    else
        UI_HINT="Gestionnaire de paquets non reconnu."; exit 1
    fi
    if selected zsh; then packages+=(zsh git); fi
    if selected tools; then
        packages+=(fzf bat ripgrep eza lf less diffutils)
        case "$manager" in apt|dnf|yum) packages+=(fd-find);; *) packages+=(fd);; esac
    fi
    if selected tmux; then
        packages+=(tmux)
        case "$manager" in apt) packages+=(procps);; dnf|yum|pacman) packages+=(procps-ng);; esac
    fi
    if selected neovim; then packages+=(neovim); fi
    if selected vim; then
        case "$manager" in dnf|yum) packages+=(vim-enhanced);; *) packages+=(vim);; esac
    fi
    if [ "$manager" = brew ]; then
        if selected starship; then packages+=(starship); fi
        if selected leaf; then packages+=(leaf-markdown-viewer); fi
    elif selected starship || selected leaf; then
        packages+=(curl ca-certificates tar unzip)
        if [ "$manager" = apt ]; then packages+=(xz-utils); else packages+=(xz); fi
    fi
    case "$manager" in
        brew) brew install "${packages[@]}";;
        apt) sudo apt-get update; sudo apt-get install -y "${packages[@]}";;
        dnf|yum) sudo "$manager" install -y "${packages[@]}";;
        pacman) sudo pacman -Syu --needed --noconfirm "${packages[@]}";;
    esac
}

copy_config() {
    local source=$1 target=$2 mode=${3:-0644}
    mkdir -p "$(dirname "$target")"
    backup_file "$target"
    install -m "$mode" "$SCRIPT_DIR/$source" "$target"
}

step "Installation des dependances selectionnees"
install_packages
DOWNLOAD_DIR="$(mktemp -d)"
mkdir -p "$HOME/.local/bin"
if selected starship; then
    step "Prompt Starship"
    if ! command -v starship >/dev/null 2>&1; then
        curl -fsSL https://starship.rs/install.sh -o "$DOWNLOAD_DIR/starship.sh"
        sh "$DOWNLOAD_DIR/starship.sh" --yes --bin-dir "$HOME/.local/bin"
    fi
    copy_config starship.toml "$HOME/.config/starship.toml"
fi
if selected leaf; then
    step "Lecteur Markdown Leaf"
    if ! command -v leaf >/dev/null 2>&1; then
        curl -fsSL https://raw.githubusercontent.com/RivoLink/leaf/main/scripts/install.sh -o "$DOWNLOAD_DIR/leaf.sh"
        sh "$DOWNLOAD_DIR/leaf.sh" "$HOME/.local/bin"
    fi
fi
if selected codex; then
    step "Preferences Codex"
    copy_config codex-config.toml "$HOME/.codex/config.toml" 0600
fi
if selected tmux; then
    step "Tmux et identite reseau"
    copy_config tmux/status-identity.sh "$HOME/.config/tmux/status-identity.sh" 0755
    copy_config tmux.conf "$HOME/.tmux.conf"
fi
if selected vim; then
    step "Configuration Vim"
    copy_config vimrc "$HOME/.vimrc"
fi
if selected zsh; then
step "Installation de Oh My Zsh"
if [ ! -d "${HOME}/.oh-my-zsh/.git" ]; then
    if [ -e "${HOME}/.oh-my-zsh" ]; then
        mv "${HOME}/.oh-my-zsh" "${HOME}/.oh-my-zsh.bak.${BACKUP_TS}"
    fi
    git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git "${HOME}/.oh-my-zsh"
else
    log "Oh My Zsh est déjà installé, conservation de l'installation existante."
fi

step "Installation des plugins Zsh"
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

step "Installation de ~/.zshrc"
backup_file "${HOME}/.zshrc"
install -m 0644 "${SCRIPT_DIR}/zshrc" "${HOME}/.zshrc"

# Session is opt-in; do not ship the embedded auto-attach block when omitted.
    if ! selected session; then
        python3 - "$HOME/.zshrc" <<'STRIP'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text()
a = s.index("# >>> tmux-shared auto-attach >>>")
b = s.index("# <<< tmux-shared auto-attach <<<") + len("# <<< tmux-shared auto-attach <<<")
p.write_text(s[:a] + s[b:])
STRIP
    fi
fi

if selected session; then
# Garde le comportement pour Bash/sh.
step "Configuration de l'auto-attach SSH dans ~/.profile"
backup_file "${HOME}/.profile"
append_or_replace_block "${HOME}/.profile" "${SCRIPT_DIR}/profile-snippet.sh"

# Zsh interactif ne lit pas ~/.profile : on ajoute aussi le bloc à ~/.zshrc.
log "Configuration de l'auto-attach SSH dans ~/.zshrc"
append_or_replace_block "${HOME}/.zshrc" "${SCRIPT_DIR}/profile-snippet.sh"

fi

if selected default-shell; then
    step "Shell de connexion Zsh"
    ZSH_BIN="$(command -v zsh)"
    if [ "$OS" = Darwin ]; then
        ZSH_BIN=/bin/zsh
        CURRENT_SHELL="$(dscl . -read "/Users/$USER" UserShell | awk '{print $2}')"
        if [ "$CURRENT_SHELL" != "$ZSH_BIN" ]; then
            interactive "Changement du shell de connexion" chsh -s "$ZSH_BIN"
        fi
    else
        CURRENT_SHELL="$(getent passwd "$USER" | cut -d: -f7 || true)"
        if [ "$CURRENT_SHELL" != "$ZSH_BIN" ]; then sudo chsh -s "$ZSH_BIN" "$USER"; fi
    fi
fi

if selected session; then
if [ "$OS" = Darwin ]; then
    step "Installation du LaunchAgent tmux (ouverture de session macOS)"
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
else
    step "Installation du service systemd utilisateur"
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

fi

step "Vérification de la session tmux"
tmux has-session -t "=${SESSION_NAME}" 2>/dev/null || \
    tmux new-session -d -s "${SESSION_NAME}" || tmux has-session -t "=${SESSION_NAME}"

fi

step "Verification des composants"
for component in $COMPONENTS; do
    case "$component" in
        zsh) command -v zsh;;
        tools) for tool in eza rg fzf lf; do command -v "$tool"; done;;
        starship|tmux|leaf|vim) command -v "$component";;
        neovim) command -v nvim;;
    esac
done
log "Installation terminee. Selection : $COMPONENTS"
log "Sauvegardes : *.bak.$BACKUP_TS"
