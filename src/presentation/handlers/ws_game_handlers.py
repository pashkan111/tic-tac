import asyncio
import logging
import uuid

from fastapi.routing import APIRouter
from fastapi.websockets import WebSocket

from src.logic.entities.events import BaseEvent
from src.logic.entities.messages import (
    BaseMessage,
    PlayerConnected,
    PlayerConnectedMessage,
    PlayerDisconnected,
    PlayerDisconnectedMessage,
)
from src.logic.entities.responses import ErrorResponse, GameStart, GameStartResponse, MoveCreatedResponse
from src.logic.enums.response_status import ResponseStatus
from src.logic.exceptions import BadEventParamsException
from src.mappers.event_mappers import map_event_from_client
from src.services.connection_manager import connect, disconnect
from src.services.messages_handlers import run_message_handler
from src.services.pubsub import get_channel_name, publish_message, read_messages
from src.services.state_machine import (
    BaseMachineRequest,
    GameState,
    GameStateMachine,
    MachineActionStatus,
    StartGameStateData,
    get_game_state,
)
from src.services.ws_handlers import handle_move_state, handle_surrender_state

logger = logging.getLogger(__name__)
ws_game_router = APIRouter(prefix="/game_ws")


@ws_game_router.websocket("/{room_id}")
async def game_ws_handler(websocket: WebSocket, room_id: uuid.UUID):
    await websocket.accept()
    data = await websocket.receive_text()
    request_event = await _process_event(event_raw=data, websocket=websocket)
    if not request_event:
        return

    channel_name = get_channel_name(room_id)

    state_machine = GameStateMachine()
    state_machine.change_state(GameState.START_STATE)

    handled_event_response = await state_machine.handle_event(BaseMachineRequest(room_id=room_id, event=request_event))
    if handled_event_response.status == MachineActionStatus.FAILED:
        await websocket.send_bytes(
            ErrorResponse(
                response_status=ResponseStatus.ERROR,
                message=handled_event_response.message,
                data=None,
            ).to_json()
        )
        await websocket.close()
        return

    state_data: StartGameStateData = handled_event_response.data
    game = state_data.game
    player = state_data.player
    player_id = player.id

    # Отправляем событие в канал, чтобы остальные игроки,
    # подключенные к этому каналу, получили уведомление
    await asyncio.gather(
        publish_message(
            channel=channel_name,
            message=PlayerConnectedMessage(
                data=PlayerConnected(player=player),
                player_sent=player,
            ),
        ),
        connect(player_id=player_id, room_id=room_id),
        websocket.send_bytes(
            GameStartResponse(
                response_status=ResponseStatus.SUCCESS,
                message=None,
                data=GameStart(
                    board=game.board.board,
                    current_move_player=game.current_move_player,
                    player=player,
                ),
            ).to_json()
        ),
    )

    state_machine.change_state(GameState.MOVE_STATE)

    try:
        queue = asyncio.Queue()

        asyncio.create_task(read_messages(channel=channel_name, queue=queue, player_id=player_id))
        asyncio.create_task(receive_ws_messages(websocket=websocket, queue=queue))

        while True:
            if queue.empty():
                await asyncio.sleep(0)
                continue

            message_or_event = await queue.get()
            print(f"\nMessage or Event. Data: {message_or_event}\n. Player: {player_id}\n")

            if isinstance(message_or_event, BaseEvent):
                request_event = message_or_event
                game_state = get_game_state(request_event.event_type)
                can_change_state = state_machine.can_change_state(game_state)
                if can_change_state is False:
                    await websocket.send_bytes(
                        ErrorResponse(
                            response_status=ResponseStatus.ERROR,
                            message=f"Incorrect event type. Event type - {request_event.event_type}",
                            data=None,
                        ).to_json()
                    )
                    continue

                state_machine.change_state(game_state)

                handled_event_response = await state_machine.handle_event(
                    BaseMachineRequest(room_id=room_id, event=request_event, player_id=player_id, game=game)
                )
                if handled_event_response.status == MachineActionStatus.FAILED:
                    await websocket.send_bytes(
                        ErrorResponse(
                            event_type=request_event.event_type,
                            response_status=ResponseStatus.ERROR,
                            message=handled_event_response.message,
                            data=None,
                        ).to_json()
                    )
                    continue

                if game_state == GameState.MOVE_STATE:
                    move_result = handled_event_response.data.move_result
                    is_finished = await handle_move_state(
                        websocket=websocket,
                        move_result=move_result,
                        game=game,
                        state_machine=state_machine,
                        player=player,
                        channel_name=channel_name,
                    )
                    if is_finished:
                        return

                if game_state == GameState.SURRENDER_STATE:
                    await handle_surrender_state(
                        websocket=websocket, game=game, channel_name=channel_name, player=player
                    )
                    return

            elif isinstance(message_or_event, BaseMessage):
                message = message_or_event
                if message.player_sent.id == player_id:
                    continue

                await run_message_handler(message=message, websocket=websocket, player_id=player_id)
                continue

    except Exception as e:
        logger.error(f"Exception. Type: {type(e)}. Message: {str(e)}")
        raise

    finally:
        await asyncio.gather(
            disconnect(room_id=room_id, player_id=player_id),
            websocket.close(),
            publish_message(
                channel=channel_name,
                message=PlayerDisconnectedMessage(data=PlayerDisconnected(player=player), player_sent=player),
            ),
        )
        # TODO remove old channel


async def _process_event(*, event_raw: str, websocket: WebSocket) -> BaseEvent | None:
    try:
        request_event = map_event_from_client(event_raw)
        return request_event
    except BadEventParamsException as e:
        logger.error(e.message)
        await websocket.send_bytes(
            ErrorResponse(
                response_status=ResponseStatus.ERROR,
                message=e.message,
                data=None,
            ).to_json()
        )


async def receive_ws_messages(*, websocket: WebSocket, queue: asyncio.Queue) -> BaseEvent | None:
    while True:
        try:
            data = await websocket.receive_text()
            event = await _process_event(event_raw=data, websocket=websocket)
            await queue.put(event)
        except Exception as e:
            logger.error(e)
            break
