# 🛡️ Sentinels

### Enterprise Deception Technology & Threat Intelligence Platform

Distributed deception sensors, real-time stream processing, MITRE ATT&CK correlation, and threat intelligence enrichment for detecting post-compromise attacker activity at scale.

---

## Overview

Sentinels is a cloud-native deception platform designed to identify attackers after they gain access to internal environments.

Instead of generating massive volumes of noisy telemetry, Sentinels deploys deceptive assets such as honeypots and canary credentials, then focuses on the high-signal interactions that indicate real attacker behavior.

The platform combines:

* Distributed deception sensors
* Real-time event streaming
* Threat intelligence enrichment
* Sigma-inspired detection rules
* MITRE ATT&CK mapping
* Stateful attack correlation

to transform attacker activity into actionable security incidents.

---

## Engineering Highlights

### Distributed Systems

* Event-driven architecture using Apache Kafka
* Stateful stream processing with Apache Flink
* Protocol Buffers for schema-driven telemetry
* Horizontally scalable sensor infrastructure

### Security Engineering

* Zero-Trust sensor enrollment
* mTLS-based authentication
* Keycloak-based identity management
* MITRE ATT&CK detection mapping

### Detection & Response

* Sigma-inspired YAML rule engine
* Threat intelligence enrichment
* Stateful multi-stage attack correlation
* Canary credential tracking

### Cloud Native Infrastructure

* Kubernetes-ready architecture
* Containerized microservices
* OpenTelemetry observability
* OpenSearch analytics pipeline

---

## Architecture

```text
Sensors
    │
    ▼
Envoy Gateway
    │
    ▼
Kafka + Protobuf
    │
    ▼
Apache Flink
    │
 ┌──┴─────────────┐
 ▼                ▼
Threat Intel      Sigma Rule Engine
Enrichment        MITRE ATT&CK Mapping
 │                │
 └──────┬─────────┘
        ▼
Incident Correlation
        │
        ▼
OpenSearch
        │
        ▼
SOC Dashboard
```

---

## Key Capabilities

### Distributed Sensor Platform

* Secure mTLS enrollment
* Adaptive heartbeat scheduling
* Offline telemetry buffering
* Persistent device identity
* Plugin-based architecture

### Deception Framework

* SSH Honeypots
* HTTP Honeypots
* Canary Credentials
* Extensible deception plugins

### Detection Engine

* Real-time Kafka ingestion
* Flink stream processing
* Sigma-style rule evaluation
* MITRE ATT&CK tagging
* Stateful attack correlation

### Threat Intelligence

* IOC extraction
* Reputation scoring
* Threat enrichment pipeline
* Redis-backed threat cache

---

## Technology Stack

| Layer          | Technology                         |
| -------------- | ---------------------------------- |
| Backend        | FastAPI, Python                    |
| Streaming      | Apache Kafka                       |
| Processing     | Apache Flink                       |
| Serialization  | Protocol Buffers                   |
| Analytics      | OpenSearch                         |
| Database       | PostgreSQL                         |
| Cache          | Redis                              |
| Identity       | Keycloak                           |
| Gateway        | Envoy                              |
| Storage        | MinIO                              |
| Infrastructure | Docker, Kubernetes                 |
| Observability  | Prometheus, Grafana, OpenTelemetry |

---

## Scalability Goals

Designed to support:

* 100,000+ Distributed Sensors
* 1,000,000+ Events Per Minute
* Multi-Tenant Deployments
* Multi-Region Architectures
* Petabyte-Scale Telemetry Retention

---

## Engineering Challenges Solved

### Zero-Trust Device Identity

Implemented secure sensor enrollment using bootstrap tokens, certificate signing requests (CSRs), and mTLS authentication.

### High-Volume Telemetry Processing

Designed a Kafka → Flink pipeline capable of processing large-scale event streams while maintaining low-latency detection.

### Attack Correlation

Correlated attacker activity across multiple protocols and sensors to reconstruct attack chains and reduce alert fatigue.

### Schema Evolution

Introduced Protocol Buffers and schema-driven event processing to support long-term telemetry compatibility.

### Threat Intelligence Enrichment

Built enrichment workflows that transform raw attacker telemetry into contextualized security intelligence.

---

## Repository Structure

```text
apps/
├── sensor-agent/
├── sensor-management/
├── detection-engine/
├── threat-intel-service/
├── soc-dashboard/

infra/
├── kubernetes/
├── helm/
├── monitoring/
├── kafka/

libs/
├── protobuf/
├── sdk/
├── shared/

plugins/
├── ssh/
├── http/
├── canary/
```

---

## Why This Project Matters

Modern security platforms require expertise across multiple domains:

* Distributed Systems
* Stream Processing
* Security Engineering
* Threat Intelligence
* Cloud Infrastructure
* Detection Engineering

Sentinels was built to explore the challenges of designing an end-to-end security platform that combines all of these disciplines into a single cloud-native architecture.

---

## Current Focus

* SOC Dashboard
* Threat Hunting Workflows
* MITRE ATT&CK Visualizations
* Incident Management
* Multi-Tenant Security Operations

---

**Built to explore large-scale security platform engineering, detection pipelines, and cloud-native security architectures.**
