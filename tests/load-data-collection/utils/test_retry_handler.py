"""
Tests for retry handler utility.
"""

import unittest
import time
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from utils.retry_handler import RetryHandler, retry_on_exception


class TestRetryHandler(unittest.TestCase):
    """Test retry handler functionality."""
    
    def test_retry_handler_initialization(self):
        """Test retry handler initialization."""
        handler = RetryHandler(max_retries=3, base_delay=1.0, max_delay=60.0)
        self.assertEqual(handler.max_retries, 3)
        self.assertEqual(handler.base_delay, 1.0)
        self.assertEqual(handler.max_delay, 60.0)
        self.assertEqual(len(handler.exceptions), 1)  # Default: [Exception]
    
    def test_retry_handler_default_values(self):
        """Test retry handler with default values."""
        handler = RetryHandler()
        self.assertEqual(handler.max_retries, 3)
        self.assertEqual(handler.base_delay, 1.0)
        self.assertEqual(handler.max_delay, 60.0)
    
    def test_retry_handler_custom_exceptions(self):
        """Test retry handler with custom exception types."""
        handler = RetryHandler(exceptions=[ValueError, TypeError])
        self.assertEqual(len(handler.exceptions), 2)
        self.assertIn(ValueError, handler.exceptions)
        self.assertIn(TypeError, handler.exceptions)
    
    def test_retry_handler_execute_success_first_attempt(self):
        """Test that successful function executes without retries."""
        handler = RetryHandler(max_retries=3)
        
        def success_func():
            return "success"
        
        result = handler.execute(success_func, "test operation")
        self.assertEqual(result, "success")
    
    def test_retry_handler_execute_success_after_retries(self):
        """Test that function succeeds after some retries."""
        handler = RetryHandler(max_retries=3, base_delay=0.1)
        attempt_count = [0]
        
        def retry_func():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = handler.execute(retry_func, "test operation")
        self.assertEqual(result, "success")
        self.assertEqual(attempt_count[0], 2)
    
    def test_retry_handler_execute_fails_after_max_retries(self):
        """Test that handler raises exception after max retries."""
        handler = RetryHandler(max_retries=2, base_delay=0.1)
        
        def fail_func():
            raise ValueError("Always fails")
        
        with self.assertRaises(ValueError) as context:
            handler.execute(fail_func, "test operation")
        
        self.assertEqual(str(context.exception), "Always fails")
    
    def test_retry_handler_exponential_backoff(self):
        """Test that retry handler uses exponential backoff."""
        handler = RetryHandler(max_retries=3, base_delay=0.1, max_delay=1.0)
        delays = []
        original_sleep = time.sleep
        
        def mock_sleep(delay):
            delays.append(delay)
            original_sleep(0.01)  # Short sleep for test speed
        
        attempt_count = [0]
        
        def retry_func():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                time.sleep = mock_sleep
                raise ValueError("Temporary error")
            time.sleep = original_sleep
            return "success"
        
        result = handler.execute(retry_func, "test operation")
        self.assertEqual(result, "success")
        # Should have 2 retries with delays approximately 0.1 and 0.2
        self.assertEqual(len(delays), 2)
        self.assertGreaterEqual(delays[0], 0.05)  # Allow some margin
        self.assertLessEqual(delays[0], 0.15)
        self.assertGreaterEqual(delays[1], 0.15)
        self.assertLessEqual(delays[1], 0.25)
    
    def test_retry_handler_respects_max_delay(self):
        """Test that handler respects max_delay."""
        handler = RetryHandler(max_retries=5, base_delay=10.0, max_delay=0.2)
        delays = []
        original_sleep = time.sleep
        
        def mock_sleep(delay):
            delays.append(delay)
            original_sleep(0.01)
        
        attempt_count = [0]
        
        def retry_func():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                time.sleep = mock_sleep
                raise ValueError("Temporary error")
            time.sleep = original_sleep
            return "success"
        
        result = handler.execute(retry_func, "test operation")
        self.assertEqual(result, "success")
        # All delays should be capped at max_delay
        for delay in delays:
            self.assertLessEqual(delay, 0.2)
    
    def test_retry_handler_only_retries_specified_exceptions(self):
        """Test that handler only retries specified exceptions."""
        handler = RetryHandler(max_retries=2, base_delay=0.1, exceptions=[ValueError])
        
        def raise_keyerror():
            raise KeyError("Not retried")
        
        with self.assertRaises(KeyError):
            handler.execute(raise_keyerror, "test operation")
    
    def test_retry_on_exception_decorator(self):
        """Test retry_on_exception decorator."""
        attempt_count = [0]
        
        @retry_on_exception(max_retries=2, base_delay=0.1)
        def decorated_func():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = decorated_func()
        self.assertEqual(result, "success")
        self.assertEqual(attempt_count[0], 2)
    
    def test_retry_on_exception_decorator_with_args(self):
        """Test retry_on_exception decorator with function arguments."""
        attempt_count = [0]
        
        @retry_on_exception(max_retries=2, base_delay=0.1)
        def decorated_func(x, y):
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ValueError("Temporary error")
            return x + y
        
        result = decorated_func(2, 3)
        self.assertEqual(result, 5)
        self.assertEqual(attempt_count[0], 2)


if __name__ == "__main__":
    unittest.main()

