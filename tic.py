"""
___ ___ ___

___ ___ ___

___ ___ ___

"""
from typing import TypeAlias, Any

Board: TypeAlias = list[list[Any]]
MAX_ROWS = 30


def show_board(board: Board):
    result = ""
    for row in board:
        string_row = list(map(str, row))
        row_result = "|"
        for elem in string_row:
            if len(elem) == 1:
                row_result += f" {elem} |"
                continue
            elif len(elem) == 2:
                row_result += f"{elem} |"
            elif len(elem) == 3:
                row_result += f"{elem}|"

        result += row_result + "\n"


def main():
    pass


board = {1: "", 2: "", 3: "", 4: "X"}
