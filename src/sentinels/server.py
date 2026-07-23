"""Server orchestration.

Builds the shared :class:`~sentinels.services.base.ServiceContext`, starts
every enabled decoy plus the Prometheus exposition endpoint, and runs until a
shutdown signal is received. Shutdown is graceful: listeners stop accepting,
in-flight sessions are cancelled, and the metrics server is closed.
"""

from __future__ import annotations

import asyncio
import signal
from typing import Any

from . import __version__
from .config import Config
from .logging_setup import get_app_logger
from .metrics import Metrics, serve_metrics
from .ratelimit import RateLimiter
from .services import BaseService, ServiceContext, create_service
from .sinks import LoggingEventSink


class SentinelsServer:
    """Lifecycle manager for a running honeypot node."""

    def __init__(self, config: Config, metrics: Metrics | None = None) -> None:
        self.config = config
        self.logger = get_app_logger()
        self.metrics = metrics or Metrics()
        self._services: list[BaseService] = []
        self._metrics_server: Any = None
        self._stop_event: asyncio.Event | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._keepalive: asyncio.Task[None] | None = None

    def serve(self) -> int:
        """Run the server to completion. Returns a process exit code."""
        try:
            return asyncio.run(self._run())
        except KeyboardInterrupt:  # pragma: no cover - interactive only
            self.logger.info("interrupted; shutting down")
            return 0

    async def _run(self) -> int:
        self._loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()
        self._install_signal_handlers()

        started = await self._start_services()
        if not started:
            self.logger.error("no enabled services could be started; exiting")
            return 1

        self._start_metrics()
        self.logger.info(
            "sentinels %s ready: %d service(s) active on node %r",
            __version__,
            len(started),
            self.config.node_id,
        )
        try:
            await self._stop_event.wait()
        except asyncio.CancelledError:  # pragma: no cover - defensive
            pass
        finally:
            await self._shutdown()
        return 0

    async def _start_services(self) -> list[BaseService]:
        context = self._build_context()
        started: list[BaseService] = []
        for svc_config in self.config.services:
            if not svc_config.enabled:
                self.logger.info("service %s disabled; skipping", svc_config.name)
                continue
            service = create_service(svc_config, context)
            try:
                await service.start()
            except OSError as exc:
                self.logger.error(
                    "failed to bind %s on %s:%d: %s",
                    svc_config.name,
                    svc_config.host,
                    svc_config.port,
                    exc,
                )
                continue
            started.append(service)
        self._services = started
        return started

    def _build_context(self) -> ServiceContext:
        rate_limiter = None
        if self.config.rate_limit.enabled:
            rate_limiter = RateLimiter(
                self.config.rate_limit.max_events_per_minute,
                self.config.rate_limit.burst,
            )
        sink = LoggingEventSink(self.metrics)
        return ServiceContext(
            node_id=self.config.node_id,
            metrics=self.metrics,
            sink=sink,
            limits=self.config.limits,
            rate_limiter=rate_limiter,
            logger=self.logger,
        )

    def _start_metrics(self) -> None:
        if not self.config.metrics.enabled:
            return
        try:
            result = serve_metrics(
                self.config.metrics.host,
                self.config.metrics.port,
                self.metrics.registry,
            )
        except OSError as exc:
            self.logger.error(
                "failed to start metrics endpoint on %s:%d: %s",
                self.config.metrics.host,
                self.config.metrics.port,
                exc,
            )
            return
        # prometheus_client >= 0.19 returns (server, thread); older returns None.
        if isinstance(result, tuple) and result:
            self._metrics_server = result[0]
        self.logger.info(
            "metrics endpoint on http://%s:%d/metrics",
            self.config.metrics.host,
            self.config.metrics.port,
        )

    async def _shutdown(self) -> None:
        if self._keepalive is not None:
            self._keepalive.cancel()
        self.logger.info("stopping %d service(s)", len(self._services))
        await asyncio.gather(
            *(svc.stop() for svc in self._services), return_exceptions=True
        )
        if self._metrics_server is not None:
            try:
                self._metrics_server.shutdown()
            except Exception:  # pragma: no cover - best-effort
                pass
        self.logger.info("shutdown complete")

    # -- signal handling -------------------------------------------------
    def _install_signal_handlers(self) -> None:
        assert self._loop is not None
        for sig in self._shutdown_signals():
            try:
                self._loop.add_signal_handler(sig, self._request_stop)
            except (NotImplementedError, RuntimeError, ValueError):
                # Windows does not support add_signal_handler; fall back to the
                # synchronous handler plus a keepalive tick that lets the
                # interpreter service the signal promptly.
                try:
                    signal.signal(sig, self._signal_fallback)
                except (ValueError, OSError):  # pragma: no cover - platform
                    continue
                if self._keepalive is None:
                    self._keepalive = asyncio.ensure_future(self._tick())

    @staticmethod
    def _shutdown_signals() -> tuple[int, ...]:
        sigs = [signal.SIGINT]
        term = getattr(signal, "SIGTERM", None)
        if term is not None:
            sigs.append(term)
        return tuple(sigs)

    def _signal_fallback(self, signum: int, frame: Any) -> None:  # pragma: no cover
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._request_stop)

    def _request_stop(self) -> None:
        if self._stop_event is not None and not self._stop_event.is_set():
            self.logger.info("shutdown requested")
            self._stop_event.set()

    async def _tick(self) -> None:  # pragma: no cover - platform specific
        try:
            while True:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass
