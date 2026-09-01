"""
Facade que centraliza construcción, conexión y desconexión
de todos los recursos de la aplicación (DB, event bus, broker MQTT, storage).
FastAPI solo le pide connect_all() al arrancar y disconnect_all() al apagar.
"""
import logging
import os

from config.mqtt_config import MosquittoConfig, AWSIoTConfig
from config.influx_config import InfluxConfig
from config.r2_config import R2Config
from config.event_bus_config import RabbitMQConfig, KafkaConfig

from core.broker.factory import create_broker
from core.event_bus.factory import create_event_bus

from repository.telemetry_repository import TelemetryRepository
from repository.storage_repository import StorageRepository

from service.telemetry_service import TelemetryService
from service.storage_service import StorageService

from controller.mqtt_controller import MQTTController

logger = logging.getLogger("app_context")


def _build_mqtt_config():
    provider = os.getenv("MQTT_PROVIDER", "mosquitto").lower()
    if provider == "aws":
        return AWSIoTConfig(host=os.getenv("AWS_IOT_ENDPOINT"))
    return MosquittoConfig(
        host=os.getenv("MOSQUITTO_HOST", "localhost"),
        username=os.getenv("MOSQUITTO_USER", "admin"),
        password=os.getenv("MOSQUITTO_PASSWORD", ""),
    )


def _build_event_bus_config():
    provider = os.getenv("EVENT_BUS_PROVIDER", "rabbitmq").lower()
    if provider == "kafka":
        return KafkaConfig()
    return RabbitMQConfig()


class AppContext:
    """
    Único punto de verdad sobre qué instancias existen en la app.
    Se construye una vez en el lifespan de FastAPI y se guarda en app.state.
    """

    def __init__(self) -> None:
        # ---- configs ----
        self.influx_config = InfluxConfig()
        self.r2_config = R2Config()
        self.mqtt_config = _build_mqtt_config()
        self.bus_config = _build_event_bus_config()

        # ---- repositories ----
        self.telemetry_repo = TelemetryRepository(self.influx_config)
        self.storage_repo = StorageRepository(self.r2_config)

        # ---- infraestructura de mensajería ----
        self.event_bus = create_event_bus(self.bus_config)
        self.mqtt_broker = create_broker(self.mqtt_config)

        # ---- services ----
        self.telemetry_service = TelemetryService(self.telemetry_repo, self.event_bus)
        self.storage_service = StorageService(self.storage_repo)

        # ---- controllers ----
        self.mqtt_controller = MQTTController(self.telemetry_service)

    async def connect_all(self) -> None:
        logger.info("Conectando a InfluxDB...")
        await self.telemetry_repo.connect()

        logger.info("Conectando al event bus (%s)...", self.bus_config.__class__.__name__)
        await self.event_bus.connect()

        logger.info("Conectando al broker MQTT (%s)...", self.mqtt_config.__class__.__name__)
        await self.mqtt_broker.connect()

        logger.info("Suscribiéndose al topic MQTT devices/# para consumir telemetría...")
        await self.mqtt_broker.subscribe("devices/#", self.mqtt_controller.on_message)

        logger.info("AppContext listo.")

    async def disconnect_all(self) -> None:
        logger.info("Cerrando conexiones (orden inverso al arranque)...")
        await self.mqtt_broker.disconnect()
        await self.event_bus.disconnect()
        await self.telemetry_repo.disconnect()