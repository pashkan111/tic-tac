from .interfaces import (
    GameAbstract,
    CheckResult,
    Chips,
)
from collections.abc import Iterator
from .board import BoardArray
from .player import Player
from .checker import CheckerArray
from .repository import Repository
from typing import Callable, Iterable
from .exceptions import PlayersNotEnoughException, GameNotStartedException
import uuid
import itertools


# в редисе есть игрок текущий ход
# нужна функция в которую я передам этого игрока, создастся итератор и я могу 
# переключать игроков бесконечно


class Game(GameAbstract):
    room_id: uuid.UUID
    players: list[Player]
    repo: Repository
    board: BoardArray
    checker: CheckerArray
    current_move_player: Player | None
    _player_iterator: Iterator[Player]
    _started: bool = False

    def __init__(
        self,
        repo: Repository,
        board: BoardArray,
        checker: CheckerArray,
        players: list[Player],
        current_move_player: Player | None = None
    ):
        self.repo = repo
        self.board = board
        self.checker = checker
        self.players = players
        self.room_id = uuid.uuid4()
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

    async def make_move(self, row: int, col: int) -> CheckResult:
        if self._started is False:
            raise GameNotStartedException(room_id=self.room_id)

        self.board.make_move(
            player=self.current_move_player, 
            row=row, 
            col=col
        )
        check_result = self.checker.check_win(self.board)
        await self._save_state()
        self._switch_player()
        return check_result

    async def _save_state(self) -> None:
        await self.repo.set_board(self.board)
        await self.repo.set_current_move(self.current_move_player)
