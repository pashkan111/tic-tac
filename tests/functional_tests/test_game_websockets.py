import pytest
import uuid
import orjson
import asyncio


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
            "type": "RESPONSE",
        }


@pytest.mark.asyncio
async def test_game_ws_handler__bad_token(websocket_client):
    room_id = uuid.uuid4()
    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket:
        await websocket.send_text(orjson.dumps({"event_type": "START", "data": {"token": "token"}}))
        response = await websocket.receive_json()
        assert response == {
            "message": "Invalid Token. Token: token",
            "status": "ERROR",
            "data": None,
            "type": "RESPONSE",
        }


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
        await websocket.send_text(orjson.dumps({"event_type": "START", "data": {"token": player_1.token}}))
        response = await websocket.receive_json()
        assert response == {
            "status": "CONNECTED",
            "message": None,
            "data": {"board": board, "current_move_player_id": 3},
            "type": "RESPONSE",
        }
        assert await redis.get_set_values(name=f"players_by_rooms:{str(room_id)}") == {
            str(player_1.id),
            str(first_player_id),
        }

    # Once clients disconnects from the server, player id is removed from redis
    assert await redis.get_set_values(name=f"players_by_rooms:{str(room_id)}") == {str(first_player_id)}


@pytest.mark.asyncio
async def test_game_ws_handler__make_moves__error(pg, websocket_client, player_1, player_2, redis):
    room_id = uuid.uuid4()
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    await redis.set(
        key=str(room_id),
        value=orjson.dumps(
            {
                "room_id": str(room_id),
                "players": [{"id": player_1.id, "chip": 1}, {"id": player_2.id, "chip": 2}],
                "current_move_player": {"id": player_1.id, "chip": 1},
                "board": board,
            }
        ),
    )
    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket:
        await websocket.send_text(orjson.dumps({"event_type": "START", "data": {"token": player_1.token}}))
        _ = await websocket.receive_json()
        await websocket.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 0, "col": 1}}))
        move_response = await websocket.receive_json()
        assert move_response == {
            "status": "ERROR",
            "message": "Error making move. Row=0, col=1",
            "data": None,
            "type": "RESPONSE",
        }

        await websocket.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 1, "col": 1}}))

        move_response = await websocket.receive_json()
        assert move_response == {
            "status": "SUCCESS",
            "message": None,
            "data": {
                "board": [
                    [player_1.id, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                ],
                "current_move_player_id": player_2.id,
                "winner": None,
            },
            "type": "RESPONSE",
        }


@pytest.mark.asyncio
# @pytest.mark.skip()
async def test_game_ws_handler__make_moves(pg, websocket_client, websocket_client2, player_1, player_2, redis):
    room_id = uuid.uuid4()
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
                "players": [{"id": player_1.id, "chip": 1}, {"id": player_2.id, "chip": 2}],
                "current_move_player": {"id": player_1.id, "chip": 1},
                "board": board,
            }
        ),
    )

    await redis.add_to_set(
        name=f"players_by_rooms:{str(room_id)}",
        values=[player_1.id, player_2.id],
    )

    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket1:
        async with websocket_client2.websocket_connect(f"/game_ws/{str(room_id)}") as websocket2:
            # Подключение игрока 1
            await websocket1.send_text(orjson.dumps({"event_type": "START", "data": {"token": player_1.token}}))
            _ = await websocket1.receive_json()

            # Подключение игрока 2
            await websocket2.send_text(orjson.dumps({"event_type": "START", "data": {"token": player_2.token}}))
            _ = await websocket2.receive_json()

            # Уведомление игрока 1 о подключении игрока 2
            message_for_player1_about_connection_player2 = await websocket1.receive_json()
            assert message_for_player1_about_connection_player2 == {
                "data": {"player": {"id": 2, "chip": 2}},
                "message_status": "CONNECTED",
                "type": "MESSAGE",
            }

            # Игрок 1 делает ход
            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 1, "col": 1}}))
            move_response = await websocket1.receive_json()
            assert move_response == {
                "status": "SUCCESS",
                "message": None,
                "data": {
                    "board": [
                        [player_1.id, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0],
                    ],
                    "current_move_player_id": player_2.id,
                    "winner": None,
                },
                "type": "RESPONSE",
            }

            # Уведомление игрока 2 о ходе игрока 1
            message_for_player2_about_move_player1 = await websocket2.receive_json()
            assert message_for_player2_about_move_player1 == {
                "data": {
                    "player": {"id": 1, "chip": 1},
                    "board": [[player_1.id, 0, 0], [0, 0, 0], [0, 0, 0]],
                    "current_move_player_id": 2,
                    "winner": None,
                },
                "message_status": "MOVE",
                "type": "MESSAGE",
            }

            # Игрок 1 снова делает ход и ожидаемо получает ошибку
            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 1, "col": 2}}))
            move_response = await websocket1.receive_json()
            assert move_response == {
                "status": "ERROR",
                "message": "Others players turn to move. Player id: 2",
                "data": None,
                "type": "RESPONSE",
            }

            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 2, "col": 1}}))
            move_response = await websocket1.receive_json()
            assert move_response == {
                "status": "ERROR",
                "message": "Others players turn to move. Player id: 2",
                "data": None,
                "type": "RESPONSE",
            }

            # Игрок 2 делает ход
            await websocket2.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 2, "col": 2}}))
            move2_response = await websocket2.receive_json()
            assert move2_response == {
                "status": "SUCCESS",
                "message": None,
                "data": {
                    "board": [
                        [player_1.id, 0, 0],
                        [0, player_2.id, 0],
                        [0, 0, 0],
                    ],
                    "current_move_player_id": player_1.id,
                    "winner": None,
                },
                "type": "RESPONSE",
            }

            message_for_player1_about_move_player2 = await websocket1.receive_json()
            assert message_for_player1_about_move_player2 == {
                "data": {
                    "player": {"id": 2, "chip": 2},
                    "board": [[player_1.id, 0, 0], [0, player_2.id, 0], [0, 0, 0]],
                    "current_move_player_id": 1,
                    "winner": None,
                },
                "message_status": "MOVE",
                "type": "MESSAGE",
            }

            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 2, "col": 1}}))
            _ = await websocket1.receive_json()
            _ = await websocket2.receive_json()

            await websocket2.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 3, "col": 3}}))
            move_response = await websocket2.receive_json()
            assert move_response["data"]["board"] == [
                [player_1.id, 0, 0],
                [player_1.id, player_2.id, 0],
                [0, 0, player_2.id],
            ]
            _ = await websocket1.receive_json()

            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 3, "col": 1}}))
            move_response = await websocket1.receive_json()
            assert move_response == {
                "status": "FINISHED",
                "message": None,
                "data": {
                    "board": [
                        [player_1.id, 0, 0],
                        [player_1.id, player_2.id, 0],
                        [player_1.id, 0, player_2.id],
                    ],
                    "current_move_player_id": None,
                    "winner": player_1.id,
                },
                "type": "RESPONSE",
            }

            message_for_player2_about_move_player1 = await websocket2.receive_json()
            assert message_for_player2_about_move_player1 == {
                "data": {
                    "player": {"id": 1, "chip": 1},
                    "board": [
                        [player_1.id, 0, 0],
                        [player_1.id, player_2.id, 0],
                        [player_1.id, 0, player_2.id],
                    ],
                    "current_move_player_id": None,
                    "winner": player_1.id,
                },
                "message_status": "FINISH",
                "type": "MESSAGE",
            }

            await asyncio.sleep(0.5)
            assert await redis.get_set_values(name=f"players_by_rooms:{str(room_id)}") == {str(player_2.id)}

    disconnect_message = await websocket2.receive_json()
    assert disconnect_message == {
        "data": {"player": {"id": 1, "chip": 1}},
        "message_status": "DISCONNECTED",
        "type": "MESSAGE",
    }
