from python_tools.pytest_tools.conftest import *


@pytest_asyncio.fixture
async def test_client():
    import httpx
    from main import app

    async with httpx.AsyncClient(app=app, base_url="http://localhost:8000") as client:
        yield client


DEFAULT_VARS = EnvVariables(
    db_schema_path="src/repo/schema.sql",
    db_drop_schema_path="src/repo/drop_schema.sql",
    db_config_path="src.repo.repository_common",
    redis_config_path="redis.config",
)


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    os.environ["ENVIRON"] = "test"
    os.environ["DB_SCHEMA"] = DEFAULT_VARS["db_schema_path"]
    os.environ["DB_DROP_SCHEMA"] = DEFAULT_VARS["db_drop_schema_path"]
    os.environ["DB_CONFIG"] = DEFAULT_VARS["db_config_path"]
    os.environ["REDIS_CONFIG"] = DEFAULT_VARS["redis_config_path"]
