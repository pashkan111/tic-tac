import pytest_asyncio


@pytest_asyncio.fixture(scope="function")
async def player_1_token(test_client):
    await test_client.post(
        "/auth/register", json={"username": "pashkan", "password": "1111"}
    )

    response = await test_client.post(
        "/auth/login", json={"username": "pashkan", "password": "1111"}
    )
    return response.json()["token"]
