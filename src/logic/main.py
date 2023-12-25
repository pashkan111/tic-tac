from .game import Game
from .checker import CheckerArray
from .board import BoardArray
from .player import Player
from ..repo.repository_game import repo
import uuid
from .exceptions import (
    NotEnoughArgsException,
    RoomNotFoundInRepoException,
    PartnerDoesNotExistsException,
)


async def create_game(
    *,
    player_id: int | None = None,
    rows_count: int | None = None,
    room_id: uuid.UUID | None = None
) -> Game:
    if not (room_id or (rows_count and player_id)):
        raise NotEnoughArgsException(
            room_id=room_id, rows_count=rows_count, player_id=player_id
        )

    game_data = None
    if room_id:
        game_data = await repo.get_game(room_id)

    if not game_data and not (rows_count and player_id):
        raise RoomNotFoundInRepoException(room_id=room_id)

    if game_data:
        board = BoardArray(board=game_data.board)
        # TODO add checking players in waiting_list
        game = Game(
            repo=repo,
            board=board,
            checker=CheckerArray(),
            players=game_data.players,
            current_move_player=game_data.current_move_player,
            room_id=room_id,
        )
        await game.start()
        return game

    partner = await repo.check_players_in_wait_list(rows_count)
    new_player = Player(id=player_id, chip=None)
    if not partner:
        await repo.set_players_to_wait_list(new_player)
        raise PartnerDoesNotExistsException(room_id=room_id)

    board = BoardArray(rows_count=rows_count)
    new_game = Game(
        repo=repo, board=board, checker=CheckerArray(), players=[partner, new_player]
    )
    await new_game.start()
    return new_game


async def main(
    *,
    player_id: int | None = None,
    rows_count: int | None = None,
    room_id: uuid.UUID | None = None
) -> Game | None:
    game = await create_game(
        player_id=player_id, rows_count=rows_count, room_id=room_id
    )
    return game
