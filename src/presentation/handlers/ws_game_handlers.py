from fastapi.websockets import WebSocket
from fastapi.routing import APIRouter
import uuid
from src.logic.consumers.connection_manager import connection_manager
from src.mappers.event_mappers import map_event_from_client
from src.mappers.response_mappers import map_response
from src.logic.game.main import create_game
from src.logic.events.events import ClientEventType
from src.presentation.entities.ws_game_entities import GameStartResponse, ResponseStatus, ClientResponse
from src.logic.exceptions import RoomNotFoundInRepoException, BadParamsException, AbstractException
from src.logic.auth.authentication import check_user
from src.logic.events.responses import StartGameResponseEvent, MoveCreatedResponseEvent

ws_game_router = APIRouter(prefix="/game_ws")


@ws_game_router.websocket("/{room_id}")
async def game_ws_handler(websocket: WebSocket, room_id: uuid.UUID):
    await websocket.accept()
    data = await websocket.receive_text()
    try:
        request_data = map_event_from_client(data)
    except BadParamsException as e:
        await websocket.send_bytes(
            map_response(GameStartResponse(status=ResponseStatus.ERROR, message=e.message, data=None))
        )
        return

    if not request_data.event_type == ClientEventType.START:
        await websocket.send_bytes(
            map_response(GameStartResponse(status=ResponseStatus.ERROR, message="Wrong event type", data=None))
        )
        return

    try:
        player_id = await check_user(request_data.token)
    except AbstractException as e:
        await websocket.send_bytes(
            map_response(GameStartResponse(status=ResponseStatus.ERROR, message=e.message, data=None))
        )
        return

    try:
        game = await create_game(room_id=room_id)
    except RoomNotFoundInRepoException as e:
        await websocket.send_bytes(
            map_response(GameStartResponse(status=ResponseStatus.ERROR, message=e.message, data=None))
        )
        return

    await connection_manager.connect(websocket=websocket, player_id=player_id, room_id=room_id)
    await websocket.send_bytes(
        map_response(
            GameStartResponse(
                status=ResponseStatus.CONNECTED,
                message=None,
                data=StartGameResponseEvent(board=game.board.board, current_move_player_id=game.current_move_player.id),
            )
        )
    )
    # await connection_manager.send_event_to_all_players()

    try:
        while True:
            data = await websocket.receive_text()
            event_data = map_event_from_client(data)
            if event_data.event_type != ClientEventType.MOVE:
                await websocket.send_bytes(
                    map_response(GameStartResponse(status=ResponseStatus.ERROR, message="Wrong event type", data=None))
                )
                continue

            try:
                move_result = await game.make_move(col=event_data.col, row=event_data.row)
            except Exception as e:
                await websocket.send_bytes(
                    map_response(GameStartResponse(status=ResponseStatus.ERROR, message=e.message, data=None))
                )
                continue

            if move_result.is_winner is True:
                await websocket.send_bytes(
                    map_response(
                        ClientResponse(
                            status=ResponseStatus.FINISHED,
                            message=None,
                            data=MoveCreatedResponseEvent(
                                board=game.board.board,
                                current_move_player_id=None,
                                winner=move_result.chip.value,  # TODO return user id
                            ),
                        )
                    )
                )
                return

            await websocket.send_bytes(
                map_response(
                    ClientResponse(
                        status=ResponseStatus.SUCCESS,
                        message=None,
                        data=MoveCreatedResponseEvent(
                            board=game.board.board,
                            current_move_player_id=game.current_move_player.id,
                            winner=None,
                        ),
                    )
                )
            )

    except Exception as e:
        print(e)
    finally:
        await connection_manager.disconnect(room_id=room_id, player_id=player_id)
