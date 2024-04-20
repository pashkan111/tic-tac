from src.crons.archive_finished_games import archive_finished_games


async def archive_finished_games_cron():
    await archive_finished_games()
