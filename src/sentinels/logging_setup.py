"""Logging configuration.

Two logical streams are configured:

* the **application log** (``sentinels``) for operational messages, and
* the **event log** (``sentinels.events``) which receives one JSON document
  per line for every :class:`~sentinels.events.Event`.

The event logger does not propagate to the application log so the two streams
never interleave, and both support size-based rotation.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from .config import LoggingConfig

APP_LOGGER = "sentinels"
EVENT_LOGGER = "sentinels.events"


def _ensure_parent(path: str) -> None:
    Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def _rotating_handler(path: str, cfg: LoggingConfig) -> logging.Handler:
    _ensure_parent(path)
    return logging.handlers.RotatingFileHandler(
        Path(path).expanduser(),
        maxBytes=cfg.rotate_max_bytes,
        backupCount=cfg.rotate_backups,
        encoding="utf-8",
    )


def configure_logging(cfg: LoggingConfig) -> logging.Logger:
    """Configure application and event loggers and return the event logger."""
    app_logger = logging.getLogger(APP_LOGGER)
    app_logger.setLevel(cfg.level)
    app_logger.handlers.clear()
    app_logger.propagate = False

    app_format = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    if cfg.console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(app_format)
        app_logger.addHandler(console_handler)

    if cfg.app_log:
        file_handler = _rotating_handler(cfg.app_log, cfg)
        file_handler.setFormatter(app_format)
        app_logger.addHandler(file_handler)

    # The event logger emits raw JSON lines; no formatter decoration.
    event_logger = logging.getLogger(EVENT_LOGGER)
    event_logger.setLevel(logging.INFO)
    event_logger.handlers.clear()
    event_logger.propagate = False

    raw_format = logging.Formatter("%(message)s")

    if cfg.event_log:
        event_handler = _rotating_handler(cfg.event_log, cfg)
        event_handler.setFormatter(raw_format)
        event_logger.addHandler(event_handler)

    if cfg.console or not cfg.event_log:
        # Always surface events somewhere: mirror to stdout when there is no
        # dedicated file, or alongside the console app log when enabled.
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(raw_format)
        event_logger.addHandler(stream_handler)

    return event_logger


def get_app_logger() -> logging.Logger:
    """Return the shared application logger."""
    return logging.getLogger(APP_LOGGER)
