#!/bin/sh
# Identity of the local tmux host and the active pane's foreground user.
# ps comes from procps (Debian) / procps-ng (Fedora, Arch).
host=$(hostname -s 2>/dev/null || uname -n)
case "$host" in
    klcentral)         color='#89b4fa' ;; # blue
    codexops)          color='#a6e3a1' ;; # green
    ainode)            color='#cba6f7' ;; # mauve
    debian-containers) color='#89dceb' ;; # cyan
    kl-ca)             color='#f9e2af' ;; # yellow
    infra-core)        color='#fab387' ;; # peach
    kl-clients*)       color='#f5c2e7' ;; # pink
    *)                 color='#a6adc8' ;; # slate
esac

# Use the foreground process group, not $USER inherited by the tmux server.
# Ignore background jobs. If the pane has disappeared, show an explicit unknown.
pane_tty=${1#/dev/}
user='?'
if [ -n "$pane_tty" ]; then
    foreground_user=$(ps -t "$pane_tty" -o user:64=,pgid=,tpgid= --sort=pid 2>/dev/null |
        awk '$2 == $3 && $3 > 0 { user = $1 } END { print user }')
    [ -z "$foreground_user" ] || user=$foreground_user
fi
# Keep host/user text from injecting tmux styles, including unusual hostnames.
host=$(printf '%s' "$host" | tr -cd 'A-Za-z0-9_.-')
user=$(printf '%s' "$user" | tr -cd 'A-Za-z0-9_.?@-')
user_color='#cdd6f4'
[ "$user" != root ] || user_color='#f38ba8'
printf '#[fg=%s,bg=default,bold] %s#[fg=#6c7086,nobold]@#[fg=%s,bold]%s#[default]  ' \
    "$user_color" "$user" "$color" "$host"
