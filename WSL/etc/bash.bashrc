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
