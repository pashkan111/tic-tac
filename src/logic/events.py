from dataclasses import dataclass
from enum import StrEnum
from src.logic.game.schemas import Board
from src.logic.auth.schemas import Token
from src.logic.game.schemas import PlayerId


class ClientEventType(StrEnum):
    START = "START"
    MOVE = "MOVE"


@dataclass(frozen=True, slots=True)
class MoveEvent:
    row: int
    col: int
    event_type: ClientEventType = ClientEventType.MOVE


@dataclass(frozen=True, slots=True)
class StartGameEvent:
    token: Token
    event_type: ClientEventType = ClientEventType.START


@dataclass(frozen=True, slots=True)
class StartGameResponseEvent:
    board: Board
    current_move_player_id: PlayerId
