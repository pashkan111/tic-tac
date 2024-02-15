from src.logic.events.events import MoveEventData, StartGameEventData, BaseEvent, ClientEventType
import orjson
from src.logic.exceptions import BadParamsException


EVENTS_MAPPERS = {
    ClientEventType.START: StartGameEventData,
    ClientEventType.MOVE: MoveEventData,
}


def map_event_from_client(data: str) -> BaseEvent:
    data_loaded = orjson.loads(data)
    try:
        event_type = data_loaded["event_type"]
        event_mapper = EVENTS_MAPPERS[event_type]
        event_data = event_mapper(**data_loaded["data"])
        return BaseEvent(event_type=event_type, data=event_data)
    except Exception:
        raise BadParamsException(**data_loaded)
