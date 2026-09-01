# worker/sector_batch_publisher.py
import logging
from typing import List

from core.event_bus.base import EventBus
from schemas.events import TelemetryEvent

logger = logging.getLogger(__name__)

SECTOR_BATCH_ROUTING_KEY = "sector.batch.completed"


class SectorBatchPublisher:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def publish_batch(self, batch: List[TelemetryEvent]) -> None:
        first = batch[0]
        payload = {
            "localityId": first.locality_id,
            "localityName": first.locality_name,
            "sector": first.sector,
            "readings": [
                {
                    "deviceId": e.device_id,
                    "sensorType": e.sensor_type.value,
                    "value": e.value,
                    "unit": e.unit,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in batch
            ],
        }
        await self.event_bus.publish_raw(SECTOR_BATCH_ROUTING_KEY, payload)
        logger.info(f"Batch publicado al bus: sector={first.sector} ({len(batch)} lecturas)")