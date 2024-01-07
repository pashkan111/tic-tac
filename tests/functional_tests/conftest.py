import pytest_asyncio
import dataclasses


@dataclasses.dataclass
class User:
    token: str
    id: int


@pytest_asyncio.fixture(scope="function")
async def player_1(test_client) -> User:
    await test_client.post(
        "/auth/register", json={"username": "pashkan", "password": "1111"}
    )

    response = (
        await test_client.post(
            "/auth/login", json={"username": "pashkan", "password": "1111"}
        )
    ).json()
    return User(
        token=response["token"],
        id=response["id"],
    )
