from src.logic.interfaces import BoardAbstract
from .player import Player
import settings
from src.logic.exceptions import MakeMoveException, RowsNumberException
from .schemas import Board


class BoardArray(BoardAbstract):
    __slots__ = ["rows_count", "board"]
    board: Board
    rows_count: int

    def __init__(self, *, rows_count: int | None = None, board: Board | None = None):
        self.rows_count = rows_count
        if not board:
            self._create_board(rows_count)
        else:
            self.board = board

    def _create_board(self, rows_count: int) -> None:
        if rows_count > settings.MAX_ROWS or rows_count < settings.MIN_ROWS:
            raise RowsNumberException(max_rows=settings.MAX_ROWS, min_rows=settings.MIN_ROWS)

        board = [[0 for _ in range(rows_count)] for _ in range(rows_count)]
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
