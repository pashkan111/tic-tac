from logging import getLogger
from uuid import UUID

from src.logic.game.schemas import PlayerId
from src.repo.repository_game import repo

logger = getLogger(__name__)


async def connect(*, player_id: PlayerId, room_id: UUID):
    await repo.add_players_to_room(room_id=room_id, player_ids=[int(player_id)])


async def disconnect(*, player_id: PlayerId, room_id: UUID):
    await repo.remove_player_from_room(room_id=room_id, player_id=player_id)
