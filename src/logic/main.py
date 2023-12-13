from .game import Game
from .checker import CheckerArray
from .board import BoardArray
from .player import Player
from .repository import repo

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


async def create_game(player_id: int, rows_count: int) -> Game | None:
    # Добавить проверку, нет ли такой игры в базе
    partner = await repo.check_players_in_wait_list(rows_count)
    new_player = Player(id=player_id, chip=None)
    if not partner:
        await repo.set_players_to_wait_list(new_player)
        return

    board = BoardArray(rows_count)
    new_game = Game(
        repo=repo, board=board, checker=CheckerArray(), players=[partner, new_player]
    )
    await new_game.start()
    return new_game
