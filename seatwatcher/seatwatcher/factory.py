from __future__ import annotations

import json
from typing import Dict, List

from .config import Config, NotifierConfig
from .notifiers.base import CompositeNotifier, Notifier
from .notifiers.console import ConsoleNotifier
from .notifiers.emailer import EmailNotifier
from .notifiers.slack import SlackNotifier
from .providers.dummy import DummyProvider
from .providers.http_json import HttpJsonProvider


def build_provider(cfg: Config):
    p = cfg.provider
    if p.type == "dummy":
        c = p.dummy
        if c is None:
            # Fall back to defaults if absent
            return DummyProvider(seed=42, min_seats=0, max_seats=10)
        return DummyProvider(seed=c.seed, min_seats=c.min_seats, max_seats=c.max_seats)
    if p.type == "http_json":
        c = p.http_json
        assert c is not None
        headers: Dict[str, str] | None = None
        if c.headers_json:
            headers = json.loads(c.headers_json)
        elif c.headers_env:
            import os

            raw = os.environ.get(c.headers_env)
            if raw:
                headers = json.loads(raw)
        return HttpJsonProvider(
            url_template=c.url_template,
            method=c.method,
            timeout_seconds=c.timeout_seconds,
            jmespath_expr=c.jmespath,
            headers=headers,
            body_template=c.body_template,
        )
    raise ValueError(f"Unknown provider type: {p.type}")


def build_notifier(cfg: Config, monitor_channels: List[str]) -> CompositeNotifier:
    notifiers: List[Notifier] = []
    for name in monitor_channels:
        nconf: NotifierConfig | None = cfg.notifiers.get(name)
        if not nconf:
            raise RuntimeError(f"Notifier '{name}' not found in config")
        if nconf.type == "console":
            notifiers.append(ConsoleNotifier())
        elif nconf.type == "slack":
            assert nconf.slack is not None
            notifiers.append(
                SlackNotifier(
                    webhook_url_env=nconf.slack.webhook_url_env,
                    webhook_url_file_env=nconf.slack.webhook_url_file_env,
                )
            )
        elif nconf.type == "email":
            assert nconf.email is not None
            e = nconf.email
            notifiers.append(
                EmailNotifier(
                    from_email=e.from_email,
                    to_emails=e.to_emails,
                    smtp_host=e.smtp_host,
                    smtp_port=e.smtp_port,
                    username_env=e.username_env,
                    password_env=e.password_env,
                    password_file_env=e.password_file_env,
                    use_tls=e.use_tls,
                    use_starttls=e.use_starttls,
                )
            )
        else:
            raise RuntimeError(f"Unsupported notifier type: {nconf.type}")
    return CompositeNotifier(notifiers)