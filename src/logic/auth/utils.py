import jwt
from dataclasses import asdict
from .schemas import PayloadData, Token, UserId
from src.logic.exceptions import InvalidTokenException, TokenExpiredException
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def check_password(*, hash: str, password: str) -> bool:
    return pwd_context.verify(password, hash)


def check_token(*, token: str, secret: str, token_lifetime: timedelta) -> UserId:
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        payload = PayloadData(user_id=decoded["user_id"], created_at=_decode_datetime(decoded["created_at"]))
    except (jwt.InvalidSignatureError, jwt.exceptions.DecodeError):
        raise InvalidTokenException(token=token)
    if payload.created_at + token_lifetime < datetime.now():
        raise TokenExpiredException

    return payload.user_id


def create_token(*, user_id: UserId, secret: str) -> Token:
    return jwt.encode(payload={"user_id": user_id, "created_at": _encode_datetime(datetime.now())}, key=secret)


def _encode_datetime(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y, %H:%M:%S")


def _decode_datetime(dt: str) -> datetime:
    return datetime.strptime(dt, "%d/%m/%Y, %H:%M:%S")
