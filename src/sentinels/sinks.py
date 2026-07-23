"""Event sinks.

A sink is the destination for :class:`~sentinels.events.Event` objects. The
production sink writes each event as a JSON line to the event logger and
updates Prometheus counters; the in-memory sink is used by the test suite to
assert on emitted events without touching the logging subsystem.
"""

from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

from .events import Event
from .logging_setup import EVENT_LOGGER
from .metrics import Metrics


@runtime_checkable
class EventSink(Protocol):
    """Anything capable of accepting an :class:`Event`."""

    def emit(self, event: Event) -> None:  # pragma: no cover - protocol
        ...


class LoggingEventSink:
    """Write events to the event logger and reflect them into metrics."""

    def __init__(self, metrics: Metrics, logger: logging.Logger | None = None) -> None:
        self._metrics = metrics
        self._logger = logger or logging.getLogger(EVENT_LOGGER)

    def emit(self, event: Event) -> None:
        self._metrics.record_event(event.service, str(event.event_type))
        self._logger.info(event.to_json())


class ListEventSink:
    """Collect events in memory. Intended for tests and diagnostics."""

    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, event: Event) -> None:
        self.events.append(event)
