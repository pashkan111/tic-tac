from src.logic.exceptions import (
    UserInvalidCredsException,
    UsernameAlreadyExistsException,
    InvalidTokenException,
    UserInvalidPasswordException,
)
from fastapi.exceptions import HTTPException
from fastapi import status
from functools import wraps
from typing import Callable


def error_handler(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (
            UserInvalidCredsException,
            UsernameAlreadyExistsException,
            InvalidTokenException,
            UserInvalidPasswordException,
        ) as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return wrapper
