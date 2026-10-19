#!/bin/sh
# Identity of the local tmux host and the active pane's foreground user.
# ps comes from procps (Debian) / procps-ng (Fedora, Arch).
host=$(hostname -s 2>/dev/null || uname -n)
# Omada client names checked on 2026-10-16. Match without case sensitivity.
# codexops is the Omada label for the local system kl-codex-runner.
host_key=$(printf '%s' "${host%%.*}" | LC_ALL=C tr '[:upper:]' '[:lower:]')
case "$host_key" in
    kl-central|klcentral)         color='#89b4fa' ;; # blue
    codexops|kl-codex-runner)          color='#a6e3a1' ;; # green
    ai-node|ainode)            color='#cba6f7' ;; # mauve
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
    if [ "$(uname -s)" = Darwin ]; then
        # BSD ps marks the foreground group with +; it has no GNU --sort.
        foreground_uid=$(ps -t "$pane_tty" -o uid=,pid=,stat= 2>/dev/null |
            awk '$3 ~ /\+/ && $2 > newest { newest = $2; uid = $1 } END { print uid }')
        foreground_user=''
        if [ -n "$foreground_uid" ]; then
            foreground_user=$(id -nu "$foreground_uid" 2>/dev/null || true)
        fi
    else
        foreground_user=$(ps -t "$pane_tty" -o user:64=,pgid=,tpgid= --sort=pid 2>/dev/null |
            awk '$2 == $3 && $3 > 0 { user = $1 } END { print user }')
    fi
    [ -z "$foreground_user" ] || user=$foreground_user
fi
# Keep host/user text from injecting tmux styles, including unusual hostnames.
host=$(printf '%s' "$host" | tr -cd 'A-Za-z0-9_.-')
user=$(printf '%s' "$user" | tr -cd 'A-Za-z0-9_.?@-')
user_color='#cdd6f4'
[ "$user" != root ] || user_color='#f38ba8'
# Separate rounded bubbles: neutral user background and colored host background.
printf '#[fg=#313244,bg=default,nobold]#[fg=%s,bg=#313244,bold]%s#[fg=#313244,bg=default,nobold]#[default] #[fg=%s,bg=default]#[fg=#1e1e2e,bg=%s,bold]%s#[fg=%s,bg=default,nobold]#[default] ' \
    "$user_color" "$user" "$color" "$color" "$host" "$color"
