# Honeytrace

A lightweight, high-signal honeypot framework. Honeytrace stands up plausible
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
  brings up Honeytrace, Prometheus, and Grafana together.

## Architecture

```
                          ┌──────────────────────────────┐
   attackers  ──tcp──▶    │  Honeytrace node             │
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
| Honeytrace  | ports 2222 / 2323 / 2121 / 8080  | the decoys (see note below)        |
| Prometheus  | http://localhost:9090            | scrapes the node every 15s         |
| Grafana     | http://localhost:3000            | dashboard "Honeytrace Overview"    |

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

honeytrace validate -c config/honeytrace.yml
honeytrace run -c config/honeytrace.yml
```

Useful commands:

```bash
honeytrace list-services      # print registered decoy types
honeytrace validate -c FILE   # validate a config and exit
honeytrace run -c FILE        # run the honeypot
```

Configuration is resolved from `-c/--config`, then `$HONEYTRACE_CONFIG`, then
`config/honeytrace.yml`, then `/etc/honeytrace/honeytrace.yml`.

## Configuration

See [`config/honeytrace.yml`](config/honeytrace.yml) for a fully commented
example. Top-level sections:

| Section       | Purpose                                                        |
| ------------- | ------------------------------------------------------------- |
| `node_id`     | Identifier stamped onto every event.                          |
| `logging`     | Levels, console mirroring, file paths, and rotation.          |
| `metrics`     | Prometheus exposition endpoint bind address.                  |
| `limits`      | Session/read timeouts and per-line / per-session byte caps.   |
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

Environment overrides (handy in containers): `HONEYTRACE_NODE_ID`,
`HONEYTRACE_LOG_LEVEL`, `HONEYTRACE_METRICS_PORT`, `HONEYTRACE_EVENT_LOG`,
`HONEYTRACE_CONFIG`.

## Event schema

Each line in the event log is one JSON object:

```json
{
  "timestamp": "2026-07-23T17:25:25.002+00:00",
  "node_id": "honeytrace-01",
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
| `honeytrace_connections_total`      | counter | `service`, `transport` |
| `honeytrace_events_total`           | counter | `service`, `event_type`|
| `honeytrace_login_attempts_total`   | counter | `service`              |
| `honeytrace_bytes_received_total`   | counter | `service`              |
| `honeytrace_rate_limited_total`     | counter | `service`              |
| `honeytrace_active_connections`     | gauge   | `service`              |
| `honeytrace_build_info`             | info    | `version`              |

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
src/honeytrace/          framework package
  services/              decoy implementations + registry
  config.py              typed config loading & validation
  events.py              event model
  metrics.py             Prometheus collectors
  ratelimit.py           token-bucket limiter
  server.py              lifecycle orchestration
  cli.py                 command-line interface
infra/                   Prometheus config + Grafana provisioning/dashboards
config/                  example configuration
tests/                   test suite
Dockerfile               non-root runtime image
docker-compose.yml       Honeytrace + Prometheus + Grafana stack
```

## License

Released under the [MIT License](LICENSE).
