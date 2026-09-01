from config.event_bus_config import EventBusConfig, RabbitMQConfig, KafkaConfig
from core.event_bus.base import EventBus
from core.event_bus.rabbitmq_bus import RabbitMQEventBus
from core.event_bus.kafka_bus import KafkaEventBus


def create_event_bus(config: EventBusConfig) -> EventBus:
    if isinstance(config, RabbitMQConfig):
        return RabbitMQEventBus(config)
    if isinstance(config, KafkaConfig):
        return KafkaEventBus(config)
    raise ValueError(f"Event bus no soportado: {type(config)}")