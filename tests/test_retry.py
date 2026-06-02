"""
Unit tests for the Retry Engine.
Verifies exponential backoff timing and retry limits.
"""
import unittest
from unittest.mock import patch, call
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../monitor')))
from retry_engine import execute_with_backoff

class TestRetryEngine(unittest.TestCase):

    @patch('time.sleep') # Mock sleep so tests run instantly
    def test_exhausted_retries(self, mock_sleep):
        # A mock action that always fails
        def always_fails():
            return {"service": "failing-api", "availability": False, "status_code": 503}
            
        result = execute_with_backoff(always_fails, max_retries=4)
        
        self.assertFalse(result['availability'])
        # If max_retries is 4, it should sleep 3 times between the 4 attempts
        self.assertEqual(mock_sleep.call_count, 3)
        # Verify exponential backoff: 2^0=1, 2^1=2, 2^2=4
        mock_sleep.assert_has_calls([call(1), call(2), call(4)])

    @patch('time.sleep')
    def test_success_on_third_attempt(self, mock_sleep):
        # A mock action that fails twice, then succeeds
        attempts = [0]
        def recovers_eventually():
            attempts[0] += 1
            if attempts[0] < 3:
                return {"service": "flaky-api", "availability": False}
            return {"service": "flaky-api", "availability": True}
            
        result = execute_with_backoff(recovers_eventually, max_retries=5)
        
        self.assertTrue(result['availability'])
        # Succeeded on 3rd attempt, so it slept twice
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_has_calls([call(1), call(2)])

if __name__ == '__main__':
    unittest.main()