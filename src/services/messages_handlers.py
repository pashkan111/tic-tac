import logging

from fastapi.websockets import WebSocket

from src.logic.entities.messages import (
    BaseMessage,
    MessageStatus,
    PlayerConnectedMessage,
    PlayerDisconnectedMessage,
    PlayerMoveMessage,
    PlayerSurrenderMessage,
)
from src.logic.entities.notifications import (
    MoveCreatedData,
    MoveCreatedResponseEvent,
    PlayerConnectedData,
    PlayerConnectedResponseEvent,
    PlayerDisconnectedData,
    PlayerDisconnectedResponseEvent,
    SurrenderData,
    SurrenderResponseEvent,
)
from src.logic.enums.notification_type import NotificationType

logger = logging.getLogger(__name__)


async def run_message_handler(*, message: BaseMessage, websocket: WebSocket, player_id: int):
    handlers_mapping = {
        MessageStatus.CONNECTED: handle_player_connected_message,
        MessageStatus.DISCONNECTED: handle_player_disconnected_message,
        MessageStatus.MOVE: handle_player_made_move_message,
        MessageStatus.SURRENDER: handle_player_surrendered_message,
        MessageStatus.FINISH: handle_player_finish_message,
    }

    handler = handlers_mapping.get(message.message_status)
    if not handler:
        logger.error("There is no handler for message. Message status: %s", message.message_status)
        return

    await handler(message=message, websocket=websocket, player_id=player_id)


async def handle_player_connected_message(*, message: PlayerConnectedMessage, websocket: WebSocket, player_id: int):
    await websocket.send_bytes(
        PlayerConnectedResponseEvent(data=PlayerConnectedData(player=message.data.player)).to_json(),
    )
    print(f"Send Ws Message to player {player_id}. Message: {message}")


async def handle_player_disconnected_message(
    *, message: PlayerDisconnectedMessage, websocket: WebSocket, player_id: int
):
    await websocket.send_bytes(
        PlayerDisconnectedResponseEvent(data=PlayerDisconnectedData(player=message.data.player)).to_json(),
    )
    print(f"Send Ws Message to player {player_id}. Message: {message}")


async def handle_player_made_move_message(*, message: PlayerMoveMessage, websocket: WebSocket, player_id: int):
    await websocket.send_bytes(
        MoveCreatedResponseEvent(
            data=MoveCreatedData(
                board=message.data.board,
                current_move_player=message.data.current_move_player,
                winner=message.data.winner,
            )
        ).to_json(),
    )
    print(f"Send Ws Message to player {player_id}. Message: {message}")


async def handle_player_surrendered_message(*, message: PlayerSurrenderMessage, websocket: WebSocket, player_id: int):
    await websocket.send_bytes(
        SurrenderResponseEvent(
            data=SurrenderData(
                winner=message.data.winner,
            )
        ).to_json(),
    )
    print(f"Send Ws Message to player {player_id}. Message: {message}")


async def handle_player_finish_message(*, message: PlayerMoveMessage, websocket: WebSocket, player_id: int):
    await websocket.send_bytes(
        MoveCreatedResponseEvent(
            data=MoveCreatedData(
                board=message.data.board,
                current_move_player=None,
                winner=message.data.winner,
            ),
            notification_type=NotificationType.FINISHED,
        ).to_json(),
    )
    print(f"Send Ws Message to player {player_id}. Message: {message}")
