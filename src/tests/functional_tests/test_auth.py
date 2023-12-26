import pytest


@pytest.mark.asyncio
async def test_check_user__user_exists(pg, test_client):

    response = await test_client.get("/users/check_user/1234567")

    assert response.json() == {
        "data": {"user": {"telegram_id": 1234567, "user_name": "Ivan"}},
        "error": None,
        "status": 200,
    }
