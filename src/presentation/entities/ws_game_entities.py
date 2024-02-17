from dataclasses import dataclass
from typing import Any
from src.logic.events.responses import MoveCreatedResponseEvent
from enum import StrEnum
from src.logic.events.messages import MessageType


class ResponseStatus(StrEnum):
    """Статусы ответов клиенту на события"""

    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    SUCCESS = "SUCCESS"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


@dataclass(slots=True)
class BaseResponse:
    status: ResponseStatus
    message: str | None
    data: Any | None
    type: MessageType = MessageType.RESPONSE


@dataclass(slots=True)
class GameStartResponse(BaseResponse):
    ...


@dataclass(slots=True)
class ClientResponse(BaseResponse):
    data: MoveCreatedResponseEvent
