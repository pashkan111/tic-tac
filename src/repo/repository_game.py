from src.logic.interfaces import RepositoryGameAbstract
from src.logic.player import Player
from src.logic.board import BoardArray
from src.logic.schemas import GameRedisSchema
from uuid import UUID


class RepositoryGame(RepositoryGameAbstract):
    async def set_board(self, board: BoardArray):
        ...

    async def get_board(self) -> BoardArray:
        ...

    async def set_current_move(self, next_move: Player):
        ...

    async def set_game(self, game: GameRedisSchema):
        ...

    async def get_game(self, room_id: UUID) -> GameRedisSchema | None:
        ...

    async def check_players_in_wait_list(self, rows_count: int) -> Player | None:
        ...

    async def set_players_to_wait_list(self, player: Player) -> Player:
        ...


repo = RepositoryGame()
