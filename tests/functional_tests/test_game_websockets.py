import asyncio
import uuid

import orjson
import pytest


@pytest.mark.asyncio
async def test_game_ws_handler__bad_message(websocket_client):
    room_id = uuid.uuid4()
    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket:
        await websocket.send_text('{"message": "Hello, WebSocket!"}')
        response = await websocket.receive_json()
        assert response == {
            "response_status": "ERROR",
            "event_type": "START",
            "message": 'Bad Params. Current params: ["message"]. Needed params: ["event_type"]',
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
            "event_type": "START",
            "response_status": "ERROR",
            "data": None,
            "type": "RESPONSE",
        }


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
        key=f"game:{str(room_id)}",
        value=orjson.dumps(
            {
                "room_id": str(room_id),
                "players": [{"id": player_1.id, "chip": 1}, {"id": player_2.id, "chip": 2}],
                "current_move_player": {"id": player_1.id, "chip": 1},
                "board": board,
                "game_status": "IN_PROGRESS",
            }
        ),
    )
    async with websocket_client.websocket_connect(f"/game_ws/{str(room_id)}") as websocket:
        await websocket.send_text(orjson.dumps({"event_type": "START", "data": {"token": player_1.token}}))
        await websocket.receive_json()
        await websocket.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 0, "col": 1}}))

        move_response = await websocket.receive_json()
        assert move_response == {
            "response_status": "ERROR",
            "message": "Error making move. Row=0, col=1",
            "data": None,
            "type": "RESPONSE",
            "event_type": "MOVE",
        }

        await websocket.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 1, "col": 1}}))
        move_response = await websocket.receive_json()
        assert move_response == {
            "response_status": "SUCCESS",
            "message": None,
            "data": {
                "player": {"id": 1, "chip": 1},
                "board": [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "current_move_player": {"id": 2, "chip": 2},
                "winner": None,
            },
            "type": "RESPONSE",
            "event_type": "MOVE",
        }


@pytest.mark.asyncio
async def test_game_ws_handler__make_moves(pg, websocket_client, websocket_client2, player_1, player_2, redis):
    room_id = uuid.uuid4()
    board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    await redis.set(
        key=f"game:{str(room_id)}",
        value=orjson.dumps(
            {
                "room_id": str(room_id),
                "players": [{"id": player_1.id, "chip": 1}, {"id": player_2.id, "chip": 2}],
                "current_move_player": {"id": player_1.id, "chip": 1},
                "board": board,
                "game_status": "IN_PROGRESS",
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
            await websocket1.receive_json()

            # Подключение игрока 2
            await websocket2.send_text(orjson.dumps({"event_type": "START", "data": {"token": player_2.token}}))
            await websocket2.receive_json()

            # Уведомление игрока 1 о подключении игрока 2
            message_for_player1_about_connection_player2 = await websocket1.receive_json()
            assert message_for_player1_about_connection_player2 == {
                "data": {"player": {"id": 2, "chip": 2}},
                "notification_type": "CONNECTED",
                "type": "NOTIFICATION",
            }
            # Уведомление игрока 2 о подключении игрока 1
            await websocket2.receive_json()

            # Игрок 1 делает ход
            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 1, "col": 1}}))
            move_response = await websocket1.receive_json()
            assert move_response == {
                "response_status": "SUCCESS",
                "message": None,
                "data": {
                    "player": {"id": 1, "chip": 1},
                    "board": [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
                    "current_move_player": {"id": 2, "chip": 2},
                    "winner": None,
                },
                "type": "RESPONSE",
                "event_type": "MOVE",
            }

            # Уведомление игрока 2 о ходе игрока 1
            message_for_player2_about_move_player1 = await websocket2.receive_json()
            assert message_for_player2_about_move_player1 == {
                "data": {
                    "board": [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
                    "current_move_player": {"id": 2, "chip": 2},
                    "winner": None,
                },
                "notification_type": "MOVE",
                "type": "NOTIFICATION",
            }

            # Игрок 1 снова делает ход и ожидаемо получает ошибку
            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 1, "col": 2}}))
            move_response = await websocket1.receive_json()
            assert move_response == {
                "response_status": "ERROR",
                "message": "Others players turn to move. Player id: 2",
                "data": None,
                "type": "RESPONSE",
                "event_type": "MOVE",
            }

            # Игрок 2 делает ход
            await websocket2.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 2, "col": 2}}))
            move2_response = await websocket2.receive_json()
            assert move2_response == {
                "response_status": "SUCCESS",
                "message": None,
                "data": {
                    "player": {"id": 2, "chip": 2},
                    "board": [[1, 0, 0], [0, 2, 0], [0, 0, 0]],
                    "current_move_player": {"id": 1, "chip": 1},
                    "winner": None,
                },
                "type": "RESPONSE",
                "event_type": "MOVE",
            }

            message_for_player1_about_move_player2 = await websocket1.receive_json()
            assert message_for_player1_about_move_player2 == {
                "data": {
                    "board": [[1, 0, 0], [0, 2, 0], [0, 0, 0]],
                    "current_move_player": {"id": 1, "chip": 1},
                    "winner": None,
                },
                "notification_type": "MOVE",
                "type": "NOTIFICATION",
            }

            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 2, "col": 1}}))
            await websocket1.receive_json()
            await websocket2.receive_json()

            await websocket2.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 3, "col": 3}}))
            move_response = await websocket2.receive_json()
            assert move_response["data"]["board"] == [
                [player_1.id, 0, 0],
                [player_1.id, player_2.id, 0],
                [0, 0, player_2.id],
            ]
            await websocket1.receive_json()

            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 3, "col": 1}}))
            move_response = await websocket1.receive_json()
            assert move_response == {
                "response_status": "SUCCESS",
                "message": None,
                "data": {
                    "player": {"id": 1, "chip": 1},
                    "board": [[1, 0, 0], [1, 2, 0], [1, 0, 2]],
                    "current_move_player": None,
                    "winner": {"chip": 1, "id": 1},
                },
                "type": "RESPONSE",
                "event_type": "MOVE",
            }

            message_for_player2_about_move_player1 = await websocket2.receive_json()
            assert message_for_player2_about_move_player1 == {
                "data": {
                    "board": [[1, 0, 0], [1, 2, 0], [1, 0, 2]],
                    "current_move_player": None,
                    "winner": {"id": 1, "chip": 1},
                },
                "notification_type": "FINISHED",
                "type": "NOTIFICATION",
            }

            await asyncio.sleep(0.5)
            assert await redis.get_set_values(name=f"players_by_rooms:{str(room_id)}") == {str(player_2.id)}

    disconnect_message = await websocket2.receive_json()
    assert disconnect_message == {
        "data": {"player": {"id": 1, "chip": 1}},
        "notification_type": "DISCONNECTED",
        "type": "NOTIFICATION",
    }


