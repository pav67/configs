#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
packages=1
sddm=0
monitors=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --configure-only) packages=0 ;;
        --sddm) sddm=1 ;;
        --monitors-paul) monitors=1 ;;
        --help|-h)
            printf '%s\n' 'Usage: desktop/install.sh [--configure-only] [--sddm] [--monitors-paul]' \
                'Debian 13 + trixie-backports. Sauvegarde les fichiers remplacés.' \
                '--configure-only : copie uniquement les fichiers utilisateur.' \
                '--sddm : installe le thème et active SDDM au prochain démarrage.' \
                '--monitors-paul : DP-7 / DP-4 / DP-6 en 4K à 150 %.'
            exit 0 ;;
        *) printf 'Option inconnue : %s\n' "$1" >&2; exit 2 ;;
    esac
    shift
done
[ "$(uname -s)" = Linux ] || { echo 'Ce bureau nécessite Linux.' >&2; exit 1; }
[ "$(id -u)" != 0 ] || { echo 'Lancer avec votre utilisateur, sans sudo devant le script.' >&2; exit 1; }
if [ "$packages" = 0 ] && [ "$sddm" = 1 ]; then
    echo '--sddm ne peut pas être combiné avec --configure-only.' >&2; exit 2
fi
if [ "$packages" = 1 ]; then
    # shellcheck source=/dev/null
    . /etc/os-release
    if [ "${ID:-}" != debian ] || [ "${VERSION_ID:-}" != 13 ]; then
        echo 'Installation des paquets prévue pour Debian 13 uniquement ; utiliser --configure-only ailleurs.' >&2; exit 1
    fi
    # Ne pas ajouter de dépôts ni modifier les pilotes graphiques implicitement.
    sudo apt-get update
    if [[ $(apt-cache policy) != *trixie-backports* ]]; then
        echo 'Activer trixie-backports (main) avant de relancer cet installateur.' >&2; exit 1
    fi
    deps=(python3 hyprland fuzzel kitty waybar swaybg hyprlock hypridle
        thunar thunar-archive-plugin file-roller gvfs-backends
        fonts-font-awesome fonts-noto-core pavucontrol pipewire-audio pulseaudio-utils
        grim slurp wl-clipboard cliphist libnotify-bin xdg-utils)
    if ! command -v google-chrome-stable >/dev/null 2>&1 && ! command -v google-chrome >/dev/null 2>&1; then
        deps+=(chromium)
    fi
    # Le poste utilise déjà les bibliothèques Hyprland/PipeWire des backports.
    if [ "$sddm" = 1 ]; then
        deps+=(sddm qml6-module-qtquick-controls qml6-module-qtquick-layouts
            qml6-module-qtquick-window qml6-module-qtquick-templates)
        # Empêcher le démarrage du gestionnaire au milieu d'une session graphique.
        if ! systemctl is-active --quiet sddm.service; then
            sudo systemctl mask --runtime sddm.service
            trap 'sudo systemctl unmask --runtime sddm.service' EXIT
        fi
    fi
    sudo apt-get install -y --no-install-recommends -t trixie-backports "${deps[@]}"
fi
python3 "$ROOT/install-configs.py" "$monitors"
if command -v xdg-mime >/dev/null 2>&1; then
    xdg-mime default thunar.desktop inode/directory
fi
if [ "$sddm" = 1 ]; then
    backup_ts=$(date +%Y%m%d-%H%M%S)-$$
    sudo install -d /usr/share/sddm/themes/paul-midnight /etc/sddm.conf.d /etc/X11/xorg.conf.d
    for file in Main.qml metadata.desktop; do
        target="/usr/share/sddm/themes/paul-midnight/$file"
        if sudo test -f "$target"; then sudo cp -a "$target" "$target.bak.$backup_ts"; fi
        sudo install -m 0644 "$ROOT/sddm/paul-midnight/$file" "$target"
    done
    for pair in '10-paul.conf:/etc/sddm.conf.d/10-paul.conf' '00-keyboard.conf:/etc/X11/xorg.conf.d/00-keyboard.conf'; do
        source_file=${pair%%:*}; target=${pair#*:}
        if sudo test -f "$target"; then sudo cp -a "$target" "$target.bak.$backup_ts"; fi
        sudo install -m 0644 "$ROOT/sddm/$source_file" "$target"
    done
    sudo systemctl unmask --runtime sddm.service
    trap - EXIT
    sudo systemctl enable sddm.service
fi
printf '%s\n' 'Configuration installée. Reconnectez-vous pour charger le bureau et ses services.' \
    'Super+T : Kitty ; Super+Q : fermer la fenêtre ; Super+C : navigateur ; Super+E : Thunar ; Super+L : verrouiller.'
