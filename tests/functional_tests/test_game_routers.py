import pytest


@pytest.mark.asyncio
async def test_create_game_handler__partner_in_waiting_list(
    pg, test_client, redis, player_1_token
):
    await redis.get().hset(name="players_waiting_list", key="5", value="3")

    response = await test_client.post(
        "/game/create", json={"rows_count": "5", "token": player_1_token}
    )

    response = response.json()
    assert response["game_started"] == True
    assert response["partner_id"] == 3


@pytest.mark.asyncio
async def test_create_game_handler__partner_not_in_waiting_list(
    pg, test_client, redis, player_1_token
):
    response = await test_client.post(
        "/game/create", json={"rows_count": "5", "token": player_1_token}
    )
    response = response.json()

    assert await redis.get().hget(name="players_waiting_list", key="5") == "1"
    assert response["game_started"] == False
