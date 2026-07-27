# core/cache_decorator.py
import functools
import json
from dataclasses import is_dataclass, asdict
from typing import Callable, Any
from core.redis import get_redis_client
from typing import List


def cache_response(prefix: str, ttl: int = 3600):
    """
    Reusable decorator to cache any function output in Redis.
    
    Args:
        prefix (str): Cache key prefix (e.g., 'gpa:semester')
        ttl (int): Time To Live in seconds (default: 1 hour)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            redis_db = get_redis_client()

            # 1. Dynamically build a cache key from args (excluding 'self')
            # Example result key: "gpa:semester:123e4567-e89b...:1"
            clean_args = [str(arg) for arg in args[1:]]  # Skip 'self'
            clean_kwargs = [f"{k}={v}" for k, v in kwargs.items()]
            param_string = ":".join(clean_args + clean_kwargs)
            cache_key = f"{prefix}:{param_string}".strip(":")

            # 2. CACHE HIT CHECK
            try:
                cached_data = redis_db.get(cache_key)
                if cached_data:
                    print(f"⚡ [REDIS CACHE HIT] Key: {cache_key}")
                    return json.loads(cached_data)
            except Exception as e:
                print(f"⚠️ [REDIS WARNING]: Failed to read cache: {e}")

            # 3. CACHE MISS -> Execute original DB function
            print(f"🐢 [REDIS CACHE MISS] Querying DB for Key: {cache_key}")
            result = func(*args, **kwargs)

            if result is None:
                return None

            # 4. Automatic Serialization (Converts Dataclasses/UUIDs to Dict/String)
            if isinstance(result, list):
                serialized = [asdict(item) if is_dataclass(item) else item for item in result]
            elif is_dataclass(result):
                serialized = asdict(result)
            else:
                serialized = result

            # 5. Save serialized result into Redis
            try:
                redis_db.setex(
                    name=cache_key,
                    time=ttl,
                    value=json.dumps(serialized, default=str)  # default=str handles UUIDs automatically
                )
            except Exception as e:
                print(f"⚠️ [REDIS WARNING]: Failed to write cache: {e}")

            return serialized

        return wrapper
    return decorator

def invalidate_cache(prefixes: List[str]):
    """
    Decorator to automatically clear Redis cache keys matching given prefixes 
    whenever a mutation function (CREATE, UPDATE, DELETE) runs successfully.
    
    Args:
        prefixes (List[str]): List of cache key prefixes to clear (e.g., ["gpa:"])
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 1. Run the database mutation (UPDATE/DELETE/CREATE) first
            result = func(*args, **kwargs)

            # 2. If mutation succeeded, clear matching Redis keys
            try:
                redis_db = get_redis_client()
                for prefix in prefixes:
                    # scan_iter safely finds keys matching pattern (e.g., "gpa:*") without blocking Redis
                    keys_to_delete = list(redis_db.scan_iter(match=f"{prefix}*"))
                    if keys_to_delete:
                        redis_db.delete(*keys_to_delete)
                        print(f"🔥 [REDIS CACHE INVALIDATED] Deleted {len(keys_to_delete)} keys matching: '{prefix}*'")
            except Exception as e:
                print(f"⚠️ [REDIS WARNING]: Failed to invalidate cache: {e}")

            return result
        return wrapper
    return decorator