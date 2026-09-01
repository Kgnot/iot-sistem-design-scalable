import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class SectorWorkerConfig:
    batch_size: int = int(os.getenv("SECTOR_BATCH_SIZE", "5"))
    spring_endpoint: str = os.getenv(
        "SPRING_BATCH_ENDPOINT", "http://spring-app:8080/api/sectors/batch"
    )
    routing_patterns: List[str] = field(default_factory=lambda: ["telemetry.*"])