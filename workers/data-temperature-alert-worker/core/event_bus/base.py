from abc import ABC, abstractmethod
from typing import Sequence, Callable, Awaitable

from schemas.events import BaseEvent

EventHandler = Callable[[BaseEvent], Awaitable[None]]


class EventBus(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def publish(self, event: BaseEvent) -> None: ...
    
    @abstractmethod
    async def publish_raw(self, routing_key: str, payload: dict) -> None:
        """
        Publica un payload arbitrario (no necesariamente un BaseEvent),
        útil para eventos derivados/agregados como batches de sector.
        """
        ...

    @abstractmethod
    async def subscribe(
            self,
            patterns: Sequence[str],
            handler: EventHandler,
            *,
            group: str | None = None,
    ) -> None:
        """
        Se queda escuchando indefinidamente. Por cada mensaje:
        deserializa -> handler(event) -> ack/commit.
        Si el handler lanza excepción, no se hace ack (Rabbit)
        o no se commitea el offset (Kafka), según implementación.
        """
        ...
