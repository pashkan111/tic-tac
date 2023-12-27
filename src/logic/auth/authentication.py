from settings import SECRET
from .schemas import Token, UserId
from .utils import check_password, get_password_hash, create_token, check_token
from src.repo.repository_common import repo


async def register_user(*, username: str, password: str) -> UserId:
    hashed_password = get_password_hash(password)
    user_id = await repo.create_user(username=username, password=hashed_password)
    return user_id


async def login_user(*, username: str, password: str) -> Token:
    user = await repo.get_user_by_username(username)
    if not (user and check_password(hash=user.password, password=password)):
        raise Exception
    return create_token(user_id=user.user_id, secret=SECRET)


async def check_user(token: Token) -> UserId:
    user_id = check_token(token=token, secret=SECRET)
    user = await repo.get_user_by_id(user_id)
    if user:
        return user.user_id
    raise Exception
