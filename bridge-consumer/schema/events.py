import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field


# Categorias
class EventCategory(str, Enum):
    TELEMETRY = "telemetry"
    MEDIA = "media"


# Tipos de sensores
class SensorType(str, Enum):
    WEATHER = "weather"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WIND = "wind"
    LUMINOSITY = "luminosity"
    PRESSURE = "pressure"
    MOTION = "motion"
    SOUND = "sound"
    GAS = "gas"
    MAGNETOMETER = "magnetometer"
    TRAFFIC = "traffic"


# Base de los eventos
class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    device_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    locality_id: str
    sector:str

    @property
    def routing_key(self) -> str:
        raise NotImplementedError


# los dos tipos de eventos que existen
class TelemetryEvent(BaseEvent):
    category: Literal[EventCategory.TELEMETRY] = EventCategory.TELEMETRY
    sensor_type: SensorType
    value: float
    unit: str
    locality_name: str

    @property
    def routing_key(self) -> str:
        return f"telemetry.{self.device_id}.{self.device_type}.{self.sensor_type.value}"


class ImageUploadedEvent(BaseEvent):
    category: Literal[EventCategory.MEDIA] = EventCategory.MEDIA
    bucket: str
    object_key: str
    content_type: str
    size_bytes: int | None = None

    @property
    def routing_key(self) -> str:
        return f"media.{self.device_type}.{self.device_id}.image.uploaded"


# union para permitir que un evento pueda ser de cualquiera de los tipos definidos
Event = Union[TelemetryEvent, ImageUploadedEvent]

_EVENT_REGISTRY = {
    EventCategory.TELEMETRY: TelemetryEvent,
    EventCategory.MEDIA: ImageUploadedEvent,
}


def deserialize_event(raw: bytes) -> BaseEvent:
    data = json.loads(raw)
    category = data.get("category")
    model = _EVENT_REGISTRY.get(category)
    if model is None:
        raise ValueError(f"Invalid event category: {category}")
    return model.model_validate(data)