from aiokafka import AIOKafkaProducer
import json


class KafkaProducerClient:
    def __init__(self, bootstrap_servers="kafka:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send(self, topic, value):
        if self.producer is None:
            raise RuntimeError("Kafka producer not started")
        await self.producer.send_and_wait(topic, value)

kafka_producer = KafkaProducerClient()
