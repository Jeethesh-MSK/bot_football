from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

from .utils.envsubst import env_substitute


class AppConfig(BaseModel):
    timezone: str = Field(default="UTC")
    log_level: str = Field(default="INFO")


class DatabaseConfig(BaseModel):
    url: str


# Provider configs
class DummyProviderConfig(BaseModel):
    seed: int = 42
    min_seats: int = 0
    max_seats: int = 10


class HttpJsonProviderConfig(BaseModel):
    url_template: str
    method: Literal["GET", "POST"] = "GET"
    timeout_seconds: float = 10.0
    # JSON pointer via JMESPath to get seat count from response
    jmespath: str
    # Optional headers stringified to JSON or provided via env variable name
    headers_json: Optional[str] = None
    headers_env: Optional[str] = None
    body_template: Optional[str] = None

    @field_validator("headers_json")
    @classmethod
    def validate_json(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        try:
            _ = json.loads(v)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"headers_json is not valid JSON: {exc}")
        return v


class ProviderConfig(BaseModel):
    type: Literal["dummy", "http_json"] = "dummy"
    dummy: Optional[DummyProviderConfig] = None
    http_json: Optional[HttpJsonProviderConfig] = None


# Notifier configs
class ConsoleNotifierConfig(BaseModel):
    pass


class SlackNotifierConfig(BaseModel):
    webhook_url_env: Optional[str] = None
    webhook_url_file_env: Optional[str] = None


class EmailNotifierConfig(BaseModel):
    from_email: str
    to_emails: List[str]
    smtp_host: str = "localhost"
    smtp_port: int = 587
    username_env: Optional[str] = None
    password_env: Optional[str] = None
    password_file_env: Optional[str] = None
    use_tls: bool = True
    use_starttls: bool = True


class NotifierConfig(BaseModel):
    type: Literal["console", "slack", "email"]
    console: Optional[ConsoleNotifierConfig] = None
    slack: Optional[SlackNotifierConfig] = None
    email: Optional[EmailNotifierConfig] = None


class MonitorConfig(BaseModel):
    name: str
    match_id: str
    seat_threshold_min: int = 1
    poll_interval_seconds: int = 15
    channels: List[str] = Field(default_factory=list)
    min_notify_interval_seconds: int = 300


class Config(BaseModel):
    app: AppConfig
    database: DatabaseConfig
    provider: ProviderConfig
    notifiers: Dict[str, NotifierConfig]
    monitors: List[MonitorConfig]


def load_config(path: str) -> Config:
    """
    Load YAML config with environment variable substitution and validate via Pydantic.

    Why: Declarative configuration keeps runtime flexible. Pydantic gives us explicit
    validation with helpful error messages, while allowing us to evolve the schema safely.
    """
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    substituted = env_substitute(raw)
    try:
        return Config(**substituted)
    except ValidationError as e:
        # Raise with a concise message so operators see actionable info
        raise RuntimeError(f"Config validation error: {e}")