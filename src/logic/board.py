from .interfaces import BoardAbstract
from .player import Player
import settings
from typing import TypeAlias, Any
from .exceptions import MakeMoveException, RowsNumberException

Board: TypeAlias = list[list[Any]]


class BoardArray(BoardAbstract):
    board: Board

    def __init__(self, rows_count: int):
        self._create_board(rows_count)

    def _create_board(self, rows_count: int) -> None:
        if rows_count > settings.MAX_ROWS or rows_count < settings.MIN_ROWS:
            raise RowsNumberException(
                max_rows=settings.MAX_ROWS, min_rows=settings.MIN_ROWS
            )

        board = [[0 for _ in range(rows_count)] for _ in range(rows_count)]
        # [j for j in range(((i-1)*rows_count)+1, (i*rows_count)+1)] for i in range(1, rows_count+1)
        self.board = board

    def make_move(self, *, player: Player, row: int, col: int) -> None:
        for line_num, line in enumerate(self.board, start=1):
            if not line_num == row:
                continue
            for num, _ in enumerate(line, start=1):
                if num == col:
                    line[num - 1] = player.chip.value
                    return
        raise MakeMoveException(row=row, col=col)
