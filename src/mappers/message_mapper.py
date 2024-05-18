import logging
from typing import Any

import orjson

from src.logic.entities.messages import (
    BaseMessage,
    MessageStatus,
    PlayerConnected,
    PlayerDisconnected,
    PlayerMove,
    PlayerSurrender,
)
from src.logic.exceptions import ParseMessageException
from src.logic.game.player import Player

logger = logging.getLogger(__name__)


MESSAGE_MAPPING = {
    MessageStatus.CONNECTED: PlayerConnected,
    MessageStatus.DISCONNECTED: PlayerDisconnected,
    MessageStatus.MOVE: PlayerMove,
    MessageStatus.SURRENDER: PlayerSurrender,
    MessageStatus.FINISH: PlayerMove,
}


def map_message(data: dict[str, Any]) -> BaseMessage | None:
    try:
        message_status = data["message_status"]
        event_mapper = MESSAGE_MAPPING[message_status]
        event_data = data["data"]
        message_data = event_mapper(**orjson.loads(event_data))
        return BaseMessage(
            data=message_data,
            message_status=MessageStatus(message_status),
            player_sent=Player(**orjson.loads(data["player_sent"])),
        )
    except Exception as e:
        raise ParseMessageException(message=str(e))
