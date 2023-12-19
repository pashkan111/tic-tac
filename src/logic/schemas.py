from dataclasses import dataclass
from .player import Player
from .board import Board
from uuid import UUID


@dataclass
class GameRedisSchema:
    room_id: UUID
    players: list[Player]
    current_move_player: Player
    board: Board
