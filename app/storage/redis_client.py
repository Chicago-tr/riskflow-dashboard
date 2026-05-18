import os, json
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
_redis = None

async def get_redis():
    global _redis
    if not _redis:
        _redis = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis

async def publish_tick(tick: dict):
    r = await get_redis()
    # values converted to strings/json for redis streams
    
    await r.xadd("ticks", {k: json.dumps(v) if isinstance(v, (dict,list)) else str(v) for k,v in tick.items()})
