import asyncio
import uuid
from logging import getLogger


import settings
from src.logic.entities.messages import BaseMessage
from src.logic.exceptions import AbstractException
from src.mappers.message_mapper import map_message
from src.repo.repository_game import conn as redis_client
from src.mappers.publish_mapper import convert_dataclass_to_dict

logger = getLogger(__name__)


async def publish_message(*, channel: str, message: BaseMessage):
    await redis_client.xadd(channel=channel, data=convert_dataclass_to_dict(message))


async def read_messages(*, channel: str, queue: asyncio.Queue) -> BaseMessage | None:
    last_id = "$"
    while True:
        message_raw = await redis_client.xread(streams={channel: last_id}, count=1)
        if message_raw:
            last_id = message_raw[0][1][-1][0]
            message_text = message_raw[0][1][-1][1]
            try:
                message = map_message(message_text)
                await queue.put(message)
            except AbstractException as e:
                logger.error(e.message)


def get_channel_name(room_id: uuid.UUID) -> str:
    return f"{settings.REDIS_CHANNEL_FOR_NOTIFICATIONS}:{str(room_id)}"
