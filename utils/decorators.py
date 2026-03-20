import functools
import time

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
                    # If it's a Rate Limit error (429), force a longer wait
                    wait_time = m_delay
                    if "429" in str(e) or "Rate limit" in str(e):
                        logger.error(
                            f"RATE LIMIT DETECTED in {func.__name__}. Cooling down for {m_delay * 5}s..."
                        )
                        wait_time = m_delay * 5

                    logger.warning(
                        f"Retrying {func.__name__} in {wait_time}s due to: {e} ({m_retries-1} left)"
                    )
                    time.sleep(wait_time)
                    m_retries -= 1
                    m_delay *= backoff
            return func(*args, **kwargs)

        return wrapper

    return decorator
