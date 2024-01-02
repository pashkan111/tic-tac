import pytest
import uuid
import orjson


# @pytest.mark.asyncio
# async def test_register_user(pg, test_client, redis):
#     room_id = str(uuid.uuid4())
#     await redis.get().set(
#         key=room_id,
#         value=orjson.dumps({
#             'game_id': room_id,
#             'players': [10, 20],
#             'current_move_player': 10,
#             'board': [[0, 0, 1], [0, 0, 0], [0, 0, 0]]
#         })
#     )
#     response = await test_client.post(
#         "/game/create", json={"username": "pashkan", "password": "1111"}
#     )
#     assert response.json() == {"username": "pashkan", "id": 1}
