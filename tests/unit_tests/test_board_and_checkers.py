import pytest

from settings import MAX_ROWS, MIN_ROWS
from src.logic.exceptions import MakeMoveException, RowsNumberException
from src.logic.game.board import BoardArray
from src.logic.game.checker import CheckerArray
from src.logic.game.player import Player
from src.logic.game.schemas import CheckResultNew, Chips, GameStatus


def test_board_created():
    new_board = BoardArray(rows_count=10)
    assert len(new_board.board) == 10
    assert len(new_board.board[0]) == 10
    assert len(new_board.board[4]) == 10
    assert new_board.board[0][5] == 0


def test_board_created__with_rows_exceed():
    with pytest.raises(RowsNumberException):
        BoardArray(rows_count=MAX_ROWS + 1)

    with pytest.raises(RowsNumberException):
        BoardArray(rows_count=MIN_ROWS - 1)


def test_check_win_gorizontal():
    board = BoardArray(rows_count=5)
    checker = CheckerArray()

    board.board[3] = [1, 1, 1, 1, 1]

    res = checker.check_win_or_draw(board=board)
    assert res == CheckResultNew(winner=Chips.X, status=GameStatus.VICTORY)


def test_check_win_gorizontal__no_win():
    board = BoardArray(rows_count=5)
    checker = CheckerArray()

    board.board[3] = [1, 1, 1, 1, 2]

    res = checker.check_win_or_draw(board=board)
    assert res == CheckResultNew(status=GameStatus.IN_PROGRESS)


def test_check_win_vertical():
    board = BoardArray(rows_count=5)
    checker = CheckerArray()

    for arr in board.board:
        arr[1] = 2

    res = checker.check_win_or_draw(board=board)
    assert res == CheckResultNew(status=GameStatus.VICTORY, winner=Chips.O)


def test_check_win_vertical__no_win():
    board = BoardArray(rows_count=5)
    checker = CheckerArray()

    for num, arr in enumerate(board.board):
        if num == len(board.board) - 1:
            arr[1] = 1
        else:
            arr[1] = 2

    res = checker.check_win_or_draw(board=board)
    assert res == CheckResultNew(status=GameStatus.IN_PROGRESS)


def test_check_win_diagonal():
    board = BoardArray(rows_count=5)
    checker = CheckerArray()

    for num, arr in enumerate(board.board):
        arr[num] = 1

    res = checker.check_win_or_draw(board=board)
    assert res == CheckResultNew(status=GameStatus.VICTORY, winner=Chips.X)


def test_check_win_diagonal__no_win():
    board = BoardArray(rows_count=5)
    checker = CheckerArray()

    for num, arr in enumerate(board.board):
        if num == len(board.board) - 1:
            arr[num] = 1
        else:
            arr[num] = 2

    res = checker.check_win_or_draw(board=board)
    assert res == CheckResultNew(status=GameStatus.IN_PROGRESS)


def test_board_make_move__move_made():
    board = BoardArray(rows_count=5)
    player = Player(id=10, chip=Chips.O)

    board.make_move(player=player, row=3, col=3)

    assert board.board[2][2] == 2


def test_create_board__with_board():
    current_board = [
        [1, 2, 0],
        [0, 0, 0],
        [1, 1, 0],
    ]
    board = BoardArray(board=current_board)
    assert board.board == current_board


def test_make_moves(player1_fixture):
    board = BoardArray(rows_count=5)
    board.make_move(player=player1_fixture, row=1, col=1)

    with pytest.raises(MakeMoveException):
        board.make_move(player=player1_fixture, row="1", col=2)
    with pytest.raises(MakeMoveException):
        board.make_move(player=player1_fixture, row=2, col="t")
    with pytest.raises(MakeMoveException):
        board.make_move(player=player1_fixture, row=2, col="4")

    with pytest.raises(MakeMoveException):
        board.make_move(player=player1_fixture, row=1, col=1)


def test_check_draw():
    board = BoardArray(rows_count=5)
    checker = CheckerArray()

    for num, arr in enumerate(board.board):
        for i in range(len(arr)):
            arr[i] = num + i + 1

    res = checker.check_win_or_draw(board=board)
    assert res == CheckResultNew(status=GameStatus.DRAW)
