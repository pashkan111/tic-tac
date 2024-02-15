from dataclasses import dataclass
from typing import Any
from src.logic.events.responses import MoveCreatedResponseEvent
from enum import StrEnum


class ResponseStatus(StrEnum):
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


@dataclass(slots=True)
class GameStartResponse(BaseResponse):
    ...


@dataclass(slots=True)
class ClientResponse(BaseResponse):
    data: MoveCreatedResponseEvent
