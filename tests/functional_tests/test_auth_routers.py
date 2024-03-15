import pytest


@pytest.mark.asyncio
async def test_register_user(pg, test_client):
    response = await test_client.post("/auth/register", json={"username": "pashkan", "password": "1111"})
    assert response.json() == {"username": "pashkan", "id": 1}


@pytest.mark.asyncio
async def test_login_user(pg, test_client):
    await test_client.post("/auth/register", json={"username": "pashkan", "password": "1111"})

    response = await test_client.post("/auth/login", json={"username": "pashkan", "password": "1111"})
    token = response.json()["token"]

    response = await test_client.post("/auth/check_token", json={"token": token})
    assert response.json() == {"user_id": 1}


@pytest.mark.asyncio
async def test_check_token(pg, test_client, player_1):
    response = await test_client.post("/auth/check_token", json={"token": player_1.token})
    assert response.json() == {"user_id": player_1.id}
    response = await test_client.post("/auth/check_token", json={"token": "12344"})
    assert response.json() == {"detail": "Invalid Token. Token: 12344"}
