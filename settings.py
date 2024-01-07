from dotenv import load_dotenv
import os


load_dotenv()

MAX_ROWS = 30
MIN_ROWS = 3

SECRET = "UHUIOB665BBB6537b37igs67t"

POSTGRES_CONNECTION_STRING = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
)

REDIS_CONNECTION_STRING = "redis://localhost:6379"
REDIS_PLAYERS_WAITING_LIST_NAME = "players_waiting_list"
REDIS_PLAYERS_BY_ROOMS = "players_by_rooms"
REDIS_ACTIVE_PLAYERS = "active_players"
