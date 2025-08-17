#!/usr/bin/env bash
set -euo pipefail

# Heavy comments: Why this script?
# - Ensure the DB schema is up to date before starting the app.
# - Avoid hard-coding credentials; rely on env vars and config file env-substitution.

if [ -n "${DB_URL:-}" ]; then
	# Pass DB URL to Alembic dynamically
	sed -i "s|^sqlalchemy.url =.*$|sqlalchemy.url = ${DB_URL}|" /app/alembic.ini
fi

# Create tables if missing as a fallback for first boot
python -m seatwatcher.cli --config configs/seatwatcher.yaml init-db || true

# Then run Alembic migrations for upgrades
alembic -c alembic.ini upgrade head || true

exec python -m seatwatcher.cli --config configs/seatwatcher.yaml run