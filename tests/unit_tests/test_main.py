from src.logic.main import create_game
import pytest
import uuid
from src.logic.exceptions import (
    NotEnoughArgsException,
    RoomNotFoundInRepoException,
    PartnerDoesNotExistsException,
)
from src.logic.schemas import GameRedisSchema
from src.logic.game import Game


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
    mocker.patch("src.logic.main.repo.set_game")

    repo_get_game_mocked = mocker.patch("src.logic.main.repo.get_game")
    repo_get_game_mocked.configure_mock(
        return_value=GameRedisSchema(
            room_id=room_id,
            players=[player1_fixture, player2_fixture],
            current_move_player=player1_fixture,
            board=board_fixture.board,
        )
    )

    repo_check_players_in_wait_list_mocked = mocker.patch(
        "src.logic.main.repo.check_players_in_wait_list"
    )
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=player1_fixture)

    game = await create_game(
        player_id=player_id,
        rows_count=rows_count,
        room_id=room_id,
    )
    assert isinstance(game, Game)


async def test_create_game__enough_args__room_not_in_repo(
    mocker,
    player1_fixture,
):
    repo_get_game_mocked = mocker.patch("src.logic.main.repo.get_game")
    repo_get_game_mocked.configure_mock(return_value=None)

    repo_check_players_in_wait_list_mocked = mocker.patch(
        "src.logic.main.repo.check_players_in_wait_list"
    )
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=player1_fixture)
    with pytest.raises(RoomNotFoundInRepoException):
        await create_game(
            room_id=uuid.uuid4(),
        )


async def test_create_game__enough_args__room_not_in_repo__game_created(
    mocker,
    player1_fixture,
):
    repo_get_game_mocked = mocker.patch("src.logic.main.repo.get_game")
    repo_get_game_mocked.configure_mock(return_value=None)

    repo_check_players_in_wait_list_mocked = mocker.patch(
        "src.logic.main.repo.check_players_in_wait_list"
    )
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=player1_fixture)
    game = await create_game(
        player_id=player1_fixture,
        rows_count=10,
        room_id=uuid.uuid4(),
    )
    assert isinstance(game, Game)


async def test_create_game__enough_args__partner_not_found_in_wait_list(
    mocker,
    player1_fixture,
):
    repo_get_game_mocked = mocker.patch("src.logic.main.repo.get_game")
    repo_get_game_mocked.configure_mock(return_value=None)

    repo_check_players_in_wait_list_mocked = mocker.patch(
        "src.logic.main.repo.check_players_in_wait_list"
    )
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=None)
    with pytest.raises(PartnerDoesNotExistsException):
        await create_game(
            player_id=player1_fixture,
            rows_count=10,
        )
    repo_check_players_in_wait_list_mocked.assert_called_once_with(player1_fixture)


@pytest.mark.asyncio
async def test_create_game__game_in_repo(
    mocker,
    player1_fixture,
    player2_fixture,
    board_fixture,
):
    room_id = uuid.uuid4()

    mocker.patch("src.logic.main.repo.set_game")

    repo_get_game_mocked = mocker.patch("src.logic.main.repo.get_game")
    repo_get_game_mocked.configure_mock(
        return_value=GameRedisSchema(
            room_id=room_id,
            players=[player1_fixture, player2_fixture],
            current_move_player=player1_fixture,
            board=board_fixture.board,
        )
    )

    game = await create_game(room_id=room_id)
    assert game.room_id == room_id
    assert game.current_move_player == player1_fixture
    assert game.players == [player1_fixture, player2_fixture]


@pytest.mark.asyncio
async def test_create_game__game_not_in_repo(
    mocker,
    player1_fixture,
    player2_fixture,
):
    repo_get_game_mocked = mocker.patch("src.logic.main.repo.get_game")
    repo_get_game_mocked.configure_mock(return_value=None)

    mocker.patch("src.logic.main.repo.set_game")

    repo_check_players_in_wait_list_mocked = mocker.patch(
        "src.logic.main.repo.check_players_in_wait_list"
    )
    repo_check_players_in_wait_list_mocked.configure_mock(return_value=player1_fixture)

    game = await create_game(player_id=player2_fixture.id, rows_count=10)

    assert game.current_move_player == player1_fixture
    assert game.players == [player1_fixture, player2_fixture]
