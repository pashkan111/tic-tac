import jwt
from dataclasses import asdict
from .schemas import PayloadData, Token, UserId

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def check_password(*, hash: str, password: str) -> bool:
    return pwd_context.verify(password, hash)


def check_token(*, token: str, secret: str) -> UserId:
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        payload = PayloadData(**decoded)
    except jwt.InvalidSignatureError:
        raise Exception("Invalid token")
    return payload.user_id


def create_token(*, user_id: UserId, secret: str) -> Token:
    return jwt.encode(payload=asdict(PayloadData(user_id=user_id)), key=secret)
