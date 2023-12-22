from src.logic.interfaces import Chips
from src.logic.game import Game
from src.logic.schemas import GameRedisSchema
from src.logic.exceptions import PlayersNotEnoughException, GameNotStartedException
import pytest
import uuid
from unittest.mock import patch
import asyncio
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_game_created(
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture
):
    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )
    with patch.object(game, "_save_state", return_value=None) as mock_save_state:
        await game.start()
        mock_save_state.assert_called_once()

    assert isinstance(game.room_id, uuid.UUID)


@pytest.mark.asyncio
async def test_make_move__game_not_started(
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture
):
    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )
    with pytest.raises(GameNotStartedException) as exc:
        await game.make_move(2, 3)
        assert str(game.room_id) in exc


@pytest.mark.asyncio
async def test_game_start__chips_assigned_to_players(
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture
):
    player1_fixture.chip = None
    player2_fixture.chip = None

    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )
    with patch.object(game, "_save_state", return_value=None) as _:
        await game.start()
        players = game.players

        assert players[0].chip == Chips.X
        assert players[1].chip == Chips.O


@pytest.mark.asyncio
async def test_game_start__not_enough_players(
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture
):
    player1_fixture.chip = None
    player2_fixture.chip = None

    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture],
        checker=checker_fixture,
    )
    with pytest.raises(PlayersNotEnoughException):
        await game.start()


@pytest.mark.asyncio
async def test_game_player_switcher(
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture
):
    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )
    with patch.object(game, "_save_state", return_value=None) as _:
        await game.start()

        assert game.current_move_player == player1_fixture
        assert game._switch_player() == player2_fixture
        assert game._switch_player() == player1_fixture
        assert game._switch_player() == player2_fixture


@pytest.mark.asyncio
async def test_game_make_move__next_move_player_changes(
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture
):
    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    with patch.object(game, "_save_state", return_value=None) as _:
        await game.start()

        await game.make_move(row=1, col=1)
        await game.make_move(row=2, col=1)
        await game.make_move(row=1, col=2)
        await game.make_move(row=2, col=2)
        await game.make_move(row=3, col=3)

    board = game.board.board

    assert board[0][0] == 1
    assert board[0][1] == 1
    assert board[1][0] == 2
    assert board[1][1] == 2

    assert game.current_move_player == player2_fixture


@pytest.mark.asyncio
async def test_game__set_state(
    player1_fixture,
    player2_fixture,
    board_fixture,
    repo_fixture,
    checker_fixture,
    mocker,
):
    repo_mocked = mocker.patch("src.logic.repository.repo")
    repo_mocked.configure_mock(**{"set_game": AsyncMock(asyncio.Future())})

    game = Game(
        repo=repo_mocked,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    await game.start()

    repo_mocked.set_game.assert_called_once_with(
        GameRedisSchema(
            room_id=game.room_id,
            players=[player1_fixture, player2_fixture],
            current_move_player=game.current_move_player,
            board=game.board.board,
        )
    )


@pytest.mark.asyncio
async def test_game__set_state__check_call_count(
    player1_fixture,
    player2_fixture,
    board_fixture,
    repo_fixture,
    checker_fixture,
    mocker,
):
    repo_mocked = mocker.patch("src.logic.repository.repo")
    repo_mocked.configure_mock(**{"set_game": AsyncMock(asyncio.Future())})

    game = Game(
        repo=repo_mocked,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    await game.start()

    await game.make_move(row=1, col=1)
    await game.make_move(row=2, col=1)
    await game.make_move(row=1, col=2)
    await game.make_move(row=2, col=2)
    await game.make_move(row=3, col=3)

    assert repo_mocked.set_game.call_count == 6
