import json
import logging

import aio_pika
from core.event_bus.base import EventBus
from config.event_bus_config import RabbitMQConfig
from schemas.events import BaseEvent, deserialize_event

logger = logging.getLogger(__name__)


class RabbitMQEventBus(EventBus):
    def __init__(self, config: RabbitMQConfig):
        self.config = config
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.Channel | None = None
        self._exchange: aio_pika.Exchange | None = None

    async def connect(self) -> None:
        logger.info("Conectando a RabbitMQ en %s", self.config.url)
        self._connection = await aio_pika.connect_robust(self.config.url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self.config.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )
        logger.info("RabbitMQ conectado y exchange '%s' listo", self.config.exchange_name)

    async def disconnect(self) -> None:
        if self._connection:
            logger.info("Cerrando conexión RabbitMQ")
            await self._connection.close()

    async def publish(self, event: BaseEvent) -> None:
        message = aio_pika.Message(
            body=event.model_dump_json().encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        logger.info("Publicando evento por RabbitMQ: routing_key=%s payload=%s", event.routing_key, event.model_dump())
        await self._exchange.publish(message, routing_key=event.routing_key)

    async def publish_raw(self, routing_key: str, payload: dict) -> None:
        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        logger.info("Publicando batch por RabbitMQ: routing_key=%s payload=%s", routing_key, payload)
        await self._exchange.publish(message, routing_key=routing_key)

    async def subscribe(self, patterns, handler, *, group=None):
        queue_name = group or f"queue.{'.'.join(patterns)}"
        queue = await self._channel.declare_queue(queue_name, durable=True)

        for pattern in patterns:
            await queue.bind(self._exchange, routing_key=pattern)

        logger.info("Worker escuchando RabbitMQ con queue=%s patterns=%s", queue_name, patterns)
        await self._channel.set_qos(prefetch_count=10)  # backpressure

        async def _on_message(message: aio_pika.IncomingMessage):
            try:
                logger.info("Mensaje recibido en RabbitMQ topic=%s", message.routing_key)
                event = deserialize_event(message.body)
                logger.info("Evento deserializado: %s", event)
                await handler(event)
                await message.ack()
                logger.info("Mensaje ACKed: %s", message.routing_key)
            except Exception:
                logger.exception("Error procesando mensaje en RabbitMQ: routing_key=%s", getattr(message, 'routing_key', 'unknown'))
                # requeue=False -> si tienes DLX configurado, va a la dead-letter queue
                await message.nack(requeue=False)

        await queue.consume(_on_message)
