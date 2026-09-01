from collections import defaultdict

from schemas.events import TelemetryEvent
from typing import Dict, List, Optional


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
        bucket = self._buffers[key]
        bucket.append(event)

        if len(bucket) >= self.batch_size:
            batch = bucket[: self.batch_size]
            self._buffers[key] = bucket[self.batch_size:]
            return batch
        return None

    @staticmethod
    def _sector_key(event: TelemetryEvent) -> str:
        return f"{event.locality_id}:{event.sector}"
    