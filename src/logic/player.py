from enum import StrEnum
from .interfaces import PlayerAbstract


class Chips(StrEnum):
    X = 1
    O = 2


class Player(PlayerAbstract):
    __slots__ = ('id', 'chip')
    id: int
    chip: Chips
