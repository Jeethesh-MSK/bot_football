from __future__ import annotations

import asyncio

from ..logging_utils import get_logger
from .base import Notifier


logger = get_logger(__name__)


class ConsoleNotifier(Notifier):
    def channel_name(self) -> str:
        return "console"

    async def send(self, subject: str, message: str | None = None) -> None:
        await asyncio.sleep(0)  # keep async signature consistent
        logger.info("[CONSOLE] %s\n%s", subject, message or "")