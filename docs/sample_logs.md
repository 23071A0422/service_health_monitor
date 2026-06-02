# Sample Production Logs

This file contains raw output from the `logs/` directory demonstrating the JSONL formatting.

### health_log.json
```json
{"timestamp": "2026-06-02T21:32:13.280239+00:00", "service": "reliable-dns-api", "url": "[https://1.1.1.1](https://1.1.1.1)", "status_code": 200, "response_time_ms": 380.87, "availability": true, "error_type": null, "classification": "healthy", "level": "INFO"}
{"timestamp": "2026-06-02T21:32:18.625063+00:00", "service": "delayed-service-mock", "url": "[https://httpstat.us/200?sleep=800](https://httpstat.us/200?sleep=800)", "status_code": null, "response_time_ms": 976.94, "availability": false, "error_type": "connection_error", "classification": "transient", "level": "INFO"}

### alerts.json
```json
{"timestamp": "2026-06-02T21:32:19.601685+00:00", "service": "delayed-service-mock", "alert_type": "AVAILABILITY_DEGRADED", "message": "Availability dropped to 0.0% over last 1 checks. (Threshold: 90.0%)", "severity": "CRITICAL"}

