import asyncio
from typing import TypeAlias

from fastapi.websockets import WebSocket

from src.logic.entities.messages import (
    MessageStatus,
    PlayerMove,
    PlayerMoveMessage,
    PlayerSurrenderMessage,
)
from src.logic.entities.messages import (
    PlayerSurrender as PlayerSurrenderMessageData,
)
from src.logic.entities.responses import GameMoveCreated, MoveCreatedResponse, PlayerSurrender, PlayerSurrenderResponse
from src.logic.enums.response_status import ResponseStatus
from src.logic.game.game import Game
from src.logic.game.player import Player
from src.logic.game.schemas import CheckResultNew, GameStatus
from src.services.pubsub import publish_message
from src.services.state_machine import (
    GameState,
    GameStateMachine,
)

IsFinishedState: TypeAlias = int


async def handle_surrender_state(*, websocket: WebSocket, game: Game, channel_name: str, player: Player) -> None:
    await asyncio.gather(
        websocket.send_bytes(
            PlayerSurrenderResponse(
                data=PlayerSurrender(winner=game.winner, player=player),
                response_status=ResponseStatus.SUCCESS,
                message=None,
            ).to_json()
        ),
        publish_message(
            channel=channel_name,
            message=PlayerSurrenderMessage(
                data=PlayerSurrenderMessageData(winner=game.winner),
                message_status=MessageStatus.SURRENDER,
                player_sent=player,
            ),
        ),
    )


async def handle_move_state(
    *,
    websocket: WebSocket,
    move_result: CheckResultNew,
    game: Game,
    state_machine: GameStateMachine,
    player: Player,
    channel_name: str,
) -> IsFinishedState:
    if move_result.status.is_finished:
        await asyncio.gather(
            websocket.send_bytes(
                MoveCreatedResponse(
                    message=None,
                    response_status=ResponseStatus.SUCCESS,
                    data=GameMoveCreated(
                        board=game.board.board,
                        current_move_player=None,
                        winner=game.winner,
                        player=player,
                    ),
                ).to_json()
            ),
            publish_message(
                channel=channel_name,
                message=PlayerMoveMessage(
                    data=PlayerMove(
                        player=player,
                        board=game.board.board,
                        winner=game.winner,
                        current_move_player=None,
                    ),
                    message_status=MessageStatus.FINISH,
                    player_sent=player,
                ),
            ),
        )

        state_machine.change_state(GameState.FINISHED_STATE)
        return True

    await asyncio.gather(
        websocket.send_bytes(
            MoveCreatedResponse(
                response_status=ResponseStatus.SUCCESS,
                message=None,
                data=GameMoveCreated(
                    board=game.board.board, current_move_player=game.current_move_player, winner=None, player=player
                ),
            ).to_json()
        ),
        publish_message(
            channel=channel_name,
            message=PlayerMoveMessage(
                data=PlayerMove(
                    player=player,
                    board=game.board.board,
                    winner=None,
                    current_move_player=game.current_move_player,
                ),
                message_status=MessageStatus.MOVE,
                player_sent=player,
            ),
        ),
    )
    return False
