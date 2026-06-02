"""
Alert Manager Module
Evaluates health metrics against defined thresholds and generates actionable alerts.
"""
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

# Logger dedicated to alerting
alert_logger = logging.getLogger("AlertManager")

class AlertManager:
    def __init__(self, thresholds: Dict[str, Any]):
        """
        Initializes the Alert Manager with specific thresholds.
        
        Args:
            thresholds (Dict[str, Any]): Dictionary containing alert thresholds.
                e.g., {"availability_min_pct": 99.0, "latency_max_ms": 500}
        """
        self.thresholds = thresholds
        # In a production environment, this would integrate with PagerDuty, Slack webhooks, etc.
        
    def evaluate_metrics(self, service: str, metrics_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluates a sliding window of metrics against thresholds to generate alerts.
        
        Args:
            service (str): The name of the service.
            metrics_history (List[Dict[str, Any]]): Recent poll results for the service.
            
        Returns:
            List[Dict[str, Any]]: A list of generated alert events.
        """
        if not metrics_history:
            return []

        alerts = []
        total_polls = len(metrics_history)
        
        # Calculate aggregate metrics
        failed_polls = sum(1 for m in metrics_history if not m.get("availability", False))
        error_rate_pct = (failed_polls / total_polls) * 100
        availability_pct = 100.0 - error_rate_pct
        
        # Extract successful latencies to calculate average
        latencies = [
            m.get("response_time_ms") for m in metrics_history 
            if m.get("response_time_ms") is not None and m.get("availability", True)
        ]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0

        # 1. Availability Alert
        min_avail = self.thresholds.get("availability_min_pct", 95.0)
        if availability_pct < min_avail:
            alerts.append(self._create_alert(
                service, "AVAILABILITY_DEGRADED", 
                f"Availability dropped to {availability_pct:.1f}% over last {total_polls} checks. (Threshold: {min_avail}%)",
                "CRITICAL"
            ))

        # 2. Latency Alert
        max_lat = self.thresholds.get("latency_max_ms", 500)
        if avg_latency > max_lat:
            alerts.append(self._create_alert(
                service, "HIGH_LATENCY", 
                f"Average latency is {avg_latency:.1f}ms. (Threshold: {max_lat}ms)",
                "WARNING"
            ))

        # Log generated alerts
        for alert in alerts:
            # We log it as a stringified JSON for easy log parsing (like in Datadog or ELK)
            alert_logger.warning(json.dumps(alert))

        return alerts

    def _create_alert(self, service: str, alert_type: str, message: str, severity: str) -> Dict[str, Any]:
        """Helper to format standard alert payloads."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": service,
            "alert_type": alert_type,
            "message": message,
            "severity": severity
        }

if __name__ == "__main__":
    # Local execution test
    logging.basicConfig(level=logging.WARNING, format='%(message)s')
    thresholds_config = {"availability_min_pct": 90.0, "latency_max_ms": 200}
    manager = AlertManager(thresholds_config)
    
    # Simulating a failing service history
    mock_history = [
        {"availability": True, "response_time_ms": 250},
        {"availability": True, "response_time_ms": 300},
        {"availability": False, "response_time_ms": 5000},
    ] # 66% availability, avg latency > 200ms
    
    print("Testing Alert Generation:")
    alerts_generated = manager.evaluate_metrics("auth-api", mock_history)
    print(json.dumps(alerts_generated, indent=2))