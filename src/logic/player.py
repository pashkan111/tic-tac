from .interfaces import PlayerAbstract


class Player(PlayerAbstract):
    __slots__ = ("id", "chip")

    def __init__(self, id, chip=None):
        self.id = id
        self.chip = chip

    def __repr__(self) -> str:
        return f"<Player {self.id}>"
