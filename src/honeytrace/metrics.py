"""Prometheus metrics.

Metrics are deliberately low-cardinality: labels are limited to the service
name, transport, and event type. Per-peer detail (source IP, credentials,
payloads) is intentionally *not* exported as labels — that data lives in the
structured event log where high cardinality is appropriate. This keeps the
Prometheus time-series database healthy under scanning storms.
"""

from __future__ import annotations

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Info,
    start_http_server,
)

from . import __version__


class Metrics:
    """Container for all Prometheus collectors used by the framework.

    A dedicated :class:`~prometheus_client.CollectorRegistry` is used so that
    multiple instances (notably in tests) never share global state.
    """

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        self.registry = registry or CollectorRegistry()

        self.build_info = Info(
            "honeytrace_build",
            "Static build information for the running node.",
            registry=self.registry,
        )
        self.build_info.info({"version": __version__})

        self.connections_total = Counter(
            "honeytrace_connections_total",
            "Total number of connections accepted by decoy services.",
            labelnames=("service", "transport"),
            registry=self.registry,
        )
        self.events_total = Counter(
            "honeytrace_events_total",
            "Total number of events emitted, by service and event type.",
            labelnames=("service", "event_type"),
            registry=self.registry,
        )
        self.login_attempts_total = Counter(
            "honeytrace_login_attempts_total",
            "Total number of credential submission attempts observed.",
            labelnames=("service",),
            registry=self.registry,
        )
        self.bytes_received_total = Counter(
            "honeytrace_bytes_received_total",
            "Total number of bytes received from peers.",
            labelnames=("service",),
            registry=self.registry,
        )
        self.rate_limited_total = Counter(
            "honeytrace_rate_limited_total",
            "Total number of connections dropped by the rate limiter.",
            labelnames=("service",),
            registry=self.registry,
        )
        self.active_connections = Gauge(
            "honeytrace_active_connections",
            "Number of currently open peer connections.",
            labelnames=("service",),
            registry=self.registry,
        )

    def record_connection(self, service: str, transport: str) -> None:
        self.connections_total.labels(service=service, transport=transport).inc()

    def record_event(self, service: str, event_type: str) -> None:
        self.events_total.labels(service=service, event_type=event_type).inc()

    def record_login_attempt(self, service: str) -> None:
        self.login_attempts_total.labels(service=service).inc()

    def record_bytes(self, service: str, count: int) -> None:
        if count > 0:
            self.bytes_received_total.labels(service=service).inc(count)

    def record_rate_limited(self, service: str) -> None:
        self.rate_limited_total.labels(service=service).inc()

    def connection_opened(self, service: str) -> None:
        self.active_connections.labels(service=service).inc()

    def connection_closed(self, service: str) -> None:
        self.active_connections.labels(service=service).dec()


def serve_metrics(host: str, port: int, registry: CollectorRegistry):
    """Start the Prometheus exposition HTTP server.

    Returns the ``(server, thread)`` pair from ``prometheus_client`` so the
    caller can shut the server down cleanly on exit.
    """
    return start_http_server(port, addr=host, registry=registry)
