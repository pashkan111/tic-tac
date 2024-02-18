from dataclasses import dataclass, asdict
from enum import StrEnum
from typing import Any
from src.logic.game.schemas import Board
from src.logic.game.player import Player
import orjson

"""
Messages for sending to all participants in the room
"""


class MessageStatus(StrEnum):
    """Types of messages"""

    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    MOVE = "MOVE"
    FINISH = "FINISH"


class MessageType(StrEnum):
    RESPONSE = "RESPONSE"
    MESSAGE = "MESSAGE"


@dataclass
class BaseMessage:
    data: Any
    message_status: MessageStatus
    type: MessageType

    def to_json(self) -> str:
        return orjson.dumps(asdict(self)).decode()


@dataclass
class PlayerConnected:
    player: Player


@dataclass
class PlayerDisconnected:
    player: Player


@dataclass
class PlayerMove:
    player: Player
    board: Board
    current_move_player: Player | None
    winner: Player | None


@dataclass
class PlayerConnectedMessage(BaseMessage):
    data: PlayerConnected
    type: MessageType = MessageType.MESSAGE
    message_status: MessageStatus = MessageStatus.CONNECTED


@dataclass
class PlayerDisconnectedMessage(BaseMessage):
    data: PlayerDisconnected
    type: MessageType = MessageType.MESSAGE
    message_status: MessageStatus = MessageStatus.DISCONNECTED


@dataclass
class PlayerMoveMessage(BaseMessage):
    data: PlayerMove
    message_status: MessageStatus
    type: MessageType = MessageType.MESSAGE
