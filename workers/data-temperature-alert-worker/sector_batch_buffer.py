import logging
from collections import defaultdict
from typing import Dict, List, Optional

from schemas.events import TelemetryEvent

logger = logging.getLogger(__name__)


class SectorBatchBuffer:
    """
    Esta clase agrupa TelemetryEvent por sector (locality_id + sector) y libera
    un batch completo apenas se alcanza el tamaño configurado
    """

    def __init__(self, batch_size: int):
        self.batch_size = batch_size
        self.buffer: Dict[str, List[TelemetryEvent]] = defaultdict(list)

    def add(self, event: TelemetryEvent) -> Optional[List[TelemetryEvent]]:
        key = self._sector_key(event)
        bucket = self.buffer[key]
        bucket.append(event)

        logger.info("Evento agregado al buffer sector=%s total=%s", key, len(bucket))

        if len(bucket) >= self.batch_size:
            batch = bucket[: self.batch_size]
            self.buffer[key] = bucket[self.batch_size:]
            logger.info("Batch emitido para sector=%s size=%s", key, len(batch))
            return batch
        return None

    @staticmethod
    def _sector_key(event: TelemetryEvent) -> str:
        return f"{event.locality_id}:{event.sector}"
   