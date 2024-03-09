from dataclasses import dataclass
from enum import StrEnum
from src.logic.auth.schemas import Token
from typing import Any
import orjson


"""События, которые отсылает клиент по вебсокетам"""


class ClientEventType(StrEnum):
    START = "START"
    """Событие начала игры. На этом этапе происходит авторизация"""
    MOVE = "MOVE"
    """Событие хода"""
    SURRENDER = "SURRENDER"
    """Событие сдачи"""


@dataclass(slots=True)
class BaseEvent:
    data: Any
    event_type: ClientEventType

    def to_json(self) -> str:
        return orjson.dumps(self.__dict__).decode()


@dataclass(slots=True)
class StartGameEventData:
    token: Token


@dataclass(slots=True)
class MoveEventData:
    row: int
    col: int


@dataclass(slots=True)
class SurrenderEventData:
    """Событие сдачи"""

    ...


@dataclass(slots=True)
class StartGameEvent(BaseEvent):
    """Событие начала игры"""

    data: StartGameEventData
    event_type: ClientEventType = ClientEventType.START


@dataclass(slots=True)
class MoveEvent(BaseEvent):
    """Событие хода"""

    data: MoveEventData
    event_type: ClientEventType = ClientEventType.MOVE


@dataclass(slots=True)
class SurrenderEvent(BaseEvent):
    """Событие сдачи"""

    data: SurrenderEventData
    event_type: ClientEventType = ClientEventType.SURRENDER
