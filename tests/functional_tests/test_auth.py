import pytest


@pytest.mark.asyncio
async def test_register_user(pg, test_client):
    response = await test_client.post(
        "/auth/register", json={"username": "pashkan", "password": "1111"}
    )
    assert response.json() == {"username": "pashkan", "id": 1}


@pytest.mark.asyncio
async def test_login_user(pg, test_client):
    await test_client.post(
        "/auth/register", json={"username": "pashkan", "password": "1111"}
    )

    response = await test_client.post(
        "/auth/login", json={"username": "pashkan", "password": "1111"}
    )
    assert "token" in response.json()
