from typing import TypeAlias
from dataclasses import dataclass, asdict
import jwt
from settings import SECRET
from src.logic.interfaces import RepositoryGameAbstract


UserId: TypeAlias = int
Token: TypeAlias = str


@dataclass(slots=True, frozen=True)
class PayloadData:
    user_id: UserId


def _create_token(payload: PayloadData, secret: str) -> Token:
    return jwt.encode(payload=asdict(payload), key=secret)


def _decode_token(token: Token, secret: str) -> PayloadData:
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    return PayloadData(**decoded)


class Authentication:
    repo: RepositoryGameAbstract
    def __init__(self, repo):
        self.repo = repo

    def _check_token(self, token: str) -> UserId | None:
        try:
            payload = _decode_token(token, SECRET)
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
        return payload.user_id

    def _create_token(self, user_id: UserId) -> Token:
        return _create_token(payload=PayloadData(user_id=user_id), secret=SECRET)

    async def register_user(self, username: str, password: str) -> UserId | None:
        ...

    async def login_user(self, username: str, password: str) -> Token | None:
        ...

    async def check_user(self, token: Token) -> UserId | None:
        ...
