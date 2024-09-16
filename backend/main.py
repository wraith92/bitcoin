from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
import os

from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

# Configuration CORS
origins = [
    "http://localhost:3000",  # Adresse de votre front-end en développement
    # Ajoutez d'autres origines si nécessaire
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Kafka à partir des variables d'environnement
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'bitcoin_prices')


@app.on_event("startup")
async def startup_event():
    # Initialiser le producteur Kafka
    app.state.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await app.state.kafka_producer.start()


@app.on_event("shutdown")
async def shutdown_event():
    # Arrêter le producteur Kafka
    await app.state.kafka_producer.stop()


# Exemple d'Endpoint pour Envoyer un Message à Kafka
@app.post("/send/")
async def send_message(message: dict):
    await app.state.kafka_producer.send_and_wait(KAFKA_TOPIC, message)
    return {"status": "Message envoyé à Kafka", "message": message}


# Endpoint GET pour lire les messages de Kafka
@app.get("/read_messages/")
async def read_messages():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="frontend-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset='latest'
    )
    await consumer.start()
    messages = []
    try:
        # Lire un nombre défini de messages (par exemple 10)
        async for msg in consumer:
            bitcoin_data = msg.value
            messages.append(bitcoin_data)
            if len(messages) >= 10:  # Limiter à 10 messages
                break
    finally:
        await consumer.stop()

    return {"messages": messages}
