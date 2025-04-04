import nats, json, asyncio

async def process_payment(msg):
    try:
        data = json.loads(msg.data.decode())
        print(f"Payment processed")
    except Exception as e:
        print(f"Payment error: {e}")

async def run():
    try:
        nc = await nats.connect("nats://localhost:4222")
        print("Connected to NATS!")
        await nc.subscribe("orders", cb=process_payment)
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"NATS connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())