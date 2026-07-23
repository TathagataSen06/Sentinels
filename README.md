# Sentinels

A lightweight, high-signal honeypot framework. Sentinels stands up plausible
decoy services on the ports attackers probe, records every interaction as a
structured JSON event, and exposes aggregate telemetry over Prometheus for
dashboards and alerting.

Because nothing legitimate should ever talk to a decoy, **every event is
signal** — a single connection is worth investigating. That property makes
honeypots one of the highest fidelity, lowest-noise detection sources you can
run.

## Features

- **Async core.** All services run on a single `asyncio` event loop — no
  thread-per-connection, low memory footprint, thousands of concurrent peers.
- **Five decoys out of the box:** `ssh`, `telnet`, `ftp`, `http`, and a
  `generic` TCP catch-all for arbitrary ports.
- **Credential capture.** Telnet/FTP login prompts, HTTP Basic auth, and HTML
  form posts are parsed and recorded as `login_attempt` events.
- **Structured events.** One JSON document per line, stable schema, ready for
  ingestion by Loki, Elasticsearch, or any SIEM.
- **Prometheus metrics.** Low-cardinality counters and gauges with a ready-made
  Grafana dashboard.
- **Safe under fire.** Per-source token-bucket rate limiting, per-read and
  per-session timeouts, and hard byte caps protect the node from resource
  exhaustion during scanning storms.
- **Strict config validation.** Unknown keys, port clashes, and type errors are
  rejected at load time, not at 3 a.m.
- **Container-native.** Runs as a non-root user; a one-command Compose stack
  brings up Sentinels, Prometheus, and Grafana together.

## Architecture

```
                          ┌──────────────────────────────┐
   attackers  ──tcp──▶    │  Sentinels node             │
                          │                              │
                          │  asyncio listeners           │
                          │   ssh / telnet / ftp / http   │
                          │   / generic                  │
                          │        │             │       │
                          │        ▼             ▼       │
                          │  JSON event log   /metrics    │
                          └────────┬─────────────┬───────┘
                                   │             │
                            forensics /      Prometheus ──▶ Grafana
                            SIEM ingest        (scrape)     (dashboard)
```

- **Event log** (`events.log`) — every interaction, high-cardinality detail
  (source IP, credentials, payload previews). This is your forensic record.
- **Metrics** (`/metrics`) — deliberately low-cardinality aggregates
  (per-service, per-event-type). Source IPs are **not** metric labels, which
  keeps Prometheus healthy when a botnet sprays millions of addresses.

## Quick start (Docker)

```bash
cp .env.example .env        # then edit Grafana credentials
docker compose up -d --build
```

This starts three services:

| Service     | URL                              | Notes                              |
| ----------- | -------------------------------- | ---------------------------------- |
| Sentinels  | ports 2222 / 2323 / 2121 / 8080  | the decoys (see note below)        |
| Prometheus  | http://localhost:9090            | scrapes the node every 15s         |
| Grafana     | http://localhost:3000            | dashboard "Sentinels Overview"    |

Captured events are written to `./data/logs/events.log` on the host.

> **Exposing real ports.** By default the Compose file maps non-privileged host
> ports so `docker compose up` never collides with your box's own SSH/HTTP. For
> a live deployment, remap the **host** side of each port to the real target,
> e.g. `"22:2222"`, `"23:2323"`, `"21:2121"`, `"80:8080"`, and make sure the
> host's own admin services listen elsewhere.

## Quick start (local)

Requires Python 3.10+.

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

sentinels validate -c config/sentinels.yml
sentinels run -c config/sentinels.yml
```

Useful commands:

```bash
sentinels list-services      # print registered decoy types
sentinels validate -c FILE   # validate a config and exit
sentinels run -c FILE        # run the honeypot
```

Configuration is resolved from `-c/--config`, then `$SENTINELS_CONFIG`, then
`config/sentinels.yml`, then `/etc/sentinels/sentinels.yml`.

## Configuration

See [`config/sentinels.yml`](config/sentinels.yml) for a fully commented
example. Top-level sections:

| Section       | Purpose                                                        |
| ------------- | ------------------------------------------------------------- |
| `node_id`     | Identifier stamped onto every event.                          |
| `logging`     | Levels, console mirroring, file paths, and rotation.          |
| `metrics`     | Prometheus exposition endpoint bind address.                  |
| `limits`      | Session/read timeouts, per-line / per-session byte caps, listen `backlog`. |
| `rate_limit`  | Per-source token bucket (`max_events_per_minute`, `burst`).   |
| `services`    | List of decoys to run.                                        |

Each service entry:

```yaml
- name: ssh          # unique label, appears in events and metrics
  type: ssh          # one of: ssh, telnet, ftp, http, generic
  host: 0.0.0.0
  port: 2222
  enabled: true
  banner: "SSH-2.0-OpenSSH_8.9p1"   # optional protocol banner
  options: {}        # service-specific options (see below)
