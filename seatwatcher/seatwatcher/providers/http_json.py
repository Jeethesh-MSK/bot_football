from __future__ import annotations

import json
from dataclasses import dataclass
from string import Template
from typing import Any, Dict, Optional

import httpx
import jmespath

from ..logging_utils import get_logger
from .base import SeatProvider


logger = get_logger(__name__)


@dataclass
class HttpJsonProvider(SeatProvider):
    url_template: str
    method: str
    timeout_seconds: float
    jmespath_expr: str
    headers: Optional[Dict[str, str]] = None
    body_template: Optional[str] = None

    async def fetch_available_seats(self, match_id: str) -> int:
        url = Template(self.url_template).safe_substitute({"match_id": match_id})
        body: Optional[str] = None
        if self.body_template:
            body = Template(self.body_template).safe_substitute({"match_id": match_id})

        timeout = httpx.Timeout(self.timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            if self.method.upper() == "POST":
                response = await client.post(url, headers=self.headers, content=body)
            else:
                response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

        # Use JMESPath to extract a value robustly even if API response changes order/structure
        try:
            value = jmespath.search(self.jmespath_expr, data)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"JMESPath extraction failed: {exc}")
        if value is None:
            raise RuntimeError("JMESPath expression returned None")
        try:
            return int(value)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Seat value is not an integer: {value!r}: {exc}")