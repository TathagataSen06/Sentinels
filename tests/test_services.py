"""Integration tests that drive each decoy over a real loopback socket."""

from __future__ import annotations

import asyncio
import base64
from contextlib import asynccontextmanager

from honeytrace.config import LimitsConfig, ServiceConfig
from honeytrace.events import EventType
from honeytrace.metrics import Metrics
from honeytrace.ratelimit import RateLimiter
from honeytrace.services import BaseService, ServiceContext, create_service
from honeytrace.sinks import ListEventSink


@asynccontextmanager
async def running_service(
    service_type: str,
    *,
    banner: str | None = None,
    options: dict | None = None,
    rate_limiter: RateLimiter | None = None,
):
    metrics = Metrics()
    sink = ListEventSink()
    context = ServiceContext(
        node_id="test",
        metrics=metrics,
        sink=sink,
        limits=LimitsConfig(session_timeout=5, read_timeout=2),
        rate_limiter=rate_limiter,
    )
    config = ServiceConfig(
        name=service_type,
        type=service_type,
        host="127.0.0.1",
        port=0,
        banner=banner,
        options=options or {},
    )
    service: BaseService = create_service(config, context)
    await service.start()
    try:
        yield service, service.bound_port, sink, metrics
    finally:
        await service.stop()


async def wait_for_event(sink: ListEventSink, event_type: EventType, timeout: float = 2.0):
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        for event in sink.events:
            if event.event_type == event_type:
                return event
        await asyncio.sleep(0.02)
    return None


async def _connect(port: int):
    return await asyncio.open_connection("127.0.0.1", port)


async def test_telnet_captures_credentials():
    async with running_service("telnet", options={"hostname": "gw"}) as (_, port, sink, metrics):
        reader, writer = await _connect(port)
        writer.write(b"admin\r\n")
        writer.write(b"hunter2\r\n")
        await writer.drain()
        await reader.read(200)
        writer.close()

        event = await wait_for_event(sink, EventType.LOGIN_ATTEMPT)
        assert event is not None
        assert event.data["username"] == "admin"
        assert event.data["password"] == "hunter2"
        assert (
            metrics.registry.get_sample_value(
                "honeytrace_login_attempts_total", {"service": "telnet"}
            )
            == 1
        )


async def test_ftp_captures_credentials():
    async with running_service("ftp") as (_, port, sink, _metrics):
        reader, writer = await _connect(port)
        assert (await reader.readline()).startswith(b"220")
        writer.write(b"USER bob\r\n")
        await writer.drain()
        assert (await reader.readline()).startswith(b"331")
        writer.write(b"PASS s3cr3t\r\n")
        await writer.drain()
        assert (await reader.readline()).startswith(b"530")
        writer.write(b"QUIT\r\n")
        await writer.drain()
        writer.close()

        event = await wait_for_event(sink, EventType.LOGIN_ATTEMPT)
        assert event is not None
        assert event.data["username"] == "bob"
        assert event.data["password"] == "s3cr3t"


async def test_http_basic_auth_captured():
    async with running_service("http") as (_, port, sink, _metrics):
        reader, writer = await _connect(port)
        token = base64.b64encode(b"root:toor").decode()
        request = (
            "GET /admin HTTP/1.1\r\n"
            "Host: decoy.local\r\n"
            "User-Agent: scanner/1.0\r\n"
            f"Authorization: Basic {token}\r\n"
            "\r\n"
        )
        writer.write(request.encode())
        await writer.drain()
        response = await reader.read(4096)
        assert b"200 OK" in response
        writer.close()

        login = await wait_for_event(sink, EventType.LOGIN_ATTEMPT)
        assert login is not None
        assert login.data["username"] == "root"
        assert login.data["password"] == "toor"

        request_event = await wait_for_event(sink, EventType.HTTP_REQUEST)
        assert request_event is not None
        assert request_event.data["method"] == "GET"
        assert request_event.data["path"] == "/admin"
        assert request_event.data["headers"]["user-agent"] == "scanner/1.0"


async def test_http_form_credentials_captured():
    async with running_service("http") as (_, port, sink, _metrics):
        reader, writer = await _connect(port)
        body = "username=alice&password=wonderland"
        request = (
            "POST /login HTTP/1.1\r\n"
            "Host: decoy.local\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
            f"{body}"
        )
        writer.write(request.encode())
        await writer.drain()
        await reader.read(4096)
        writer.close()

        login = await wait_for_event(sink, EventType.LOGIN_ATTEMPT)
        assert login is not None
        assert login.data["username"] == "alice"
        assert login.data["password"] == "wonderland"


async def test_ssh_records_client_identification():
    async with running_service("ssh", banner="SSH-2.0-TestServer") as (_, port, sink, _m):
        reader, writer = await _connect(port)
        server_banner = await reader.readline()
        assert server_banner.startswith(b"SSH-2.0-")
        writer.write(b"SSH-2.0-libssh_0.9.6\r\n")
        await writer.drain()
        writer.close()

        event = await wait_for_event(sink, EventType.BANNER)
        assert event is not None
        assert event.data["client_version"] == "SSH-2.0-libssh_0.9.6"


async def test_generic_records_payload():
    async with running_service(
        "generic", banner="READY", options={"max_reads": 1}
    ) as (_, port, sink, _metrics):
        reader, writer = await _connect(port)
        assert (await reader.readline()).strip() == b"READY"
        writer.write(b"PING\r\n")
        await writer.drain()
        writer.close()

        event = await wait_for_event(sink, EventType.DATA)
        assert event is not None
        assert "PING" in event.data["preview_text"]


async def test_connection_lifecycle_events_and_metrics():
    async with running_service("ssh") as (_, port, sink, metrics):
        reader, writer = await _connect(port)
        await reader.readline()
        writer.close()
        await writer.wait_closed()

        opened = await wait_for_event(sink, EventType.CONNECTION_OPEN)
        closed = await wait_for_event(sink, EventType.CONNECTION_CLOSE)
        assert opened is not None
        assert closed is not None
        assert (
            metrics.registry.get_sample_value(
                "honeytrace_connections_total",
                {"service": "ssh", "transport": "tcp"},
            )
            == 1
        )


async def test_rate_limited_connection_is_dropped():
    limiter = RateLimiter(max_events_per_minute=1, burst=1)
    # Drain the single available token so the incoming connection is denied.
    assert limiter.allow("127.0.0.1") is True
    async with running_service("ssh", rate_limiter=limiter) as (_, port, sink, metrics):
        reader, writer = await _connect(port)
        # The server should close almost immediately without a banner exchange.
        await reader.read(100)
        writer.close()

        event = await wait_for_event(sink, EventType.RATE_LIMITED)
        assert event is not None
        assert (
            metrics.registry.get_sample_value(
                "honeytrace_rate_limited_total", {"service": "ssh"}
            )
            == 1
        )
        # A dropped connection must not have opened a session.
        assert not any(e.event_type == EventType.CONNECTION_OPEN for e in sink.events)
