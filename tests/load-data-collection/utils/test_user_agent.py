"""
Tests for user agent rotator utility.
"""

import unittest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from utils.user_agent import UserAgentRotator, USER_AGENTS


class TestUserAgentRotator(unittest.TestCase):
    """Test user agent rotator functionality."""
    
    def test_user_agent_rotator_initialization(self):
        """Test user agent rotator initialization with default agents."""
        rotator = UserAgentRotator()
        self.assertIsInstance(rotator.user_agents, list)
        self.assertGreater(len(rotator.user_agents), 0)
        # Should use default USER_AGENTS
        self.assertEqual(len(rotator.user_agents), len(USER_AGENTS))
    
    def test_user_agent_rotator_custom_agents(self):
        """Test user agent rotator with custom user agents."""
        custom_agents = [
            "Custom Agent 1",
            "Custom Agent 2",
            "Custom Agent 3"
        ]
        rotator = UserAgentRotator(user_agents=custom_agents)
        self.assertEqual(rotator.user_agents, custom_agents)
    
    def test_user_agent_rotator_get_default(self):
        """Test getting default user agent."""
        rotator = UserAgentRotator()
        default = rotator.get_default()
        
        self.assertIsInstance(default, str)
        self.assertGreater(len(default), 0)
        # Should be the first user agent
        self.assertEqual(default, rotator.user_agents[0])
    
    def test_user_agent_rotator_get_default_custom(self):
        """Test getting default user agent with custom agents."""
        custom_agents = ["Agent1", "Agent2", "Agent3"]
        rotator = UserAgentRotator(user_agents=custom_agents)
        default = rotator.get_default()
        self.assertEqual(default, "Agent1")
    
    def test_user_agent_rotator_get_random(self):
        """Test getting random user agent."""
        rotator = UserAgentRotator()
        random_agent = rotator.get_random()
        
        self.assertIsInstance(random_agent, str)
        self.assertGreater(len(random_agent), 0)
        # Should be one of the user agents
        self.assertIn(random_agent, rotator.user_agents)
    
    def test_user_agent_rotator_get_random_custom(self):
        """Test getting random user agent with custom agents."""
        custom_agents = ["Agent1", "Agent2", "Agent3"]
        rotator = UserAgentRotator(user_agents=custom_agents)
        
        # Get multiple random agents to ensure randomness
        random_agents = [rotator.get_random() for _ in range(10)]
        
        # All should be valid
        for agent in random_agents:
            self.assertIn(agent, custom_agents)
        
        # With 10 attempts, we should get at least 2 different agents (likely)
        unique_agents = set(random_agents)
        self.assertGreaterEqual(len(unique_agents), 1)
    
    def test_user_agent_rotator_single_agent(self):
        """Test user agent rotator with single agent."""
        single_agent = ["Single Agent"]
        rotator = UserAgentRotator(user_agents=single_agent)
        
        default = rotator.get_default()
        random_agent = rotator.get_random()
        
        self.assertEqual(default, "Single Agent")
        self.assertEqual(random_agent, "Single Agent")
    
    def test_default_user_agents_not_empty(self):
        """Test that default USER_AGENTS list is not empty."""
        self.assertGreater(len(USER_AGENTS), 0)
        for agent in USER_AGENTS:
            self.assertIsInstance(agent, str)
            self.assertGreater(len(agent), 0)
    
    def test_default_user_agents_format(self):
        """Test that default user agents have reasonable format."""
        for agent in USER_AGENTS:
            # Should contain browser identifiers
            self.assertTrue(
                "Mozilla" in agent or 
                "Chrome" in agent or 
                "Firefox" in agent or 
                "Safari" in agent
            )


if __name__ == "__main__":
    unittest.main()

