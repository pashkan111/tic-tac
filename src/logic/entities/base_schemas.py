from dataclasses import asdict, dataclass
from typing import Any

import orjson

from src.logic.enums.client_event_types import ClientEventType
from src.logic.enums.event_type import EventType
from src.logic.enums.message_statuses import MessageStatus
from src.logic.enums.notification_type import NotificationType
from src.logic.enums.response_status import ResponseStatus


@dataclass(slots=True)
class Base:
    def to_json(self) -> bytes:
        return orjson.dumps(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BaseEvent(Base):
    """Base class for events (message from client to backend)"""

    data: Any
    event_type: ClientEventType


@dataclass(slots=True)
class BaseMessage(Base):
    """Событие, отправляемое в очередь при совершении определенных
    действий клиентом"""

    data: Any
    message_status: MessageStatus


@dataclass(slots=True)
class BaseNotificationEvent(Base):
    """Уведомление клиента о действиях другого игрока"""

    data: Any
    notification_type: NotificationType
    type: EventType = EventType.NOTIFICATION


@dataclass(slots=True)
class BaseResponse(Base):
    response_status: ResponseStatus
    message: str | None
    data: Any | None
    type: EventType = EventType.RESPONSE
