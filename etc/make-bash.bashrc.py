import os
import textwrap


class Config:
    def __init__(self):
        self._env_var_cache = {}

    def _get_env_var(self, env_var):
        if (cached := self._env_var_cache.get(env_var)) is not None:
            return cached
        value = env_var_to_bool(os.getenv(env_var))
        self._env_var_cache[env_var] = value
        return value

    @property
    def prompt_battery(self):
        return self._get_env_var("LAPTOP")

    @property
    def wsl(self):
        return self._get_env_var("WSL")


config = Config()


def env_var_to_bool(value):
    if not value:
        return False
    lowercase = value.lower()
    if lowercase in {'1', 't', 'true', 'y', 'yes'}:
        return True
    if lowercase in {'0', 'f', 'false', 'n', 'no'}:
        return False
    raise ValueError(f"expected a boolean-ish string")


def print_fmt(text, indent=0):
    text = textwrap.dedent(text).lstrip("\n")
    if indent > 0:
        text = textwrap.indent(text, " " * indent)
    print(text, end="")


def make():
    print_fmt(r"""
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

        function __col {
            local _row col
            IFS=';' read -sdR -p $'\e[6n' _row col
            echo "${col#*[}"
        }

        function __prompt_command {
            local return_code=$?
            __timer_stop
            local title_bar='\w'
            echo -en "\e]2;${title_bar@P}\a"

            if [[ $(__col) = 1 ]]; then
                PS1='\[\e[0m\]'
            else
                PS1='\n\[\e[0;37;41m\]'$' \u2936 '
            fi
            PS1+='\[\e[0;30;103m\] \t \[\e[102m\] \u@\h '
            local number_jobs=$(jobs | grep -Fcv Done)
            (( $number_jobs > 0 )) && PS1+=$'\[\e[103m\] \UF0AA2'" $number_jobs "
            PS1+='\[\e[97;104m\] \w \[\e[0;30m\]'
            [[ $VIRTUAL_ENV ]] && PS1+=$'\[\e[105m\] \[\e[30m\]\UF150E '

            local git_branch=$(git rev-parse --abbrev-ref HEAD 2> /dev/null)
            if [[ $git_branch ]]; then
                local git_bg
                if [[ $(git status --porcelain 2> /dev/null) ]]; then
                    git_bg='\[\e[103m\]'
                else
                    git_bg='\[\e[102m\]'
                fi
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

    """)

    if config.prompt_battery:
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

    print_fmt(r"""
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
        alias la='ls -A'
        alias ll='ls -Al'

        alias vi=vim
    """)

    if config.wsl:
        print()
        print_fmt("""
            export WHOME=$(wslpath 'C:/Users/I')
            export DESKTOP=$WHOME/Desktop

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
    """)


if __name__ == "__main__":
    make()
