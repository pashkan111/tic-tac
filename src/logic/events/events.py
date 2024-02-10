from dataclasses import dataclass
from enum import StrEnum
from src.logic.auth.schemas import Token


class ClientEventType(StrEnum):
    START = "START"
    MOVE = "MOVE"
    SURRENDER = "SURRENDER"


@dataclass(slots=True)
class MoveEvent:
    row: int
    col: int
    event_type: ClientEventType = ClientEventType.MOVE


@dataclass(slots=True)
class StartGameEvent:
    token: Token
    event_type: ClientEventType = ClientEventType.START
