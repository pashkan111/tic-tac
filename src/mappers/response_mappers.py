from dataclasses import asdict
from orjson import dumps
from src.presentation.entities.ws_game_entities import BaseResponse


def map_response(response_class: BaseResponse) -> bytes:
    return dumps(asdict(response_class))
