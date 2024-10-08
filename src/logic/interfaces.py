import abc
import uuid
from typing import Any

from .entities.events import MoveEvent
from .game.schemas import Chips


class CheckerAbstract(abc.ABC):
    @abc.abstractmethod
    def check_win_or_draw(self) -> bool:
        ...

    @abc.abstractmethod
    def _check_diagonal(self, board: "BoardAbstract") -> bool:
        ...

    @abc.abstractmethod
    def _check_gorizontal(self, board: "BoardAbstract") -> bool:
        ...

    @abc.abstractmethod
    def _check_vertical(self, board: "BoardAbstract") -> bool:
        ...


class PlayerAbstract(abc.ABC):
    id: int
    chip: Chips | None


class BoardAbstract(abc.ABC):
    board: Any

    @abc.abstractmethod
    def _create_board(self, rows_count: int) -> None:
        pass

    @abc.abstractmethod
    def make_move(self, *, player: PlayerAbstract, row: int, col: int) -> None:
        pass


class GameAbstract(abc.ABC):
    @abc.abstractmethod
    async def start(self):
        ...

    @abc.abstractmethod
    async def make_move(self, *, row: int, col: int) -> MoveEvent:
        ...
