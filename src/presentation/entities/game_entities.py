import pydantic as pd
import uuid


class GameStartRequest(pd.BaseModel):
    rows_count: int
    token: str


class GameStartResponse(pd.BaseModel):
    game_started: bool
    partner_id: int | None
    room_id: uuid.UUID | None
