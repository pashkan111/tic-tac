import orjson

from src.logic.entities.events import BaseEvent, ClientEventType, MoveEventData, StartGameEventData, SurrenderEventData
from src.logic.exceptions import BadEventParamsException, BadEventTypeException

EVENT_MAPPING = {
    ClientEventType.START: StartGameEventData,
    ClientEventType.MOVE: MoveEventData,
    ClientEventType.SURRENDER: SurrenderEventData,
}


def map_event_from_client(data: str) -> BaseEvent:
    data_loaded = orjson.loads(data)
    try:
        event_type = data_loaded["event_type"]
    except KeyError:
        raise BadEventParamsException(current_params=list(data_loaded.keys()), needed_params=["event_type"])
    try:
        event_mapper = EVENT_MAPPING[event_type]
    except KeyError:
        raise BadEventTypeException(event=event_type)
    event_data = data_loaded.get("data", {})
    try:
        event = event_mapper(**event_data)
        return BaseEvent(event_type=event_type, data=event)
    except Exception:
        raise BadEventParamsException(
            current_params=list(data_loaded.keys()), needed_params=list(event_mapper.__dataclass_fields__.keys())
        )
