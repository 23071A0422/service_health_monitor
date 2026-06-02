"""
Configuration Loader Module
Parses external YAML configurations to dynamically load monitoring targets and thresholds.
"""
import yaml
import logging
import sys
from typing import List, Dict, Any
from pathlib import Path

def load_endpoints(config_path: str = "config/endpoints.yaml") -> List[Dict[str, Any]]:
    """
    Loads service endpoint configurations from the specified YAML file.
    
    Args:
        config_path (str): Relative or absolute path to the YAML configuration.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a service to monitor.
    """
    path = Path(config_path)
    if not path.is_file():
        logging.error(f"CRITICAL: Configuration file not found at {config_path}. Halting monitor.")
        sys.exit(1)

    try:
        with open(path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            
            # Extract the services list, defaulting to an empty list if malformed
            endpoints = config.get('services', [])
            if not endpoints:
                logging.warning("WARNING: No services found in configuration file. Monitor will idle.")
                
            return endpoints
            
    except yaml.YAMLError as e:
        logging.error(f"CRITICAL: Error parsing YAML configuration. Invalid syntax: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"CRITICAL: Unexpected I/O error loading configuration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Local execution for testing the parser
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    print("Test output (requires config/endpoints.yaml to exist):")
    # This will fail gracefully right now because we haven't created the yaml yet
    load_endpoints()