from fastapi.websockets import WebSocket
from fastapi.routing import APIRouter
import uuid
import asyncio
from src.services.connection_manager import connection_manager
from src.mappers.event_mappers import map_event_from_client
from src.presentation.entities.ws_game_entities import GameStartResponse, ResponseStatus
from src.logic.exceptions import BadEventParamsException
from src.logic.events.responses import (
    StartGameResponseEvent,
    StartGameData,
)
from src.logic.events.messages import (
    PlayerConnectedMessage,
    PlayerConnected,
    PlayerDisconnected,
    PlayerDisconnectedMessage,
)
from src.services.state_machine import (
    GameStateMachine,
    MachineActionStatus,
    StartGameStateData,
    BaseMachineRequest,
    get_game_state,
    GameState,
)
from src.services.ws_handlers import handle_move_state, handle_surrender_state
import logging


logger = logging.getLogger(__name__)
ws_game_router = APIRouter(prefix="/game_ws")


@ws_game_router.websocket("/{room_id}")
async def game_ws_handler(websocket: WebSocket, room_id: uuid.UUID):
    await websocket.accept()
    data = await websocket.receive_text()
    try:
        request_event = map_event_from_client(data)
    except BadEventParamsException as e:
        await websocket.send_bytes(
            GameStartResponse(status=ResponseStatus.ERROR, message=e.message, data=None).to_json()
        )
        return

    state_machine = GameStateMachine()
    state_machine.change_state(GameState.START_STATE)

    handled_event_response = await state_machine.handle_event(BaseMachineRequest(room_id=room_id, event=request_event))
    if handled_event_response.status == MachineActionStatus.FAILED:
        await websocket.send_bytes(
            GameStartResponse(status=ResponseStatus.ERROR, message=handled_event_response.message, data=None).to_json()
        )
        await websocket.close()
        return

    state_data: StartGameStateData = handled_event_response.data
    game = state_data.game
    player_id = state_data.player_id

    await connection_manager.connect(
        websocket=websocket, player_id=handled_event_response.data.player_id, room_id=room_id
    )

    player = next(filter(lambda p: p.id == player_id, game.players))

    async with asyncio.TaskGroup() as tg:
        tg.create_task(
            websocket.send_bytes(
                GameStartResponse(
                    status=ResponseStatus.CONNECTED,
                    message=None,
                    data=StartGameResponseEvent(
                        StartGameData(board=game.board.board, current_move_player=game.current_move_player)
                    ),
                ).to_json()
            )
        )
        tg.create_task(
            connection_manager.send_event_to_all_players(
                message=PlayerConnectedMessage(data=PlayerConnected(player=player)),
                player_id=player_id,
                room_id=room_id,
            )
        )

    state_machine.change_state(GameState.MOVE_STATE)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                request_event = map_event_from_client(data)
            except BadEventParamsException as e:
                await websocket.send_bytes(
                    GameStartResponse(status=ResponseStatus.ERROR, message=e.message, data=None).to_json()
                )
                continue
            game_state = get_game_state(request_event.event_type)
            can_change_state = state_machine.can_change_state(game_state)
            if can_change_state is False:
                await websocket.send_bytes(
                    GameStartResponse(
                        status=ResponseStatus.ERROR,
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
                    GameStartResponse(
                        status=ResponseStatus.ERROR, message=handled_event_response.message, data=None
                    ).to_json()
                )
                continue

            if game_state == GameState.MOVE_STATE:
                move_result = handled_event_response.data.move_result
                is_finished = await handle_move_state(
                    websocket=websocket, move_result=move_result, game=game, state_machine=state_machine, player=player
                )
                if not is_finished:
                    continue
                return

            if game_state == GameState.SURRENDER_STATE:
                await handle_surrender_state(
                    websocket=websocket,
                    game=game,
                    player=player,
                    winner=handled_event_response.data.winner,
                )
                return

    except Exception as e:
        logger.error(f"Exception. Type: {type(e)}. Message: {str(e)}")
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
