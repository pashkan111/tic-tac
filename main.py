from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.presentation.handlers.auth_handlers import user_router
from src.presentation.handlers.game_handlers import game_router
from src.presentation.handlers.ws_game_handlers import ws_game_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.repo.repository_user import pg

    await pg.create_pool()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(game_router)
app.include_router(ws_game_router)
