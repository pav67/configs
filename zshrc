export PATH="$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH"
export EDITOR=nvim
export VISUAL=nvim

export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME=""
plugins=(
  git
  zsh-vi-mode
  zsh-autosuggestions
  history-substring-search
)


source "$ZSH/oh-my-zsh.sh"

# >>> tmux-shared auto-attach >>>
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

mkdir -p "$HOME/.cache/zsh"
HISTFILE="$HOME/.cache/zsh/history"

HISTSIZE=100000
SAVEHIST=100000

setopt APPEND_HISTORY
setopt SHARE_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_EXPIRE_DUPS_FIRST
setopt HIST_FIND_NO_DUPS

setopt AUTOCD
setopt NOBEEP
setopt NUMERIC_GLOB_SORT

zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'

# Package paths differ between Debian, Fedora and Arch.
_source_fzf() {
  local script=$1 dir
  for dir in /usr/share/doc/fzf/examples /usr/share/fzf /usr/share/fzf/shell; do
    if [[ -f "$dir/$script.zsh" ]]; then
      source "$dir/$script.zsh"
      return
    fi
  done
  return 1
}
_source_fzf completion || true


# =========================================================
# fzf
# =========================================================

if command -v fdfind >/dev/null 2>&1; then
  export FZF_DEFAULT_COMMAND='fdfind --type f --hidden'
else
  export FZF_DEFAULT_COMMAND='fd --type f --hidden'
fi

# Ctrl-T uses fd
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

# UI
export FZF_DEFAULT_OPTS='
  --height=60%
  --layout=reverse
  --border=rounded
  --prompt="  "
  --pointer="  "
  --preview-window=right:65%:wrap:border-left
'

if command -v batcat >/dev/null 2>&1; then
  alias cat='batcat'
  export _FZF_PREVIEW_CMD='batcat --color=always --style=plain,numbers --line-range=:500 {}'
else
  alias cat='bat'
  export _FZF_PREVIEW_CMD='bat --color=always --style=plain,numbers --line-range=:500 {}'
fi
export FZF_CTRL_T_OPTS="--preview '$_FZF_PREVIEW_CMD'"

# Ctrl+F: file picker excluding hidden files
_fzf_file_no_hidden() {
  local cmd result
  cmd="${FZF_DEFAULT_COMMAND/--hidden /}"
  result=$(eval "${cmd:-find . -type f}" | fzf --preview "$_FZF_PREVIEW_CMD") \
    && LBUFFER+="${(q)result}"  # LBUFFER is the text left of the cursor
  zle reset-prompt
}
zle -N _fzf_file_no_hidden


# Better ls
alias ls='eza --icons'

# Detailed listing
alias ll='eza -lh --sort=modified --reverse --icons --git'

# Detailed listing including hidden files
alias la='eza -lah --icons --git'

# Tree view
alias tree='eza --tree --icons'

# Reuse ls completions for eza (avoids defining a separate completion function)
compdef eza=ls

alias grep='rg --color=auto'
alias diff='diff --color=auto'
alias df='df -h'

alias -- -='cd -'  # -- prevents - being parsed as a flag; cd - jumps to previous directory

lf() { # zsh follow lf navigation
    local tmp dir
    tmp=$(mktemp) || return
    command lf -last-dir-path="$tmp" "$@"
    if [ -f "$tmp" ]; then
        dir=$(command cat "$tmp")
        rm -f "$tmp"
        [ -d "$dir" ] && [ "$dir" != "$(pwd)" ] && cd "$dir"
    fi
}

alias glog='PAGER="less -F -X" git log'                              # -F quit if one screen, -X no clear on exit
alias gadog='PAGER="less -F -X" git log --all --decorate --oneline --graph'
alias dotfiles='git --git-dir=$HOME/.dotfiles --work-tree=$HOME'

# Cursor shape per vi mode
ZVM_INSERT_MODE_CURSOR=$ZVM_CURSOR_BEAM
ZVM_NORMAL_MODE_CURSOR=$ZVM_CURSOR_BLOCK
ZVM_VISUAL_MODE_CURSOR=$ZVM_CURSOR_BLOCK

# Disable command mode line highlight
ZVM_VI_HIGHLIGHT_BACKGROUND=none
ZVM_VI_HIGHLIGHT_FOREGROUND=none
ZVM_VI_HIGHLIGHT_EXTRASTYLE=none

# zsh-vi-mode resets all bindings on init, so custom bindings
# must be registered via this hook to survive.
zvm_after_init() {

  _source_fzf key-bindings || source <(fzf --zsh)

  # Ctrl+Right -> move forward one word (^[[1;5C is the terminal escape code)
  bindkey '^[[1;5C' forward-word

  # Ctrl+Left -> move backward one word (^[[1;5D is the terminal escape code)
  bindkey '^[[1;5D' backward-word

  # Ctrl+F -> fzf file picker (no hidden files)
  bindkey '^F' _fzf_file_no_hidden

  # Ctrl+\ -> toggle autosuggestions (useful for screen recordings)
  bindkey '^\' autosuggest-toggle

  # Up/Down -> history search by substring (^[[A/^[[B are up/down arrow escape codes)
  bindkey '^[[A' history-substring-search-up
  bindkey '^[[B' history-substring-search-down
}

# opencode
export PATH="$HOME/.opencode/bin:$PATH"

eval "$(starship init zsh)"
