from fastapi.websockets import WebSocket
from src.repo.repository_game import repo, RepositoryGame
from uuid import UUID
from src.logic.game.schemas import PlayerId
from src.logic.events.messages import BaseMessage
from .pubsub import publish_message, get_channel_name, read_messages
from logging import getLogger


logger = getLogger(__name__)


class PlayerConnectionManager:
    active_connections: dict[PlayerId, WebSocket]
    # TODO update it after every action
    repo: RepositoryGame

    def __init__(self, repo: RepositoryGame):
        self.repo = repo
        self.active_connections: dict[PlayerId, WebSocket] = {}

    async def connect(self, *, websocket: WebSocket, player_id: PlayerId, room_id: UUID):
        if player_id in self.active_connections:
            return
        self.active_connections[player_id] = websocket
        await self.repo.add_players_to_room(room_id=room_id, player_ids=[int(player_id)])

    async def disconnect(self, *, player_id: PlayerId, room_id: UUID):
        del self.active_connections[player_id]
        await self.repo.remove_player_from_room(room_id=room_id, player_id=player_id)
        return await self.repo.get_players_from_room(room_id)

    async def send_event_to_all_players(self, *, message: BaseMessage, player_id: PlayerId, room_id: UUID):
        all_players = await self.repo.get_players_from_room(room_id)
        for player in all_players:
            if player == player_id:
                continue
            websocket = self.active_connections.get(player)
            if websocket:
                await websocket.send_bytes(message.to_json().encode())
        # channel_name =  get_channel_name(room_id)
        # await publish_message(channel=channel_name, message=message)

    async def process_messages(self, room_id: UUID) -> BaseMessage | None:
        channel = get_channel_name(room_id)
        last_id = "0-0"
        while True:
            message = await self.repo.redis_client.get().xread(streams={channel: last_id}, count=5, block=5)
            if message:
                logger.info(message)
                last_id = message[0][1][-1][0]
                message_text = message[0][1][-1][1]
                return message_text
            return None


connection_manager = PlayerConnectionManager(repo)