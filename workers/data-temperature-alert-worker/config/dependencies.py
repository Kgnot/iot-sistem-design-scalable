from config.influx_config import InfluxConfig
from config.r2_config import R2Config
from config.event_bus_config import RabbitMQConfig
from repository.telemetry_repository import TelemetryRepository
from repository.storage_repository import StorageRepository
from service.telemetry_service import TelemetryService
from service.storage_service import StorageService
from core.event_bus.factory import create_event_bus

influx_repo = TelemetryRepository(InfluxConfig())
event_bus = create_event_bus(RabbitMQConfig())
telemetry_service = TelemetryService(influx_repo, event_bus)

storage_repo = StorageRepository(R2Config())
storage_service = StorageService(storage_repo)


def get_storage_service() -> StorageService:
    return storage_service
