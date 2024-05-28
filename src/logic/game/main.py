import uuid
from logging import getLogger

from src.logic.exceptions import (
    NotEnoughArgsException,
    PlayersAlreadyInWaitingListException,
    PlayersNotEnoughException,
    RoomNotFoundInRepoException,
    ServerException,
)
from src.repo.repository_game import repo

from .board import BoardArray
from .checker import CheckerArray
from .game import Game
from .player import Player
from .schemas import GameRedisSchema

logger = getLogger(__name__)

"""
1. Проверка на наличие аргументов либо room_id либо (player_id, rows_count)

Если есть только room_id, то,
    1. Проверяем наличие игры в редисе, если она есть, то проверяем 
        Дату создания
Есди нет, то кидаем исключение что игра не найдена

Если только (player_id, rows_count) тогда:
    1. Проверяем, есть ли у игрока активные игры. Если есть, то
        получаем ее и возвращаем
    
    Если нет, то пытаемся получить соперника для него из списка ожидания 
    Если соперник есть, то создаем игру, возвращаем ее,
      удаляем партнера из списка ожидания,
      добавляем игрока в комнату players_by_rooms
      добавляем игрока в словарь active_players
    Если нет, то PartnerDoesNotExistsException и добавляем игрока
    в список ожидания
"""


async def create_game(
    *, player_id: int | None = None, rows_count: int | None = None, room_id: uuid.UUID | None = None
) -> Game:
    if player_id and rows_count:
        # Check if player has active games
        existing_game_id = await repo.get_player_active_game(player_id)

        if existing_game_id:
            game_data = await repo.get_game(existing_game_id)
            if game_data:
                game = _make_game(game_data)
                await game.start()
                return game

            error_msg = (
                f"Player has active game but game does not exist. Player_id: {player_id}, existing_game_id: {room_id}"
            )
            logger.error(error_msg)
            raise ServerException(message=error_msg)

        partner = await repo.check_players_in_wait_list(rows_count)
        if partner and partner.id == int(player_id):
            raise PlayersAlreadyInWaitingListException(rows_count=rows_count)

        new_player = Player(id=player_id, chip=None)
        if not partner:
            await repo.set_players_to_wait_list(player=new_player, rows_count=rows_count)
            raise PlayersNotEnoughException(room_id=room_id)

        board = BoardArray(rows_count=rows_count)
        new_game = Game(
            repo=repo,
            board=board,
            checker=CheckerArray(),
            players=[partner, new_player],
        )
        await new_game.start()
        return new_game

    if not room_id:
        raise NotEnoughArgsException(room_id=room_id, rows_count=rows_count, player_id=player_id)

    game_data = await repo.get_game(room_id)

    if not game_data and not (rows_count and player_id):
        raise RoomNotFoundInRepoException(room_id=room_id)

    game = _make_game(game_data)
    await game.start()
    return game


async def main(
    *, player_id: int | None = None, rows_count: int | None = None, room_id: uuid.UUID | None = None
) -> Game | None:
    game = await create_game(player_id=player_id, rows_count=rows_count, room_id=room_id)
    return game


def _make_game(game_data: GameRedisSchema) -> Game:
    board = BoardArray(board=game_data.board)
    return Game(
        repo=repo,
        board=board,
        checker=CheckerArray(),
        players=game_data.players,
        current_move_player=game_data.current_move_player,
        room_id=game_data.room_id,
    )
