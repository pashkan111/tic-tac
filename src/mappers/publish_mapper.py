import dataclasses
from typing import Any

import orjson

from src.logic.entities.messages import BaseMessage


def convert_dataclass_to_dict(dataclass: BaseMessage) -> dict[str, Any]:
    result = {}
    for field in dataclass.__dataclass_fields__.keys():
        value = getattr(dataclass, field)
        if isinstance(value, (list, dict)):
            value = orjson.dumps(value)
        elif dataclasses.is_dataclass(value):
            value = orjson.dumps(dataclasses.asdict(value)).decode()
        result[field] = value
    return result
