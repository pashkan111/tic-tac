from contextlib import asynccontextmanager

from fastapi import FastAPI
import asyncpg
from src.presentation.handlers.auth_handlers import user_router
from src.presentation.handlers.game_handlers import game_router
from src.presentation.handlers.ws_game_handlers import ws_game_router
from settings import POSTGRES_CONNECTION_STRING


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.repo.postgres import pg
    pool = await asyncpg.create_pool(
        dsn=POSTGRES_CONNECTION_STRING
    )
    pg.pool = pool

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(game_router)
app.include_router(ws_game_router)
