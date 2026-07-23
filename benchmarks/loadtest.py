"""Load generator for Sentinels decoy services.

Two modes:

* ``throughput`` — open ``--total`` short-lived connections at a bounded
  ``--concurrency``, each performing a connect / read-banner / optional-send /
  close cycle. Reports connections-per-second and latency percentiles.
* ``hold`` — open ``--total`` connections and keep them open for ``--hold``
  seconds, so an external observer can sample the server's memory while a large
  number of connections are concurrently established.

The tool is intentionally dependency-free (standard library only) and prints a
single JSON object to stdout so results can be captured and compared over time.

Example::

    # in one shell, with rate limiting disabled for a ceiling measurement:
    sentinels run -c benchmarks/sentinels.bench.yml

    # in another:
    python benchmarks/loadtest.py throughput --port 9401 --total 4000 --concurrency 100
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time


async def _one_connection(
    host: str, port: int, payload: bytes, read_bytes: int, timeout: float
) -> tuple[float | None, str | None]:
    """Run a single connect/read/close cycle. Returns (latency, error_name)."""
    start = time.perf_counter()
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout
        )
    except (OSError, asyncio.TimeoutError) as exc:
        return None, type(exc).__name__
    try:
        try:
            await asyncio.wait_for(reader.read(read_bytes), timeout)
        except asyncio.TimeoutError:
            pass
        if payload:
            writer.write(payload)
            await writer.drain()
            try:
                await asyncio.wait_for(reader.read(read_bytes), timeout)
            except asyncio.TimeoutError:
                pass
        writer.close()
        try:
            await asyncio.wait_for(writer.wait_closed(), timeout)
        except (asyncio.TimeoutError, OSError):
            pass
        return time.perf_counter() - start, None
    except (OSError, asyncio.TimeoutError) as exc:
        return None, type(exc).__name__


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, min(len(ordered) - 1, round((pct / 100.0) * (len(ordered) - 1))))
    return ordered[rank]


async def _run_throughput(args: argparse.Namespace) -> dict:
    semaphore = asyncio.Semaphore(args.concurrency)
    payload = args.payload.encode("latin-1") if args.payload else b""
    latencies: list[float] = []
    errors: dict[str, int] = {}

    async def worker() -> None:
        async with semaphore:
            latency, error = await _one_connection(
                args.host, args.port, payload, args.read_bytes, args.timeout
            )
            if error is not None:
                errors[error] = errors.get(error, 0) + 1
            else:
                latencies.append(latency)  # type: ignore[arg-type]

    start = time.perf_counter()
    await asyncio.gather(*(asyncio.create_task(worker()) for _ in range(args.total)))
    duration = time.perf_counter() - start

    completed = len(latencies)
    return {
        "mode": "throughput",
        "target": f"{args.host}:{args.port}",
        "requested": args.total,
        "completed": completed,
        "errors": errors,
        "concurrency": args.concurrency,
        "duration_s": round(duration, 4),
        "throughput_conn_per_s": round(completed / duration, 1) if duration else 0.0,
        "latency_ms": {
            "mean": round(1000 * sum(latencies) / completed, 3) if completed else 0.0,
            "p50": round(1000 * _percentile(latencies, 50), 3),
            "p95": round(1000 * _percentile(latencies, 95), 3),
            "p99": round(1000 * _percentile(latencies, 99), 3),
            "max": round(1000 * max(latencies), 3) if latencies else 0.0,
        },
    }


async def _run_hold(args: argparse.Namespace) -> dict:
    writers = []
    errors: dict[str, int] = {}
    for _ in range(args.total):
        try:
            reader, writer = await asyncio.open_connection(args.host, args.port)
            try:
                await asyncio.wait_for(reader.read(args.read_bytes), args.timeout)
            except asyncio.TimeoutError:
                pass
            writers.append(writer)
        except (OSError, asyncio.TimeoutError) as exc:
            name = type(exc).__name__
            errors[name] = errors.get(name, 0) + 1

    # Signal readiness so an external sampler can measure the server now.
    print(json.dumps({"event": "held", "connections": len(writers)}), flush=True)
    await asyncio.sleep(args.hold)

    for writer in writers:
        writer.close()
    return {
        "mode": "hold",
        "target": f"{args.host}:{args.port}",
        "requested": args.total,
        "held": len(writers),
        "errors": errors,
        "hold_s": args.hold,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sentinels load generator")
    parser.add_argument("mode", choices=["throughput", "hold"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--total", type=int, default=4000)
    parser.add_argument("--concurrency", type=int, default=100)
    parser.add_argument("--payload", default="", help="optional bytes to send after banner")
    parser.add_argument("--read-bytes", type=int, default=256)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument(
        "--hold", type=float, default=5.0, help="hold mode: seconds to keep connections open"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    runner = _run_throughput if args.mode == "throughput" else _run_hold
    result = asyncio.run(runner(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
