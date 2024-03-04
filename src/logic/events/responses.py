from dataclasses import dataclass
from src.logic.game.schemas import Board
from src.logic.game.player import Player


@dataclass(frozen=True, slots=True)
class StartGameResponseEvent:
    board: Board
    current_move_player: Player


@dataclass(frozen=True, slots=True)
class MoveCreatedResponseEvent:
    board: Board
    current_move_player: Player | None
    winner: Player | None


@dataclass(frozen=True, slots=True)
class SurrenderResponseEvent:
    winner: Player
