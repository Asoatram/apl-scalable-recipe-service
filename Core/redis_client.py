import redis.asyncio as redis

redis_client = None

async def init_redis():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url("redis://redis:6379", decode_responses=True)
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None