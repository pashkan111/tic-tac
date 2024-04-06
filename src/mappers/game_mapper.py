from src.logic.game.schemas import GameRedisSchema, Chips
from src.logic.game.player import Player
from typing import Any


def map_player(*, player_id: int, chip: Chips | None = None) -> Player:
    return Player(id=player_id, chip=chip)


def map_game_data_from_redis(data: dict[str, Any]) -> GameRedisSchema:
    return GameRedisSchema(
        room_id=data["room_id"],
        board=data["board"],
        is_active=data["is_active"],
        current_move_player=map_player(
            player_id=data["current_move_player"]["id"],
            chip=Chips(data["current_move_player"]["chip"]),
        ),
        players=[map_player(player_id=player["id"], chip=player["chip"]) for player in data["players"]],
        winner=map_player(
            player_id=data["winner"]["id"],
            chip=Chips(data["winner"]["chip"]),
        )
        if data.get("winner")
        else None,
    )
