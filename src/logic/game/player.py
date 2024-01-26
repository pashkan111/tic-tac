from src.logic.interfaces import PlayerAbstract
from dataclasses import dataclass
from .schemas import Chips


@dataclass(slots=True)
class Player(PlayerAbstract):
    id: int
    chip: Chips | None = None

    def __eq__(self, __value: "Player") -> bool:
        return self.id == __value.id
