import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

MAX_ROWS = 30
MIN_ROWS = 3

SECRET = "UHUIOB665BBB6537b37igs67t"
TOKEN_LIFETIME = timedelta(days=1)


POSTGRES_CONNECTION_STRING = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

env = os.getenv("ENVIRON")
if env == "test":
    POSTGRES_CONNECTION_STRING = (
        f"postgresql://{os.getenv('TEST_POSTGRES_USER')}:{os.getenv('TEST_POSTGRES_PASSWORD')}@"
        f"{os.getenv('TEST_POSTGRES_HOST')}:{os.getenv('TEST_POSTGRES_PORT')}/{os.getenv('TEST_POSTGRES_DB')}"
    )


REDIS_CONNECTION_STRING = "redis://localhost:6379"

REDIS_PLAYERS_WAITING_LIST_NAME_KEY = "players_waiting_list"
REDIS_GAME_KEY = "game"
REDIS_PLAYERS_BY_ROOMS_KEY = "players_by_rooms"
REDIS_ACTIVE_PLAYERS_KEY = "active_players"
REDIS_CHANNEL_FOR_NOTIFICATIONS = "notifications_channel"
