"""
Structured Logging Engine Module
Outputs machine-readable JSON logs (JSONL format) for downstream ingestion
by observability platforms (e.g., Datadog, Splunk, ELK stack).
"""
import logging
import json
from pathlib import Path
from typing import Tuple

class JSONFormatter(logging.Formatter):
    """Custom standard library logging formatter to output strictly JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        # If the log message is already a JSON string (like from our AlertManager or health payload),
        # parse it so it isn't double-escaped as a string inside a JSON object.
        try:
            message_dict = json.loads(record.getMessage())
            if isinstance(message_dict, dict):
                # Inject the severity level for easier querying in log aggregation tools
                if "severity" not in message_dict and "level" not in message_dict:
                    message_dict["level"] = record.levelname
                return json.dumps(message_dict)
        except (ValueError, TypeError):
            pass
        
        # Fallback for standard string logs
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name
        }
        return json.dumps(log_record)

def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configures and returns a structured JSON logger that writes to both file and stdout.
    
    Args:
        name (str): The name of the logger.
        log_file (str): The file path to write logs to.
        level (int): The logging threshold.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent propagation to root logger to avoid duplicate console prints
    logger.propagate = False
    
    # Clear existing handlers if re-initialized
    if logger.hasHandlers():
        logger.handlers.clear()
        
    formatter = JSONFormatter()
    
    # Append-only file handler
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

def init_logging(log_dir: str = "logs") -> Tuple[logging.Logger, logging.Logger]:
    """
    Initializes the primary loggers for the monitoring daemon.
    
    Returns:
        Tuple[logging.Logger, logging.Logger]: The health logger and the alert logger.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    health_logger = setup_logger("HealthMonitor", f"{log_dir}/health_log.json", level=logging.INFO)
    alert_logger = setup_logger("AlertManager", f"{log_dir}/alerts.json", level=logging.WARNING)
    
    return health_logger, alert_logger

if __name__ == "__main__":
    # Local execution test
    h_log, a_log = init_logging()
    
    # Simulate a structured health log
    h_log.info(json.dumps({"service": "payment-api", "availability": True, "response_time_ms": 120}))
    
    # Simulate a structured alert log
    a_log.warning(json.dumps({"service": "auth-api", "alert_type": "HIGH_LATENCY", "severity": "WARNING"}))
    print("Test logs written. Check the logs/ directory.")