from fastapi import FastAPI
import nats, json

app = FastAPI()

@app.post("/order")
async def create_order():
    nc = await nats.connect("nats://localhost:4222")
    await nc.publish("orders", json.dumps({"product_id": 123}).encode())
    await nc.close()
    return {"message": "Order queued"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)