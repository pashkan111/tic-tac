import pydantic as pd

from enum import StrEnum


class Status(StrEnum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class BaseResponse(pd.BaseModel):
    status: Status
    message: str | None


class GameStartResponse(BaseResponse): ...
