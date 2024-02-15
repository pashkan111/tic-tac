from dataclasses import dataclass
from enum import StrEnum
from src.logic.auth.schemas import Token
from typing import Any
import orjson


class ClientEventType(StrEnum):
    START = "START"
    MOVE = "MOVE"
    SURRENDER = "SURRENDER"


@dataclass(slots=True)
class BaseEvent:
    data: Any
    event_type: ClientEventType

    def to_json(self) -> str:
        return orjson.dumps(self.__dict__).decode()


@dataclass(slots=True)
class MoveEventData:
    row: int
    col: int


@dataclass(slots=True)
class StartGameEventData:
    token: Token


@dataclass(slots=True)
class MoveEvent(BaseEvent):
    data: MoveEventData
    event_type: ClientEventType = ClientEventType.MOVE


@dataclass(slots=True)
class StartGameEvent:
    data: StartGameEventData
    event_type: ClientEventType = ClientEventType.START
