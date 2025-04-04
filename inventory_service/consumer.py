import nats
import aiosqlite
import json
import asyncio
import random

async def handle_message(msg, nc):
    try:
        print(f"Raw message: {msg.data}")  # Debug log
        data = json.loads(msg.data.decode())
        print(f"Processing order: {data}")  # Debug log

        async with aiosqlite.connect("cache.db") as db:
            cursor = await db.execute("SELECT product_id, stock FROM inventory")
            products = await cursor.fetchall()  # Fetch all products
            print(f"Available inventory: {products}")  # Debug log

            if not products:
                print("No products in inventory!")
                return

            # Randomly select products to decrement
            selected_products = random.sample(products, min(len(products), random.randint(1, len(products))))
            print(f"Selected products for order: {selected_products}")  # Debug log

            updated_inventory = []
            for product in selected_products:
                product_id, stock = product
                quantity_to_deduct = random.randint(1, min(stock, 5))  # Randomly deduct up to 5 items

                if stock >= quantity_to_deduct:
                    await db.execute("UPDATE inventory SET stock = stock - ? WHERE product_id = ?", (quantity_to_deduct, product_id))
                    print(f"Reduced stock for product {product_id} by {quantity_to_deduct}")  # Debug log
                    updated_inventory.append((product_id, stock - quantity_to_deduct))
                else:
                    print(f"Not enough stock for product {product_id}")  # Debug log

            await db.commit()

            # Fetch updated inventory
            cursor = await db.execute("SELECT * FROM inventory")
            updated_stock = await cursor.fetchall()
            print("Updated inventory:", updated_stock)  # Debug log

            # Publish inventory update
            update_message = json.dumps({"inventory": updated_stock})
            await nc.publish("inventory_updates", update_message.encode())

    except Exception as e:
        print(f"Error processing message: {e}")

async def run():
    try:
        print("Connecting to NATS...")
        nc = await nats.connect("nats://localhost:4222")
        print("Connected to NATS! Subscribing...")

        # Subscribe to orders and pass nc
        async def message_callback(msg):
            await handle_message(msg, nc)

        await nc.subscribe("orders", cb=message_callback)

        # Initialize DB
        async with aiosqlite.connect("cache.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS inventory (product_id INT PRIMARY KEY, stock INT)")
            await db.execute("INSERT OR IGNORE INTO inventory VALUES (123, 100), (124, 50)")
            await db.commit()
            print("DB initialized with sample stock")

        # Keep running
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"NATS error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
