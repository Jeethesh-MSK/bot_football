from __future__ import annotations

import abc
from typing import Protocol


class Notifier(Protocol):
    def channel_name(self) -> str:  # pragma: no cover - protocol
        ...

    async def send(self, subject: str, message: str | None = None) -> None:  # pragma: no cover - protocol
        ...


class NotifierFactory(abc.ABC):
    @abc.abstractmethod
    def create(self) -> Notifier:  # pragma: no cover - abstract factory
        ...


class CompositeNotifier:
    """
    Aggregate multiple notifiers and send to all of them.

    Why: Keeps the watcher logic simple; a single call fans out to configured channels.
    """

    def __init__(self, notifiers: list[Notifier]):
        self._notifiers = notifiers

    async def send_all(self, subject: str, message: str | None = None) -> None:
        for notifier in self._notifiers:
            await notifier.send(subject=subject, message=message)

    def channels(self) -> list[str]:
        return [n.channel_name() for n in self._notifiers]