"""
Health Checker Module
Performs the actual HTTP polling against configured endpoints, measuring latency and availability.
"""
import requests
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

def check_endpoint(name: str, url: str, timeout: int = 5) -> Dict[str, Any]:
    """
    Polls a single HTTP endpoint and returns structured health metrics.
    
    Args:
        name (str): The logical name of the service.
        url (str): The HTTP/HTTPS endpoint to poll.
        timeout (int): Request timeout in seconds.
        
    Returns:
        Dict[str, Any]: A dictionary containing raw metrics from the poll.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    metrics = {
        "timestamp": timestamp,
        "service": name,
        "url": url,
        "status_code": None,
        "response_time_ms": None,
        "availability": False,
        "error_type": None
    }

    start_time = time.perf_counter()

    try:
        # We use a GET request here. In a stricter production environment, 
        # a HEAD request might be preferred to save bandwidth, but GET tests full stack response.
        response = requests.get(url, timeout=timeout)
        
        # Calculate latency in milliseconds
        latency = (time.perf_counter() - start_time) * 1000
        metrics["response_time_ms"] = round(latency, 2)
        metrics["status_code"] = response.status_code
        
        # We consider HTTP 2xx and 3xx as available
        if 200 <= response.status_code < 400:
            metrics["availability"] = True
        else:
            metrics["error_type"] = "http_error"

    except requests.exceptions.Timeout:
        metrics["error_type"] = "timeout"
    except requests.exceptions.ConnectionError:
        metrics["error_type"] = "connection_error"
    except requests.exceptions.RequestException as e:
        metrics["error_type"] = "unknown_request_error"

    # If it failed to connect or timed out, we still want to record the time it took to fail
    if metrics["response_time_ms"] is None:
        latency = (time.perf_counter() - start_time) * 1000
        metrics["response_time_ms"] = round(latency, 2)

    return metrics

if __name__ == "__main__":
    # Local execution for testing
    print(check_endpoint("google-dns", "https://8.8.8.8", timeout=2))