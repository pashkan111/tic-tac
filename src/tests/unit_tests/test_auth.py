from src.logic.authentication import (
    _create_token,
    _decode_token,
    PayloadData,
    Authentication,
)
import jwt
import pytest

SECRET = "secret"


def test_create_token():
    token = jwt.encode(payload={"user_id": 11}, key=SECRET)
    assert _create_token(PayloadData(user_id=11), SECRET) == token


def test_decode_token():
    token = jwt.encode(payload={"user_id": 11}, key=SECRET)
    assert _decode_token(token, SECRET) == PayloadData(user_id=11)


def test_decode_token__raise_exc():
    token = jwt.encode(payload={"user_id": 11}, key=SECRET)
    token += "a"
    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        _decode_token(token, SECRET)


# def test_auth_check_token(mocker):
#     mocker.patch("src.logic.authentication.SECRET", SECRET)

#     token = jwt.encode(payload={"user_id": 11}, key=SECRET)
#     auth = Authentication()

#     user_id = auth.check_token(token)
#     assert user_id == 11
