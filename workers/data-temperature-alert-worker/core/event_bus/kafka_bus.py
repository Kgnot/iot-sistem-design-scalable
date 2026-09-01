import json

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from core.event_bus.base import EventBus
from config.event_bus_config import KafkaConfig
from schemas.events import BaseEvent, deserialize_event


class KafkaEventBus(EventBus):
    def __init__(self, config: KafkaConfig):
        self.config = config
        self._producer: AIOKafkaProducer | None = None

    async def connect(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self.config.bootstrap_servers)
        await self._producer.start()

    async def disconnect(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def publish(self, event: BaseEvent) -> None:
        topic = self.config.topic_map.get(event.routing_key, self.config.default_topic)
        await self._producer.send_and_wait(
            topic,
            value=event.model_dump_json().encode(),
            key=event.device_id.encode(),
        )
        
    async def publish_raw(self, routing_key: str, payload: dict) -> None:
        topic = self.config.topic_map.get(routing_key, self.config.default_topic)
        await self._producer.send_and_wait(topic, value=json.dumps(payload).encode())

    async def subscribe(self, patterns, handler, *, group=None):
        # Kafka no tiene wildcards de routing como Rabbit;
        # resolvemos patterns -> topics reales usando el mismo topic_map
        topics = [
            real_topic
            for pattern in patterns
            for real_topic in self.config.topic_map.values()
            if pattern.rstrip("*").rstrip(".") in real_topic or pattern == real_topic
        ]
        # más simple y explícito: exige topics reales, no patterns con *
        # topics = [self.config.topic_map[p] for p in patterns]
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.config.bootstrap_servers,
            group_id=group or "default-group",
            enable_auto_commit=False,
        )
        await consumer.start()
        try:
            async for msg in consumer:
                try:
                    event = deserialize_event(msg.value)
                    await handler(event)
                    await consumer.commit()
                except Exception:
                    # no se commitea -> el mensaje se reprocesa en el próximo poll
                    # (aquí normalmente metes logging + métricas + límite de reintentos)
                    pass
        finally:
            await consumer.stop()
