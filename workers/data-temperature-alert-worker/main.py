# worker/main.py — ajustado (quita SectorBatchClient/httpx, ya no hace falta)
import asyncio
import logging

from config.event_bus_config import RabbitMQConfig
from core.event_bus.factory import create_event_bus

from config.worker_config import SectorWorkerConfig
from sector_batch_buffer import SectorBatchBuffer
from sector_batch_publisher import SectorBatchPublisher
from sector_alert_service import SectorAlertService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sector_worker")


async def main():
    bus_config = RabbitMQConfig()
    worker_config = SectorWorkerConfig()

    event_bus = create_event_bus(bus_config)
    buffer = SectorBatchBuffer(batch_size=worker_config.batch_size)
    publisher = SectorBatchPublisher(event_bus)
    service = SectorAlertService(buffer, publisher)

    await event_bus.connect()
    logger.info("Sector worker conectado, escuchando %s", worker_config.routing_patterns)

    await event_bus.subscribe(
        patterns=worker_config.routing_patterns,
        handler=service.handle_event,
        group="sector-alert-worker",
    )

    try:
        await asyncio.Event().wait()
    finally:
        await event_bus.disconnect()


if __name__ == "__main__":
    asyncio.run(main())