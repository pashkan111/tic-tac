from dataclasses import dataclass
from enum import StrEnum
from src.logic.game.schemas import PlayerId
from src.logic.auth.schemas import Token


class ClientEventType(StrEnum):
    START = "START"
    MOVE = "MOVE"


# @dataclass(frozen=True, slots=True)
# class BaseEvent:
#     """Базовое событие для передачи по вебсокетам"""

#     event_type: ClientEventType


@dataclass(frozen=True, slots=True)
class MoveEvent:
    row: int
    col: int
    event_type: ClientEventType = ClientEventType.MOVE


@dataclass(frozen=True, slots=True)
class StartGameEvent:
    token: Token
    event_type: ClientEventType = ClientEventType.START
