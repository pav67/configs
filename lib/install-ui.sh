#!/usr/bin/env bash
# Bash 3.2-compatible progress UI. Commands stay in the foreground so shell
# state and errexit propagate normally; only the animation runs in a child.
ui_init() {
    local log_dir
    log_dir="${XDG_STATE_HOME:-$HOME/.local/state}/shell-kit"
    mkdir -p "$log_dir"
    chmod 0700 "$log_dir"
    LOG_FILE=$(umask 077; mktemp "$log_dir/install-$(date +%Y%m%d-%H%M%S)-XXXXXX")
    exec 3>&1 4>&2
    UI_TTY=0
    if [ -t 3 ] && [ "${TERM:-dumb}" != dumb ]; then UI_TTY=1; fi
    UI_BLUE='' UI_GREEN='' UI_RED='' UI_DIM='' UI_RESET=''
    if [ "$UI_TTY" = 1 ] && [ "${TERM:-dumb}" != dumb ] && [ -z "${NO_COLOR:-}" ]; then
        UI_BLUE=$'\033[36m' UI_GREEN=$'\033[32m' UI_RED=$'\033[31m'
        UI_DIM=$'\033[2m' UI_RESET=$'\033[0m'
    fi
    UI_STEP='' UI_SPINNER='' UI_COUNT=0 UI_START=$SECONDS UI_STEP_START=$SECONDS
    UI_ERROR_LINE='' UI_HINT='' DOWNLOAD_DIR=''
    UI_FULLSCREEN=0 UI_CANCELLED=0
    UI_DONE=()
    exec >>"$LOG_FILE" 2>&1
    trap 'ui_error "$?" "$LINENO" "$BASH_COMMAND"' ERR
    trap 'ui_exit "$?"' EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    printf '\n%s  SHELL KIT%s\n%s  Ton environnement, prêt à travailler.%s\n\n' \
        "$UI_BLUE" "$UI_RESET" "$UI_DIM" "$UI_RESET" >&3
    printf '  Journal : %s\n\n' "$LOG_FILE" >&3
    log "Début de l'installation"
}

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

ui_stop_spinner() {
    if [ -n "$UI_SPINNER" ]; then
        kill "$UI_SPINNER" 2>/dev/null || :
        wait "$UI_SPINNER" 2>/dev/null || :
        UI_SPINNER=''
    fi
    if [ "$UI_TTY" = 1 ]; then printf '\r\033[K' >&3; fi
}

ui_start_spinner() {
    if [ "$UI_TTY" = 1 ]; then
        (
            trap - EXIT ERR INT
            trap 'exit 0' TERM
            while :; do
                for frame in '⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏'; do
                    printf '\r\033[K  %s%s%s %02d · %s %s(%ss)%s' \
                        "$UI_BLUE" "$frame" "$UI_RESET" "$UI_COUNT" "$UI_STEP" \
                        "$UI_DIM" "$((SECONDS - UI_STEP_START))" "$UI_RESET" >&3
                    sleep 0.12
                done
            done
        ) &
        UI_SPINNER=$!
    else
        printf '  … %02d · %s\n' "$UI_COUNT" "$UI_STEP" >&3
    fi
}

ui_finish_step() {
    ui_stop_spinner
    if [ -n "$UI_STEP" ]; then
        if [ "${UI_FULLSCREEN:-0}" = 1 ]; then
            UI_DONE+=("$UI_STEP ($((SECONDS - UI_STEP_START))s)")
        else
        printf '  %s✓%s %02d · %s %s(%ss)%s\n' "$UI_GREEN" "$UI_RESET" \
            "$UI_COUNT" "$UI_STEP" "$UI_DIM" "$((SECONDS - UI_STEP_START))" "$UI_RESET" >&3
        fi
        log "Étape terminée : $UI_STEP"
    fi
}

step() {
    ui_finish_step
    UI_STEP=$1 UI_STEP_START=$SECONDS
    UI_COUNT=$((UI_COUNT + 1))
    log "Étape $UI_COUNT : $UI_STEP"
    if [ "${UI_FULLSCREEN:-0}" = 1 ]; then
        local i first
        printf '\033[H\033[2J' >&3
        wizard_header
        printf '  INSTALLATION  /  etape %s\n\n' "$UI_COUNT" >&3
        first=$((${#UI_DONE[@]} - 5))
        if [ "$first" -lt 0 ]; then first=0; fi
        for ((i=first; i<${#UI_DONE[@]}; i++)); do
            printf '  %s✓%s %s\n' "$UI_GREEN" "$UI_RESET" "${UI_DONE[$i]}" >&3
        done
        printf '\n' >&3
    fi
    ui_start_spinner
}

# A password prompt must stay visible and must not compete with the spinner.
interactive() {
    ui_stop_spinner
    printf '  ↳ %s\n' "$1" >&3
    shift
    "$@" >&3 2>&4
    ui_start_spinner
}

sudo() {
    if ! command sudo -n -v; then
        interactive 'Authentification sudo requise' command sudo -v
    fi
    command sudo -n "$@"
}

ui_error() {
    local status=$1
    UI_ERROR_LINE=$2
    log "Erreur (code $status), ligne $2 : $3"
}

ui_exit() {
    local status=$1
    trap - EXIT ERR INT TERM
    if [ "${UI_FULLSCREEN:-0}" = 1 ]; then
        ui_stop_spinner
        printf '\033[?1049l' >&3
        UI_FULLSCREEN=0
    fi
    if [ "${UI_CANCELLED:-0}" = 1 ]; then
        printf '  Installation annulee ; aucun composant modifie.\n' >&3
        exit "$status"
    fi
    if [ "$status" -eq 0 ]; then
        ui_finish_step
        printf '\n  %s✓ Installation terminée%s en %ss\n' "$UI_GREEN" "$UI_RESET" "$((SECONDS - UI_START))" >&3
        printf '  Composants : %s\n' "${COMPONENTS:-installation complete}" >&3
    else
        ui_stop_spinner
        printf '\n  %s✗ %s%s — code %s\n' "$UI_RED" "${UI_STEP:-Préparation}" "$UI_RESET" "$status" >&4
        if [ -n "$UI_HINT" ]; then printf '  %s\n' "$UI_HINT" >&4; fi
        if [ -n "$UI_ERROR_LINE" ]; then printf '  Échec à la ligne %s ; détail dans le journal.\n' "$UI_ERROR_LINE" >&4; fi
        log "Installation interrompue (code $status)"
    fi
    printf '  Journal complet : %s\n\n' "$LOG_FILE" >&3
    if [ -n "$DOWNLOAD_DIR" ]; then rm -rf "$DOWNLOAD_DIR" || :; fi
    exit "$status"
}
