"""
Unit tests for the Health Checker engine.
Verifies correct handling of successes, HTTP errors, and timeouts.
"""
import unittest
from unittest.mock import patch, Mock
import requests
import sys
import os

# Ensure the monitor module is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../monitor')))
from health_checker import check_endpoint

class TestHealthChecker(unittest.TestCase):
    
    @patch('requests.get')
    def test_successful_request(self, mock_get):
        # Mock a 200 OK response
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        
        result = check_endpoint("test-api", "http://example.com")
        
        self.assertTrue(result['availability'])
        self.assertEqual(result['status_code'], 200)
        self.assertIsNone(result['error_type'])
        self.assertIsNotNone(result['response_time_ms'])

    @patch('requests.get')
    def test_http_error(self, mock_get):
        # Mock a 500 Internal Server Error
        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp
        
        result = check_endpoint("test-api", "http://example.com")
        
        self.assertFalse(result['availability'])
        self.assertEqual(result['status_code'], 500)
        self.assertEqual(result['error_type'], "http_error")

    @patch('requests.get')
    def test_timeout_failure(self, mock_get):
        # Mock a Request Timeout
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
        
        result = check_endpoint("test-api", "http://example.com")
        
        self.assertFalse(result['availability'])
        self.assertIsNone(result['status_code'])
        self.assertEqual(result['error_type'], "timeout")

if __name__ == '__main__':
    unittest.main()