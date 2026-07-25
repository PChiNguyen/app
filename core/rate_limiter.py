# core/rate_limiter.py
from fastapi import HTTPException, Request, Depends
import redis
from core.redis import get_redis_client

class RateLimiter:
    def __init__(self, requests_limit: int = 5, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds

    def __call__(self, request: Request, redis_db: redis.Redis = Depends(get_redis_client)):
        # Identify the user by IP address and route endpoint
        client_ip = request.client.host if request.client else "unknown"
        rate_key = f"rate_limit:{client_ip}:{request.url.path}"

        # Increment request count in Redis
        request_count = redis_db.incr(rate_key)

        # Set expiration on first request
        if request_count == 1:
            redis_db.expire(rate_key, self.window_seconds)

        # Block request if limit exceeded (HTTP 429 Too Many Requests)
        if request_count > self.requests_limit:
            ttl = redis_db.ttl(rate_key)
            raise HTTPException(
                status_code=429,
                detail=f"🚫 Anti-spam triggered! You reached the request limit. Retry in {ttl} seconds."
            )