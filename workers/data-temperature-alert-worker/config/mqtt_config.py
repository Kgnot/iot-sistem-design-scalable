"""
Clase de configuraciones de MQTT, en este caso broker de Mosquitto
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseMQTTConfig:
    host: str
    port: int = 1883
    client_id: str = os.getenv("MQTT_CLIENT_ID")
    tls: bool = False


@dataclass
class MosquittoConfig(BaseMQTTConfig):
    username: str = "admin"
    password: str = ""
    ca_cert: Optional[str] = None  # hace referencia al certificado de la CA que firmó el certificado del broker
    client_cert: Optional[
        str] = None  # hace referencia al certificado del cliente que se usará para autenticarse con el broker
    client_key: Optional[str] = None  # este es la llave del cliente


@dataclass
class AWSIoTConfig(BaseMQTTConfig):
    ca_cert: str = os.getenv("AWS_CA_CERT")
    client_cert: str = os.getenv("AWS_CLIENT_CERT")
    client_key: str = os.getenv("AWS_CLIENT_KEY")
    port: int = 8883
    tls: bool = True
