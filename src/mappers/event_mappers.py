from src.logic.events import MoveEvent, StartGameEvent, ClientEventType
import orjson
from src.logic.exceptions import BadParamsException


EVENTS_MAPPERS = {
    ClientEventType.START: StartGameEvent,
    ClientEventType.MOVE: MoveEvent,
}


def map_event_from_client(data: str) -> StartGameEvent | MoveEvent:
    data_loaded = orjson.loads(data)
    try:
        event_type = data_loaded["event_type"]
        event_mapper = EVENTS_MAPPERS[event_type]
        return event_mapper(**data_loaded)
    except Exception:
        raise BadParamsException(**data_loaded)
