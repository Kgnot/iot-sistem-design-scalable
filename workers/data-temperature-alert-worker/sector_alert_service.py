import logging

from schemas.events import BaseEvent, TelemetryEvent
from sector_batch_buffer import SectorBatchBuffer
from sector_batch_publisher import SectorBatchPublisher

logger = logging.getLogger(__name__)


class SectorAlertService:
    def __init__(self, buffer: SectorBatchBuffer, publisher: SectorBatchPublisher):
        self.buffer = buffer
        self.publisher = publisher

    async def handle_event(self, event: BaseEvent) -> None:
        logger.info("Evento recibido por el worker: %s", event)

        if not isinstance(event, TelemetryEvent):
            logger.warning("Evento ignorado porque no es TelemetryEvent: %s", type(event).__name__)
            return

        batch = self.buffer.add(event)
        if batch:
            logger.info("Lote listo para publicar sector=%s size=%s", event.sector, len(batch))
            await self.publisher.publish_batch(batch)
        else:
            logger.debug("Evento encolado, batch aún no completo para sector=%s", event.sector)