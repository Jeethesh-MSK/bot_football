from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


_ENGINE: Engine | None = None
_SessionLocal: sessionmaker | None = None


def init_engine(db_url: str) -> Engine:
    """
    Initialize and memoize the SQLAlchemy engine.

    Why: A single process-wide Engine is the recommended pattern. Using a factory
    avoids accidentally creating many engines (costly in connection pools).
    """
    global _ENGINE, _SessionLocal
    if _ENGINE is None:
        _ENGINE = create_engine(db_url, pool_pre_ping=True, future=True)
        _SessionLocal = sessionmaker(bind=_ENGINE, expire_on_commit=False, future=True)
    return _ENGINE


def get_engine() -> Engine:
    if _ENGINE is None:
        raise RuntimeError("Engine not initialized. Call init_engine(db_url) first.")
    return _ENGINE


def get_session_factory() -> sessionmaker:
    if _SessionLocal is None:
        raise RuntimeError("Session factory not initialized. Call init_engine(db_url) first.")
    return _SessionLocal


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope for a series of operations.

    Why: Ensures commits/rollbacks are handled consistently and prevents session leaks.
    """
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()