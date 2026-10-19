#!/usr/bin/env bash
# Globals are shared with install.sh and the other UI modules.
# shellcheck disable=SC2034
wizard_header() {
    printf '%s' "$UI_BLUE" >&3
    cat >&3 <<'ART'
   ____  _   _ _____ _     _       _  _____ _____
  / ___|| | | | ____| |   | |     | |/ /_ _|_   _|
  \___ \| |_| |  _| | |   | |     | ' / | |  | |
   ___) |  _  | |___| |___| |___  | . \ | |  | |
  |____/|_| |_|_____|_____|_____| |_|\_\___| |_|  v2
ART
    printf '%s\n' "$UI_RESET" >&3
}
wizard_size() {
    local size
    size=$(stty size 2>/dev/null || printf '24 80')
    read -r WIZ_ROWS WIZ_COLS <<< "$size"
    [ "${WIZ_ROWS:-0}" -ge 24 ] && [ "${WIZ_COLS:-0}" -ge 70 ]
}
wizard_draw() {
    local i mark cursor
    printf '\033[H\033[2J' >&3
    if ! wizard_size; then
        printf '  Agrandis le terminal a 70 colonnes x 24 lignes.\n  Q : quitter sans installer.\n' >&3
        return
    fi
    wizard_header
    printf '  COMPOSANTS  /  %s\n  [x] choisi   [+] dependance automatique   [ ] ignore\n\n' "$OS" >&3
    for ((i=0; i<${#COMPONENT_IDS[@]}; i++)); do
        mark=' '; cursor=' '
        if requested "${COMPONENT_IDS[$i]}"; then mark=x
        elif selected "${COMPONENT_IDS[$i]}"; then mark=+
        fi
        if [ "$i" = "$WIZ_INDEX" ]; then cursor='>'; printf '%s' "$UI_BLUE" >&3; fi
        printf ' %s [%s] %s%s\n' "$cursor" "$mark" "${COMPONENT_LABELS[$i]}" "$UI_RESET" >&3
    done
    printf '\n  Fleches/j/k : naviguer   Espace : cocher   A : tout\n  N : rien   Entree : recapitulatif   Q : quitter\n' >&3
}
wizard_confirm() {
    local i key
    printf '\033[H\033[2J' >&3
    wizard_header
    printf '  RECAPITULATIF — %s\n\n' "$OS" >&3
    for ((i=0; i<${#COMPONENT_IDS[@]}; i++)); do
        if selected "${COMPONENT_IDS[$i]}"; then
            printf '  + %s\n' "${COMPONENT_LABELS[$i]}" >&3
        fi
    done
    printf '\n  Sauvegarde avant remplacement. Les elements ignores restent en place.\n' >&3
    printf '  Entree : installer   R : revenir   Q : quitter\n' >&3
    while IFS= read -r -s -n 1 key; do
        case "$key" in
            '') return 0;;
            r|R|$'\033') return 1;;
            q|Q) UI_CANCELLED=1; exit 0;;
        esac
    done
    UI_CANCELLED=1; exit 0
}
wizard() {
    local key rest item
    WIZ_INDEX=0 UI_FULLSCREEN=1
    printf '\033[?1049h' >&3
    trap 'WIZ_RESIZED=1; wizard_draw' WINCH
    while :; do
        resolve_components
        wizard_draw
        WIZ_RESIZED=0
        if ! IFS= read -r -s -n 1 key; then
            if [ "$WIZ_RESIZED" = 1 ]; then continue; fi
            UI_CANCELLED=1; exit 0
        fi
        case "$key" in
            q|Q) UI_CANCELLED=1; exit 0;;
            $'\033')
                rest=''; IFS= read -r -s -n 2 -t 1 rest || :
                case "$rest" in '[A') key=k;; '[B') key=j;; *) continue;; esac;;
        esac
        if ! wizard_size; then continue; fi
        case "$key" in
            k) WIZ_INDEX=$(((WIZ_INDEX + ${#COMPONENT_IDS[@]} - 1) % ${#COMPONENT_IDS[@]}));;
            j) WIZ_INDEX=$(((WIZ_INDEX + 1) % ${#COMPONENT_IDS[@]}));;
            ' ')
                item=${COMPONENT_IDS[$WIZ_INDEX]}
                if requested "$item"; then REQUESTED=" ${REQUESTED} "; REQUESTED=${REQUESTED// $item / }
                else REQUESTED="$REQUESTED $item"
                fi;;
            a|A) REQUESTED="${COMPONENT_IDS[*]}";;
            n|N) REQUESTED='';;
            '')
                if [ -n "${COMPONENTS// /}" ] && wizard_confirm; then break; fi;;
        esac
    done
    trap - WINCH
    printf '\033[H\033[2J' >&3
    wizard_header
    printf '  INSTALLATION EN COURS\n  Sorties detaillees dans le journal.\n\n' >&3
}
