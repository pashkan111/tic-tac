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
        }


@pytest.mark.asyncio
async def test_game_ws_handler__connected(pg, websocket_client, player_1, redis):
    room_id = uuid.uuid4()
    await redis.set(
        key=str(room_id),
        value=orjson.dumps(
            {
                "room_id": str(room_id),
                "players": [{"id": 3, "chip": 1}, {"id": player_1.id, "chip": 2}],
                "current_move_player": {"id": 3, "chip": 1},
                "board": [
                    [0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0],
                ],
            }
        ),
    )
    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket:
        await websocket.send_text(orjson.dumps({"event_type": "START", "token": player_1.token}))
        response = await websocket.receive_json()
        assert response == {"status": "CONNECTED", "message": None}
