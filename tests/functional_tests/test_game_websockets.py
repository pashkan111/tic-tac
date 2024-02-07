import pytest
import uuid
import orjson


@pytest.mark.asyncio
async def test_game_ws_handler__bad_message(websocket_client, pg):
    room_id = uuid.uuid4()
    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket:
        await websocket.send_text('{"message": "Hello, WebSocket!"}')
        response = await websocket.receive_json()
        assert response == {
            "status": "ERROR",
            "message": "Bad Params. Params: message=Hello, WebSocket!;",
            "data": None,
        }


@pytest.mark.asyncio
async def test_game_ws_handler__bad_token(websocket_client):
    room_id = uuid.uuid4()
    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket:
        await websocket.send_text(orjson.dumps({"event_type": "START", "token": "token"}))
        response = await websocket.receive_json()
        assert response == {"message": "Invalid Token. Token: token", "status": "ERROR", "data": None}


@pytest.mark.asyncio
async def test_game_ws_handler__connected(pg, websocket_client, player_1, redis):
    room_id = uuid.uuid4()
    first_player_id = 6
    board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    await redis.set(
        key=str(room_id),
        value=orjson.dumps(
            {
                "room_id": str(room_id),
                "players": [{"id": first_player_id, "chip": 1}, {"id": player_1.id, "chip": 2}],
                "current_move_player": {"id": 3, "chip": 1},
                "board": board,
            }
        ),
    )
    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket:
        await websocket.send_text(orjson.dumps({"event_type": "START", "token": player_1.token}))
        response = await websocket.receive_json()
        assert response == {
            "status": "CONNECTED",
            "message": None,
            "data": {"board": board, "current_move_player_id": 3},
        }
        assert await redis.get_set_values(name=f"players_by_rooms:{str(room_id)}") == {
            str(player_1.id),
            str(first_player_id),
        }

    # Once clients disconnects from the server, player id is removed from redis
    assert await redis.get_set_values(name=f"players_by_rooms:{str(room_id)}") == {str(first_player_id)}
