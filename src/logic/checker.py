from .interfaces import CheckerAbstract, Chips
from .board import BoardArray
from collections import defaultdict


class CheckerArray(CheckerAbstract):
    def check_win(self, board: BoardArray) -> bool:
        return any([
            self._check_diagonal(board), self._check_gorizontal(board), self._check_vertical(board)
        ])

    def _check_diagonal(self, board: BoardArray) -> Chips | None:
        values = []
        for num, row in enumerate(board.cells):
            values.append(row[num])

        unique_values: set[int] = set(values)
        if len(unique_values) == 1 and unique_values != {0}:
            return Chips.get_chip_by_id(tuple(unique_values)[0])
        return None

    def _check_gorizontal(self, board: BoardArray) -> Chips | None:
        for row in board.cells:
            unique_values: set[int] = set(row)
            if len(unique_values) == 1 and unique_values != {0}:
                return Chips.get_chip_by_id(tuple(unique_values)[0])
        return None

    def _check_vertical(self, board: BoardArray) -> Chips | None:
        values = defaultdict(list)
        for _, row in enumerate(board.cells):
            for num, i in enumerate(row):
                values[num].append(i)
        
        for _, value in values.items():
            unique_values: set[int] = set(value)
            if len(unique_values) == 1 and unique_values != {0}:
                return Chips.get_chip_by_id(tuple(unique_values)[0])
        return None

