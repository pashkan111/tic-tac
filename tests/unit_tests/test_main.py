from src.logic.game.main import create_game
import pytest
from unittest.mock import call
import uuid
from src.logic.exceptions import (
    NotEnoughArgsException,
    RoomNotFoundInRepoException,
    PlayersAlreadyInWaitingListException,
    ServerException,
)
from src.logic.game.schemas import GameRedisSchema
from src.logic.game.game import Game, Player


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "player_id, rows_count, room_id",
    [
        (None, None, None),
        (None, 5, None),
    ],
)
async def test_create_game__not_enough_args(player_id, rows_count, room_id):
    with pytest.raises(NotEnoughArgsException):
        await create_game(
            player_id=player_id,
            rows_count=rows_count,
            room_id=room_id,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "player_id, rows_count, room_id",
    [
        (1, 4, None),
        (None, None, 3),
    ],
)
async def test_create_game__enough_args(
    player_id,
    rows_count,
    room_id,
    mocker,
    player1_fixture,
    player2_fixture,
    board_fixture,
):
    mocker.patch("src.logic.game.main.repo.set_game")

    repo_get_game_mocked = mocker.patch("src.logic.game.main.repo.get_game")
    repo_get_game_mocked.configure_mock(
        return_value=GameRedisSchema(
            room_id=room_id,
            is_active=True,
            players=[player1_fixture, player2_fixture],
            current_move_player=player1_fixture,
            board=board_fixture.board,
            winner=None,
        )
    )

    repo_check_players_in_wait_list_mocked = mocker.patch("src.logic.game.main.repo.check_players_in_wait_list")
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=player1_fixture)

    repo_get_game_players_mocked = mocker.patch("src.logic.game.main.repo.get_player_active_game")
    repo_get_game_players_mocked.configure_mock(return_value=None)

    mocker.patch("src.logic.game.main.repo.add_players_to_room")

    mocker.patch("src.logic.game.main.repo.remove_players_from_wait_list")
    mocker.patch("src.logic.game.game.Game._save_state")

    game = await create_game(
        player_id=player_id,
        rows_count=rows_count,
        room_id=room_id,
    )
    assert isinstance(game, Game)


@pytest.mark.asyncio
async def test_create_game__enough_args__room_not_in_repo(
    mocker,
):
    repo_get_game_mocked = mocker.patch("src.logic.game.main.repo.get_game")
    repo_get_game_mocked.configure_mock(return_value=None)

    with pytest.raises(RoomNotFoundInRepoException):
        await create_game(
            room_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_create_game__enough_args__player_exist_in_repo(
    mocker,
    player1_fixture: Player,
):
    repo_get_game_mocked = mocker.patch("src.logic.game.main.repo.get_game")
    repo_get_game_mocked.configure_mock(return_value=None)

    repo_check_players_in_wait_list_mocked = mocker.patch("src.logic.game.main.repo.check_players_in_wait_list")
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=player1_fixture)
    with pytest.raises(PlayersAlreadyInWaitingListException):
        await create_game(
            player_id=player1_fixture.id,
            rows_count=10,
            room_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_create_game__enough_args__room_not_in_repo__game_not_created(
    mocker,
    player1_fixture: Player,
    player2_fixture: Player,
):
    room_id = uuid.uuid4()

    repo_get_game_mocked = mocker.patch("src.logic.game.main.repo.get_player_active_game")
    repo_get_game_mocked.configure_mock(return_value=room_id)

    repo_get_game_mocked = mocker.patch("src.logic.game.main.repo.get_game")
    repo_get_game_mocked.configure_mock(return_value=None)

    repo_check_players_in_wait_list_mocked = mocker.patch("src.logic.game.main.repo.check_players_in_wait_list")
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=player2_fixture)

    with pytest.raises(ServerException) as e:
        await create_game(
            player_id=player1_fixture.id,
            rows_count=10,
            room_id=room_id,
        )
    assert (
        e.value.message
        == f"Server Exception. Player has active game but game does not exist. Player_id: {player1_fixture.id}, existing_game_id: {str(room_id)}"
    )


@pytest.mark.asyncio
async def test_create_game__game_not_in_repo(
    mocker,
    player1_fixture,
    player2_fixture,
):
    repo_get_game_mocked = mocker.patch("src.logic.game.main.repo.get_game")
    repo_get_game_mocked.configure_mock(return_value=None)

    mocker.patch("src.logic.game.main.repo.set_game")

    repo_check_players_in_wait_list_mocked = mocker.patch("src.logic.game.main.repo.check_players_in_wait_list")
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=player1_fixture)

    repo_get_game_players_mocked = mocker.patch("src.logic.game.main.repo.get_player_active_game")
    repo_get_game_players_mocked.configure_mock(return_value=None)

    repo_add_players_to_room_mocked = mocker.patch("src.logic.game.main.repo.add_players_to_room")
    repo_remove_players_from_wait_list_mocked = mocker.patch("src.logic.game.main.repo.remove_players_from_wait_list")

    repo_set_game_players_mocked = mocker.patch("src.logic.game.main.repo.set_game_players")

    game = await create_game(player_id=player2_fixture.id, rows_count=10)

    assert game.current_move_player == player1_fixture
    assert game.players == [player1_fixture, player2_fixture]
    repo_add_players_to_room_mocked.assert_called_once_with(
        player_ids=[player1_fixture.id, player2_fixture.id], room_id=game.room_id
    )
    repo_remove_players_from_wait_list_mocked.assert_called_once_with(rows_count=10)
    repo_set_game_players_mocked.assert_has_calls(
        [
            call(player_id=player1_fixture.id, room_id=game.room_id),
            call(player_id=player2_fixture.id, room_id=game.room_id),
        ]
    )
