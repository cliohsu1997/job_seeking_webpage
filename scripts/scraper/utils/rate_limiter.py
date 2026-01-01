"""
Rate limiting utilities for web scraping.
"""

import time
from typing import Optional


class RateLimiter:
    """Simple rate limiter that enforces delays between requests."""
    
    def __init__(self, delay_seconds: float = 2.0):
        """
        Initialize rate limiter.
        
        Args:
            delay_seconds: Minimum delay between requests in seconds
        """
        self.delay_seconds = delay_seconds
        self.last_request_time: Optional[float] = None
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limiting."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay_seconds:
                sleep_time = self.delay_seconds - elapsed
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def reset(self):
        """Reset the rate limiter."""
        self.last_request_time = None

