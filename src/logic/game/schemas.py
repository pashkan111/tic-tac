from dataclasses import dataclass
from datetime import datetime
from enum import Enum, StrEnum
from typing import TYPE_CHECKING, TypeAlias
from uuid import UUID

from src.logic.exceptions import ChipDoesNotExistsException

if TYPE_CHECKING:
    from .player import Player


PlayerId: TypeAlias = int
Board: TypeAlias = list[list[int]]


class GameStatus(StrEnum):
    VICTORY = "VICTORY"
    DRAW = "DRAW"
    IN_PROGRESS = "IN_PROGRESS"

    @property
    def is_finished(self):
        return self in [GameStatus.VICTORY, GameStatus.DRAW]

    @property
    def in_progress(self):
        return self == GameStatus.IN_PROGRESS


class Chips(Enum):
    X = 1
    O = 2

    @classmethod
    def get_chip_by_id(cls, id: int) -> "Chips":
        for chip in cls:
            if chip.value == id:
                return chip
        raise ChipDoesNotExistsException(id=id)


@dataclass(slots=True)
class CheckResultNew:
    status: GameStatus
    winner: Chips | None = None


@dataclass(slots=True)
class GameRedisSchema:
    room_id: UUID
    players: list["Player"]
    current_move_player: "Player | None"
    board: "Board"
    game_status: GameStatus | None
    winner: "Player | None"
    last_updated: datetime = datetime.now()


@dataclass(slots=True)
class GameRedisWriteSchema:
    room_id: UUID
    players: list[PlayerId]
    current_move_player: PlayerId
    board: "Board"
