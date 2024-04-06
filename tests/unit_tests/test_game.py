from src.logic.interfaces import Chips
from src.logic.game.game import Game
from src.logic.exceptions import PlayersNotEnoughException, GameNotActiveException
import pytest
import uuid
from unittest.mock import patch
from unittest.mock import AsyncMock
from src.logic.game.schemas import GameRedisSchema
from asyncio import Future


@pytest.mark.asyncio
async def test_game_created(player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture):
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
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture, mocker
):
    repo_fixture.get_game.return_value = GameRedisSchema(
        room_id=uuid.uuid4(),
        is_active=False,
        players=[player1_fixture, player2_fixture],
        current_move_player=player1_fixture,
        board=board_fixture.board,
        winner=None,
    )

    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    with pytest.raises(GameNotActiveException) as exc:
        await game.make_move(player_id=player1_fixture.id, row=2, col=3)
        assert str(game.room_id) in str(exc)


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
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture, mocker
):
    repo_fixture.get_game.return_value = AsyncMock()
    mocker.patch("src.logic.game.game.Game._save_state")
    mocker.patch("src.logic.game.game.Game._update_state")

    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    await game.start()

    assert game.current_move_player == player1_fixture
    game._switch_player()
    assert game.current_move_player == player2_fixture
    game._switch_player()
    assert game.current_move_player == player1_fixture


@pytest.mark.asyncio
async def test_game_make_move__next_move_player_changes(
    player1_fixture, player2_fixture, board_fixture, repo_fixture, checker_fixture, mocker
):
    repo_fixture.get_game.return_value = AsyncMock()
    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    mocker.patch("src.logic.game.game.Game._save_state")
    mocker.patch("src.logic.game.game.Game._update_state")

    await game.start()

    await game.make_move(row=1, col=1, player_id=player1_fixture.id)
    await game.make_move(row=2, col=1, player_id=player2_fixture.id)
    await game.make_move(row=1, col=2, player_id=player1_fixture.id)
    await game.make_move(row=2, col=2, player_id=player2_fixture.id)
    await game.make_move(row=3, col=3, player_id=player1_fixture.id)

    board = game.board.board

    assert board[0][0] == 1
    assert board[0][1] == 1
    assert board[1][0] == 2
    assert board[1][1] == 2

    assert game.current_move_player == player2_fixture


@pytest.mark.asyncio
async def test_game__set_state__check_call_count(
    player1_fixture,
    player2_fixture,
    board_fixture,
    checker_fixture,
    repo_fixture,
    mocker,
):
    save_state_mocked = mocker.patch("src.logic.game.game.Game._save_state")
    mocker.patch("src.logic.game.game.Game._update_state")

    repo_fixture.set_game.return_value = AsyncMock()

    game = Game(
        repo=repo_fixture,
        board=board_fixture,
        players=[player1_fixture, player2_fixture],
        checker=checker_fixture,
    )

    await game.start()

    assert game.current_move_player == player1_fixture

    await game.make_move(row=1, col=1, player_id=player1_fixture.id)
    await game.make_move(row=2, col=1, player_id=player2_fixture.id)
    await game.make_move(row=1, col=2, player_id=player1_fixture.id)
    await game.make_move(row=2, col=2, player_id=player2_fixture.id)
    await game.make_move(row=3, col=3, player_id=player1_fixture.id)

    assert save_state_mocked.call_count == 6
