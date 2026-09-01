import logging

import aiomqtt

from config.mqtt_config import MosquittoConfig
from core.broker.mqtt_broker import MQTTBroker

logger = logging.getLogger(__name__)

"""
Broker de mosquitto
"""


class MosquittoBroker(MQTTBroker):

    def __init__(self, config: MosquittoConfig):
        super().__init__(config)
        self._config = config

    def _build_tls_context(self):
        if not self._config.tls:
            return None
        import ssl
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if self._config.ca_cert:
            ctx.load_verify_locations(self._config.ca_cert)
        if self._config.client_cert:
            ctx.load_cert_chain(self._config.client_cert, self._config.client_key)
        return ctx

    async def connect(self):
        self._client = aiomqtt.Client(
            hostname=self._config.host,
            port=self._config.port,
            identifier=self._config.client_id,
            username=self._config.username,
            password=self._config.password,
            tls_context=self._build_tls_context(),
        )
        logger.debug("Connected to broker")
        await self._client.__aenter__()
