from typing import TypeAlias
from dataclasses import dataclass


UserId: TypeAlias = int
Token: TypeAlias = str


@dataclass(slots=True, frozen=True)
class PayloadData:
    user_id: UserId


@dataclass(slots=True, frozen=True)
class UserData:
    user_id: UserId
    username: str
    password: str
