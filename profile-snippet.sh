# >>> tmux-shared auto-attach >>>
# shellcheck shell=sh
# Auto-attache SSH ; sur macOS, attache aussi les terminaux locaux interactifs.
# TMUX_AUTO_ATTACH=0 permet de désactiver ce comportement.
# Ne s'exécute pas :
# - dans une session tmux existante
# - pour scp / rsync / sftp
# - pour "ssh serveur commande"
case $- in
*i*)
if [ "${TMUX_AUTO_ATTACH:-1}" != 0 ] \
   && { [ -n "${SSH_TTY:-}" ] || [ "$(uname -s)" = Darwin ]; } \
   && [ -z "${TMUX:-}" ] \
   && [ -t 0 ] \
   && [ -t 1 ] \
   && command -v tmux >/dev/null 2>&1
then
    TMUX_SHARED_SESSION="${TMUX_SHARED_SESSION:-shared}"
    tmux new-session -A -s "$TMUX_SHARED_SESSION"
fi
;;
esac
# <<< tmux-shared auto-attach <<<
