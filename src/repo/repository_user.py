from src.logic.auth.schemas import UserData
from src.logic.exceptions import UserNotFoundException

from .postgres import Pg, pg


class RepositoryUser:
    pg: Pg

    def __init__(self, pg):
        self.pg = pg

    async def create_user(self, *, username: str, password: str) -> int:
        insert_query = """
            INSERT INTO users (username, password)
            VALUES ($1, $2) RETURNING id
        """
        return await self.pg.get().fetchval(query=insert_query, args=[username, password])

    async def get_user_by_username(self, username: str) -> UserData | None:
        query = """
            SELECT * FROM users
            WHERE username = $1
        """
        user = await self.pg.get().fetchrow(query=query, args=[username])
        if user:
            return UserData(user_id=user["id"], username=user["username"], password=user["password"])
        return None

    async def get_user_by_id(self, id: int) -> UserData:
        query = """
            SELECT * FROM users
            WHERE id = $1
        """
        user = await self.pg.get().fetchrow(query=query, args=[id])
        if user:
            return UserData(user_id=user["id"], username=user["username"], password=user["password"])
        raise UserNotFoundException(user_id=id)


user_repo = RepositoryUser(pg)
