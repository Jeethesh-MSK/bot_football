from __future__ import annotations

import asyncio
from dataclasses import dataclass

from .config import Config, MonitorConfig
from .db import session_scope
from .factory import build_notifier, build_provider
from .logging_utils import get_logger
from .repository import last_notification_within, record_notification, record_observation


logger = get_logger(__name__)


@dataclass
class MonitorRuntime:
    config: MonitorConfig


class WatcherService:
    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg
        self._provider = build_provider(cfg)

    async def run(self) -> None:
        tasks = [self._run_monitor(monitor) for monitor in self._cfg.monitors]
        await asyncio.gather(*tasks)

    async def _run_monitor(self, monitor: MonitorConfig) -> None:
        notifier = build_notifier(self._cfg, monitor.channels)
        poll_interval = max(1, int(monitor.poll_interval_seconds))
        logger.info(
            "Starting monitor '%s' for match_id=%s interval=%ss channels=%s",
            monitor.name,
            monitor.match_id,
            poll_interval,
            ",".join(notifier.channels()),
        )
        while True:
            try:
                seats = await self._provider.fetch_available_seats(monitor.match_id)
                logger.debug("Observed %s seats for %s", seats, monitor.match_id)
                with session_scope() as session:
                    record_observation(session, monitor.match_id, seats)

                    if seats >= monitor.seat_threshold_min:
                        should_skip = False
                        for channel in notifier.channels():
                            existing = last_notification_within(
                                session,
                                monitor.match_id,
                                channel,
                                monitor.min_notify_interval_seconds,
                            )
                            if existing:
                                should_skip = True
                                logger.debug(
                                    "Skipping notify for %s on %s: last at %s",
                                    monitor.match_id,
                                    channel,
                                    existing.created_at,
                                )
                        if not should_skip:
                            subject = f"Seats available for {monitor.match_id}: {seats}"
                            body = (
                                f"Monitor: {monitor.name}\n"
                                f"Match: {monitor.match_id}\n"
                                f"Seats available: {seats}\n"
                            )
                            await notifier.send_all(subject=subject, message=body)
                            for ch in notifier.channels():
                                record_notification(
                                    session,
                                    match_id=monitor.match_id,
                                    channel=ch,
                                    subject=subject,
                                    message=body,
                                    seats_available=seats,
                                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error in monitor '%s': %s", monitor.name, exc)

            await asyncio.sleep(poll_interval)