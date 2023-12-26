from src.logic.auth.utils import create_token, check_token
from src.logic.auth.schemas import PayloadData
import jwt
import pytest

SECRET = "secret"


def test_create_token():
    token = jwt.encode(payload={"user_id": 11}, key=SECRET)
    assert create_token(user_id=11, secret=SECRET) == token


def test_check_token():
    token = jwt.encode(payload={"user_id": 11}, key=SECRET)
    assert check_token(token=token, secret=SECRET) == 11



# def test_auth_check_token(mocker):
#     mocker.patch("src.logic.authentication.SECRET", SECRET)

#     token = jwt.encode(payload={"user_id": 11}, key=SECRET)
#     auth = Authentication()

#     user_id = auth.check_token(token)
#     assert user_id == 11
