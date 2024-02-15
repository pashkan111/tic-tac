from src.logic.interfaces import GameAbstract
from .schemas import Chips, CheckResult
from collections.abc import Iterator
from .board import BoardArray
from .player import Player
from .checker import CheckerArray
from src.repo.repository_game import RepositoryGame
from src.logic.exceptions import PlayersNotEnoughException, GameNotStartedException
import uuid
import itertools
from .schemas import GameRedisSchema
import asyncio


class Game(GameAbstract):
    __slots__ = (
        "room_id",
        "players",
        "repo",
        "board",
        "checker",
        "current_move_player",
        "_player_iterator",
    )
    room_id: uuid.UUID
    players: list[Player]
    repo: RepositoryGame
    board: BoardArray
    checker: CheckerArray
    current_move_player: Player
    _player_iterator: Iterator[Player]
    _started: bool = False

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

    def _set_player_iterator(self, current_move_player: Player) -> None:
        players = sorted(self.players, key=lambda player: player.id == current_move_player.id)
        players_iterator = itertools.repeat(players)
        self._player_iterator = itertools.chain.from_iterable(players_iterator)

    def _switch_player(self) -> Player:
        self.current_move_player = next(self._player_iterator)
        return self.current_move_player

    def _set_chips_to_players(self) -> None:
        chips_iterator = iter(Chips)
        for player in self.players:
            player.chip = next(chips_iterator)

    def _check_players_count(self):
        return len(self.players) > 1

    async def start(self):
        if not self._check_players_count():
            raise PlayersNotEnoughException(room_id=self.room_id)

        self._set_chips_to_players()

        if self.current_move_player is None:
            self.current_move_player = self.players[0]

        self._set_player_iterator(self.current_move_player)
        self._started = True

        await self._save_state()

    async def make_move(self, *, row: int, col: int) -> CheckResult:
        if self._started is False:
            raise GameNotStartedException(room_id=self.room_id)

        self.board.make_move(player=self.current_move_player, row=row, col=col)
        check_result = self.checker.check_win(self.board)
        self._switch_player()
        await self._save_state()
        return check_result

    async def _save_state(self) -> None:
        game_data = GameRedisSchema(
            room_id=self.room_id,
            players=self.players,
            current_move_player=self.current_move_player,
            board=self.board.board,
        )

        await asyncio.gather(
            *[
                self.repo.set_game(game_data),
                self.repo.set_game_players(player_id=self.players[0].id, room_id=self.room_id),
                self.repo.set_game_players(player_id=self.players[1].id, room_id=self.room_id),
                self.repo.add_players_to_room(
                    player_ids=[self.players[0].id, self.players[1].id],
                    room_id=self.room_id,
                ),
                self.repo.remove_players_from_wait_list(rows_count=self.board.rows_count),
            ]
        )

    async def finish(self):
        ...
