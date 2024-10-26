from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(user_router)
app.include_router(game_router)
app.include_router(ws_game_router)
