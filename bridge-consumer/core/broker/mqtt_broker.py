import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Optional

import aiomqtt

from config.mqtt_config import BaseMQTTConfig

logger = logging.getLogger(__name__)

MessageHandler = Callable[[str, bytes], Awaitable[None]]


class MQTTBroker(ABC):
    """ Interfaz comun para cualquier broker"""

    def __init__(self, config: BaseMQTTConfig):
        self.config = config
        self._client: Optional[aiomqtt.Client] = None
        self._listen_task: Optional[asyncio.Task] = None

    @abstractmethod
    def _build_tls_context(self):
        """ Construye el contexto TLS para la conexión segura al broker"""
        ...

    async def connect(self):
        tls = self._build_tls_context()
        self._client = aiomqtt.Client(
            hostname=self.config.host,
            port=self.config.port,
            identifier=self.config.client_id,
            tls_context=tls
        )
        await self._client.__aenter__()

    async def disconnect(self):
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None

        if self._client:
            await self._client.__aexit__(None, None, None)

    async def publish(self, topic: str, payload: str):
        if self._client:
            await self._client.publish(topic, payload)
            logger.debug(f"Published {topic} to {payload}")
        else:
            logger.warning("No se puede publicar en el topic: {}".format(topic))

    async def subscribe(self, topic: str, handler: MessageHandler):
        """
        Se suscribe al topic y arranca una tarea en background que
        escucha mensajes indefinidamente, delegando cada uno al handler.
        """
        if not self._client:
            raise RuntimeError("El broker no está conectado, llama a connect() primero")

        await self._client.subscribe(topic)
        logger.info(f"Suscrito al topic: {topic}")

        self._listen_task = asyncio.create_task(self._listen(handler))

    async def _listen(self, handler: MessageHandler):
        try:
            async for message in self._client.messages:
                try:
                    await handler(str(message.topic), message.payload)
                except Exception:
                    logger.exception(f"Error procesando mensaje de {message.topic}")
        except asyncio.CancelledError:
            logger.info("Listener MQTT cancelado, cerrando limpiamente.")
            raise