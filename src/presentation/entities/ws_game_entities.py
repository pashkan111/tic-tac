from dataclasses import dataclass
from typing import Any
from src.logic.events import MoveCreatedResponseEvent
from enum import StrEnum


class Status(StrEnum):
    CONNECTED = "CONNECTED"
    SUCCESS = "SUCCESS"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


@dataclass(slots=True)
class BaseResponse:
    status: Status
    message: str | None
    data: Any | None


@dataclass(slots=True)
class GameStartResponse(BaseResponse): ...


@dataclass(slots=True)
class ClientResponse(BaseResponse):
    data: MoveCreatedResponseEvent
