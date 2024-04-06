from src.repo.repository_game import repo


async def delete_finished_games_from_redis():
    """Removes ald and finished games from redis"""
