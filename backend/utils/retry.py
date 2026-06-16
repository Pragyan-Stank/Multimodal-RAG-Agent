import logging
import inspect
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_random,
    wait_combine,
    retry_if_exception,
    before_sleep_log,
    AsyncRetrying,
)

logger = logging.getLogger(__name__)


# ---------------------------------
# Error classification
# ---------------------------------

def is_retryable(exception: BaseException) -> bool:
    msg = str(exception).lower()

    retryable_codes = ["429", "500", "502", "503", "504"]
    if any(code in msg for code in retryable_codes):
        return True

    retryable_terms = ["timeout", "connection", "network", "temporarily"]
    if any(term in msg for term in retryable_terms):
        return True

    permanent_codes = ["400", "401", "403", "404"]
    if any(code in msg for code in permanent_codes):
        return False

    return True


# ---------------------------------
# Sync retry decorators
# (used only for sync functions in ThreadPoolExecutor)
# ---------------------------------

llm_retry = retry(
    retry=retry_if_exception(is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_combine(
        wait_exponential(multiplier=1, min=1, max=8),
        wait_random(min=0, max=1)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)

api_retry = retry(
    retry=retry_if_exception(is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_combine(
        wait_exponential(multiplier=1, min=2, max=10),
        wait_random(min=0, max=2)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)


# ---------------------------------
# Async retry helpers
# (uses AsyncRetrying — correct for async functions)
# ---------------------------------

async def async_llm_retry(func, *args, **kwargs):
    """
    Async retry for LLM calls.
    Usage: result = await async_llm_retry(some_async_func, arg1, arg2)
    """
    async for attempt in AsyncRetrying(
        retry=retry_if_exception(is_retryable),
        stop=stop_after_attempt(3),
        wait=wait_combine(
            wait_exponential(multiplier=1, min=1, max=8),
            wait_random(min=0, max=1)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    ):
        with attempt:
            result = func(*args, **kwargs)
            if inspect.iscoroutine(result):
                return await result
            return result


async def async_api_retry(func, *args, **kwargs):
    """
    Async retry for external APIs (Tavily, YouTube).
    Usage: result = await async_api_retry(some_async_func, arg1, arg2)
    """
    async for attempt in AsyncRetrying(
        retry=retry_if_exception(is_retryable),
        stop=stop_after_attempt(3),
        wait=wait_combine(
            wait_exponential(multiplier=1, min=2, max=10),
            wait_random(min=0, max=2)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    ):
        with attempt:
            result = func(*args, **kwargs)
            if inspect.iscoroutine(result):
                return await result
            return result