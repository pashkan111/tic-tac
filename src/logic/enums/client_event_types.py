from enum import StrEnum


class ClientEventType(StrEnum):
    START = "START"
    """Событие начала игры. На этом этапе происходит авторизация"""
    MOVE = "MOVE"
    """Событие хода"""
    SURRENDER = "SURRENDER"
    """Событие сдачи"""
