from fastapi.websockets import WebSocket
from fastapi.routing import APIRouter
import uuid
import asyncio
from src.logic.consumers.connection_manager import connection_manager
from src.mappers.event_mappers import map_event_from_client
from src.presentation.entities.ws_game_entities import GameStartResponse, ResponseStatus, ClientResponse
from src.logic.exceptions import BadParamsException
from src.logic.events.responses import (
    StartGameResponseEvent,
    MoveCreatedResponseEvent,
    SurrenderResponseEvent,
    SurrenderData,
    StartGameData,
    MoveCreatedData,
)
from src.logic.events.messages import (
    PlayerConnectedMessage,
    PlayerConnected,
    PlayerMove,
    PlayerMoveMessage,
    MessageStatus,
    PlayerDisconnected,
    PlayerDisconnectedMessage,
)
from src.logic.consumers.state_machine import (
    GameStateMachine,
    MachineActionStatus,
    StartGameStateData,
    BaseMachineRequest,
    get_game_state,
    GameState,
)
from typing import TypeAlias
from src.logic.game.game import Game
from src.logic.game.schemas import CheckResult
from src.logic.game.player import Player


IsFinishedState: TypeAlias = int

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

    # TODO add finish state
    state_machine.change_state(GameState.MOVE_STATE)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                request_event = map_event_from_client(data)
            except BadParamsException as e:
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
                # TODO winner defines in Game
                return

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


async def handle_surrender_state(*, websocket: WebSocket, game: Game, player: Player, winner: Player) -> None:
    await asyncio.gather(
        websocket.send_bytes(
            ClientResponse(
                status=ResponseStatus.SURRENDER,
                message=None,
                data=SurrenderResponseEvent(SurrenderData(winner=winner)),
            ).to_json()
        ),
        connection_manager.send_event_to_all_players(
            message=PlayerMoveMessage(
                data=PlayerMove(
                    player=player,
                    board=game.board.board,
                    winner=winner,
                    current_move_player=game.current_move_player,
                ),
                message_status=MessageStatus.SURRENDER,
            ),
            player_id=player.id,
            room_id=game.room_id,
        ),
    )


async def handle_move_state(
    *, websocket: WebSocket, move_result: CheckResult, game: Game, state_machine: GameStateMachine, player: Player
) -> IsFinishedState:
    if move_result.is_winner is True:
        await asyncio.gather(
            websocket.send_bytes(
                ClientResponse(
                    status=ResponseStatus.FINISHED,
                    message=None,
                    data=MoveCreatedResponseEvent(
                        MoveCreatedData(
                            board=game.board.board,
                            current_move_player=None,
                            winner=game._get_player_by_chip(move_result.chip),
                        )
                    ),
                ).to_json()
            ),
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
                player_id=player.id,
                room_id=game.room_id,
            ),
        )

        state_machine.change_state(GameState.FINISHED_STATE)
        return True

    await asyncio.gather(
        websocket.send_bytes(
            ClientResponse(
                status=ResponseStatus.SUCCESS,
                message=None,
                data=MoveCreatedResponseEvent(
                    MoveCreatedData(board=game.board.board, current_move_player=game.current_move_player, winner=None)
                ),
            ).to_json()
        ),
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
            player_id=player.id,
            room_id=game.room_id,
        ),
    )
    return False
