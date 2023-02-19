import os
import textwrap


def env_var_to_bool(value):
    if not value:
        return False
    lowercase = value.lower()
    if lowercase in {'1', 't', 'true', 'y', 'yes'}:
        return True
    if lowercase in {'0', 'f', 'false', 'n', 'no'}:
        return False
    raise ValueError(f"expected a boolean-ish string")


class Config:
    def __init__(self):
        self._env_var_cache = {}

    def _get_env_var(self, env_var, type_=None):
        if (cached := self._env_var_cache.get(env_var)) is not None:
            return cached
        value = os.getenv(env_var)
        converters = {
            "bool": env_var_to_bool,
        }
        if type_ is not None:
            value = converters[type_](value)

        self._env_var_cache[env_var] = value
        return value


    @property
    def battery(self):
        return self._get_env_var("LAPTOP", "bool")

    @property
    def prompt(self):
        if self._get_env_var("PROOT", "bool"):
            return "$"
        return r"\$"

    @property
    def user_hostname(self):
        if self._get_env_var("PROOT", "bool"):
            value = self._get_env_var("USER_HOSTNAME")
            assert value and "'" not in value and "\\" not in value
            return value
        return r"\u@\h"

    @property
    def wsl(self):
        return self._get_env_var("WSL", "bool")


config = Config()


def print_fmt(text, indent=0):
    text = textwrap.dedent(text).lstrip("\n")
    if indent > 0:
        text = textwrap.indent(text, " " * indent)
    print(text, end="")


