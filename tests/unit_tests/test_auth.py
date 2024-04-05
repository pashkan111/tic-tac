from src.logic.auth.utils import (
    check_token,
    check_password,
    get_password_hash,
)
import pytest
from src.logic.exceptions import TokenExpiredException

import jwt
from datetime import timedelta, datetime


SECRET = "secret"
TOKEN_LIFETIME = timedelta(days=1)


def test_check_token():
    token = jwt.encode(payload={"user_id": 11, "created_at": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}, key=SECRET)
    assert check_token(token=token, secret=SECRET, token_lifetime=TOKEN_LIFETIME) == 11


def test_check_token__lifetime_exceed():
    token = jwt.encode(
        payload={"user_id": 11, "created_at": (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y, %H:%M:%S")},
        key=SECRET,
    )
    with pytest.raises(TokenExpiredException):
        check_token(token=token, secret=SECRET, token_lifetime=TOKEN_LIFETIME)


def test_passwords():
    password = "1qet6K"
    hashed_password = get_password_hash(password)
    assert check_password(hash=hashed_password, password=password) is True
