import json
import asyncio
import websockets
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'bitcoin_prices')
BINANCE_WS_URI = os.getenv('BINANCE_WS_URI', 'wss://stream.binance.com:9443/ws/btcusdt@trade')

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

async def get_bitcoin_data():
    async with websockets.connect(BINANCE_WS_URI) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                bitcoin_data = {
                    "timestamp": data['E'],  # Keeping it in milliseconds as BIGINT
                    "buy_price": float(data['p']),
                    "sell_price": float(data['p']),  # Assuming sell price is the same for now
                    "volume": float(data['q'])
                }
                producer.send(KAFKA_TOPIC, bitcoin_data)
                producer.flush()
                print(f"Sent to Kafka: {bitcoin_data}")
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket closed, reconnecting...")
                await asyncio.sleep(5)
                return await get_bitcoin_data()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_bitcoin_data())
