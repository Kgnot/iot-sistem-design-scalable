import os
from dataclasses import dataclass, field


@dataclass
class EventBusConfig:
    pass


@dataclass
class RabbitMQConfig(EventBusConfig):
    url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
    exchange_name: str = "events"


@dataclass
class KafkaConfig(EventBusConfig):
    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092", )

    topic_map: dict[str, str] = field(default_factory=lambda: {
        "telemetry.weather": "telemetry-weather",
        "telemetry.temperature": "telemetry-temperature",
        "telemetry.humidity": "telemetry-humidity",
        "telemetry.wind": "telemetry-wind",
        "telemetry.luminosity": "telemetry-luminosity",
        "telemetry.pressure": "telemetry-pressure",
        "telemetry.motion": "telemetry-motion",
        "telemetry.sound": "telemetry-sound",
        "telemetry.gas": "telemetry-gas",
        "telemetry.magnetometer": "telemetry-magnetometer",
        "telemetry.traffic": "telemetry-traffic",
        "media.image.uploaded": "media-images",
    })

    default_topic: str = "events-dlq"
