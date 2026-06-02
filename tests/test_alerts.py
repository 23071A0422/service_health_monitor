"""
Unit tests for the Alert Manager.
Verifies correct triggering of threshold-based warnings and critical alerts.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../monitor')))
from alert_manager import AlertManager

class TestAlertManager(unittest.TestCase):

    def setUp(self):
        self.thresholds = {"availability_min_pct": 90.0, "latency_max_ms": 500}
        self.manager = AlertManager(self.thresholds)

    def test_healthy_metrics_no_alerts(self):
        history = [
            {"availability": True, "response_time_ms": 100},
            {"availability": True, "response_time_ms": 150},
            {"availability": True, "response_time_ms": 120}
        ]
        alerts = self.manager.evaluate_metrics("stable-api", history)
        self.assertEqual(len(alerts), 0)

    def test_high_latency_alert(self):
        history = [
            {"availability": True, "response_time_ms": 600},
            {"availability": True, "response_time_ms": 700}
        ]
        alerts = self.manager.evaluate_metrics("slow-api", history)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['alert_type'], "HIGH_LATENCY")
        self.assertEqual(alerts[0]['severity'], "WARNING")

    def test_availability_drop_alert(self):
        # 2 failures out of 5 polls = 60% availability (Below 90% threshold)
        history = [
            {"availability": True, "response_time_ms": 100},
            {"availability": True, "response_time_ms": 100},
            {"availability": True, "response_time_ms": 100},
            {"availability": False, "response_time_ms": 5000},
            {"availability": False, "response_time_ms": 5000}
        ]
        alerts = self.manager.evaluate_metrics("failing-api", history)
        
        self.assertTrue(any(a['alert_type'] == "AVAILABILITY_DEGRADED" for a in alerts))
        
if __name__ == '__main__':
    unittest.main()