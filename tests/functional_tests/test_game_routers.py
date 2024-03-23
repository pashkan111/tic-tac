import pytest
import orjson
import uuid


@pytest.mark.asyncio
async def test_get_chips(pg, test_client):
    response = await test_client.get("/game/chips")
    response = response.json()

    assert response == {
        "chips": [
            {"id": 1, "chip": "X"},
            {"id": 2, "chip": "O"},
        ]
    }


@pytest.mark.asyncio
async def test_create_game_handler__wrong_token(pg, test_client, redis):
    await redis.hset(name="players_waiting_list", key="5", value="3")

    response = await test_client.post("/game/create", json={"rows_count": "5", "token": "token"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_game_handler__partner_in_waiting_list(pg, test_client, redis, player_1, mocker):
    await redis.hset(name="players_waiting_list", key="5", value="3")

    response = await test_client.post("/game/create", json={"rows_count": "5", "token": player_1.token})

    response = response.json()
    assert response["game_started"] is True
    assert response["partner_id"] == 3
    assert orjson.loads(await redis.get(key=response["room_id"])) == {
        "room_id": response["room_id"],
        "players": [{"id": 3, "chip": 1}, {"id": player_1.id, "chip": 2}],
        "current_move_player": {"id": 3, "chip": 1},
        "board": [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ],
        "created": mocker.ANY,
        "is_active": True,
    }

    assert await redis.get_set_values(f'players_by_rooms:{response["room_id"]}') == {
        str(player_1.id),
        "3",
    }
    assert await redis.hget(name="players_waiting_list", key="5") is None


@pytest.mark.asyncio
async def test_create_game_handler__partner_not_in_waiting_list(pg, test_client, redis, player_1):
    response = await test_client.post("/game/create", json={"rows_count": "5", "token": player_1.token})
    response = response.json()

    assert await redis.hget(name="players_waiting_list", key="5") == "1"
    assert response["game_started"] is False
    assert response["added_to_queue"] is True


@pytest.mark.asyncio
async def test_create_game_handler__thereis_a_game_with_such_player(pg, test_client, redis, player_1):
    room_id = uuid.uuid4()

    await redis.hset(name="active_players", key=str(player_1.id), value=str(room_id))
    await redis.set(
        key=str(room_id),
        value=orjson.dumps(
            {
                "room_id": room_id,
                "players": [{"id": 3, "chip": 1}, {"id": player_1.id, "chip": 2}],
                "current_move_player": {"id": 3, "chip": 1},
                "board": [
                    [0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0],
                ],
                "is_active": False,
            }
        ),
    )

    response = await test_client.post("/game/create", json={"rows_count": "5", "token": player_1.token})

    response = response.json()
    assert response["game_started"] is True
    assert response["added_to_queue"] is False
    assert response["room_id"] == str(room_id)
