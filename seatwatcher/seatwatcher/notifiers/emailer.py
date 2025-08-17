from __future__ import annotations

from email.message import EmailMessage
from typing import Optional

import aiosmtplib

from ..logging_utils import get_logger
from ..utils.secrets import read_env_or_file
from .base import Notifier


logger = get_logger(__name__)


class EmailNotifier(Notifier):
    def __init__(
        self,
        from_email: str,
        to_emails: list[str],
        smtp_host: str,
        smtp_port: int,
        username_env: Optional[str],
        password_env: Optional[str],
        password_file_env: Optional[str],
        use_tls: bool,
        use_starttls: bool,
    ) -> None:
        self._from_email = from_email
        self._to_emails = to_emails
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._username_env = username_env
        self._password_env = password_env
        self._password_file_env = password_file_env
        self._use_tls = use_tls
        self._use_starttls = use_starttls

    def channel_name(self) -> str:
        return "email"

    async def send(self, subject: str, message: str | None = None) -> None:
        email_message = EmailMessage()
        email_message["From"] = self._from_email
        email_message["To"] = ", ".join(self._to_emails)
        email_message["Subject"] = subject
        email_message.set_content(message or "")

        username = self._username_env and read_env_or_file(self._username_env, None)
        password = read_env_or_file(self._password_env or "", self._password_file_env)

        if self._use_tls:
            # Implicit TLS (SMTPS)
            await aiosmtplib.send(
                email_message,
                hostname=self._smtp_host,
                port=self._smtp_port,
                username=username,
                password=password,
                use_tls=True,
            )
            return

        # STARTTLS flow
        client = aiosmtplib.SMTP(hostname=self._smtp_host, port=self._smtp_port, use_tls=False)
        await client.connect()
        if self._use_starttls:
            await client.starttls()
        if username and password:
            await client.login(username, password)
        await client.send_message(email_message)
        await client.quit()