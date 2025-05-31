import os
import json
from aiokafka import AIOKafkaConsumer
import asyncio

from dotenv import load_dotenv

from Services.RecipeService import pending_responses
load_dotenv()

class KafkaConsumerClient:
    def __init__(self, bootstrap_servers="kafka:9092", group_id="my-group", topic=None):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topic = topic or os.getenv("KAFKA_RESPONSE_TOPIC")
        self.consumer = None
        self._task = None

    async def start(self, on_message):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        await self.consumer.start()
        self._task = asyncio.create_task(self._consume_loop(on_message))

    async def _consume_loop(self, on_message):
        try:
            async for msg in self.consumer:
                await on_message(msg.value)
        finally:
            await self.consumer.stop()

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self.consumer:
            await self.consumer.stop()

kafka_consumer = KafkaConsumerClient()

async def handle_kafka_response(message):
    correlation_id = message.get("id")
    response = message.get("response")

    future = pending_responses.pop(correlation_id, None)
    if future is not None and not future.done():
        future.set_result(response)
    else:
        pass
