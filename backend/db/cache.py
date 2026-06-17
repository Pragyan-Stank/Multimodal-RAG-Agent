import hashlib
import json
from upstash_redis import AsyncRedis
from backend.config import UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN

# ---------------------------------
# TTLs
# ---------------------------------

TTL_LLM_RESPONSE = 60 * 60 * 24        # 24 hours — LLM responses
TTL_DOCUMENT_INDEXED = 60 * 60 * 24 * 7 

# ---------------------------------
# Client (lazy initialized)
# ---------------------------------

_redis: AsyncRedis | None = None


def get_redis() -> AsyncRedis:
    global _redis
    if _redis is None:
        _redis = AsyncRedis(
            url=UPSTASH_REDIS_REST_URL,
            token=UPSTASH_REDIS_REST_TOKEN,
        )
    return _redis


# ---------------------------------
# Key builders
# ---------------------------------

def _llm_key(prompt_hash: str) -> str:
    return f"llm:response:{prompt_hash}"


def _doc_key(file_hash: str, user_id: str) -> str:
    return f"doc:indexed:{user_id}:{file_hash}"


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# ---------------------------------
# LLM response cache
# ---------------------------------

async def get_cached_llm_response(prompt: str) -> str | None:
    """Return cached LLM response for this prompt, or None if not cached."""
    key = _llm_key(_hash(prompt))
    redis = get_redis()
    result = await redis.get(key)
    return result if result else None


async def set_cached_llm_response(prompt: str, response: str) -> None:
    """Cache an LLM response for 24 hours."""
    key = _llm_key(_hash(prompt))
    redis = get_redis()
    await redis.set(key, response, ex=TTL_LLM_RESPONSE)


# ---------------------------------
# Document indexed cache
# ---------------------------------

async def is_document_indexed(file_hash: str, user_id: str) -> bool:
    """
    Fast Redis check before hitting Postgres.
    Returns True if this doc is already chunked and stored for this user.
    """
    key = _doc_key(file_hash, user_id)
    redis = get_redis()
    result = await redis.get(key)
    return result is not None


async def mark_document_indexed(file_hash: str, user_id: str) -> None:
    """Mark document as indexed in Redis after successful Postgres insert."""
    key = _doc_key(file_hash, user_id)
    redis = get_redis()
    await redis.set(key, "1", ex=TTL_DOCUMENT_INDEXED)