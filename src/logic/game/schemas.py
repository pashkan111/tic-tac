from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, Enum
from src.logic.exceptions import ChipDoesNotExistsException
from typing import TYPE_CHECKING, TypeAlias
from uuid import UUID

if TYPE_CHECKING:
    from .player import Player


PlayerId: TypeAlias = int
Board: TypeAlias = list[list[int]]


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


@dataclass(slots=True)
class CheckResult:
    is_winner: bool
    chip: Chips | None = None


@dataclass(slots=True)
class GameRedisSchema:
    room_id: UUID
    players: list["Player"]
    current_move_player: "Player | None"
    board: "Board"
    is_active: bool
    winner: "Player | None"
    last_updated: datetime = datetime.now()


@dataclass(slots=True)
class GameRedisWriteSchema:
    room_id: UUID
    players: list[PlayerId]
    current_move_player: PlayerId
    board: "Board"
