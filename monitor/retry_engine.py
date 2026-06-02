"""
Retry Engine Module
Implements exponential backoff strategy for network resiliency.
"""
import time
import logging
from typing import Callable, Any, Dict

# Configure a basic logger for the retry engine (will be overridden by main logger later)
logger = logging.getLogger("RetryEngine")

def execute_with_backoff(
    action: Callable[..., Dict[str, Any]], 
    max_retries: int = 4, 
    *args, 
    **kwargs
) -> Dict[str, Any]:
    """
    Executes a given callable with exponential backoff on failure.
    
    Args:
        action: The function to execute (expected to return our health metric dictionary).
        max_retries: Maximum number of retry attempts.
        *args, **kwargs: Arguments to pass to the action.
        
    Returns:
        Dict[str, Any]: The final result of the action (either success or exhausted failure).
    """
    attempt = 0
    
    while True:
        result = action(*args, **kwargs)
        
        # If the endpoint is available, return immediately
        if result.get("availability") is True:
            if attempt > 0:
                logger.info(f"SUCCESS: {result.get('service')} recovered on attempt {attempt + 1}")
            return result
            
        attempt += 1
        
        # If we have exhausted all retries, return the final failed result
        if attempt >= max_retries:
            logger.warning(f"FAILURE: {result.get('service')} failed after {max_retries} attempts.")
            return result
            
        # Calculate exponential backoff: 1s, 2s, 4s, 8s...
        delay = 2 ** (attempt - 1)
        
        logger.warning(
            f"RETRY: {result.get('service')} check failed "
            f"(Status: {result.get('status_code')}, Error: {result.get('error_type')}). "
            f"Attempt {attempt}/{max_retries}. Retrying in {delay} seconds..."
        )
        
        time.sleep(delay)

if __name__ == "__main__":
    # Local execution for testing
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    # Mocking a failing function to demonstrate backoff
    def failing_action(name="mock-service"):
        return {"service": name, "availability": False, "status_code": 503, "error_type": "http_error"}
        
    print("Testing backoff on failing action...")
    execute_with_backoff(failing_action, max_retries=4)