import uuid

import pydantic as pd


class GameStartRequest(pd.BaseModel):
    rows_count: int
    token: str


class GameStartResponse(pd.BaseModel):
    game_started: bool
    added_to_queue: bool
    partner_id: int | None
    room_id: uuid.UUID | None


class PlayerDeleteFromWaitingRequest(pd.BaseModel):
    rows_count: int
    player_id: int


class PlayerDeleteFromWaitingResponse(pd.BaseModel):
    deleted: bool
