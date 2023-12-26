import jwt
from dataclasses import asdict
from .schemas import PayloadData, Token, UserId
import bcrypt


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return str(hashed)


def check_password(*, hash: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash.encode())


def check_token(*, token: str, secret: str) -> UserId:
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        payload = PayloadData(**decoded)
    except jwt.InvalidSignatureError:
        raise Exception("Invalid token")
    return payload.user_id


def create_token(*, user_id: UserId, secret: str) -> Token:
    return jwt.encode(
        payload=asdict(PayloadData(user_id=user_id)), key=secret
    )
