from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
from enum import StrEnum, Enum
from .exceptions import ChipDoesNotExistsException
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .player import Player
    from .board import Board


PlayerId: TypeAlias = int


class MoveStatus(StrEnum):
    VICTORY = "VICTORY"
    END = "END"
    NEXT_MOVE = "NEXT_MOVE"


@dataclass(frozen=True, slots=True)
class MoveEvent:
    status: MoveStatus
    winner: int | None = None


class Chips(Enum):
    X = 1
    O = 2

    @classmethod
    def get_chip_by_id(cls, id: int) -> "Chips":
        for chip in cls:
            if chip.value == id:
                return chip
        raise ChipDoesNotExistsException(id=id)


@dataclass
class CheckResult:
    is_winner: bool
    chip: Chips | None = None


@dataclass
class GameRedisSchema:
    room_id: UUID
    players: list["Player"]
    current_move_player: "Player"
    board: "Board"
    created: datetime = datetime.now()


@dataclass
class GameRedisWriteSchema:
    room_id: UUID
    players: list[PlayerId]
    current_move_player: PlayerId
    board: "Board"
