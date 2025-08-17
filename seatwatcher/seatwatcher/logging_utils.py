import logging
import sys
from typing import Optional


def configure_logging(level: str = "INFO") -> None:
    """
    Configure application-wide logging.

    Why: Centralizing logging configuration ensures consistent formatting and
    makes it trivial to adjust verbosity. Using stdout aligns with cloud-native
    logging best practices (aggregators scrape stdout/stderr).
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)

    # Remove existing handlers to avoid duplicate logs when re-configured
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or __name__)