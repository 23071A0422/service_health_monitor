# Lightweight Production-Style Service Health Monitor with Retry Logic and Alert Threshold Tuning

*A collaborative observability project engineered by G. Varun Sai Kumar and Theja Sri Kanagala.*

## 1. Motivation
In modern microservice architectures, localized failures are inevitable. Service monitoring matters because blind spots in infrastructure lead to silent outages and degraded user experiences. This project applies core Site Reliability Engineering (SRE) principles to solve the challenge of failure detection. It addresses the common pitfalls of naive health checkers—namely alert fatigue from network blips—by introducing stateful failure classification and exponential backoff, ensuring on-call engineers are only paged for actionable, sustained degradation.

## 2. Architecture
This standalone daemon is composed of modular engines, drawing architectural inspiration from established tools like Prometheus and Datadog:
* **Configuration Loader:** Ingests `endpoints.yaml` to dynamically manage targets and global thresholds without code deployments.
* **Monitoring Engine:** Handles the raw HTTP polling, capturing latency, status codes, and availability metrics.
* **Retry Engine:** Implements an exponential backoff strategy (1s, 2s, 4s, 8s) to gracefully handle transient network partitions.
* **Failure Classification:** A state machine that tracks consecutive failures to suppress noise.
* **Alert Engine:** Evaluates a sliding window of telemetry against configurable SLA thresholds (e.g., `< 99% availability` or `> 500ms latency`).
* **Logging Pipeline:** Bypasses human-readable standard out in favor of machine-readable JSON Lines (JSONL), ready for instant ingestion by SIEMs or log aggregators.

## 3. Failure Classification
Not all failures require an alert. 
* **Transient Failures:** A single timeout or brief DNS resolution drop. The system logs these but suppresses alerts, allowing the retry engine to recover the state.
* **Persistent Failures:** When a service exhausts its retry budget or exceeds the `persistent_threshold` of consecutive failed polls. This indicates a hard outage requiring intervention, triggering immediate threshold evaluation and alerting.

## 4. Results & Telemetry
The daemon continuously streams stateful metrics. 

**Sample Structured Health Log:**
```json
{"timestamp": "2026-06-02T21:32:13.280239+00:00", "service": "reliable-dns-api", "status_code": 200, "response_time_ms": 380.87, "availability": true, "classification": "healthy"}

Sample Actionable Alert:

JSON
{"timestamp": "2026-06-02T21:32:19.601685+00:00", "service": "delayed-service-mock", "alert_type": "AVAILABILITY_DEGRADED", "message": "Availability dropped to 0.0% over last 1 checks. (Threshold: 90.0%)", "severity": "CRITICAL"}
5. Tools & Acknowledgments
Language: Python 3.10+

Libraries: requests, schedule, pyyaml, standard logging, json, and unittest.

Deployment: Bash (Cron-compatible).

Conceptual Architecture: Adapted patterns from Prometheus Exporters (scraping), Nagios (stateful checks), and standard Python resilience tooling.

6. Rubrik Relevance
This project demonstrates production-style service observability, failure classification, alerting workflows, and reliability engineering concepts aligned with modern Site Reliability Engineering practices.

Authors:

G. Varun Sai Kumar * Theja Sri Kanagala ```