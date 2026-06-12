import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_random,
    wait_combine,
    retry_if_exception,
    before_sleep_log,
)

logger = logging.getLogger(__name__)


# ---------------------------------
# Error classification
# ---------------------------------

def is_retryable(exception: BaseException) -> bool:
    """
    Returns True only for transient errors worth retrying.
    Permanent errors (400, 401, 403, 404) fail immediately.
    """
    msg = str(exception).lower()

    # Rate limits and server-side failures — always retry
    retryable_codes = ["429", "500", "502", "503", "504"]
    if any(code in msg for code in retryable_codes):
        return True

    # Network-level failures
    retryable_terms = ["timeout", "connection", "network", "temporarily"]
    if any(term in msg for term in retryable_terms):
        return True

    # Permanent failures — don't retry
    permanent_codes = ["400", "401", "403", "404"]
    if any(code in msg for code in permanent_codes):
        return False

    # Unknown errors — retry conservatively
    return True


# ---------------------------------
# Retry configs
# ---------------------------------

# For Groq LLM + Whisper + Vision calls
llm_retry = retry(
    retry=retry_if_exception(is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_combine(
        wait_exponential(multiplier=1, min=1, max=8),
        wait_random(min=0, max=1)          # jitter
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True                           # re-raise original exception after all attempts fail
)

# For external APIs with stricter rate limits (Tavily, YouTube)
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