import abc
from typing import Any
import uuid
from dataclasses import dataclass
from enum import StrEnum, Enum
from .exceptions import ChipDoesNotExistsException


class MoveStatus(StrEnum):
    VICTORY = 'VICTORY'
    END = 'END'
    NEXT_MOVE = 'NEXT_MOVE'


@dataclass(frozen=True, slots=True)
class MoveEvent:
    status: MoveStatus
    winner: int | None = None


class Chips(Enum):
    X = 1
    O = 2

    @classmethod
    def get_chip_by_id(cls, id: int) -> 'Chips':
        for chip in cls:
            if chip.value == id:
                return chip
        raise ChipDoesNotExistsException(id=id)
            

@dataclass
class CheckResult:
    is_winner: bool
    chip: Chips | None


class CheckerAbstract(abc.ABC):
    @abc.abstractmethod
    def check_win(self) -> bool:
        ...

    @abc.abstractmethod
    def _check_diagonal(self, board: 'BoardAbstract') -> bool:
        ...
    
    @abc.abstractmethod
    def _check_gorizontal(self, board: 'BoardAbstract') -> bool:
        ...
    
    @abc.abstractmethod
    def _check_vertical(self, board: 'BoardAbstract') -> bool:
        ...


class BoardAbstract(abc.ABC):
    board: Any

    @abc.abstractmethod
    def _create_board(self, rows_count: int) -> None:
        pass

    @abc.abstractmethod
    def make_move(self, player_id: int, row: int, col: int) -> None:
        pass


class PlayerAbstract(abc.ABC):
    id: int
    chip: Chips


class RepositoryAbstract(abc.ABC):
    @abc.abstractmethod
    async def set_board(self, board: BoardAbstract):
        ...

    @abc.abstractmethod
    async def get_board(self) -> BoardAbstract:
        ...

    @abc.abstractmethod
    async def check_players(self, rows_count: int) -> PlayerAbstract | None:
        ...


class GameAbstract(abc.ABC):
    __slots__ = ('room_id', 'players', 'repo', 'board', 'checker', 'next_move')
    room_id: uuid.UUID
    players: list[PlayerAbstract]
    repo: RepositoryAbstract
    board: BoardAbstract
    checker: CheckerAbstract
    next_move: PlayerAbstract

    @abc.abstractmethod
    async def start(self):
        ...

    @abc.abstractmethod
    async def make_move(self, row: int, col: int, player_id: int) -> MoveEvent:
        ...
