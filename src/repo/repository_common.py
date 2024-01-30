from python_tools.postgres_tools import Pg
from settings import POSTGRES_CONNECTION_STRING
from src.logic.auth.schemas import UserData


class RepositoryCommon:
    pg: Pg

    def __init__(self, pg):
        self.pg = pg

    async def create_user(self, *, username: str, password: str) -> int:
        insert_query = """
            INSERT INTO users (username, password)
            VALUES ($1, $2) RETURNING id
        """
        return await self.pg.get().fetchval(insert_query, username, password)

    async def get_user_by_username(self, username: str) -> UserData | None:
        query = """
            SELECT * FROM users
            WHERE username = $1
        """
        user = await self.pg.get().fetchrow(query, username)
        if user:
            return UserData(user_id=user["id"], username=user["username"], password=user["password"])
        return None

    async def get_user_by_id(self, id: int) -> UserData | None:
        query = """
            SELECT * FROM users
            WHERE id = $1
        """
        user = await self.pg.get().fetchrow(query, id)
        if user:
            return UserData(user_id=user["id"], username=user["username"], password=user["password"])
        return None


pg = Pg(POSTGRES_CONNECTION_STRING)
repo = RepositoryCommon(pg)
