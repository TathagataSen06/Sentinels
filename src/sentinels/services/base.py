"""Base classes for decoy services.

A concrete service subclasses :class:`BaseService` and implements
:meth:`BaseService.handle`, driving the peer through a plausible protocol
exchange using the helpers on :class:`Session`. All connection accounting,
rate limiting, timeouts, byte caps, metrics, and graceful shutdown are handled
here so individual services stay small and focused on protocol behaviour.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from ..config import LimitsConfig, ServiceConfig
from ..events import Event, EventType
from ..logging_setup import get_app_logger
from ..metrics import Metrics
from ..ratelimit import RateLimiter
from ..sinks import EventSink


class ServiceContext:
    """Shared, process-wide dependencies handed to every service."""

    def __init__(
        self,
        node_id: str,
        metrics: Metrics,
        sink: EventSink,
        limits: LimitsConfig,
        rate_limiter: RateLimiter | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.node_id = node_id
        self.metrics = metrics
        self.sink = sink
        self.limits = limits
        self.rate_limiter = rate_limiter
        self.logger = logger or get_app_logger()


class Session:
    """Per-connection state and I/O helpers.

    Instances are created by :class:`BaseService` and passed to
    :meth:`BaseService.handle`. All reads enforce the configured per-read
    timeout, per-line byte cap, and cumulative per-session byte cap.
    """

    def __init__(
        self,
        service: BaseService,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        src_ip: str,
        src_port: int,
        dst_port: int,
    ) -> None:
        self._service = service
        self._context = service.context
        self.reader = reader
        self.writer = writer
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.bytes_received = 0

    # -- event helpers ---------------------------------------------------
    def build_event(
        self, event_type: EventType, message: str = "", **data: Any
    ) -> Event:
        return Event(
            node_id=self._context.node_id,
            service=self._service.name,
            event_type=event_type,
            transport=self._service.transport,
            src_ip=self.src_ip,
            src_port=self.src_port,
            dst_port=self.dst_port,
            message=message,
            data=dict(data),
        )

    def emit(self, event_type: EventType, message: str = "", **data: Any) -> None:
        self._context.sink.emit(self.build_event(event_type, message, **data))

    def emit_login(
        self, username: str, password: str, message: str = "", **extra: Any
    ) -> None:
        """Record a credential submission and update the login metric."""
        self._context.metrics.record_login_attempt(self._service.name)
        self.emit(
            EventType.LOGIN_ATTEMPT,
            message or "credential submission",
            username=username,
            password=password,
            **extra,
        )

    def emit_protocol_error(self, message: str, **data: Any) -> None:
        self.emit(EventType.PROTOCOL_ERROR, message, **data)

    # -- I/O helpers -----------------------------------------------------
    def _account(self, count: int) -> None:
        if count > 0:
            self.bytes_received += count
            self._context.metrics.record_bytes(self._service.name, count)

    @property
    def _session_exhausted(self) -> bool:
        return self.bytes_received >= self._context.limits.max_session_bytes

    async def readline(self, prompt: str | None = None) -> str | None:
        """Read a single CRLF/LF-terminated line, honouring all limits.

        Returns the decoded line without trailing newline characters, or
        ``None`` on EOF, timeout, or when a byte cap is reached.
        """
        if prompt is not None:
            if not await self.send(prompt):
                return None
        if self._session_exhausted:
            self.emit_protocol_error("session byte cap exceeded")
            return None
        try:
            data = await asyncio.wait_for(
                self.reader.readuntil(b"\n"), self._context.limits.read_timeout
            )
        except asyncio.TimeoutError:
            return None
        except asyncio.IncompleteReadError as exc:
            data = exc.partial
            if not data:
                return None
        except asyncio.LimitOverrunError:
            self.emit_protocol_error("line length cap exceeded")
            return None
        except (ConnectionError, OSError):
            return None
        self._account(len(data))
        return data.rstrip(b"\r\n").decode("latin-1", errors="replace")

    async def read_some(self, max_bytes: int | None = None) -> bytes:
        """Read up to ``max_bytes`` bytes, bounded by the session byte cap."""
        remaining = self._context.limits.max_session_bytes - self.bytes_received
        if remaining <= 0:
            return b""
        want = remaining if max_bytes is None else min(max_bytes, remaining)
        try:
            data = await asyncio.wait_for(
                self.reader.read(want), self._context.limits.read_timeout
            )
        except asyncio.TimeoutError:
            return b""
        except (ConnectionError, OSError):
            return b""
        self._account(len(data))
        return data

    async def send(self, payload: str | bytes) -> bool:
        """Write ``payload`` to the peer and flush. Returns success."""
        if isinstance(payload, str):
            payload = payload.encode("latin-1", errors="replace")
        try:
            self.writer.write(payload)
            await self.writer.drain()
            return True
        except (ConnectionError, OSError):
            return False


class BaseService:
    """Abstract TCP decoy service built on :func:`asyncio.start_server`."""

    #: Registry key used in configuration (``type:``). Set by subclasses.
    service_type: str = ""
    #: Default banner used when the config does not override it.
    default_banner: str | None = None
    transport: str = "tcp"

    def __init__(self, config: ServiceConfig, context: ServiceContext) -> None:
        self.config = config
        self.context = context
        self.name = config.name
        self._server: asyncio.base_events.Server | None = None
        self._sessions: set[asyncio.Task[None]] = set()

    @property
    def banner(self) -> str | None:
        return self.config.banner if self.config.banner is not None else self.default_banner

    def option(self, key: str, default: Any = None) -> Any:
        return self.config.options.get(key, default)

    @property
    def bound_port(self) -> int | None:
        """The first port the listener is bound to, or ``None`` if not started.

        Useful when binding to port 0 to let the OS choose an ephemeral port.
        """
        if self._server is None or not self._server.sockets:
            return None
        return self._server.sockets[0].getsockname()[1]

    async def start(self) -> None:
        """Bind and begin accepting connections."""
        self._server = await asyncio.start_server(
            self._on_connect,
            host=self.config.host,
            port=self.config.port,
            limit=self.context.limits.max_line_bytes,
            backlog=self.context.limits.backlog,
        )
        self.context.logger.info(
            "service %s (%s) listening on %s:%d",
            self.name,
            self.service_type,
            self.config.host,
            self.config.port,
        )

    async def stop(self) -> None:
        """Stop accepting connections and cancel in-flight sessions."""
        if self._server is not None:
            self._server.close()
            try:
                await self._server.wait_closed()
            except Exception:  # pragma: no cover - best-effort shutdown
                pass
        for task in list(self._sessions):
            task.cancel()
        if self._sessions:
            await asyncio.gather(*self._sessions, return_exceptions=True)

    async def _on_connect(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        task = asyncio.current_task()
        if task is not None:
            self._sessions.add(task)
        try:
            await self._serve(reader, writer)
        finally:
            if task is not None:
                self._sessions.discard(task)

    async def _serve(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer = writer.get_extra_info("peername") or ("unknown", 0)
        sock = writer.get_extra_info("sockname") or ("unknown", self.config.port)
        src_ip, src_port = str(peer[0]), int(peer[1]) if len(peer) > 1 else 0
        dst_port = int(sock[1]) if len(sock) > 1 else self.config.port

        session = Session(self, reader, writer, src_ip, src_port, dst_port)
        self.context.metrics.record_connection(self.name, self.transport)

        limiter = self.context.rate_limiter
        if limiter is not None and not limiter.allow(src_ip):
            self.context.metrics.record_rate_limited(self.name)
            session.emit(EventType.RATE_LIMITED, "connection rate limited")
            await self._close(writer)
            return

        self.context.metrics.connection_opened(self.name)
        session.emit(EventType.CONNECTION_OPEN, "connection opened")
        try:
            await asyncio.wait_for(
                self.handle(session), self.context.limits.session_timeout
            )
        except asyncio.TimeoutError:
            session.emit(EventType.CONNECTION_CLOSE, "session timed out")
        except asyncio.CancelledError:
            raise
        except (ConnectionError, OSError):
            session.emit(EventType.CONNECTION_CLOSE, "connection reset")
        except Exception as exc:  # pragma: no cover - defensive
            self.context.logger.exception(
                "unhandled error in service %s: %s", self.name, exc
            )
            session.emit(EventType.PROTOCOL_ERROR, f"internal error: {exc!r}")
        else:
            session.emit(EventType.CONNECTION_CLOSE, "connection closed")
        finally:
            self.context.metrics.connection_closed(self.name)
            await self._close(writer)

    @staticmethod
    async def _close(writer: asyncio.StreamWriter) -> None:
        try:
            writer.close()
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass

    async def handle(self, session: Session) -> None:
        """Drive the protocol exchange. Implemented by subclasses."""
        raise NotImplementedError
