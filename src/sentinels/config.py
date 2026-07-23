"""Configuration loading and validation.

Configuration is expressed in YAML and mapped onto typed dataclasses. All
fields have sensible defaults, unknown keys are rejected early, and a small
set of environment variables can override the most deployment-sensitive
values without editing the file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when a configuration file is malformed or invalid."""


def _require_mapping(value: Any, where: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{where}: expected a mapping, got {type(value).__name__}")
    return value


def _reject_unknown(mapping: dict[str, Any], allowed: set[str], where: str) -> None:
    unknown = set(mapping) - allowed
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise ConfigError(f"{where}: unknown option(s): {joined}")


def _as_int(value: Any, where: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{where}: expected an integer, got {value!r}")
    if minimum is not None and value < minimum:
        raise ConfigError(f"{where}: must be >= {minimum}, got {value}")
    return value


def _as_bool(value: Any, where: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{where}: expected a boolean, got {value!r}")
    return value


def _as_str(value: Any, where: str) -> str:
    if not isinstance(value, str):
        raise ConfigError(f"{where}: expected a string, got {value!r}")
    return value


def _as_opt_str(value: Any, where: str) -> str | None:
    return None if value is None else _as_str(value, where)


@dataclass(slots=True)
class LoggingConfig:
    level: str = "INFO"
    console: bool = True
    app_log: str | None = None
    event_log: str | None = None
    rotate_max_bytes: int = 10 * 1024 * 1024
    rotate_backups: int = 5

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoggingConfig:
        _reject_unknown(
            data,
            {
                "level",
                "console",
                "app_log",
                "event_log",
                "rotate_max_bytes",
                "rotate_backups",
            },
            "logging",
        )
        level = _as_str(data.get("level", "INFO"), "logging.level").upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ConfigError(f"logging.level: invalid level {level!r}")
        return cls(
            level=level,
            console=_as_bool(data.get("console", True), "logging.console"),
            app_log=_as_opt_str(data.get("app_log"), "logging.app_log"),
            event_log=_as_opt_str(data.get("event_log"), "logging.event_log"),
            rotate_max_bytes=_as_int(
                data.get("rotate_max_bytes", 10 * 1024 * 1024),
                "logging.rotate_max_bytes",
                minimum=0,
            ),
            rotate_backups=_as_int(
                data.get("rotate_backups", 5), "logging.rotate_backups", minimum=0
            ),
        )


@dataclass(slots=True)
class MetricsConfig:
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 9101

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MetricsConfig:
        _reject_unknown(data, {"enabled", "host", "port"}, "metrics")
        return cls(
            enabled=_as_bool(data.get("enabled", True), "metrics.enabled"),
            host=_as_str(data.get("host", "0.0.0.0"), "metrics.host"),
            port=_as_int(data.get("port", 9101), "metrics.port", minimum=1),
        )


@dataclass(slots=True)
class LimitsConfig:
    session_timeout: float = 30.0
    read_timeout: float = 10.0
    max_line_bytes: int = 4096
    max_session_bytes: int = 65536

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LimitsConfig:
        _reject_unknown(
            data,
            {"session_timeout", "read_timeout", "max_line_bytes", "max_session_bytes"},
            "limits",
        )

        def _as_positive_number(value: Any, where: str) -> float:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ConfigError(f"{where}: expected a number, got {value!r}")
            if value <= 0:
                raise ConfigError(f"{where}: must be > 0, got {value}")
            return float(value)

        return cls(
            session_timeout=_as_positive_number(
                data.get("session_timeout", 30.0), "limits.session_timeout"
            ),
            read_timeout=_as_positive_number(
                data.get("read_timeout", 10.0), "limits.read_timeout"
            ),
            max_line_bytes=_as_int(
                data.get("max_line_bytes", 4096), "limits.max_line_bytes", minimum=1
            ),
            max_session_bytes=_as_int(
                data.get("max_session_bytes", 65536),
                "limits.max_session_bytes",
                minimum=1,
            ),
        )


@dataclass(slots=True)
class RateLimitConfig:
    enabled: bool = True
    max_events_per_minute: int = 120
    burst: int = 30

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RateLimitConfig:
        _reject_unknown(
            data, {"enabled", "max_events_per_minute", "burst"}, "rate_limit"
        )
        return cls(
            enabled=_as_bool(data.get("enabled", True), "rate_limit.enabled"),
            max_events_per_minute=_as_int(
                data.get("max_events_per_minute", 120),
                "rate_limit.max_events_per_minute",
                minimum=1,
            ),
            burst=_as_int(data.get("burst", 30), "rate_limit.burst", minimum=1),
        )


@dataclass(slots=True)
class ServiceConfig:
    name: str
    type: str
    host: str = "0.0.0.0"
    port: int = 0
    enabled: bool = True
    banner: str | None = None
    options: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any], index: int) -> ServiceConfig:
        where = f"services[{index}]"
        _reject_unknown(
            data,
            {"name", "type", "host", "port", "enabled", "banner", "options"},
            where,
        )
        if "type" not in data:
            raise ConfigError(f"{where}: missing required option 'type'")
        svc_type = _as_str(data["type"], f"{where}.type")
        name = _as_str(data.get("name", svc_type), f"{where}.name")
        return cls(
            name=name,
            type=svc_type,
            host=_as_str(data.get("host", "0.0.0.0"), f"{where}.host"),
            port=_as_int(data.get("port", 0), f"{where}.port", minimum=1),
            enabled=_as_bool(data.get("enabled", True), f"{where}.enabled"),
            banner=_as_opt_str(data.get("banner"), f"{where}.banner"),
            options=_require_mapping(data.get("options"), f"{where}.options"),
        )


@dataclass(slots=True)
class Config:
    node_id: str = "sentinels"
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    services: list[ServiceConfig] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        data = _require_mapping(data, "root")
        _reject_unknown(
            data,
            {"node_id", "logging", "metrics", "limits", "rate_limit", "services"},
            "root",
        )

        raw_services = data.get("services", [])
        if not isinstance(raw_services, list):
            raise ConfigError("services: expected a list")
        services = [
            ServiceConfig.from_dict(_require_mapping(item, f"services[{i}]"), i)
            for i, item in enumerate(raw_services)
        ]

        names = [s.name for s in services]
        duplicates = {n for n in names if names.count(n) > 1}
        if duplicates:
            raise ConfigError(
                f"services: duplicate service name(s): {', '.join(sorted(duplicates))}"
            )

        bindings: dict[tuple[str, int], str] = {}
        for svc in services:
            if not svc.enabled:
                continue
            key = (svc.host, svc.port)
            if key in bindings:
                raise ConfigError(
                    f"services: {svc.name!r} and {bindings[key]!r} both bind {svc.host}:{svc.port}"
                )
            bindings[key] = svc.name

        return cls(
            node_id=_as_str(data.get("node_id", "sentinels"), "node_id"),
            logging=LoggingConfig.from_dict(_require_mapping(data.get("logging"), "logging")),
            metrics=MetricsConfig.from_dict(_require_mapping(data.get("metrics"), "metrics")),
            limits=LimitsConfig.from_dict(_require_mapping(data.get("limits"), "limits")),
            rate_limit=RateLimitConfig.from_dict(
                _require_mapping(data.get("rate_limit"), "rate_limit")
            ),
            services=services,
        )

    def apply_env_overrides(self, environ: dict[str, str] | None = None) -> Config:
        """Apply ``SENTINELS_*`` environment overrides in place and return self."""
        env = environ if environ is not None else dict(os.environ)

        if "SENTINELS_NODE_ID" in env:
            self.node_id = env["SENTINELS_NODE_ID"]
        if "SENTINELS_LOG_LEVEL" in env:
            level = env["SENTINELS_LOG_LEVEL"].upper()
            if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
                raise ConfigError(f"SENTINELS_LOG_LEVEL: invalid level {level!r}")
            self.logging.level = level
        if "SENTINELS_METRICS_PORT" in env:
            try:
                self.metrics.port = int(env["SENTINELS_METRICS_PORT"])
            except ValueError as exc:
                raise ConfigError("SENTINELS_METRICS_PORT: must be an integer") from exc
        if "SENTINELS_EVENT_LOG" in env:
            self.logging.event_log = env["SENTINELS_EVENT_LOG"] or None
        return self


def load_config(path: str | os.PathLike[str], *, apply_env: bool = True) -> Config:
    """Load, validate and return a :class:`Config` from a YAML file."""
    file_path = Path(path)
    if not file_path.is_file():
        raise ConfigError(f"configuration file not found: {file_path}")
    try:
        raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"failed to parse YAML: {exc}") from exc

    config = Config.from_dict(_require_mapping(raw, "root"))
    if apply_env:
        config.apply_env_overrides()
    return config
