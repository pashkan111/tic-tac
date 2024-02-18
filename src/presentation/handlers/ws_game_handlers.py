from fastapi.websockets import WebSocket
from fastapi.routing import APIRouter
import uuid
import asyncio
from src.logic.consumers.connection_manager import connection_manager
from src.mappers.event_mappers import map_event_from_client
from src.mappers.response_mappers import map_response
from src.logic.game.main import create_game
from src.logic.events.events import ClientEventType
from src.presentation.entities.ws_game_entities import GameStartResponse, ResponseStatus, ClientResponse
from src.logic.exceptions import RoomNotFoundInRepoException, BadParamsException, AbstractException
from src.logic.auth.authentication import check_user
from src.logic.events.responses import StartGameResponseEvent, MoveCreatedResponseEvent
from src.logic.events.messages import (
    PlayerConnectedMessage,
    PlayerConnected,
    PlayerMove,
    PlayerMoveMessage,
    MessageStatus,
    PlayerDisconnected,
    PlayerDisconnectedMessage,
)


ws_game_router = APIRouter(prefix="/game_ws")


# TODO make state machine


@ws_game_router.websocket("/{room_id}")
async def game_ws_handler(websocket: WebSocket, room_id: uuid.UUID):
    await websocket.accept()
    data = await websocket.receive_text()
    try:
        request_event = map_event_from_client(data)
    except BadParamsException as e:
        await websocket.send_bytes(
            map_response(GameStartResponse(status=ResponseStatus.ERROR, message=e.message, data=None))
        )
        return

    if not request_event.event_type == ClientEventType.START:
        await websocket.send_bytes(
            map_response(GameStartResponse(status=ResponseStatus.ERROR, message="Wrong event type", data=None))
        )
        return

    try:
        player_id = await check_user(request_event.data.token)
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

    player = next(filter(lambda p: p.id == player_id, game.players))

    async with asyncio.TaskGroup() as tg:
        tg.create_task(
            websocket.send_bytes(
                map_response(
                    GameStartResponse(
                        status=ResponseStatus.CONNECTED,
                        message=None,
                        data=StartGameResponseEvent(
                            board=game.board.board, current_move_player=game.current_move_player
                        ),
                    )
                )
            )
        )
        tg.create_task(
            connection_manager.send_event_to_all_players(
                message=PlayerConnectedMessage(data=PlayerConnected(player=player)),
                player_id=player_id,
                room_id=room_id,
            )
        )

    try:
        while True:
            data = await websocket.receive_text()
            request_event = map_event_from_client(data)
            if request_event.event_type != ClientEventType.MOVE:
                await websocket.send_bytes(
                    map_response(GameStartResponse(status=ResponseStatus.ERROR, message="Wrong event type", data=None))
                )
                continue

            try:
                move_result = await game.make_move(
                    col=request_event.data.col, row=request_event.data.row, player_id=player_id
                )
            except Exception as e:
                await websocket.send_bytes(
                    map_response(GameStartResponse(status=ResponseStatus.ERROR, message=e.message, data=None))
                )
                continue

            if move_result.is_winner is True:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(
                        websocket.send_bytes(
                            map_response(
                                ClientResponse(
                                    status=ResponseStatus.FINISHED,
                                    message=None,
                                    data=MoveCreatedResponseEvent(
                                        board=game.board.board,
                                        current_move_player=None,
                                        winner=game._get_player_by_chip(move_result.chip),
                                    ),
                                )
                            )
                        )
                    )
                    tg.create_task(
                        connection_manager.send_event_to_all_players(
                            message=PlayerMoveMessage(
                                data=PlayerMove(
                                    player=player,
                                    board=game.board.board,
                                    winner=game._get_player_by_chip(move_result.chip),
                                    current_move_player=None,
                                ),
                                message_status=MessageStatus.FINISH,
                            ),
                            player_id=player_id,
                            room_id=room_id,
                        )
                    )
                return

            async with asyncio.TaskGroup() as tg:
                tg.create_task(
                    websocket.send_bytes(
                        map_response(
                            ClientResponse(
                                status=ResponseStatus.SUCCESS,
                                message=None,
                                data=MoveCreatedResponseEvent(
                                    board=game.board.board,
                                    current_move_player=game.current_move_player,
                                    winner=None,
                                ),
                            )
                        )
                    )
                )
                tg.create_task(
                    connection_manager.send_event_to_all_players(
                        message=PlayerMoveMessage(
                            data=PlayerMove(
                                player=player,
                                board=game.board.board,
                                winner=None,
                                current_move_player=game.current_move_player,
                            ),
                            message_status=MessageStatus.MOVE,
                        ),
                        player_id=player_id,
                        room_id=room_id,
                    )
                )

    except Exception as e:
        print(e)
    finally:
        await connection_manager.disconnect(room_id=room_id, player_id=player_id)
        await connection_manager.send_event_to_all_players(
            message=PlayerDisconnectedMessage(
                data=PlayerDisconnected(
                    player=player,
                )
            ),
            player_id=player_id,
            room_id=room_id,
        )
