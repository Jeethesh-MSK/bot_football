import os
import re
from typing import Any

_ENV_PATTERN = re.compile(r"\$\{([^:}]+)(?::-(.*?))?\}")


def _substitute_value(value: str) -> str:
    """
    Substitute ${VAR:-default} patterns in a single string.

    Why: We want configs to be deployable across environments without code changes.
    Supporting a simple ${VAR:-default} pattern keeps YAML readable while enabling
    secure secret injection via env vars.
    """
    def repl(match: re.Match[str]) -> str:
        var = match.group(1)
        default = match.group(2) or ""
        return os.environ.get(var, default)

    return _ENV_PATTERN.sub(repl, value)


def env_substitute(obj: Any) -> Any:
    """
    Recursively substitute environment variables in YAML-loaded structures.
    """
    if isinstance(obj, str):
        return _substitute_value(obj)
    if isinstance(obj, list):
        return [env_substitute(i) for i in obj]
    if isinstance(obj, dict):
        return {k: env_substitute(v) for k, v in obj.items()}
    return obj