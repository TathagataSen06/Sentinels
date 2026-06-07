# 🛡️ Sentinels — Enterprise Deception & Threat Intelligence Platform

<p align="center">
  <b>Distributed Deception Technology • Threat Detection • Stream Processing • Cloud-Native Security</b>
</p>

<p align="center">
A production-grade deception platform designed to detect, enrich, correlate, and investigate attacker activity across distributed environments using honeypots, canary assets, threat intelligence, and real-time stream processing.
</p>

---

## Why Sentinels?

Traditional security tools generate enormous amounts of noisy telemetry.

Sentinels takes a different approach:

Instead of attempting to monitor every system, it deploys deceptive assets, honeypots, and canary credentials throughout an environment and only generates alerts when an attacker interacts with those resources.

The platform combines:

* Distributed deception sensors
* Real-time event streaming
* MITRE ATT&CK mapping
* Threat intelligence enrichment
* Multi-stage attack correlation
* Enterprise-scale telemetry processing

to transform attacker interactions into actionable security incidents.

---

## Key Highlights

### Distributed Sensor Platform

* Secure sensor enrollment using mTLS
* Adaptive heartbeat management
* Offline telemetry buffering
* Persistent sensor identity
* Plugin-based architecture

### Multi-Protocol Deception

* SSH Honeypots
* HTTP Honeypots
* Canary Credentials
* Extensible plugin framework for SMB, Database, FTP, and future protocols

### Real-Time Detection Pipeline

* Apache Kafka event streaming
* Apache Flink stream processing
* Sigma-inspired YAML detection rules
* Stateful attack correlation
* MITRE ATT&CK enrichment

### Threat Intelligence

* AbuseIPDB integration
* VirusTotal integration
* Redis-backed IOC caching
* Automated enrichment pipeline

### Enterprise Security

* mTLS everywhere
* Keycloak Identity Provider
* OIDC / OAuth2 / SAML
* Role-Based Access Control
* Zero-Trust Sensor Registration

### Cloud Native

* Kubernetes-ready
* Dockerized microservices
* GitOps-compatible architecture
* Horizontal scalability

---

# Architecture

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

# Technology Stack

| Layer               | Technologies                       |
| ------------------- | ---------------------------------- |
| Backend             | FastAPI, Python 3.11               |
| Streaming           | Apache Kafka, Kafka Connect        |
| Processing          | Apache Flink                       |
| Serialization       | Protocol Buffers                   |
| Search & Analytics  | OpenSearch                         |
| Database            | PostgreSQL                         |
| Cache               | Redis                              |
| Object Storage      | MinIO                              |
| Identity & Access   | Keycloak                           |
| API Gateway         | Envoy                              |
| Infrastructure      | Docker, Kubernetes                 |
| Observability       | Prometheus, Grafana, OpenTelemetry |
| Detection           | Sigma-style Rule Engine            |
| Threat Intelligence | AbuseIPDB, VirusTotal              |

---

# System Capabilities

### Zero-Trust Sensor Enrollment

Each sensor:

1. Authenticates using a bootstrap token
2. Generates a CSR
3. Receives a signed client certificate
4. Establishes mTLS communication

This prevents unauthorized sensors from entering the platform.

---

### Event Streaming Pipeline

Raw attacker activity is transformed through multiple stages:

```text
Raw Event
    ↓
Normalization
    ↓
Threat Intel Enrichment
    ↓
MITRE ATT&CK Mapping
    ↓
Rule Evaluation
    ↓
Correlation
    ↓
Incident Generation
```

---

### Sigma-Inspired Detection Engine

Detection logic is defined using YAML rules rather than hardcoded Python.

Example:

```yaml
title: SSH Brute Force

selection:
  event_type: ssh.login.attempt

severity: high

mitre:
  technique: T1110
```

New detections can be deployed without modifying application code.

---

### Stateful Attack Correlation

The platform correlates attacker behavior across multiple services.

Example:

```text
HTTP Reconnaissance
      ↓
SSH Authentication Attempts
      ↓
Canary Credential Access
      ↓
High-Severity Incident
```

This dramatically reduces alert fatigue while improving detection fidelity.

---

# Repository Structure

```text
apps/
├── sensor-agent/
├── sensor-management/
├── detection-engine/
├── threat-intel-service/

infra/
├── kubernetes/
├── helm/
├── envoy/
├── kafka/
├── monitoring/

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

# Scalability Targets

Designed for:

* 100,000+ Sensors
* 1,000,000+ Events / Minute
* Multi-Tenant Deployments
* Multi-Region Architectures
* Petabyte-Scale Telemetry Retention

---

# Engineering Challenges Solved

* Distributed sensor management
* Secure certificate-based enrollment
* Real-time stream processing
* Stateful attack correlation
* Threat intelligence enrichment
* Rule-driven detections
* Event schema evolution
* High-volume telemetry pipelines
* Cloud-native deployment patterns

---

# Future Roadmap

* SMB Honeypots
* Database Honeypots
* Attack Graph Visualization
* ATT&CK Heatmaps
* Threat Hunting Dashboard
* Cross-Sensor Correlation
* Multi-Tenant SaaS Platform
* Purple-Team Simulation Engine

---

# Why This Project Matters

Sentinels was built to explore the challenges of designing a cloud-native security platform capable of processing high-volume telemetry from distributed deception sensors.

The project combines:

- Distributed systems engineering
- Stream processing
- Security engineering
- Threat intelligence
- Cloud-native infrastructure
- Detection and response workflows

into a single end-to-end platform.
