from __future__ import annotations

import abc
from typing import Protocol


class SeatProvider(Protocol):
    async def fetch_available_seats(self, match_id: str) -> int:  # pragma: no cover - protocol
        ...


class ProviderFactory(abc.ABC):
    @abc.abstractmethod
    def create(self) -> SeatProvider:  # pragma: no cover - abstract factory
        ...