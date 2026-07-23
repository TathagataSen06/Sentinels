"""Structured event model.

Every observable interaction with a decoy service is represented as an
:class:`Event`. Events are immutable, JSON-serialisable, and carry a stable
schema so that downstream consumers (log shippers, SIEMs, notebooks) can rely
on the field names.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Canonical set of event types emitted by the framework."""

    CONNECTION_OPEN = "connection_open"
    CONNECTION_CLOSE = "connection_close"
    LOGIN_ATTEMPT = "login_attempt"
    HTTP_REQUEST = "http_request"
    BANNER = "banner"
    DATA = "data"
    RATE_LIMITED = "rate_limited"
    PROTOCOL_ERROR = "protocol_error"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


def _utc_now_iso() -> str:
    """Return the current UTC time as an RFC 3339 / ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass(frozen=True, slots=True)
class Event:
    """A single, structured observation.

    Attributes:
        node_id: Identifier of the honeypot node that produced the event.
        service: Logical name of the decoy service (e.g. ``ssh``).
        event_type: One of :class:`EventType`.
        transport: Transport protocol, typically ``tcp``.
        src_ip: Remote peer address.
        src_port: Remote peer port.
        dst_port: Local port the peer connected to.
        message: Human-readable summary.
        data: Arbitrary structured detail (credentials seen, headers, ...).
        timestamp: RFC 3339 UTC timestamp; auto-populated when omitted.
    """

    node_id: str
    service: str
    event_type: EventType
    transport: str
    src_ip: str
    src_port: int
    dst_port: int
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain ``dict`` suitable for JSON serialisation."""
        return {
            "timestamp": self.timestamp,
            "node_id": self.node_id,
            "service": self.service,
            "event_type": str(self.event_type),
            "transport": self.transport,
            "src_ip": self.src_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "message": self.message,
            "data": self.data,
        }

    def to_json(self) -> str:
        """Serialise the event to a compact single-line JSON string."""
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)
