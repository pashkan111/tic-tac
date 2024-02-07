from dataclasses import dataclass
from typing import Any
from src.logic.events import StartGameResponseEvent
from enum import StrEnum


class Status(StrEnum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


@dataclass(slots=True)
class BaseResponse:
    status: Status
    message: str | None
    data: Any | None


@dataclass(slots=True)
class GameStartResponse(BaseResponse): ...


#     data:


@dataclass(slots=True)
class ClientConnectedResponse(BaseResponse):
    data: StartGameResponseEvent
