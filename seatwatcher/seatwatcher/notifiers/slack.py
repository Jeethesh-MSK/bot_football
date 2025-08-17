from __future__ import annotations

import json
from typing import Optional

import httpx

from ..logging_utils import get_logger
from ..utils.secrets import read_env_or_file
from .base import Notifier


logger = get_logger(__name__)


class SlackNotifier(Notifier):
    def __init__(self, webhook_url_env: Optional[str], webhook_url_file_env: Optional[str]) -> None:
        self._webhook_url_env = webhook_url_env
        self._webhook_url_file_env = webhook_url_file_env
        self._webhook_url: Optional[str] = None

    def _get_webhook_url(self) -> str:
        if not self._webhook_url:
            value = read_env_or_file(self._webhook_url_env or "", self._webhook_url_file_env)
            if not value:
                raise RuntimeError("Slack webhook URL not configured via env or file env.")
            self._webhook_url = value
        return self._webhook_url

    def channel_name(self) -> str:
        return "slack"

    async def send(self, subject: str, message: str | None = None) -> None:
        text = subject if not message else f"{subject}\n{message}"
        payload = {"text": text}
        url = self._get_webhook_url()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()