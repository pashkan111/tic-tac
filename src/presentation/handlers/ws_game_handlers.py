from fastapi.websockets import WebSocket
from fastapi.routing import APIRouter
import uuid
from src.logic.consumers.connection_manager import connection_manager
from src.mappers.event_mappers import map_event_from_client
from src.logic.game.main import create_game
from src.logic.events import ClientEventType
from src.presentation.entities.ws_game_entities import GameStartResponse, Status
from src.logic.exceptions import RoomNotFoundInRepoException, BadParamsException


ws_game_router = APIRouter(prefix="/game_ws")


@ws_game_router.websocket("/{room_id}")
async def game_ws_handler(websocket: WebSocket, room_id: uuid.UUID):
    await websocket.accept()
    data = await websocket.receive_text()
    try:
        event_data = map_event_from_client(data)
    except BadParamsException as e:
        await websocket.send_text(
            GameStartResponse(status=Status.ERROR, message=e.message).model_dump_json()
        )
        return

    if not event_data.event_type == ClientEventType.START:
        await websocket.send_text(
            GameStartResponse(
                status=Status.ERROR, message="Wrong event type"
            ).model_dump_json()
        )
        return

    try:
        game = await create_game(room_id=room_id)
    except RoomNotFoundInRepoException as e:
        await websocket.send_text(
            GameStartResponse(status=Status.ERROR, message=e.message).model_dump_json()
        )
        return

    # await connection_manager.connect(
    #     websocket=websocket, player_id=event_data.player_id, room_id=room_id
    # )
    await websocket.send_text(
        GameStartResponse(status=Status.CONNECTED, message=None).model_dump_json()
    )

    try:
        while True:
            data = await websocket.receive_text()
            event_data = map_event_from_client(data)
            if event_data.event_type == ClientEventType.MOVE:
                await game.make_move(col=event_data.col, row=event_data.row)

    except Exception as e:
        print(e)
    finally:
        await connection_manager.disconnect(room_id=room_id, player_id=1)
