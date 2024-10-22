import asyncio
import uuid

from src.logic.exceptions import (
    GameNotActiveException,
    MoveTurnException,
    PlayersNotEnoughException,
    RoomNotFoundInRepoException,
)
from src.logic.interfaces import GameAbstract
from src.repo.repository_game import RepositoryGame

from .board import BoardArray
from .checker import CheckerArray
from .player import Player
from .schemas import CheckResultNew, Chips, GameRedisSchema, GameStatus, PlayerId


class Game(GameAbstract):
    room_id: uuid.UUID
    players: list[Player]
    repo: RepositoryGame
    board: BoardArray
    checker: CheckerArray
    current_move_player: Player | None
    winner: Player | None
    game_status: GameStatus | None

    def __init__(
        self,
        repo: RepositoryGame,
        board: BoardArray,
        checker: CheckerArray,
        players: list[Player],
        current_move_player: Player | None = None,
        room_id: uuid.UUID | None = None,
    ):
        self.repo = repo
        self.board = board
        self.checker = checker
        self.players = players
        self.room_id = room_id or uuid.uuid4()
        self.current_move_player = current_move_player
        self.winner = None

    def _switch_player(self) -> None:
        self.current_move_player = list(
            filter(
                lambda player: player.id != self.current_move_player.id,
                self.players,
            )
        )[0]

    def get_player_by_chip(self, chip: Chips) -> Player:
        return list(filter(lambda player: player.chip == chip, self.players))[0]

    def get_player_by_id(self, player_id: PlayerId) -> Player:
        return list(filter(lambda player: player.id == player_id, self.players))[0]

    def _set_chips_to_players(self) -> None:
        chips_iterator = iter(Chips)
        for player in self.players:
            player.chip = next(chips_iterator)

    def _check_players_count(self):
        return len(self.players) > 1

    def _check_player_move(self, player_id: PlayerId):
        if not player_id == self.current_move_player.id:
            raise MoveTurnException(player_id=self.current_move_player.id)

    async def _update_state(self):
        game_data = await self.repo.get_game(self.room_id)
        if not game_data:
            raise RoomNotFoundInRepoException(room_id=self.room_id)
        self.current_move_player = game_data.current_move_player
        self.board.board = game_data.board
        self.game_status = game_data.game_status
        self.winner = game_data.winner
        self.game_status = game_data.game_status

    async def _save_state(self) -> None:
        game_data = GameRedisSchema(
            room_id=self.room_id,
            players=self.players,
            current_move_player=self.current_move_player,
            board=self.board.board,
            game_status=self.game_status,
            winner=self.winner,
        )
        await self.repo.set_game(game_data)

    async def start(self):
        if not self._check_players_count():
            raise PlayersNotEnoughException(room_id=self.room_id)

        self._set_chips_to_players()

        if self.current_move_player is None:
            self.current_move_player = self.players[0]

        self.game_status = GameStatus.IN_PROGRESS

        await asyncio.gather(
            self.repo.remove_players_from_wait_list(rows_count=self.board.rows_count),
            self.repo.set_game_players(player_id=self.players[0].id, room_id=self.room_id),
            self.repo.set_game_players(player_id=self.players[1].id, room_id=self.room_id),
            self.repo.add_players_to_room(
                player_ids=[self.players[0].id, self.players[1].id],
                room_id=self.room_id,
            ),
            self._save_state(),
        )

    async def make_move(self, *, player_id: PlayerId, row: int, col: int) -> CheckResultNew:
        await self._update_state()
        if not (self.game_status and self.game_status.in_progress and self.current_move_player):
            raise GameNotActiveException(room_id=self.room_id)

        self._check_player_move(player_id)
        self.board.make_move(player=self.current_move_player, row=row, col=col)
        check_result = self.checker.check_win_or_draw(self.board)
        if check_result.status.is_finished:
            self.winner = self.get_player_by_chip(check_result.winner) if check_result.winner else None
            await self._save_state()
            await self.finish(winner=self.winner)
            return check_result

        self._switch_player()
        await self._save_state()
        return check_result

    async def finish(self, winner: Player | None):
        print("finish")
        await self._update_state()
        self.winner = winner
        self.game_status = GameStatus.VICTORY if winner else GameStatus.DRAW
        self.current_move_player = None
        await self._save_state()

        for player in self.players:
            await self.repo.remove_player_active_game(player_id=player.id)

    async def surrender(self, player_id: PlayerId):
        await self._update_state()
        self.winner = list(filter(lambda p: p.id != player_id, self.players))[0]
        await self.finish(winner=self.winner)
