import orjson

from src.logic.game.schemas import GameRedisSchema

from .postgres import pg, PostgresConnection


class RepositoryGame:
    pg: PostgresConnection

    def __init__(self, pg):
        self.pg = pg

    async def upsert(self, game_schema: GameRedisSchema) -> None:
        query = """
            INSERT INTO game (
                player1_id,
                player2_id,
                winner,
                game_finished,
                board
            ) values ($1, $2, $3, $4, $5)
        """
        await self.pg.execute(
            command=query,
            args=[
                game_schema.players[0].id,
                game_schema.players[1].id,
                game_schema.winner.id,
                game_schema.last_updated,
                orjson.dumps(game_schema.board).decode(),
            ],
        )


game_repo = RepositoryGame(pg)
