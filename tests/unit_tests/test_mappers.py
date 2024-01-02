from src.mappers.game_mapper import (
    map_game_data_from_redis,
    GameRedisSchema,
    Player,
    Chips,
)


def test_map_game_data_from_redis():
    data = dict(
        room_id=111,
        board=[],
        current_move_player={"id": 1, "chip": Chips.O},
        players=[{"id": 1, "chip": Chips.O}, {"id": 2, "chip": Chips.X}],
    )
    mapped = map_game_data_from_redis(data)

    assert mapped.board == []
    assert mapped.room_id == 111
    assert mapped.current_move_player == Player(id=1, chip=Chips.O)
