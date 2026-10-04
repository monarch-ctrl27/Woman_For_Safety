import time
from django.core.cache import cache


def is_rate_limited(key: str, limit: int, window_seconds: int) -> bool:
    """
    Checks if an action identified by `key` has exceeded `limit` requests
    within `window_seconds`.
    Uses atomic cache operations where available.
    Returns True if user is rate-limited (blocked), False otherwise.
    """
    cache_key = f"ratelimit:{key}"
    current = cache.get(cache_key)
    if current is None:
        cache.set(cache_key, 1, timeout=window_seconds)
        return False

    if current >= limit:
        return True

    try:
        cache.incr(cache_key)
    except Exception:
        cache.set(cache_key, current + 1, timeout=window_seconds)

    return False
