from config.mqtt_config import BaseMQTTConfig, MosquittoConfig, AWSIoTConfig
from core.broker.aws_iot_broker import AWSIoTBroker
from core.broker.mosquitto_broker import MosquittoBroker
from core.broker.mqtt_broker import MQTTBroker


def create_broker(config: BaseMQTTConfig) -> MQTTBroker:
    if isinstance(config, MosquittoConfig):
        return MosquittoBroker(config)
    if isinstance(config, AWSIoTConfig):
        return AWSIoTBroker(config)
    raise ValueError(f"Broker no soportado: {type(config)}")