```

Service options:

| Type      | Option        | Default   | Meaning                                    |
| --------- | ------------- | --------- | ------------------------------------------ |
| `telnet`  | `hostname`    | `server`  | Name shown in the `login:` prompt.         |
| `telnet`  | `max_attempts`| `3`       | Login prompts before disconnecting.        |
| `http`    | `title`       | —         | Title on the fake login page.              |
| `generic` | `max_reads`   | `4`       | Number of payload reads to record.         |
| `generic` | `banner_crlf` | `true`    | Append CRLF to the banner.                 |

Environment overrides (handy in containers): `SENTINELS_NODE_ID`,
`SENTINELS_LOG_LEVEL`, `SENTINELS_METRICS_PORT`, `SENTINELS_EVENT_LOG`,
`SENTINELS_CONFIG`.

## Event schema

Each line in the event log is one JSON object:

```json
{
  "timestamp": "2026-07-23T17:25:25.002+00:00",
  "node_id": "sentinels-01",
  "service": "telnet",
  "event_type": "login_attempt",
  "transport": "tcp",
  "src_ip": "203.0.113.7",
  "src_port": 51234,
  "dst_port": 23,
  "message": "credential submission",
  "data": { "username": "root", "password": "toor" }
}
```

Event types: `connection_open`, `connection_close`, `login_attempt`,
`http_request`, `banner`, `data`, `rate_limited`, `protocol_error`.

## Metrics

Exposed at `http://<metrics.host>:<metrics.port>/metrics`:

| Metric                              | Type    | Labels                 |
| ----------------------------------- | ------- | ---------------------- |
| `sentinels_connections_total`      | counter | `service`, `transport` |
| `sentinels_events_total`           | counter | `service`, `event_type`|
| `sentinels_login_attempts_total`   | counter | `service`              |
| `sentinels_bytes_received_total`   | counter | `service`              |
| `sentinels_rate_limited_total`     | counter | `service`              |
| `sentinels_active_connections`     | gauge   | `service`              |
| `sentinels_build_info`             | info    | `version`              |

## Performance

The numbers below are **measured, not estimated** — reproduce them with the
harness in [`benchmarks/`](benchmarks/). Each decoy interaction is a full
connect → banner → (optional exchange) → close cycle with structured event
logging enabled and written to disk.

**Test environment:** AMD Ryzen 7 7445HS (6 cores / 12 threads), Windows 11,
CPython 3.11 (asyncio `ProactorEventLoop`), loopback networking. Rate limiting
was disabled for these runs to measure the server's ceiling rather than the
per-source limiter. A single Sentinels event loop was under test.

| Metric | Result | Notes |
| ------ | ------ | ----- |
| Idle memory (RSS) | **~33 MB** | Interpreter + asyncio + metrics endpoint |
| Baseline latency (unloaded) | **~0.8 ms** min, ~15 ms median | Sequential connect/banner/close |
| Sustained throughput | **~1,000 conn/s** (855–1,086 across runs) | One event loop; saturates ~1 CPU core at this rate |
| In-flight latency @ 100 concurrent | **p50 ~94 ms**, p95 ~130 ms | Full interaction incl. event logging |
| Concurrency capacity | **3,000 simultaneous connections** in ~216 MB (~74 KB/conn) | Long-lived held connections |

**Validated against the server's own telemetry.** In a mixed run driving 10,963
connections, the `/metrics` counters reported exactly `connections_total=10963`
and `events_total=21926` — precisely two lifecycle events (open + close) per
connection, matching the load generator's completed count with zero drift. The
accounting is exact under load, not sampled.

**Scaling model.** asyncio is single-threaded, so one instance saturates one CPU
core (observed ~96% of a core at ceiling). Scale **horizontally**: run one
instance per core / per decoy port range (the provided Compose service scales
cleanly to replicas), each exporting its own metrics for Prometheus to aggregate.
The Linux/epoll deployment target (the Docker image) typically sustains higher
throughput and lower per-connection memory than the Windows loopback figures
above. In production the per-source rate limiter — off for this ceiling test —
caps any single abusive source to a configured burst, so real single-origin load
is bounded by design regardless of raw capacity.

## Security considerations

- **Isolate the node.** A honeypot is deliberately attacked. Run it in a
  segmented network with no path to production systems or secrets.
- **Low interaction by design.** The SSH decoy performs only the identification
  exchange; no service exposes a shell, filesystem, or real authentication.
  This bounds the attack surface of the honeypot itself.
- **Least privilege.** The container runs as a non-root user and binds only
  high ports internally; low ports are mapped in by the host.
- **Change Grafana credentials** before exposing port 3000, and keep Prometheus
  and Grafana off the public internet.

## Development

```bash
pip install -e ".[dev]"
pytest            # run the test suite
ruff check .      # lint
```

The test suite drives every decoy over a real loopback socket and asserts on
both emitted events and Prometheus metrics.

## Project layout

```
src/sentinels/          framework package
  services/              decoy implementations + registry
  config.py              typed config loading & validation
  events.py              event model
  metrics.py             Prometheus collectors
  ratelimit.py           token-bucket limiter
  server.py              lifecycle orchestration
  cli.py                 command-line interface
infra/                   Prometheus config + Grafana provisioning/dashboards
config/                  example configuration
benchmarks/              reproducible load-test harness
tests/                   test suite
Dockerfile               non-root runtime image
docker-compose.yml       Sentinels + Prometheus + Grafana stack
```

## License

Released under the [MIT License](LICENSE).
