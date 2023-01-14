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
    def server(self):
        return self._get_env_var("SERVER")


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
    print_fmt("""
        unbind-key C-b
    """)

    if config.server:
        print_fmt("""
            set-option -g prefix M-s
            set-option -g status-style fg=green,bg=black
        """)
    else:
        print_fmt("""
            set-option -g prefix C-s
        """)

    print_fmt("""
        set-window-option -g xterm-keys on
    """)


if __name__ == "__main__":
    make()
