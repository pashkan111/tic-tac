from src.mappers.game_mapper import (
    map_game_data_from_redis,
    Player,
    Chips,
)
from src.mappers.event_mappers import map_event_from_client
from src.logic.events.events import StartGameEventData
import json


def test_map_game_data_from_redis():
    data = dict(
        room_id=111,
        is_active=True,
        board=[],
        current_move_player={"id": 1, "chip": Chips.O},
        players=[{"id": 1, "chip": Chips.O}, {"id": 2, "chip": Chips.X}],
    )
    mapped = map_game_data_from_redis(data)

    assert mapped.board == []
    assert mapped.room_id == 111
    assert mapped.is_active is True
    assert mapped.current_move_player == Player(id=1, chip=Chips.O)


def test_map_event_from_client():
    data = {"event_type": "START", "data": {"token": "Token"}}

    event = map_event_from_client(json.dumps(data))
    assert event.event_type == "START"
    assert isinstance(event.data, StartGameEventData)
