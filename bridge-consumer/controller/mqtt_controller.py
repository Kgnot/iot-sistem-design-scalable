import json
import logging

from schema.events import TelemetryEvent, SensorType
from service.telemetry_service import TelemetryService

logger = logging.getLogger(__name__)


class MQTTController:
    def __init__(self, telemetry_service: TelemetryService):
        self.telemetry_service = telemetry_service

    async def on_message(self, topic: str, payload: bytes) -> None:
        logger.info("MQTT message received on topic '%s'", topic)

        parts = topic.split("/")
        if len(parts) < 4 or parts[0] != "devices":
            logger.warning("Topic no soportado: %s", topic)
            return

        device_type, device_id, message_kind = parts[1], parts[2], parts[3]
        data = json.loads(payload)
        logger.info("Processing MQTT payload for device_id=%s, kind=%s, payload=%s", device_id, message_kind, data)

        if message_kind == "telemetry":
            event = TelemetryEvent(
                device_id=device_id,
                device_type=device_type,
                sensor_type=SensorType(data["sensor_type"]),
                value=data["value"],
                unit=data["unit"],
                locality_id=data["locality_id"],
                locality_name=data["locality_name"],
                sector=data["sector"],
            )
            logger.info("Telemetry event created: %s", event)
            await self.telemetry_service.handle_incoming(event)