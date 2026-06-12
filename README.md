# 🛡️ Sentinels — Enterprise Deception & Threat Intelligence Platform

<p align="center">
  <b>Distributed Deception Technology • SOC Analyst Workflows • MITRE ATT&CK Mapping • Real-Time Stream Processing</b>
</p>

<p align="center">
A production-grade deception platform that detects, enriches, correlates, and investigates attacker activity across distributed environments using honeypots, canary assets, threat intelligence, and an interactive SOC dashboard purpose-built for security analysts.
</p>

---

## Why Sentinels?

Traditional security tools generate enormous volumes of noisy telemetry.

Sentinels takes a different approach: instead of monitoring every system, it deploys **deceptive assets** — honeypots, canary credentials, and fake services — throughout an environment and **only alerts when an attacker interacts with them**.

The platform combines:

* Distributed deception sensors with zero-trust enrollment
* Real-time event streaming and correlation
* MITRE ATT&CK mapping across the full kill chain
* Threat intelligence enrichment (AbuseIPDB, VirusTotal, GreyNoise)
* An interactive SOC dashboard with attack-chain visualization, threat hunting, and incident investigation

to transform raw attacker interactions into actionable, correlated security incidents.

---

## SOC Dashboard

The Sentinels dashboard is a full-featured **Security Operations Center** interface built with Next.js 16, React 19, and Tailwind CSS. It is designed to be demonstrated to recruiters, engineers, judges, and security professionals within 2–3 minutes.

### Pages & Features

| Page | Description |
|---|---|
| **Global Dashboard** | Real-time KPIs (active incidents, events/min, sensor count), incident trend charts, and a live WebSocket activity stream |
| **Incident Management** | Sortable incident table with severity badges, assignees, MITRE tags, and one-click investigation links |
| **Incident Investigation** | 3-column war room — interactive attack-chain graph (React Flow), event timeline, raw log viewer, analyst notes, and threat intel sidebar |
| **Threat Hunting** | SIEM-style query interface with saved searches, expandable raw JSON rows, IOC pivot buttons, and quick stats |
| **MITRE ATT&CK Dashboard** | ATT&CK trend area chart, detection coverage bar chart, and a full technique heatmap with deterministic color-coded hit counts |
| **Threat Intel Center** | IOC enrichment across AbuseIPDB, VirusTotal, and GreyNoise with environmental observation table |
| **Sensor Fleet Management** | Fleet overview with health status, plugin badges, version tracking, heartbeat monitoring, and provisioning controls |
| **Administration** | Multi-tenant user management, RBAC configuration, organization setup, and API key management |

### Interactive Attack-Chain Graph

The crown jewel of the dashboard is the **Alert Correlation Graph** — an interactive, draggable, zoomable node-based visualization built with `@xyflow/react` (React Flow) that maps an attacker's progression through the MITRE ATT&CK kill chain:

```
Attacker IP → Reconnaissance → Credential Access → Command Execution → Incident
```

Each node displays the MITRE technique ID, source details, and severity. Edges are color-coded and animated to show the attack flow direction.

---

## Architecture

```text
Sensors (SSH, HTTP, Canary Credentials)
    │
    ▼
Envoy Gateway (mTLS)
    │
    ▼
Kafka + Protobuf
    │
    ▼
Apache Flink (Stream Processing)
    │
 ┌──┴─────────────┐
 ▼                ▼
Threat Intel      Sigma Rule Engine
Enrichment        MITRE ATT&CK Mapping
 │                │
 └──────┬─────────┘
        ▼
Incident Correlation (Redis-backed)
        │
        ▼
FastAPI REST API (PostgreSQL)
        │
        ▼
SOC Dashboard (Next.js 16 / React 19)
```

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 16, React 19, Tailwind CSS 4, Recharts, React Flow, Framer Motion |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy (async), Pydantic v2 |
| **Streaming** | Apache Kafka, Kafka Connect |
| **Processing** | Apache Flink, Redis Streams |
| **Serialization** | Protocol Buffers (Protobuf) |
| **Search & Analytics** | OpenSearch |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Identity & Access** | Keycloak (OIDC / OAuth2 / SAML), RBAC |
| **API Gateway** | Envoy |
| **Infrastructure** | Docker, Kubernetes, Helm |
| **Observability** | Prometheus, Grafana, OpenTelemetry |
| **Detection** | Sigma-style YAML Rule Engine |
| **Threat Intelligence** | AbuseIPDB, VirusTotal, GreyNoise |

---

## Key Highlights

### Distributed Sensor Platform

* Secure sensor enrollment using mTLS and zero-trust bootstrap tokens
* Adaptive heartbeat management with offline telemetry buffering
* Persistent sensor identity with certificate-based authentication
* Plugin-based architecture for extensible protocol support

