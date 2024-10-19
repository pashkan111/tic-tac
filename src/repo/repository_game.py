from dataclasses import asdict
from uuid import UUID

from orjson import dumps, loads
from python_tools.redis_tools.redis_client import RedisConnection
import redis.asyncio as redis
import settings
from src.logic.game.player import Player
from src.logic.game.schemas import GameRedisSchema
from src.mappers.game_mapper import map_game_data_from_redis


class RepositoryGame:
    # redis_client: RedisClient
    conn: RedisConnection

    def __init__(self, conn: RedisConnection):
        self.conn = conn

    async def set_game(self, game: GameRedisSchema):
        await self.conn.set(
            key=f"{settings.REDIS_GAME_KEY}:{str(game.room_id)}",
            value=dumps(asdict(game)).decode(),
        )

    async def remove_game(self, room_ids: list[UUID]):
        keys = [f"{settings.REDIS_GAME_KEY}:{str(room_id)}" for room_id in room_ids]
        await self.conn.delete(keys)

    async def get_game(self, room_id: UUID) -> GameRedisSchema | None:
        data = await self.conn.get(f"{settings.REDIS_GAME_KEY}:{str(room_id)}")
        if not data:
            return None
        return map_game_data_from_redis(loads(data))

    async def check_players_in_wait_list(self, rows_count: int) -> Player | None:
        player_id = await self.conn.hget(name=settings.REDIS_PLAYERS_WAITING_LIST_NAME_KEY, key=str(rows_count))
        if not player_id:
            return None
        return Player(id=int(player_id))

    async def set_players_to_wait_list(self, *, player: Player, rows_count: int):
        await self.conn.hset(
            name=settings.REDIS_PLAYERS_WAITING_LIST_NAME_KEY,
            key=str(rows_count),
            value=str(player.id),
        )

    async def remove_players_from_wait_list(self, rows_count: int) -> bool:
        is_deleted = await self.conn.hdel(
            name=settings.REDIS_PLAYERS_WAITING_LIST_NAME_KEY,
            keys=[str(rows_count)],
        )
        return bool(is_deleted)

    async def add_players_to_room(self, *, player_ids: list[int], room_id: UUID) -> None:
        await self.conn.add_to_set(
            name=f"{settings.REDIS_PLAYERS_BY_ROOMS_KEY}:{str(room_id)}",
            values=list(map(str, player_ids)),
        )

    async def get_players_from_room(self, room_id: UUID) -> list[int]:
        """Хранит игроков, привязанных к определенной комнате"""
        player_ids = await self.conn.get_set_values(
            name=f"{settings.REDIS_PLAYERS_BY_ROOMS_KEY}:{str(room_id)}",
        )
        return [int(player_id) for player_id in player_ids]

    async def remove_player_from_room(self, *, player_id: int, room_id: UUID) -> None:
        await self.conn.remove_from_set(
            name=f"{settings.REDIS_PLAYERS_BY_ROOMS_KEY}:{str(room_id)}",
            values=[str(player_id)],
        )

    async def set_game_players(self, *, player_id: int, room_id: UUID):
        await self.conn.hset(
            name=settings.REDIS_ACTIVE_PLAYERS_KEY,
            key=str(player_id),
            value=str(room_id),
        )

    async def get_player_active_game(self, player_id: int) -> UUID | None:
        """Проверяет, есть ли у пользователя незаконченная игра"""
        room_id = await self.conn.hget(name=settings.REDIS_ACTIVE_PLAYERS_KEY, key=str(player_id))
        return room_id

    async def remove_player_active_game(self, player_id: int):
        await self.conn.hdel(
            name=settings.REDIS_ACTIVE_PLAYERS_KEY,
            keys=[str(player_id)],
        )


pool = redis.ConnectionPool.from_url(
    settings.REDIS_CONNECTION_STRING,
    max_connections=10,
    encoding="utf-8",
    decode_responses=True,
)
client = redis.Redis.from_pool(pool)
conn = RedisConnection(client)
repo = RepositoryGame(conn)
