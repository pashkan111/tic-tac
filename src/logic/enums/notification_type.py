from enum import StrEnum


class NotificationType(StrEnum):
    """Статусы ответов клиенту"""

    START = "START"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    MOVE = "MOVE"
    FINISHED = "FINISHED"
    SURRENDER = "SURRENDER"
