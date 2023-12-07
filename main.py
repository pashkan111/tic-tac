"""
___ ___ ___

___ ___ ___

___ ___ ___

"""
from typing import TypeAlias, Any, Callable
from settings import MAX_ROWS
import itertools
from checkers import check_win

Board: TypeAlias = list[list[Any]]



PLAYERS = {1: "X", 2: "O"}


def create_board(rows: int) -> Board:
    board = [[j for j in range(((i-1)*rows)+1, (i*rows)+1)] for i in range(1, rows+1)]
    return board


def show_board(board: Board) -> str:
    result = ''
    for row in board:
        string_row = list(map(str, row))
        row_result = '|'
        for elem in string_row:
            if len(elem) == 1:
                row_result += f' {elem} |'
                continue
            elif len(elem) == 2:
                row_result += f'{elem} |'
            elif len(elem) == 3:
                row_result += f'{elem}|'

        result += row_result + '\n'
    return result


def make_move(*, move_cell: int, player: int, board: Board) -> None:
    for row in board:
        for num, cell in enumerate(row):
            if cell == move_cell:
                row[num] = PLAYERS[player]
                return
    raise Exception("Невозможно сделать ход на это поле. Выберете другое")


def _player_changer() -> Callable[[], int]:
    players_numbers = itertools.repeat(PLAYERS.keys())
    iterator = itertools.chain.from_iterable(players_numbers)

    def switch_player() -> int:
        return next(iterator)
    return switch_player


def main():
    get_player = _player_changer()

    while True:
        try:
            rows_count = int(input(f"Введите размер поля. Максимально значение: {MAX_ROWS}: "))
            break
        except ValueError:
            print("Введите число!")
            continue

    board = create_board(rows_count)

    while True:
        print(show_board(board))

        current_player = get_player()
        
        print(f"Игрок {current_player}, Ваш ход: ")

        while True:
            try:
                move = int(input())
                try:
                    make_move(move_cell=move, player=current_player, board=board)
                    break
                except Exception as e:
                    print(e)
                    continue
                
            except ValueError:
                print("Введите число!")
                continue
    
        is_win = check_win(board)
        if is_win:
            print(f'{current_player} Победил!')
            break
        continue


main()
