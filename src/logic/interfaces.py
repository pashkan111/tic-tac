import abc
from typing import Any
import uuid
from .schemas import Chips
from .events import MoveEvent


class CheckerAbstract(abc.ABC):
    @abc.abstractmethod
    def check_win(self) -> bool:
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


class RepositoryGameAbstract(abc.ABC):
    @abc.abstractmethod
    async def set_board(self, board: BoardAbstract):
        ...

    @abc.abstractmethod
    async def get_board(self) -> BoardAbstract:
        ...

    @abc.abstractmethod
    async def set_current_move(self, next_move: PlayerAbstract):
        ...

    @abc.abstractmethod
    async def check_players_in_wait_list(
        self, rows_count: int
    ) -> PlayerAbstract | None:
        ...

    @abc.abstractmethod
    async def set_players_to_wait_list(self, rows_count: int) -> PlayerAbstract | None:
        ...


class GameAbstract(abc.ABC):
    __slots__ = ("room_id", "players", "repo", "board", "checker", "next_move")
    room_id: uuid.UUID
    players: list[PlayerAbstract]
    repo: RepositoryGameAbstract
    board: BoardAbstract
    checker: CheckerAbstract
    next_move: PlayerAbstract

    @abc.abstractmethod
    async def start(self):
        ...

    @abc.abstractmethod
    async def make_move(self, *, row: int, col: int) -> MoveEvent:
        ...
