from dataclasses import dataclass
from typing import Any

from src.logic.game.player import Player
from src.logic.game.schemas import Board

from .base_schemas import BaseResponse
from .events import ClientEventType


@dataclass(slots=True)
class GameStart:
    player: Player
    board: Board
    current_move_player: Player | None


@dataclass(slots=True)
class GameMoveCreated(GameStart):
    winner: Player | None


@dataclass(slots=True)
class PlayerSurrender:
    player: Player
    winner: Player


@dataclass(slots=True)
class GameStartResponse(BaseResponse):
    data: GameStart | None
    event_type: ClientEventType = ClientEventType.START


@dataclass(slots=True)
class MoveCreatedResponse(BaseResponse):
    data: GameMoveCreated | None
    event_type: ClientEventType = ClientEventType.MOVE


@dataclass(slots=True)
class PlayerSurrenderResponse(BaseResponse):
    data: PlayerSurrender
    event_type: ClientEventType = ClientEventType.SURRENDER


@dataclass(slots=True)
class ErrorResponse(BaseResponse):
    event_type: ClientEventType = ClientEventType.START
