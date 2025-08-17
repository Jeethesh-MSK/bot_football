# SeatWatcher

SeatWatcher is a production-ready, configurable service that monitors seat availability for matches/events and notifies via multiple channels (Slack, Email, Console).

- Clean, modular, maintainable code with inline rationale comments
- Configurable: match IDs, seat thresholds, poll intervals, and notification channels
- Secure: never hard-code credentials; secrets are read from environment variables or mounted secret files
- Storage: tracks observations and notification state in a relational database (SQLite locally, Postgres in production)

## Quick start (local)

1. Create and activate a virtualenv, then install deps:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy and edit environment variables:

```bash
cp .env.example .env
```

3. Initialize the database (runs Alembic migrations):

```bash
python -m seatwatcher.cli init-db --config configs/seatwatcher.yaml
```

4. Run the watcher with the dummy provider and console notifier:

```bash
python -m seatwatcher.cli run --config configs/seatwatcher.yaml
```

You should see periodic observations and console notifications when the available seats are >= threshold.

## Configuration

- File: `configs/seatwatcher.yaml`
- Environment variables override sensitive values (e.g., `DB_URL`, `SLACK_WEBHOOK_URL`, SMTP creds)
- Example monitors are included. Add more entries under `monitors`.

### Providers

- `dummy`: generates random seat counts for local testing
- `http_json`: calls an HTTP endpoint and extracts a seat count using a JMESPath expression

### Notifiers

- `console`: prints to stdout
- `slack`: posts to an Incoming Webhook (`SLACK_WEBHOOK_URL` or `SLACK_WEBHOOK_URL_FILE`)
- `email`: sends via SMTP (supports `_FILE` env for password)

## Production deployment

- Use Postgres and set `DB_URL` accordingly, e.g.: `postgresql+psycopg2://seatwatcher:seatwatcher@db:5432/seatwatcher`
- Configure real provider `http_json` with endpoint and JMESPath
- Prefer Docker or Kubernetes; see `docker/docker-compose.yml` and `docker/Dockerfile`

### Docker (local stack)

```bash
docker compose -f docker/docker-compose.yml up --build
```

This brings up Postgres, MailHog (email testing), and SeatWatcher.

## Security

- No secrets are hard-coded
- Secrets are read from env vars or mounted files (e.g., `SMTP_PASSWORD_FILE`, `SLACK_WEBHOOK_URL_FILE`)

## Database and migrations

- SQLAlchemy ORM models are in `src/seatwatcher/models.py`
- Alembic migrations live under `alembic/versions`
- CLI commands `init-db` and `upgrade-db` run migrations programmatically

## Example

Trigger a test notification on all configured channels:

```bash
python -m seatwatcher.cli test-notify --config configs/seatwatcher.yaml --subject "Test" --body "This is a test"
```

## License

MIT