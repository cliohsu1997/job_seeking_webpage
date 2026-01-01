"""
User agent rotation for web scraping.
"""

import random
from typing import List, Optional


# Common user agents for web scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
]


class UserAgentRotator:
    """Rotate user agents for requests."""
    
    def __init__(self, user_agents: Optional[List[str]] = None):
        """
        Initialize user agent rotator.
        
        Args:
            user_agents: List of user agent strings (default: predefined list)
        """
        self.user_agents = user_agents if user_agents else USER_AGENTS
    
    def get_random(self) -> str:
        """Get a random user agent."""
        return random.choice(self.user_agents)
    
    def get_default(self) -> str:
        """Get the default (first) user agent."""
        return self.user_agents[0]

