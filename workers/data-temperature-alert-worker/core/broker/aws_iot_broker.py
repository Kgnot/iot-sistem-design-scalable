import logging

import aiomqtt

from config.mqtt_config import AWSIoTConfig
from core.broker.mqtt_broker import MQTTBroker

logger = logging.getLogger(__name__)

"""
Broker de AWS IoT
"""


class AWSIoTBroker(MQTTBroker):
    def __init__(self, config: AWSIoTConfig):
        super().__init__(config)
        self._config = config

    def _build_tls_context(self):
        import ssl
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(self._config.ca_cert)
        ctx.load_cert_chain(self._config.client_cert, self._config.client_key)
        return ctx

    async def connect(self):
        self._client = aiomqtt.Client(
            hostname=self._config.host,
            port=self._config.port,
            identifier=self._config.client_id,
            tls_context=self._build_tls_context(),
        )
        logger.debug("Connected to AWS IoT broker")
        await self._client.__aenter__()
