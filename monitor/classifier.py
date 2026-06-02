"""
Failure Classification Engine Module
Statefully tracks service health over time to differentiate between
transient blips and persistent outages, reducing alert fatigue.
"""
from typing import Dict, Any

class FailureClassifier:
    def __init__(self, persistent_threshold: int = 3):
        """
        Initializes the classifier.
        
        Args:
            persistent_threshold (int): Number of consecutive failures required 
                                        to classify an incident as 'persistent'.
        """
        self.persistent_threshold = persistent_threshold
        # Tracks consecutive failures per service: {"auth-service": 2}
        self.failure_states: Dict[str, int] = {}
        
    def process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single health check result, updates the internal state,
        and determines the classification.
        
        Args:
            result (Dict[str, Any]): The health check metrics dictionary.
            
        Returns:
            Dict[str, Any]: A classification payload.
        """
        service = result.get("service", "unknown")
        is_available = result.get("availability", False)
        
        if is_available:
            # If the service recovers, reset its failure counter to 0
            self.failure_states[service] = 0
            return {
                "service": service, 
                "classification": "healthy",
                "consecutive_failures": 0
            }
            
        # If unavailable, increment the failure count for this service
        current_failures = self.failure_states.get(service, 0) + 1
        self.failure_states[service] = current_failures
        
        # Evaluate against the threshold
        if current_failures >= self.persistent_threshold:
            classification = "persistent"
        else:
            classification = "transient"
            
        return {
            "service": service,
            "classification": classification,
            "consecutive_failures": current_failures
        }

if __name__ == "__main__":
    # Local execution for testing state changes
    classifier = FailureClassifier(persistent_threshold=3)
    
    mock_poll_results = [
        {"service": "database-tier", "availability": False}, # Poll 1: Fails (Transient)
        {"service": "database-tier", "availability": False}, # Poll 2: Fails (Transient)
        {"service": "database-tier", "availability": False}, # Poll 3: Fails (Persistent)
        {"service": "database-tier", "availability": True},  # Poll 4: Recovers (Healthy)
        {"service": "database-tier", "availability": False}, # Poll 5: Fails (Transient)
    ]
    
    print("Testing Classification Engine:")
    for poll in mock_poll_results:
        print(classifier.process_result(poll))