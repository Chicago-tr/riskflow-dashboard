import asyncio
import os
import json
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def main():
    r = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    # read up to 5 items from the stream
    res = await r.xread({"ticks": "0-0"}, count=5, block=1000)
    # res is a list ex: [(b'ticks', [(b'id', {b'field': b'value', ...}), ...])]
    for stream_name, entries in res:
        print(f"stream: {stream_name}")
        for entry_id, fields in entries:
            parsed = {k: (json.loads(v) if (v and (v[0] == "{" or v[0] == "[")) else v) for k, v in fields.items()}
            print(entry_id, parsed)

if __name__ == "__main__":
    asyncio.run(main())










