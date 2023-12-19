from dataclasses import dataclass
from enum import StrEnum
import uuid

class ClientEventType(StrEnum):
    START = 'START'
    MOVE = 'MOVE'


@dataclass
class MoveSchema:
    room_id: uuid.UUID
    player_id: int
    row: int
    col: int


@dataclass
class GameStartSchema:
    player_id: int
    rows_count: int