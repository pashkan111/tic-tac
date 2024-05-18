from dataclasses import dataclass

from src.logic.enums.notification_type import NotificationType
from src.logic.game.player import Player
from src.logic.game.schemas import Board

from .base_schemas import BaseNotificationEvent


@dataclass(frozen=True, slots=True)
class StartGameData:
    board: Board
    current_move_player: Player
    player: Player


@dataclass(frozen=True, slots=True)
class MoveCreatedData:
    board: Board
    current_move_player: Player | None
    winner: Player | None


@dataclass(frozen=True, slots=True)
class SurrenderData:
    winner: Player


@dataclass(frozen=True, slots=True)
class PlayerConnectedData:
    player: Player


@dataclass(frozen=True, slots=True)
class PlayerDisconnectedData:
    player: Player


@dataclass(slots=True)
class StartGameResponseEvent(BaseNotificationEvent):
    data: StartGameData
    notification_type: NotificationType = NotificationType.START


@dataclass(slots=True)
class MoveCreatedResponseEvent(BaseNotificationEvent):
    data: MoveCreatedData
    notification_type: NotificationType = NotificationType.MOVE


@dataclass(slots=True)
class SurrenderResponseEvent(BaseNotificationEvent):
    data: SurrenderData
    notification_type: NotificationType = NotificationType.SURRENDER


@dataclass(slots=True)
class PlayerConnectedResponseEvent(BaseNotificationEvent):
    data: PlayerConnectedData
    notification_type: NotificationType = NotificationType.CONNECTED


@dataclass(slots=True)
class PlayerDisconnectedResponseEvent(BaseNotificationEvent):
    data: PlayerDisconnectedData
    notification_type: NotificationType = NotificationType.DISCONNECTED
