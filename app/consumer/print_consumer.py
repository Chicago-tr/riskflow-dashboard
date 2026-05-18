import asyncio, os, json, aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def main():
    r = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    res = await r.xread({"ticks":"0-0"}, count=5, block=1000)
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
