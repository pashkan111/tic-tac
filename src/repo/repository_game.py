from src.logic.interfaces import RepositoryGameAbstract
from src.logic.player import Player
from src.logic.schemas import GameRedisSchema
from uuid import UUID
from python_tools.redis_tools.redis_client import RedisClient
from settings import REDIS_CONNECTION_STRING
from orjson import dumps, loads
from dataclasses import asdict
from src.mappers.game_mapper import map_game_data_from_redis


class RepositoryGame(RepositoryGameAbstract):
    redis_client: RedisClient

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def set_game(self, game: GameRedisSchema):
        await self.redis_client.get().set(
            key=str(game.room_id), value=dumps(asdict(game)).decode("utf-8")
        )

    async def remove_game(self, room_id: UUID):
        await self.redis_client.get().delete([str(room_id)])

    async def get_game(self, room_id: UUID) -> GameRedisSchema | None:
        data = await self.redis_client.get().get(str(room_id))
        if not data:
            return None
        return map_game_data_from_redis(loads(data))

    async def check_players_in_wait_list(self, rows_count: int) -> Player | None:
        ...

    async def set_players_to_wait_list(self, player: Player) -> Player:
        ...


redis_client = RedisClient(REDIS_CONNECTION_STRING)
repo = RepositoryGame(redis_client=redis_client)
