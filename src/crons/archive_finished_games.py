import asyncio

import orjson

from src.mappers.game_mapper import map_game_data_from_redis
from src.repo.repository_game import conn
from src.repo.repository_game_pg import game_repo


async def archive_finished_games():
    """Removes ald and finished games from redis"""
    keys = await conn.keys("game:*")

    upsert_tasks: list[asyncio.Task] = []
    count = 0

    if not keys:
        return

    for key in keys:
        game_data_raw = await conn.get(key)
        game_data = map_game_data_from_redis(orjson.loads(game_data_raw))
        if game_data.game_status.is_finished:
            await conn.delete(key)

        if count == 5:
            await asyncio.gather(*upsert_tasks)
            count = 0
            upsert_tasks = []
        else:
            upsert_tasks.append(asyncio.create_task(game_repo.upsert(game_data)))
