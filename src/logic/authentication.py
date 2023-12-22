from typing import TypeAlias
from dataclasses import dataclass, asdict
import jwt
from settings import SECRET

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
    def check_token(self, token: str) -> UserId | None:
        try:
            payload = _decode_token(token, SECRET)
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
        return payload.user_id

    def create_token(self, user_id: UserId) -> Token:
        return _create_token(payload=PayloadData(user_id=user_id), secret=SECRET)

    # async def create_user(self, username: str, password: str) -> user_id
