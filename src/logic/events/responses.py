from dataclasses import dataclass
from src.logic.game.schemas import Board
from src.logic.game.player import Player
from typing import Any

"""Ответы на обработку событий клиентам"""


@dataclass(frozen=True, slots=True)
class StartGameData:
    board: Board
    current_move_player: Player


@dataclass(frozen=True, slots=True)
class MoveCreatedData:
    board: Board
    current_move_player: Player | None
    winner: Player | None


@dataclass(frozen=True, slots=True)
class SurrenderData:
    winner: Player


@dataclass(frozen=True, slots=True)
class BaseResponseEvent:
    data: Any


@dataclass(frozen=True, slots=True)
class StartGameResponseEvent(BaseResponseEvent):
    data: StartGameData


@dataclass(frozen=True, slots=True)
class MoveCreatedResponseEvent(BaseResponseEvent):
    data: MoveCreatedData


@dataclass(frozen=True, slots=True)
class SurrenderResponseEvent(BaseResponseEvent):
    data: SurrenderData
