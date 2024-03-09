from dataclasses import dataclass, asdict
import orjson
from typing import Any
from src.logic.events.responses import BaseResponseEvent
from enum import StrEnum
from src.logic.events.messages import MessageType


class ResponseStatus(StrEnum):
    """Статусы ответов клиенту на события"""

    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    SUCCESS = "SUCCESS"
    FINISHED = "FINISHED"
    SURRENDER = "SURRENDER"
    ERROR = "ERROR"


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
    data: BaseResponseEvent
