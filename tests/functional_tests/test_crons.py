import pytest
import orjson
import asyncio
import datetime


@pytest.mark.asyncio
async def test_archive_finished_games_cron(pg, redis, player_1, player_2):
    from cli import archive_finished_games_cron
    from src.mappers.dt import encode_datetime

    await redis.set(
        key="game:1",
        value=orjson.dumps(
            {
                "room_id": "1",
                "players": [{"id": player_1.id, "chip": 1}, {"id": player_2.id, "chip": 2}],
                "current_move_player": None,
                "board": [
                    [0, 0, 1],
                    [1, 0, 0],
                    [0, 1, 0],
                ],
                "is_active": False,
                "winner": {"id": player_2.id, "chip": 2},
                "last_updated": encode_datetime(datetime.datetime(2022, 12, 12, 6, 10, 22)),
            }
        ),
    )

    await redis.set(
        key="game:2",
        value=orjson.dumps(
            {
                "room_id": "2",
                "players": [{"id": player_1.id, "chip": 1}, {"id": player_2.id, "chip": 2}],
                "current_move_player": None,
                "board": [
                    [1, 0, 0],
                    [1, 0, 0],
                    [1, 1, 0],
                ],
                "is_active": False,
                "winner": {"id": player_1.id, "chip": 1},
                "last_updated": encode_datetime(datetime.datetime(2022, 12, 12, 6, 10, 22)),
            }
        ),
    )
    await archive_finished_games_cron()
    await asyncio.sleep(1)

    pg_data = [dict(row) for row in await pg.fetch(query="SELECT * FROM game;")]
    assert {
        "player1_id": 1,
        "player2_id": 2,
        "winner": 1,
        "game_finished": datetime.datetime(2022, 12, 12, 3, 10, 22, tzinfo=datetime.timezone.utc),
        "board": "[[1,0,0],[1,0,0],[1,1,0]]",
    } in pg_data

    assert {
        "player1_id": 1,
        "player2_id": 2,
        "winner": 2,
        "game_finished": datetime.datetime(2022, 12, 12, 3, 10, 22, tzinfo=datetime.timezone.utc),
        "board": "[[0,0,1],[1,0,0],[0,1,0]]",
    } in pg_data

    assert await redis.keys("game:*") == []
