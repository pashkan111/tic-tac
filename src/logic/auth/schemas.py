from typing import TypeAlias
from dataclasses import dataclass
import datetime


UserId: TypeAlias = int
Token: TypeAlias = str


@dataclass(slots=True, frozen=True)
class PayloadData:
    user_id: UserId
    created_at: datetime.datetime


@dataclass(slots=True, frozen=True)
class UserData:
    user_id: UserId
    username: str
    password: str


@dataclass(slots=True, frozen=True)
class UserLoginData:
    user_id: UserId
    token: Token
