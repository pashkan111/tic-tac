import json

from src.logic.entities.events import StartGameEventData
from src.logic.game.schemas import GameStatus
from src.mappers.event_mappers import map_event_from_client
from src.mappers.game_mapper import (
    Chips,
    Player,
    map_game_data_from_redis,
)


def test_map_game_data_from_redis():
    data = dict(
        room_id=111,
        board=[],
        game_status=GameStatus.IN_PROGRESS,
        current_move_player={"id": 1, "chip": Chips.O},
        players=[{"id": 1, "chip": Chips.O}, {"id": 2, "chip": Chips.X}],
    )
    mapped = map_game_data_from_redis(data)

    assert mapped.board == []
    assert mapped.room_id == 111
    assert mapped.current_move_player == Player(id=1, chip=Chips.O)
    assert mapped.game_status == GameStatus.IN_PROGRESS


def test_map_event_from_client():
    data = {"event_type": "START", "data": {"token": "Token"}}

    event = map_event_from_client(json.dumps(data))
    assert event.event_type == "START"
    assert isinstance(event.data, StartGameEventData)
