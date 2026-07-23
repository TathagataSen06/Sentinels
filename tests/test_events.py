"""Tests for the event model."""

from __future__ import annotations

import json

from honeytrace.events import Event, EventType


def _event(**overrides) -> Event:
    base = dict(
        node_id="node-1",
        service="ssh",
        event_type=EventType.LOGIN_ATTEMPT,
        transport="tcp",
        src_ip="203.0.113.7",
        src_port=51234,
        dst_port=22,
        message="test",
        data={"username": "root", "password": "toor"},
    )
    base.update(overrides)
    return Event(**base)


def test_to_dict_has_stable_schema():
    event = _event()
    d = event.to_dict()
    assert set(d) == {
        "timestamp",
        "node_id",
        "service",
        "event_type",
        "transport",
        "src_ip",
        "src_port",
        "dst_port",
        "message",
        "data",
    }
    assert d["event_type"] == "login_attempt"
    assert d["data"]["username"] == "root"


def test_to_json_roundtrips():
    event = _event()
    parsed = json.loads(event.to_json())
    assert parsed["src_ip"] == "203.0.113.7"
    assert parsed["dst_port"] == 22


def test_timestamp_is_populated_and_iso():
    event = _event()
    # RFC 3339 / ISO 8601 with millisecond precision and timezone offset.
    assert "T" in event.timestamp
    assert event.timestamp.endswith("+00:00")


def test_event_is_immutable():
    event = _event()
    try:
        event.message = "changed"  # type: ignore[misc]
    except Exception as exc:  # frozen dataclass raises FrozenInstanceError
        assert exc.__class__.__name__ == "FrozenInstanceError"
    else:  # pragma: no cover - should not happen
        raise AssertionError("event should be immutable")
