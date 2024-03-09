from src.logic.events.events import MoveEventData, StartGameEventData, BaseEvent, SurrenderEventData, ClientEventType
import orjson
from src.logic.exceptions import BadParamsException


EVENTS_MAPPERS = {
    ClientEventType.START: StartGameEventData,
    ClientEventType.MOVE: MoveEventData,
    ClientEventType.SURRENDER: SurrenderEventData,
}


def map_event_from_client(data: str) -> BaseEvent:
    data_loaded = orjson.loads(data)
    try:
        event_type = data_loaded["event_type"]
        event_mapper = EVENTS_MAPPERS[event_type]
        event_data = data_loaded.get("data", {})
        event = event_mapper(**event_data)
        return BaseEvent(event_type=event_type, data=event)
    except Exception:
        raise BadParamsException(**data_loaded)
