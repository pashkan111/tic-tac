from collections import defaultdict

from src.logic.interfaces import CheckerAbstract

from .board import BoardArray
from .schemas import CheckResultNew, Chips, GameStatus


class CheckerArray(CheckerAbstract):
    def check_win_or_draw(self, board: BoardArray) -> CheckResultNew:
        winner = self._check_diagonal(board) or self._check_gorizontal(board) or self._check_vertical(board)
        if winner:
            return CheckResultNew(winner=winner, status=GameStatus.VICTORY)
        has_empty_sells = self._check_empty_sells(board)
        if has_empty_sells:
            return CheckResultNew(status=GameStatus.IN_PROGRESS)
        return CheckResultNew(status=GameStatus.DRAW)

    def _check_diagonal(self, board: BoardArray) -> Chips | None:
        values = []
        for num, row in enumerate(board.board):
            values.append(row[num])

        unique_values: set[int] = set(values)
        if len(unique_values) == 1 and unique_values != {0}:
            return Chips.get_chip_by_id(tuple(unique_values)[0])
        return None

    def _check_gorizontal(self, board: BoardArray) -> Chips | None:
        for row in board.board:
            unique_values: set[int] = set(row)
            if len(unique_values) == 1 and unique_values != {0}:
                return Chips.get_chip_by_id(tuple(unique_values)[0])
        return None

    def _check_vertical(self, board: BoardArray) -> Chips | None:
        values = defaultdict(list)
        for _, row in enumerate(board.board):
            for num, i in enumerate(row):
                values[num].append(i)

        for _, value in values.items():
            unique_values: set[int] = set(value)
            if len(unique_values) == 1 and unique_values != {0}:
                return Chips.get_chip_by_id(tuple(unique_values)[0])
        return None

    def _check_empty_sells(self, board: BoardArray) -> bool:
        for row in board.board:
            if 0 in row:
                return True
        return False