### Multi-Protocol Deception

* **SSH Honeypots** — Brute-force detection and credential harvesting
* **HTTP Honeypots** — Reconnaissance and web attack surface simulation
* **Canary Credentials** — Planted tokens that trigger high-fidelity alerts on use
* Extensible plugin framework for SMB, Database, FTP, and future protocols

### Real-Time Detection Pipeline

```text
Raw Event → Normalization → Threat Intel Enrichment → MITRE ATT&CK Mapping → Rule Evaluation → Correlation → Incident
```

* Apache Kafka event streaming with Protobuf serialization
* Apache Flink stateful stream processing
* Sigma-inspired YAML detection rules (deploy without code changes)
* Multi-stage attack correlation across sensors and time windows

### Sigma-Inspired Detection Engine

Detection logic is defined using declarative YAML rules:

```yaml
title: SSH Brute Force
selection:
  event_type: ssh.login.attempt
severity: high
mitre:
  technique: T1110
```

New detections can be deployed without modifying application code.

### Stateful Attack Correlation

The platform correlates attacker behavior across multiple services and time windows:

```text
HTTP Reconnaissance → SSH Brute Force → Canary Credential Access → High-Severity Incident
```

This reduces alert fatigue while dramatically improving detection fidelity.

---

## Repository Structure

```text
apps/
├── api-server/            # FastAPI REST API (PostgreSQL, Redis, auth)
├── soc-dashboard/         # Next.js 16 SOC analyst dashboard
├── sensor-agent/          # Distributed deception sensor agent
├── sensor-management/     # Sensor enrollment & lifecycle management
├── detection-engine/      # Sigma rule engine & MITRE mapping
├── processing-engine/     # Redis Streams correlation engine
├── threat-intel-service/  # IOC enrichment (AbuseIPDB, VirusTotal)
├── schemas/               # Protobuf event schemas
└── load-tester/           # Performance testing harness

infra/
├── docker-compose.yml     # Full local deployment
├── prometheus/            # Metrics collection
├── grafana/               # Dashboards & alerting
└── kubernetes/            # K8s manifests (Helm-ready)

libs/                      # Shared libraries & SDK
plugins/                   # Deception protocol plugins (SSH, HTTP, Canary)
legacy/                    # Original Sentinels legacy code
```

---

## Quick Start

### Prerequisites

* Docker & Docker Compose
* Node.js 20+ (for the dashboard)

### Start the Backend

```bash
# From the project root
cd infra
docker compose up -d
```

This brings up PostgreSQL, Redis, the API server, the processing engine, Prometheus, and Grafana.

| Service | URL |
|---|---|
| API Docs | http://localhost:8000/docs |
| Grafana | http://localhost:3000 (admin/admin) |
| Prometheus | http://localhost:9090 |

### Start the Dashboard

```bash
cd apps/soc-dashboard
npm install
npm run dev
```

The SOC dashboard will be available at **http://localhost:3000**.

---

## Scalability Targets

* **100,000+** sensors
* **1,000,000+** events per minute
* Multi-tenant deployments with strict data isolation
* Multi-region architectures
* Petabyte-scale telemetry retention

---

## Engineering Challenges Solved

* Distributed sensor management with zero-trust enrollment
* Secure certificate-based mTLS communication
* Real-time stream processing at scale
* Stateful multi-stage attack correlation
* Threat intelligence enrichment pipelines
* Declarative rule-driven detection engine
* Event schema evolution with Protobuf
* High-volume telemetry pipelines (Kafka + Flink)
* Cloud-native deployment patterns (Docker, K8s, Helm)
* Interactive attack-chain visualization (React Flow)
* SOC analyst workflow design (investigation, hunting, triage)

---

## Future Roadmap

* SMB & Database Honeypots
* Cross-Sensor Attack Graph Correlation
* Purple-Team Simulation Engine
* Automated Response Playbooks (SOAR)
* Multi-Tenant SaaS Mode
* Framer Motion page transitions & micro-animations

---

## Why This Project Matters

Sentinels was built to explore the full-stack challenges of designing a cloud-native security platform — from distributed sensor management and real-time stream processing to interactive analyst workflows and attack-chain visualization.

The project combines:

- **Distributed systems engineering** — sensor fleet, mTLS, heartbeats
- **Stream processing** — Kafka, Flink, Redis Streams
- **Security engineering** — honeypots, canary credentials, MITRE ATT&CK
- **Threat intelligence** — IOC enrichment, reputation scoring
- **Cloud-native infrastructure** — Docker, Kubernetes, Helm, GitOps
- **Frontend engineering** — React Flow graphs, Recharts analytics, responsive dark-mode UI
- **Detection & response workflows** — incident investigation, threat hunting, correlation

into a single end-to-end platform that can be demonstrated in under 3 minutes.
