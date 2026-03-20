import time
import functools
from utils.logger import setup_logger

logger = setup_logger("retry", "logs/retry.log")

def retry_on_failure(retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Decorator for automatic retries with exponential backoff.
    Useful for exchange API calls that may flake due to network issues.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            m_retries, m_delay = retries, delay
            while m_retries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"Retrying {func.__name__} in {m_delay}s due to: {e}")
                    time.sleep(m_delay)
                    m_retries -= 1
                    m_delay *= backoff
            return func(*args, **kwargs)
        return wrapper
    return decorator
