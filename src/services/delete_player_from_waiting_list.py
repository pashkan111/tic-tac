from src.repo.repository_game import repo


async def delete_player_from_waiting_list(rows_count: int) -> bool:
    return await repo.remove_players_from_wait_list(rows_count)
