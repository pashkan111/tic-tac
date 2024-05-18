from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

import orjson

from src.logic.enums.event_type import EventType

MessageType = EventType
# TODO REMOVE


class ResponseStatus(StrEnum):
    """Статусы ответов клиенту"""

    START = "START"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    MOVE = "MOVE"
    FINISHED = "FINISHED"
    SURRENDER = "SURRENDER"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


# TODO статус будет error or success


@dataclass(slots=True)
class BaseResponse:
    status: ResponseStatus
    message: str | None
    data: Any | None
    type: MessageType = MessageType.RESPONSE

    def to_json(self) -> bytes:
        return orjson.dumps(asdict(self))


@dataclass(slots=True)
class GameStartResponse(BaseResponse):
    ...


@dataclass(slots=True)
class ClientResponse(BaseResponse):
    data: Any
