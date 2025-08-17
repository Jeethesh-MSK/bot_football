from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    match_id: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    seats_available: Mapped[int] = mapped_column(Integer, nullable=False)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    match_id: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(512), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Optional linkage to observation values
    seats_available: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        # App-level dedupe can be done via querying, but unique constraints
        # can prevent accidental flooding if subject repeats rapidly.
        UniqueConstraint("created_at", "match_id", "channel", name="uq_notif_time_match_channel"),
    )