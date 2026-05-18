import asyncio, websockets, json, random, time

PORT = 8765
SYMS = ["ESZ6", "NQZ6", "CLZ6"]

async def producer(ws):
    while True:
        s = random.choice(SYMS)
        mid = round(4000 + random.random()*100, 2)
        spread = round(0.25 + random.random()*0.75, 2)
        tick = {
            "symbol": s,
            "source": "simulator",
            "ts": time.time(),
            "bid": mid - spread/2,
            "ask": mid + spread/2,
            "bid_size": random.randint(1,5),
            "ask_size": random.randint(1,5),
            "price": mid,
            "trade_size": random.choice([0,1,2])
        }
        await ws.send(json.dumps(tick))
        await asyncio.sleep(0.05)  # 20 ticks/sec total approx

async def handler(ws, path):
    await producer(ws)

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
