from dataclasses import dataclass
from src.logic.game.schemas import Board, PlayerId


@dataclass(frozen=True, slots=True)
class StartGameResponseEvent:
    board: Board
    current_move_player_id: PlayerId


@dataclass(frozen=True, slots=True)
class MoveCreatedResponseEvent(StartGameResponseEvent):
    board: Board
    current_move_player_id: PlayerId | None
    winner: PlayerId | None
