[[ $- = *i* ]] || return 0

function append_path {
  case ":$PATH:" in
    *:"$1":*)
      ;;
    *)
      PATH=${PATH:+$PATH:}$1
  esac
}

function prepend_path {
  case ":$PATH:" in
    *:"$1":*)
      ;;
    *)
      PATH=$1${PATH:+:$PATH}
  esac
}

prepend_path "$HOME/.local/bin"

shopt -s histappend
HISTCONTROL=ignoreboth

export EDITOR=vim

if [[ -r /usr/share/bash-completion/bash_completion ]]; then
  source /usr/share/bash-completion/bash_completion
fi

function __timer_now {
  date +%s%N
}

function __timer_start {
    __timer_start=${__timer_start:-$(__timer_now)}
}
trap __timer_start DEBUG

function __timer_stop {
  local delta_us=$((($(__timer_now) - __timer_start) / 1000))
  local us=$((delta_us % 1000))
  local ms=$(((delta_us / 1000) % 1000))
  local s=$(((delta_us / 1000000) % 60))
  local m=$(((delta_us / 60000000) % 60))
  local h=$((delta_us / 3600000000))
  if ((h > 0)); then __duration=${h}h${m}m
  elif ((m > 0)); then __duration=${m}m${s}s
  elif ((s >= 10)); then __duration=${s}.$((ms / 100))s
  elif ((s > 0)); then __duration=${s}.$(printf %03d $ms)s
  elif ((ms >= 100)); then __duration=${ms}ms
  elif ((ms > 0)); then __duration=${ms}.$((us / 100))ms
  else __duration=${us}us
  fi
  unset __timer_start
}

function __next_git_bg {
  if [[ $1 = '\[\e[43m\]' ]]; then echo '\[\e[103m\]'
  elif [[ $1 = '\[\e[103m\]' ]]; then echo '\[\e[43m\]'
  elif [[ $1 = '\[\e[42m\]' ]]; then echo '\[\e[102m\]'
  elif [[ $1 = '\[\e[102m\]' ]]; then echo '\[\e[42m\]'
  fi
}

function __battery_icon {
  if [[ $1 = Discharging ]]; then
    if (( $2 >= 90 )); then echo $'\UF0079'
    elif (( $2 >= 80 )); then echo $'\UF0082'
    elif (( $2 >= 70 )); then echo $'\UF0081'
    elif (( $2 >= 60 )); then echo $'\UF0080'
    elif (( $2 >= 50 )); then echo $'\UF007F'
    elif (( $2 >= 40 )); then echo $'\UF007E'
    elif (( $2 >= 30 )); then echo $'\UF007D'
    elif (( $2 >= 20 )); then echo $'\UF007C'
    elif (( $2 >= 10 )); then echo $'\UF007B'
    else echo $'\UF007A'
    fi
  else
    echo $'\UF140B'
  fi
}

function __prompt_command {
  local return_code=$?
  __timer_stop
  local title_bar='\w'
  echo -en "\e]2;${title_bar@P}\a"

  PS1='\[\e[30;103m\] \t \[\e[102m\] \u@\h '
  local number_jobs=$(jobs | grep -Fcv Done)
  (( $number_jobs > 0 )) && PS1+=$'\[\e[103m\] \UF0AA2'" $number_jobs "
  PS1+='\[\e[97;104m\] \w \[\e[0;30m\]'
  [[ $VIRTUAL_ENV ]] && PS1+=$'\[\e[105m\] \[\e[30m\]\UF150E '

  local git_branch=$(git rev-parse --abbrev-ref HEAD 2> /dev/null)
  if [[ $git_branch ]]; then
    local git_bg
    [[ $(git status --porcelain 2> /dev/null) ]] && git_bg='\[\e[103m\]' || git_bg='\[\e[102m\]'
    PS1+="$git_bg "$'\UF062C'" $git_branch "

    local ahead_behind=$(git rev-list --count --left-right '@{upstream}...HEAD' 2> /dev/null)
    local number_ahead=$(cut -f2 <<< "$ahead_behind")
    local number_behind=$(cut -f1 <<< "$ahead_behind")
    if [[ $number_ahead -ne 0 ]]; then
      git_bg=$(__next_git_bg "$git_bg")
      PS1+="$git_bg "$'\UF005D'" $number_ahead "
    fi
    if [[ $number_behind -ne 0 ]]; then
      git_bg=$(__next_git_bg "$git_bg")
      PS1+="$git_bg "$'\UF0045'" $number_behind "
    fi
    local number_conflicts=$(git diff --name-only --diff-filter=U 2> /dev/null | wc -l)
    if [[ $number_conflicts -ne 0 ]]; then
      git_bg=$(__next_git_bg "$git_bg")
      PS1+="$git_bg \[\e[31m\]"$'\UF0029'"\[\e[30m\] $number_conflicts "
    fi
    local number_staged=$(git diff --staged --name-only --diff-filter=AM 2>/dev/null | wc -l)
    if [[ $number_staged -ne 0 ]]; then
      git_bg=$(__next_git_bg "$git_bg")
      PS1+="$git_bg "$'\UF012C'" $number_staged "
    fi
    local number_modified=$(git diff --name-only --diff-filter=M 2> /dev/null | wc -l)
    if [[ $number_modified -ne 0 ]]; then
      git_bg=$(__next_git_bg "$git_bg")
      PS1+="$git_bg "$'\UF03EB'" $number_modified "
    fi
    local number_untracked=$(git ls-files --other --exclude-standard 2> /dev/null | wc -l)
    if [[ $number_untracked -ne 0 ]]; then
      git_bg=$(__next_git_bg "$git_bg")
      PS1+="$git_bg "$'\UF0415'" $number_untracked "
    fi
  fi

  PS1+='\[\e[0m\]\n'
  while (( $(wc -c <<< "$__duration") < 7 )); do
    __duration=" $__duration"
  done
  PS1+=$'\[\e[30;43m\] \UF051B $__duration '
  [[ $return_code -ne 0 ]] && PS1+=$'\[\e[1;37;41m\] \U1F643'" $return_code "
  local battery_dir=/sys/class/power_supply/BAT
  if [[ -d ${battery_dir}0 ]]; then
    battery_dir=${battery_dir}0
  elif [[ -d ${battery_dir}1 ]]; then
    battery_dir=${battery_dir}1
  fi
  if [[ -d $battery_dir ]]; then
    local battery_level=$(<$battery_dir/capacity)
    local battery_icon=$(__battery_icon "$(<$battery_dir/status)" "$battery_level")
    PS1+="\[\e[0;30;46m\] $battery_icon $battery_level% "
  fi
  PS1+='\[\e[0;1m\] \$ \[\e[0m\]'
}
PROMPT_COMMAND=__prompt_command

alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias cpf=/usr/bin/cp
alias mvf=/usr/bin/mv
alias rmf=/usr/bin/rm

alias diff='diff --color'

alias ls='ls --color=auto'
alias ll='ls -l'
alias la='ls -Al'

alias vi=vim
