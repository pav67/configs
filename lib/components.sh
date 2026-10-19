#!/usr/bin/env bash
# Globals are shared with install.sh and the other UI modules.
# shellcheck disable=SC2034
# Explicit choices are separate from dependencies, which are recomputed each time.
COMPONENT_IDS=(zsh tools starship tmux session neovim vim leaf codex default-shell)
COMPONENT_LABELS=(
    'Zsh + Oh My Zsh + plugins Vim/historique'
    'Outils modernes : eza, bat, rg, fd, fzf, lf'
    'Prompt Starship + theme epure'
    'Tmux + bulles utilisateur / hote'
    'Session persistante + attachement automatique'
    'Neovim'
    'Vim + configuration'
    'Leaf : lecteur Markdown'
    'Preferences Codex (sans installer le CLI)'
    'Faire de Zsh le shell par defaut'
)
REQUESTED='' COMPONENTS=''
selected() { case " $COMPONENTS " in *" $1 "*) return 0;; *) return 1;; esac; }
requested() { case " $REQUESTED " in *" $1 "*) return 0;; *) return 1;; esac; }
resolve_components() {
    COMPONENTS=$REQUESTED
    if selected default-shell && ! selected zsh; then COMPONENTS="$COMPONENTS zsh"; fi
    if selected zsh; then
        selected tools || COMPONENTS="$COMPONENTS tools"
    fi
    if selected session && ! selected tmux; then COMPONENTS="$COMPONENTS tmux"; fi
}
parse_components() {
    local input=$1 item known id
    REQUESTED=''
    [ -n "$input" ] || { echo 'Selection vide.' >&2; return 2; }
    case "$input" in ,*|*,|*,,*) echo 'Liste de composants invalide.' >&2; return 2;; esac
    input=${input//,/ }
    for item in $input; do
        known=0
        for id in "${COMPONENT_IDS[@]}"; do [ "$item" != "$id" ] || known=1; done
        [ "$known" = 1 ] || { printf 'Composant inconnu : %s\n' "$item" >&2; return 2; }
        requested "$item" || REQUESTED="$REQUESTED $item"
    done
    resolve_components
}
