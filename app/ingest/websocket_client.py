import asyncio, json, os, time, websockets
from app.storage.redis_client import publish_tick

WS_URL = os.getenv("MARKET_WS", "ws://localhost:8765")

def normalize(raw):
    # ensure canonical types; fill defaults where needed
    return {
        "symbol": raw.get("symbol"),
        "source": raw.get("source", "unknown"),
        "ts": float(raw.get("ts", time.time())),
        "bid": float(raw.get("bid", 0.0)),
        "ask": float(raw.get("ask", 0.0)),
        "bid_size": int(raw.get("bid_size", 0)),
        "ask_size": int(raw.get("ask_size", 0)),
        "price": float(raw.get("price", 0.0)),
        "trade_size": int(raw.get("trade_size", 0))
    }

async def run():
    backoff = 1
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                backoff = 1
                async for msg in ws:
                    raw = json.loads(msg)
                    tick = normalize(raw)
                    tick["t_ingested"] = time.time()
                    # basic validation
                    if not tick["symbol"] or tick["bid"] <= 0 or tick["ask"] <= 0:
                        continue
                    await publish_tick(tick)
        except Exception as e:
            print("ingest error", e)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)

if __name__ == "__main__":
    asyncio.run(run())
