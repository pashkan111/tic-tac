from dataclasses import asdict, dataclass
from typing import Any

import orjson

from src.logic.enums.message_statuses import MessageStatus
from src.logic.game.player import Player
from src.logic.game.schemas import Board


@dataclass(slots=True)
class BaseMessage:
    """Событие, отправляемое в очередь при совершении определенных
    действий клиентом"""

    data: Any
    player_sent: Player
    message_status: MessageStatus

    def to_json(self) -> bytes:
        return orjson.dumps(asdict(self))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PlayerConnected:
    player: Player


@dataclass(slots=True)
class PlayerDisconnected:
    player: Player


@dataclass(slots=True)
class PlayerMove:
    player: Player
    board: Board
    current_move_player: Player | None
    winner: Player | None


@dataclass(slots=True)
class PlayerSurrender:
    winner: Player


@dataclass(slots=True)
class PlayerConnectedMessage(BaseMessage):
    data: PlayerConnected
    message_status: MessageStatus = MessageStatus.CONNECTED


@dataclass(slots=True)
class PlayerDisconnectedMessage(BaseMessage):
    data: PlayerDisconnected
    message_status: MessageStatus = MessageStatus.DISCONNECTED


@dataclass(slots=True)
class PlayerMoveMessage(BaseMessage):
    data: PlayerMove
    message_status: MessageStatus = MessageStatus.MOVE


@dataclass(slots=True)
class PlayerSurrenderMessage(BaseMessage):
    data: PlayerSurrender
    message_status: MessageStatus = MessageStatus.SURRENDER
