from .interfaces import BoardAbstract
from .player import Player
import settings
from typing import TypeAlias, Any
from .exceptions import MakeMoveException

Board: TypeAlias = list[list[Any]]


class BoardArray(BoardAbstract):
    board: Board

    def __init__(self, rows_count: int):
        self._create_board(rows_count)

    def _create_board(self, rows_count: int) -> None:
        if rows_count > settings.MAX_ROWS and rows_count < settings.MIN_ROWS:
            raise Exception(f"Wrong Rows count. Max: {settings.MAX_ROWS}, Min: {settings.MIN_ROWS}")

        board = [
            [j for j in range(((i-1)*rows_count)+1, (i*rows_count)+1)] for i in range(1, rows_count+1)
        ]
        self.cells = board

    def make_move(self, player: Player, row: int, col: int) -> None:
        for line in self.board:
            if not line == row:
                continue
            for num, _ in enumerate(line, start=1):
                if num == col:
                    line[num - 1] = player.chip.value
                    return
        raise MakeMoveException(row=row, col=col)
