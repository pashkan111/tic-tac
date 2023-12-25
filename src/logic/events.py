from dataclasses import dataclass
from enum import StrEnum
import uuid


class ClientEventType(StrEnum):
    START = "START"
    MOVE = "MOVE"


@dataclass
class MoveEvent:
    room_id: uuid.UUID
    player_id: int
    row: int
    col: int


@dataclass
class GameStartEvent:
    player_id: int
    rows_count: int
