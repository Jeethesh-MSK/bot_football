from __future__ import annotations

import asyncio
import os
from typing import Optional

import click
from sqlalchemy import text

from .config import load_config
from .db import get_engine, init_engine
from .logging_utils import configure_logging, get_logger
from .models import Base
from .watcher import WatcherService
from .factory import build_notifier


logger = get_logger(__name__)


@click.group()
@click.option("--config", "config_path", required=True, type=click.Path(exists=True))
@click.pass_context
def cli(ctx: click.Context, config_path: str) -> None:
    cfg = load_config(config_path)
    configure_logging(cfg.app.log_level)
    init_engine(cfg.database.url)
    ctx.ensure_object(dict)
    ctx.obj["cfg"] = cfg


@cli.command("init-db")
@click.pass_context
def init_db(ctx: click.Context) -> None:
    """
    Initialize database by creating tables.

    Why: For simple deployments, table creation via ORM metadata is sufficient. We
    also support Alembic migrations separately for schema evolution.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)
    click.echo("Database initialized")


@cli.command("upgrade-db")
@click.option("--revision", default="head", help="Alembic revision to upgrade to")
@click.pass_context
def upgrade_db(ctx: click.Context, revision: str) -> None:
    """
    Run Alembic upgrade programmatically.

    This keeps the operational interface through the same CLI. The Alembic config is
    defined in alembic.ini and env.py.
    """
    from alembic import command
    from alembic.config import Config as AlembicConfig

    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, os.pardir))
    alembic_cfg = AlembicConfig(os.path.join(root, "alembic.ini"))
    # Pass SQLAlchemy URL dynamically so alembic uses our config
    alembic_cfg.set_main_option("sqlalchemy.url", ctx.obj["cfg"].database.url)
    command.upgrade(alembic_cfg, revision)


@cli.command("run")
@click.pass_context
def run(ctx: click.Context) -> None:
    cfg = ctx.obj["cfg"]
    service = WatcherService(cfg)
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        logger.info("Shutting down")


@cli.command("test-notify")
@click.option("--subject", required=True)
@click.option("--body", required=True)
@click.option("--channels", default="", help="Comma-separated notifier names to use; default uses all in first monitor")
@click.pass_context
def test_notify(ctx: click.Context, subject: str, body: str, channels: str) -> None:
    cfg = ctx.obj["cfg"]
    if channels:
        channel_list = [c.strip() for c in channels.split(",") if c.strip()]
    else:
        channel_list = cfg.monitors[0].channels
    notifier = build_notifier(cfg, channel_list)

    async def _run() -> None:
        await notifier.send_all(subject=subject, message=body)

    asyncio.run(_run())
    click.echo("Test notification sent")


if __name__ == "__main__":  # pragma: no cover
    cli()