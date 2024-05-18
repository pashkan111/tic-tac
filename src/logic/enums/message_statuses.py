from enum import StrEnum


class MessageStatus(StrEnum):
    """Types of messages"""

    CONNECTED = "CONNECTED"
    """Player connected to the room"""
    DISCONNECTED = "DISCONNECTED"
    """Player disconnected from the room"""
    MOVE = "MOVE"
    """Player made move"""
    FINISH = "FINISH"
    """Game is finished"""
    SURRENDER = "SURRENDER"
    """One player surrendered"""
