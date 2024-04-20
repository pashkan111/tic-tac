from settings import SECRET, TOKEN_LIFETIME
from .schemas import Token, UserId, UserLoginData
from .utils import check_password, get_password_hash, create_token, check_token
from src.repo.repository_user import user_repo
from src.logic.exceptions import UserInvalidCredsException, UsernameAlreadyExistsException, UserInvalidPasswordException
from asyncpg.exceptions import UniqueViolationError


async def register_user(*, username: str, password: str) -> UserId:
    hashed_password = get_password_hash(password)
    try:
        user_id = await user_repo.create_user(username=username, password=hashed_password)
    except UniqueViolationError:
        raise UsernameAlreadyExistsException(username=username)
    return user_id


async def login_user(*, username: str, password: str) -> UserLoginData:
    user = await user_repo.get_user_by_username(username)
    if not user:
        raise UserInvalidCredsException(username=username)
    if not check_password(hash=user.password, password=password):
        raise UserInvalidPasswordException

    token = create_token(user_id=user.user_id, secret=SECRET)
    return UserLoginData(user_id=user.user_id, token=token)


async def check_user(token: Token) -> UserId:
    user_id = check_token(token=token, secret=SECRET, token_lifetime=TOKEN_LIFETIME)
    user = await user_repo.get_user_by_id(user_id)
    return user.user_id