@pytest.mark.asyncio
async def test_game_ws_handler__surrender(pg, websocket_client, websocket_client2, player_1, player_2, redis):
    room_id = uuid.uuid4()
    board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    await redis.set(
        key=f"game:{str(room_id)}",
        value=orjson.dumps(
            {
                "room_id": str(room_id),
                "players": [{"id": player_1.id, "chip": 1}, {"id": player_2.id, "chip": 2}],
                "current_move_player": {"id": player_1.id, "chip": 1},
                "board": board,
                "game_status": "IN_PROGRESS",
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
            await websocket1.receive_json()

            # Подключение игрока 2
            await websocket2.send_text(orjson.dumps({"event_type": "START", "data": {"token": player_2.token}}))
            await websocket2.receive_json()

            # Уведомление игрока 1 о подключении игрока 2
            await websocket1.receive_json()

            # Уведомление игрока 2 о подключении игрока 1
            await websocket2.receive_json()

            # Игрок 1 делает ход
            await websocket1.send_text(orjson.dumps({"event_type": "MOVE", "data": {"row": 1, "col": 1}}))
            await websocket1.receive_json()

            # Уведомление игрока 2 о том что 1 сделал ход
            await websocket2.receive_json()
            # Игрок 2 сдается
            await websocket2.send_text(orjson.dumps({"event_type": "SURRENDER"}))
            assert await websocket2.receive_json() == {
                "response_status": "SUCCESS",
                "message": None,
                "data": {"player": {"id": 2, "chip": 2}, "winner": {"id": 1, "chip": 1}},
                "type": "RESPONSE",
                "event_type": "SURRENDER",
            }

            # Уведомление игрока 1 о сдаче игрока 2
            assert await websocket1.receive_json() == {
                "data": {"winner": {"id": 1, "chip": 1}},
                "notification_type": "SURRENDER",
                "type": "NOTIFICATION",
            }

            # disconnect_message = await websocket1.receive_json()
            # assert disconnect_message == {
            #     "data": {"player": {"id": 2, "chip": 2}},
            #     "notification_type": "DISCONNECTED",
            #     "type": "NOTIFICATION",
            # }

        game_data = await redis.get(f"game:{str(room_id)}")
        assert orjson.loads(game_data)["winner"]["id"] == player_1.id
