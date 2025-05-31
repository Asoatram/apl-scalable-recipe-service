import json
from functools import wraps

def redis_cache(key_fn, ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from Core.redis_client import redis_client

            key = key_fn(*args, **kwargs)
            try:
                cached = await redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass

            result = await func(*args, **kwargs)

            try:
                if result is not None:
                    print(json.dumps(result))
                    print(key)
                    await redis_client.set(key, json.dumps(result), ex=ttl)
            except Exception:
                pass

            return result
        return wrapper
    return decorator
