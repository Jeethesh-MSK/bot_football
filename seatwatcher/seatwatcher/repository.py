from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .models import NotificationLog, Observation


def record_observation(session: Session, match_id: str, seats_available: int) -> Observation:
    obs = Observation(
        created_at=datetime.now(timezone.utc),
        match_id=match_id,
        seats_available=seats_available,
    )
    session.add(obs)
    return obs


def record_notification(
    session: Session,
    match_id: str,
    channel: str,
    subject: str,
    message: Optional[str],
    seats_available: Optional[int] = None,
) -> NotificationLog:
    entry = NotificationLog(
        created_at=datetime.now(timezone.utc),
        match_id=match_id,
        channel=channel,
        subject=subject,
        message=message,
        seats_available=seats_available,
    )
    session.add(entry)
    return entry


def last_notification_within(
    session: Session,
    match_id: str,
    channel: str,
    within_seconds: int,
) -> Optional[NotificationLog]:
    if within_seconds <= 0:
        return None
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=within_seconds)
    stmt = (
        select(NotificationLog)
        .where(
            NotificationLog.match_id == match_id,
            NotificationLog.channel == channel,
            NotificationLog.created_at >= cutoff,
        )
        .order_by(desc(NotificationLog.created_at))
        .limit(1)
    )
    return session.execute(stmt).scalars().first()