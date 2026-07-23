"""Tests for the Prometheus metrics wrapper."""

from __future__ import annotations

from prometheus_client import generate_latest

from sentinels.metrics import Metrics


def _value(metrics: Metrics, name: str, **labels) -> float:
    return metrics.registry.get_sample_value(name, labels) or 0.0


def test_counters_increment():
    m = Metrics()
    m.record_connection("ssh", "tcp")
    m.record_connection("ssh", "tcp")
    m.record_login_attempt("ssh")
    m.record_bytes("ssh", 128)
    m.record_event("ssh", "login_attempt")

    assert _value(m, "sentinels_connections_total", service="ssh", transport="tcp") == 2
    assert _value(m, "sentinels_login_attempts_total", service="ssh") == 1
    assert _value(m, "sentinels_bytes_received_total", service="ssh") == 128
    assert (
        _value(m, "sentinels_events_total", service="ssh", event_type="login_attempt")
        == 1
    )


def test_active_connections_gauge():
    m = Metrics()
    m.connection_opened("http")
    m.connection_opened("http")
    m.connection_closed("http")
    assert _value(m, "sentinels_active_connections", service="http") == 1


def test_zero_bytes_not_recorded():
    m = Metrics()
    m.record_bytes("ftp", 0)
    assert _value(m, "sentinels_bytes_received_total", service="ftp") == 0


def test_registries_are_isolated():
    a = Metrics()
    b = Metrics()
    a.record_connection("ssh", "tcp")
    assert _value(b, "sentinels_connections_total", service="ssh", transport="tcp") == 0


def test_build_info_exposed():
    m = Metrics()
    exposition = generate_latest(m.registry).decode()
    assert "sentinels_build_info" in exposition