def make():
    print_fmt(r"""
        [[ $- = *i* ]] || return 0

        shopt -s direxpand dotglob

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

        export HISTCONTROL=ignoreboth
        export HISTFILE=~/.bash_full_history
        export HISTFILESIZE=
        export HISTSIZE=
        export HISTTIMEFORMAT='[%F %T] '

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
            if ((h > 0)); then __timer_duration=${h}h${m}m
            elif ((m > 0)); then __timer_duration=${m}m${s}s
            elif ((s >= 10)); then __timer_duration=${s}.$((ms / 100))s
            elif ((s > 0)); then __timer_duration=${s}.$(printf %03d $ms)s
            elif ((ms >= 100)); then __timer_duration=${ms}ms
            elif ((ms > 0)); then __timer_duration=${ms}.$((us / 100))ms
            else __timer_duration=${us}us
            fi
            unset -v __timer_start
        }

    """)

    if config.battery:
        print_fmt(r"""
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

        """)

    print_fmt(r"""
        function __col {
            local _row col
            IFS=';' read -sdR -p $'\e[6n' _row col
            echo "${col#*[}"
        }

        function __prompt_command {
            local return_code=$?
            __timer_stop
            history -a
            local title_bar='\w'
            echo -en "\e]2;${title_bar@P}\a"

            local no_newline_icon=$'\UF17A5'
            if [[ $(__col) = 1 ]]; then
                PS1='\[\e[0m\]'
            else
                PS1="\[\e[0;37;41m\] $no_newline_icon \[\e[0m\]\n"
            fi

            while (( ${#__timer_duration} < 6 )); do
                __timer_duration=" $__timer_duration"
            done

            local timer_icon=$'\UF051B'
            PS1+="\[\e[30;43m\] $timer_icon $__timer_duration "
    """)

    print_fmt(fr"""
            PS1+='\[\e[102m\] {config.user_hostname} '
    """, 4)

    print_fmt(r"""
        local jobs_icon=$'\UF0AA2'
        local number_jobs=$(jobs | grep -Fcv Done)
        (( $number_jobs > 0 )) && PS1+="\[\e[103m\] $jobs_icon $number_jobs "
        PS1+='\[\e[105m\] \w \[\e[30m\]'

        local virtual_env_icon=$'\UF150E'
        [[ $VIRTUAL_ENV ]] && PS1+="\[\e[105m\] \[\e[30m\]$virtual_env_icon "

        local git_branch_icon=$'\UF062C'
        local git_conflict_icon=$'\UF11CF'
        local git_ahead_behind_icon=$'\UF0E79'
        local git_ahead_icon=$'\UF005D'
        local git_behind_icon=$'\UF0045'
        local git_staged_icon=$'\UF012C'
        local git_untracked_icon=$'\UF1A9E'

        local git_branch=$(git rev-parse --abbrev-ref HEAD 2> /dev/null)

        if [[ $git_branch ]]; then
            local git_number_conflicts=$(git diff --name-only --diff-filter=U 2> /dev/null | wc -l)
            local git_ahead_behind=$(git rev-list --count --left-right '@{upstream}...HEAD' 2> /dev/null)
            local git_number_ahead=$(cut -f2 <<< $git_ahead_behind)
            local git_number_behind=$(cut -f1 <<< $git_ahead_behind)
            local git_number_modified=$(git diff --name-only --diff-filter=M 2> /dev/null | wc -l)
            local git_number_staged=$(git diff --staged --name-only --diff-filter=AM 2>/dev/null | wc -l)
            local git_number_untracked=$(git ls-files --other --exclude-standard 2> /dev/null | wc -l)

            local git_color
            local git_symbols

            if [[ $git_number_conflicts -gt 0 ]]; then
                git_color='\[\e[30;101m\]'
                git_symbols+=" $git_conflict_icon"
            fi

            if [[ $git_number_ahead -gt 0 && $git_number_behind -gt 0 ]]; then
                git_color=${git_color:-'\[\e[30;105m\]'}
                git_symbols+=" $git_ahead_behind_icon"
            elif [[ $git_number_ahead -gt 0 ]]; then
                git_symbols+=" $git_ahead_icon"
            elif [[ $git_number_behind -gt 0 ]]; then
                git_color=${git_color:-'\[\e[37;44m\]'}
                git_symbols+=" $git_behind_icon"
            fi

            [[ $git_number_staged -gt 0 ]] && git_symbols+=" $git_staged_icon"
            [[ $git_number_untracked -gt 0 ]] && git_symbols+=" $git_untracked_icon"
            [[ $git_number_modified -gt 0 ]] && git_color=${git_color:-'\[\e[30;103m\]'}
            git_color=${git_color:-'\[\e[30;102m\]'}

            PS1+="$git_color $git_branch_icon $git_branch"
            [[ $git_number_modified -gt 0 ]] && PS1+='*'
            PS1+="$git_symbols "
        fi

        PS1+='\[\e[0m\]\n\[\e[30;103m\] \t '

        local nonzero_return_icon=$'\U1F643'
        [[ $return_code -ne 0 ]] && PS1+="\[\e[1;37;41m\] $nonzero_return_icon $return_code "

    """, 4)

    if config.battery:
        print_fmt(r"""
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

        """, 4)

    print_fmt(fr"""
        PS1+='\[\e[0;1m\] {config.prompt} \[\e[0m\]'
    """, 4)
    print_fmt(r"""
        }
        PROMPT_COMMAND=__prompt_command

        alias cp='cp -i'
        alias mv='mv -i'
        alias rm='rm -i'
        alias cpf=/usr/bin/cp
        alias mvf=/usr/bin/mv
        alias rmf=/usr/bin/rm

        alias diff='diff --color'

        alias ls=exa
        alias la='exa --all'
        alias ll='exa --all --long --group'

        alias as='sudo su'
        alias R=reset
        alias vi=vim
    """)

    if config.wsl:
        print()
        print_fmt("""
            export WHOME=$(wslpath 'C:/Users/I')
            export DESKTOP=$WHOME/Desktop

            function cw {
                local options=()
                local paths=()
                local end_of_options=false

                for arg in "$@"; do
                    if [[ $arg != -* || $end_of_options = true ]]; then
                        end_of_options=true
                        paths+=("$(wslpath "$arg")")
                    elif [[ $arg = -- ]]; then
                        end_of_options=true
                    else
                        options+=("$arg")
                    fi
                done
                cd "${options[@]}" -- "${paths[@]}"
            }

            function mpc {
                "$(wslpath 'C:/Program Files/MPC-HC/mpc-hc64.exe')" "$(wslpath -w "$1")"
            }

            function mpv {
                local options=()
                local files=()
                local end_of_options=false

                for arg in "$@"; do
                    if [[ $arg != --* || $end_of_options = true ]]; then
                        end_of_options=true
                        local winpath
                        winpath=$(wslpath -w $arg 2> /dev/null)
                        if [[ $? -eq 0 ]]; then
                            files+=("$winpath")
                        else
                            files+=("$arg")
                        fi
                    elif [[ $arg = -- ]]; then
                        end_of_options=true
                    else
                        options+=("$arg")
                    fi
                done
                "$(wslpath 'C:/Program Files/mpv/mpv.com')" "${options[@]}" -- "${files[@]}"
            }

            function mpvp {
                mpv --profile=performance "$@"
            }

            function mpvhp {
                mpv --profile=high-performance "$@"
            }

            function yt {
                local options=()
                local videos=()
                local end_of_options=false

                for arg in "$@"; do
                    if [[ $arg != --* || $end_of_options = true ]]; then
                        end_of_options=true
                        videos+=("ytdl://$arg")
                    elif [[ $arg = -- ]]; then
                        end_of_options=true
                    else
                        options+=("$arg")
                    fi
                done
                mpv "${options[@]}" -- "${videos[@]}"
            }

            function ytsearch {
                local options=()
                local search_terms=()
                local end_of_options=false

                for arg in "$@"; do
                    if [[ $arg != --* || $end_of_options = true ]]; then
                        end_of_options=true
                        search_terms+=("$arg")
                    elif [[ $arg = -- ]]; then
                        end_of_options=true
                    else
                        options+=("$arg")
                    fi
                done
                mpv --keep-open "${options[@]}" -- "ytdl://ytsearch10:${search_terms[*]}"
            }

            function rr {
                "$(wslpath 'C:/Program Files/rr/rr.exe')" "$@"
            }

            function qr {
                qrencode --type=UTF8i -- "$*"
            }
    """)


if __name__ == "__main__":
    make()
