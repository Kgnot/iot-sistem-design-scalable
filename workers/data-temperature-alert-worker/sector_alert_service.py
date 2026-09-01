from schemas.events import BaseEvent, TelemetryEvent
from sector_batch_buffer import SectorBatchBuffer
from sector_batch_publisher import SectorBatchPublisher


class SectorAlertService:
    def __init__(self, buffer: SectorBatchBuffer, publisher: SectorBatchPublisher):
        self.buffer = buffer
        self.publisher = publisher

    async def handle_event(self, event: BaseEvent) -> None:
        if not isinstance(event, TelemetryEvent):
            return

        batch = self.buffer.add(event)
        if batch:
            await self.publisher.publish_batch(batch)