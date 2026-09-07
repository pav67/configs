# >>> tmux-shared auto-attach >>>
# Auto-attache uniquement les connexions SSH interactives.
# Ne s'exécute pas :
# - dans une session tmux existante
# - pour scp / rsync / sftp
# - pour "ssh serveur commande"
if [ -n "${SSH_TTY:-}" ] \
   && [ -z "${TMUX:-}" ] \
   && [ -t 0 ] \
   && [ -t 1 ] \
   && command -v tmux >/dev/null 2>&1
then
    TMUX_SHARED_SESSION="${TMUX_SHARED_SESSION:-shared}"
    tmux attach-session -t "$TMUX_SHARED_SESSION" 2>/dev/null \
        || tmux new-session -s "$TMUX_SHARED_SESSION"
fi
# <<< tmux-shared auto-attach <<<
