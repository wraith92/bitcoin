import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import os
import json

# Initialize FastAPI app
app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",  # Front-end address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Kafka configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'bitcoin_prices')

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()  # Get the event loop
    # Initialize Kafka producer
    app.state.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        loop=loop  # Pass event loop explicitly
    )
    await app.state.kafka_producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    # Stop Kafka producer
    await app.state.kafka_producer.stop()

# Endpoint to send message to Kafka
@app.post("/send/")
async def send_message(message: dict):
    await app.state.kafka_producer.send_and_wait(KAFKA_TOPIC, message)
    return {"status": "Message sent to Kafka", "message": message}

# Endpoint to read messages from Kafka
@app.get("/read_messages/")
async def read_messages():
    loop = asyncio.get_event_loop()  # Get the event loop
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="frontend-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset='latest',
        loop=loop  # Pass event loop explicitly
    )
    await consumer.start()
    messages = []
    try:
        # Read a set number of messages (e.g., 10)
        async for msg in consumer:
            bitcoin_data = msg.value
            messages.append(bitcoin_data)
            if len(messages) >= 10:  # Limit to 10 messages
                break
    finally:
        await consumer.stop()

    return {"messages": messages}

# Example: Endpoint to trigger Bitcoin data processing manually
@app.get("/process_bitcoin_data/")
async def trigger_processing():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="processing-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    await consumer.start()
    processed_data = []
    try:
        async for message in consumer:
            bitcoin_data = message.value
            processed_data.append(bitcoin_data)
            print(f"Processing Bitcoin data: {bitcoin_data}")
            if len(processed_data) >= 10:
                break
    finally:
        await consumer.stop()
    
    return {"status": "Data processed", "data": processed_data}
