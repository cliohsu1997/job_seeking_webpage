"""
Tests for rate limiter utility.
"""

import unittest
import time
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "scraper"))

from utils.rate_limiter import RateLimiter


class TestRateLimiter(unittest.TestCase):
    """Test rate limiter functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(delay_seconds=2.0)
        self.assertEqual(limiter.delay_seconds, 2.0)
        self.assertIsNone(limiter.last_request_time)
    
    def test_rate_limiter_default_delay(self):
        """Test rate limiter with default delay."""
        limiter = RateLimiter()
        self.assertEqual(limiter.delay_seconds, 2.0)
    
    def test_rate_limiter_custom_delay(self):
        """Test rate limiter with custom delay."""
        limiter = RateLimiter(delay_seconds=5.0)
        self.assertEqual(limiter.delay_seconds, 5.0)
    
    def test_rate_limiter_wait_if_needed_first_call(self):
        """Test that first call doesn't wait."""
        limiter = RateLimiter(delay_seconds=1.0)
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        # Should be very fast (no wait on first call)
        self.assertLess(elapsed, 0.1)
        self.assertIsNotNone(limiter.last_request_time)
    
    def test_rate_limiter_wait_if_needed_respects_delay(self):
        """Test that rate limiter respects delay between calls."""
        limiter = RateLimiter(delay_seconds=0.5)
        
        # First call - no wait
        limiter.wait_if_needed()
        first_time = limiter.last_request_time
        
        # Second call immediately - should wait
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        # Should have waited approximately delay_seconds
        self.assertGreaterEqual(elapsed, 0.4)  # Allow some margin
        self.assertLess(elapsed, 0.7)  # Should not wait too long
        self.assertGreater(limiter.last_request_time, first_time)
    
    def test_rate_limiter_wait_if_needed_no_wait_if_enough_time_passed(self):
        """Test that rate limiter doesn't wait if enough time has passed."""
        limiter = RateLimiter(delay_seconds=0.1)
        
        # First call
        limiter.wait_if_needed()
        
        # Wait longer than delay
        time.sleep(0.2)
        
        # Second call - should not wait
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        # Should be very fast (no wait needed)
        self.assertLess(elapsed, 0.1)
    
    def test_rate_limiter_reset(self):
        """Test rate limiter reset."""
        limiter = RateLimiter()
        limiter.wait_if_needed()
        self.assertIsNotNone(limiter.last_request_time)
        
        limiter.reset()
        self.assertIsNone(limiter.last_request_time)
    
    def test_rate_limiter_reset_after_wait(self):
        """Test rate limiter reset after waiting."""
        limiter = RateLimiter(delay_seconds=0.1)
        limiter.wait_if_needed()
        time.sleep(0.05)
        limiter.wait_if_needed()  # This should wait
        limiter.reset()
        self.assertIsNone(limiter.last_request_time)
        
        # After reset, next call should not wait
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 0.1)


if __name__ == "__main__":
    unittest.main()

