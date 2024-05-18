from dataclasses import dataclass

from src.logic.auth.schemas import Token
from src.logic.enums.client_event_types import ClientEventType

from .base_schemas import BaseEvent


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
