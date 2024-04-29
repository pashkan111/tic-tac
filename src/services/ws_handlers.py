from fastapi.websockets import WebSocket
import asyncio
from src.services.connection_manager import connection_manager
from src.presentation.entities.ws_game_entities import ResponseStatus, ClientResponse
from src.logic.events.responses import (
    MoveCreatedResponseEvent,
    SurrenderResponseEvent,
    SurrenderData,
    MoveCreatedData,
)
from src.logic.events.messages import (
    PlayerMove,
    PlayerMoveMessage,
    MessageStatus,
)
from src.services.state_machine import (
    GameStateMachine,
    GameState,
)
from typing import TypeAlias
from src.logic.game.game import Game
from src.logic.game.schemas import CheckResult
from src.logic.game.player import Player


IsFinishedState: TypeAlias = int


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
                    current_move_player=None,
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
        winner = game.get_player_by_chip(move_result.chip)
        await asyncio.gather(
            websocket.send_bytes(
                ClientResponse(
                    status=ResponseStatus.FINISHED,
                    message=None,
                    data=MoveCreatedResponseEvent(
                        MoveCreatedData(
                            board=game.board.board,
                            current_move_player=None,
                            winner=winner,
                        )
                    ),
                ).to_json()
            ),
            connection_manager.send_event_to_all_players(
                message=PlayerMoveMessage(
                    data=PlayerMove(
                        player=player,
                        board=game.board.board,
                        winner=winner,
                        current_move_player=None,
                    ),
                    message_status=MessageStatus.FINISH,
                ),
                player_id=player.id,
                room_id=game.room_id,
            ),
            game.finish(winner),
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
