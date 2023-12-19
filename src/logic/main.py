from .game import Game
from .checker import CheckerArray
from .board import BoardArray
from .player import Player
from .repository import repo
import uuid
from .schemas import GameRedisSchema
# REQUEST: {
#     rows_count: int
# }
# HEADERS: {
#     token: str
# }
# RESPONSE: {
#     game_started: bool
#     partner_id: int | None
#     room_id: UUID | None
# }

# Когда игрок начинает новую игру, уходит пост запрос на бэк,
# там в редисе смотрим наличие ожидающего игрока с
# таким количеством клеток, если он есть, то
# возвращаем его айди и game_started=True и айди комнаты
# Если нет, то создаем в редисе новую запись и game_started=False


class Authentication:
    ...


async def create_game(*, player_id: int | None = None, rows_count: int | None = None, room_id: uuid.UUID | None = None) -> Game | None:
    game_data = await repo.get_game(room_id)
    if game_data:
        board = BoardArray(board=game_data.board)
        game = Game(
            repo=repo, board=board, checker=CheckerArray(), players=game_data.players, current_move_player=game_data.current_move_player
        )
        await game.start()
        return game

    partner = await repo.check_players_in_wait_list(rows_count)
    new_player = Player(id=player_id, chip=None)
    if not partner:
        await repo.set_players_to_wait_list(new_player)
        return

    board = BoardArray(rows_count=rows_count)
    new_game = Game(
        repo=repo, board=board, checker=CheckerArray(), players=[partner, new_player]
    )
    await new_game.start()
    return new_game


async def main(
    *, player_id: int | None = None, rows_count: int | None = None, room_id: uuid.UUID | None = None
) -> Game:
    game = await create_game(player_id=player_id, rows_count=rows_count, room_id=room_id)
    return game
