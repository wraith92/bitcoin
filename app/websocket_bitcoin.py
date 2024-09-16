# app/websocket_bitcoin.py

import json
import asyncio
import websockets
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration Kafka à partir des variables d'environnement
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'bitcoin_prices')

# URI du WebSocket de Binance à partir des variables d'environnement
BINANCE_WS_URI = os.getenv('BINANCE_WS_URI', 'wss://stream.binance.com:9443/ws/btcusdt@trade')

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
                    "timestamp": data['E'] / 1000,  # Convertir en secondes
                    "buy_price": float(data['p']),
                    "sell_price": float(data['p']),  # Binance ne fournit pas de prix de vente distinct
                    "volume": float(data['q'])
                }
                producer.send(KAFKA_TOPIC, bitcoin_data)
                producer.flush()
                print(f"Message envoyé à Kafka: {bitcoin_data}")
            except websockets.exceptions.ConnectionClosed:
                print("Connexion WebSocket fermée, tentative de reconnexion...")
                await asyncio.sleep(5)
                return await get_bitcoin_data()

# Exécuter la fonction principale
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_bitcoin_data())
