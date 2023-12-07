from .interfaces import GameAbstract
from .player import Player
from .board import BoardArray
from .checker import CheckerArray


class Game(GameAbstract):
    players: list[Player]
    board: BoardArray
    checker: CheckerArray

    def __init__(self, players, board, checker):
        self.players = players
        self.board = board
        self.checker = checker

    def start(self):
        ...