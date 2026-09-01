import logging

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point

from config.influx_config import InfluxConfig
from schema.events import TelemetryEvent

logger = logging.getLogger(__name__)


class TelemetryRepository:
    def __init__(self, config: InfluxConfig):
        self.config = config
        self._client: InfluxDBClientAsync | None = None

    async def connect(self) -> None:
        self._client = InfluxDBClientAsync(
            url=self.config.url, token=self.config.token, org=self.config.org
        )

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()

    async def save(self, event: TelemetryEvent) -> None:
        logger.info("Guardando telemetría en InfluxDB: device_id=%s sensor_type=%s value=%s", event.device_id, event.sensor_type.value, event.value)
        point = (
            Point("telemetry")
            .tag("device_id", event.device_id)
            .tag("sensor_type", event.sensor_type.value)
            .tag("locality_id", event.locality_id)
            .tag("sector", event.sector)
            .field("value", event.value)
            .field("unit", event.unit)
            .time(event.timestamp)
        )
        write_api = self._client.write_api()
        await write_api.write(bucket=self.config.bucket, record=point)
        logger.info("Telemetría guardada en InfluxDB correctamente para device_id=%s", event.device_id)