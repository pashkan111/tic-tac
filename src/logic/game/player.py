from dataclasses import dataclass

from src.logic.interfaces import PlayerAbstract

from .schemas import Chips, PlayerId


@dataclass(slots=True)
class Player(PlayerAbstract):
    id: PlayerId
    chip: Chips | None = None

    def __eq__(self, __value: "Player") -> bool:
        return self.id == __value.id
