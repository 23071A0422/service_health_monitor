"""
Main Daemon Orchestrator
Ties together configuration, monitoring, retries, classification, and alerting.
"""
import time
import argparse
import schedule
import sys
import yaml
import json
from pathlib import Path

# Import our modular engines
from config_loader import load_endpoints
from health_checker import check_endpoint
from retry_engine import execute_with_backoff
from classifier import FailureClassifier
from alert_manager import AlertManager
from logger import init_logging

def load_thresholds(config_path: str = "config/endpoints.yaml") -> dict:
    """Helper to extract global thresholds from the YAML."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f).get('thresholds', {})
    except Exception:
        return {"availability_min_pct": 90.0, "latency_max_ms": 500}

def run_poll_cycle(endpoints, classifier, alert_manager, h_log):
    """Executes a single pass over all configured endpoints."""
    # Maintain a sliding window of the last 10 polls for the alert manager
    if not hasattr(run_poll_cycle, "history"):
        run_poll_cycle.history = {ep['name']: [] for ep in endpoints}
        
    for ep in endpoints:
        # 1. Execute check with exponential backoff
        action = lambda: check_endpoint(ep['name'], ep['url'])
        result = execute_with_backoff(action, max_retries=3)
        
        # 2. Classify the failure state
        classification = classifier.process_result(result)
        result['classification'] = classification['classification']
        
        # 3. Log structured health metric
        h_log.info(json.dumps(result))
        
        # 4. Update metrics history window
        history = run_poll_cycle.history[ep['name']]
        history.append(result)
        if len(history) > 10:
            history.pop(0)
            
        # 5. Evaluate and generate alerts
        alert_manager.evaluate_metrics(ep['name'], history)

def main():
    parser = argparse.ArgumentParser(description="SRE Service Health Monitor")
    parser.add_argument('--cron', action='store_true', help="Run a single poll cycle and exit")
    args = parser.parse_args()

    # Initialize Observability
    h_log, a_log = init_logging()
    
    # Load Configurations
    endpoints = load_endpoints()
    thresholds = load_thresholds()
    
    # Initialize Engines
    classifier = FailureClassifier(persistent_threshold=3)
    alert_manager = AlertManager(thresholds)

    if args.cron:
        print("Executing single cron polling cycle...")
        run_poll_cycle(endpoints, classifier, alert_manager, h_log)
        sys.exit(0)

    print("Starting Continuous Monitoring Daemon...")
    print("Metrics streaming to logs/health_log.json")
    print("Alerts streaming to logs/alerts.json")
    print("(Press Ctrl+C to stop)\n")
    
    # Run once immediately, then schedule
    run_poll_cycle(endpoints, classifier, alert_manager, h_log)
    schedule.every(10).seconds.do(run_poll_cycle, endpoints, classifier, alert_manager, h_log)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived interrupt. Shutting down monitor daemon gracefully.")

if __name__ == "__main__":
    main()