# Benchmarks

A dependency-free load-test harness for measuring Sentinels throughput,
latency, and concurrency capacity. Results in the top-level README's
[Performance](../README.md#performance) section were produced with these tools.

## Files

- `loadtest.py` — standard-library load generator (`throughput` and `hold` modes)
- `sentinels.bench.yml` — benchmark configuration (rate limiting **disabled** to
  measure the server ceiling; event logging on, written to `data/`; large listen
  backlog)

## Running

Start a node with the benchmark config in one shell:

```bash
sentinels run -c benchmarks/sentinels.bench.yml
```

Then drive load from another shell.

**Throughput + latency** — open `--total` short-lived connections at a bounded
`--concurrency`, each doing connect → read banner → close:

```bash
python benchmarks/loadtest.py throughput --port 9401 --total 4000 --concurrency 100
```

Emits JSON with `throughput_conn_per_s` and latency percentiles (p50/p95/p99).

**Concurrency capacity** — open `--total` connections and hold them open for
`--hold` seconds so you can sample the server's memory (e.g. via your process
monitor) while they are all established:

```bash
python benchmarks/loadtest.py hold --port 9402 --total 3000 --hold 6
```

## Validating results

Because rate limiting is off, the server should process every connection. Cross-
check the load generator's `completed` count against the server's own counters:

```bash
curl -s http://127.0.0.1:9199/metrics | grep -E 'sentinels_(connections|events)_total'
```

`events_total` should equal `2 × connections_total` (one `connection_open` and
one `connection_close` per connection), which confirms exact accounting with no
dropped or double-counted events.

## Notes on interpretation

- Sentinels runs a single asyncio event loop, so one instance saturates one CPU
  core. Scale horizontally by running multiple instances.
- On Windows, the client's ~16k ephemeral ports (and TIME_WAIT) cap how many
  short-lived connections a single load-generator process can open before
  connections are refused — keep per-run totals well under that ceiling, or run
  the generator on a separate host.
- Linux/epoll (the container deployment target) generally outperforms Windows
  loopback for both throughput and per-connection memory.
