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
