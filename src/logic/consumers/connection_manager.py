from fastapi.websockets import WebSocket
from src.repo.repository_game import repo, RepositoryGame
from uuid import UUID
from src.logic.game.schemas import PlayerId


class PlayerConnectionManager:
    active_connections: dict[PlayerId, WebSocket]
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

    async def send_event_to_all_players(self, *, event, player_id: PlayerId, room_id: UUID):
        all_players = await self.repo.get_players_from_room(room_id)
        for player in all_players:
            if player == player_id:
                continue
            await self.active_connections[player].send_bytes(event)


connection_manager = PlayerConnectionManager(repo)
