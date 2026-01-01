"""
Retry logic with exponential backoff for handling transient errors.
"""

import time
import logging
from typing import Callable, TypeVar, Optional, List, Type
from functools import wraps

T = TypeVar('T')

logger = logging.getLogger(__name__)


class RetryHandler:
    """Handle retries with exponential backoff."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exceptions: Optional[List[Type[Exception]]] = None
    ):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay in seconds
            exceptions: List of exception types to retry on (default: all exceptions)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions if exceptions else [Exception]
    
    def execute(
        self,
        func: Callable[[], T],
        operation_name: str = "operation"
    ) -> T:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute (must take no arguments)
            operation_name: Name of the operation for logging
        
        Returns:
            Result of the function
        
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func()
            except tuple(self.exceptions) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"{operation_name} failed after {self.max_retries + 1} attempts: {e}")
        
        raise last_exception


def retry_on_exception(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: Optional[List[Type[Exception]]] = None
):
    """
    Decorator for retrying functions on exceptions.
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay for exponential backoff
        exceptions: Exception types to retry on
    """
    handler = RetryHandler(max_retries=max_retries, base_delay=base_delay, exceptions=exceptions)
    
    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.execute(lambda: func(*args, **kwargs), operation_name=func.__name__)
        return wrapper
    
    return decorator

