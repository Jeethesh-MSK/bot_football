import os
from typing import Optional


def read_env_or_file(env_var: str, file_env_var: Optional[str]) -> Optional[str]:
    """
    Read a secret from an environment variable or a file pointed to by another env var.

    Why: In many orchestrators (Kubernetes, Docker Swarm), secrets are mounted as files.
    Reading via *_FILE enables secure delivery without exposing values in env history.
    """
    # File var takes precedence to encourage file-based secrets where available
    if file_env_var:
        file_path = os.environ.get(file_env_var)
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    return fh.read().strip()
            except OSError:
                pass
    value = os.environ.get(env_var)
    return value.strip() if value else None


def optional_bool_env(var_name: str, default: bool) -> bool:
    raw = os.environ.get(var_name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}