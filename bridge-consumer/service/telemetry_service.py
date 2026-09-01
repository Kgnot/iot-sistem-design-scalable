import logging

from core.event_bus.base import EventBus
from repository.telemetry_repository import TelemetryRepository
from schema.events import TelemetryEvent

logger = logging.getLogger(__name__)


class TelemetryService:
    def __init__(self, repository: TelemetryRepository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    async def handle_incoming(self, event: TelemetryEvent) -> None:
        logger.info("Received telemetry event: %s", event)

        # apenas llega lo guardamos y luego
        await self.repository.save(event)
        logger.info("Telemetry event saved to repository: %s", event)

        # lo publicamos
        await self.event_bus.publish(event)
        logger.info("Telemetry event published to event bus: %s", event)