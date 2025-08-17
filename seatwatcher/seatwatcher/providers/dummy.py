from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass

from .base import SeatProvider


@dataclass
class DummyProvider(SeatProvider):
    seed: int
    min_seats: int
    max_seats: int

    def __post_init__(self) -> None:
        # Using a dedicated RNG ensures deterministic sequences per process for reproducibility
        self._rng = random.Random(self.seed)

    async def fetch_available_seats(self, match_id: str) -> int:
        # Simulate network latency slightly to mimic real behavior without tight loops
        await asyncio.sleep(0.01)
        return self._rng.randint(self.min_seats, self.max_seats)